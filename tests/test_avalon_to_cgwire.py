import sys
import os
import contextlib

from nose.tools import with_setup

import avalon.io
import avalon.inventory
import avalon_to_cgwire
import gazu
import pymongo


self = sys.modules[__name__]


os.environ["AVALON_PROJECT"] = "batman"
os.environ["AVALON_ASSET"] = "bruce"
os.environ["AVALON_SILO"] = "assets"
avalon.io.install()


@contextlib.contextmanager
def setup():
    pass


@contextlib.contextmanager
def teardown():
    for project in gazu.project.all_projects():
        for shot in gazu.shot.all_shots_for_project(project):
            gazu.shot.remove_shot(shot, force=True)
        for asset in gazu.asset.all_assets_for_project(project):
            gazu.asset.remove_asset(asset, force=True)

        for sequence in gazu.shot.all_sequences_for_project(project):
            gazu.shot.remove_sequence(sequence)

        # CGWire projects needs to be closed before deletion.
        gazu.project.close_project(project)
        gazu.project.remove_project(project, force=True)

    avalon.io.delete_many({})


@with_setup(setup, teardown)
def test_project_sync():
    """Syncing project from Avalon to CGWire works."""
    project_name = "batman"
    project_id = avalon.inventory.create_project(project_name)
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_project = db[project_name].find_one({"_id": project_id})

    avalon_to_cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    assert avalon_project["name"] == cgwire_project["name"]
    assert str(avalon_project["_id"]) == cgwire_project["data"]["avalon_id"]

    task_types = [x["name"] for x in gazu.task.all_task_types()]
    missing_task_types = []
    for task in avalon_project["config"]["tasks"]:
        if task["name"].title() not in task_types:
            missing_task_types.append(task)

    assert not missing_task_types


@with_setup(setup, teardown)
def test_asset_sync():
    """Syncing asset from Avalon to CGWire works."""
    project_name = "batman"
    project_id = avalon.inventory.create_project(project_name)
    asset_id = avalon.inventory.create_asset(
        "Bruce", "assets", {"tasks": ["modeling"]}, project_id
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_asset = db[project_name].find_one({"_id": asset_id})

    avalon_to_cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    # There should only be one asset in CGWire at this point.
    cgwire_asset = gazu.asset.all_assets_for_project(cgwire_project)[0]

    assert avalon_asset["name"] == cgwire_asset["name"]
    assert str(avalon_asset["_id"]) == cgwire_asset["data"]["avalon_id"]

    cgwire_tasks = [
        task["name"] for task in gazu.task.all_tasks_for_asset(cgwire_asset)
    ]
    assert avalon_asset["data"]["tasks"] == cgwire_tasks


@with_setup(setup, teardown)
def test_sequence_sync():
    """Syncing sequence from Avalon to CGWire works."""
    project_name = "batman"
    project_id = avalon.inventory.create_project(project_name)
    sequence_id = avalon.inventory.create_asset(
        "sequence", "film", {}, project_id
    )
    shot_id = avalon.inventory.create_asset(
        "shot",
        "film",
        {"tasks": ["layout"], "visualParent": sequence_id},
        project_id
    )

    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_sequence = db[project_name].find_one({"_id": sequence_id})
    avalon_shot = db[project_name].find_one({"_id": shot_id})

    avalon_to_cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    # There should only be one sequence in CGWire at this point.
    cgwire_sequence = gazu.shot.all_sequences_for_project(cgwire_project)[0]

    assert avalon_sequence["name"] == cgwire_sequence["name"]
    assert str(avalon_sequence["_id"]) == cgwire_sequence["data"]["avalon_id"]

    # There should only be one shot in CGWire at this point.
    cgwire_shot = gazu.shot.all_shots_for_project(cgwire_project)[0]

    assert avalon_shot["name"] == cgwire_shot["name"]
    assert str(avalon_shot["_id"]) == cgwire_shot["data"]["avalon_id"]

    cgwire_tasks = [
        task["name"] for task in gazu.task.all_tasks_for_shot(cgwire_shot)
    ]
    assert avalon_shot["data"]["tasks"] == cgwire_tasks

# Avalon sequence/shot to CGWire sequence/shot: sequence name, sequence id, shot name, shot tasks, shot id.
# Avalon episode/sequence/shot to CGWire episode/sequence/shot: episode name, episode tasks, episode id, sequence name, sequence tasks, sequence id, shot name, shot tasks, shot id.
