import sys
import os
import contextlib

from nose.tools import with_setup

import avalon.io
import avalon.inventory
import avalon_to_cgwire
import gazu
import pymongo
from bson.objectid import ObjectId


self = sys.modules[__name__]


os.environ["AVALON_PROJECT"] = "temp"
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

        # CGWire projects needs to be closed before deletion.
        gazu.project.close_project(project)
        gazu.project.remove_project(project, force=True)

    avalon.io.delete_many({})


@with_setup(setup, teardown)
def test_project_sync():
    """Syncing project from Avalon to CGWire works."""
    project_name = "temp"
    avalon.inventory.create_project(project_name)
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]
    avalon_project = db[project_name].find_one({"type": "project"})

    avalon_to_cgwire.full_sync()

    # There should only be one project in CGWire at this point.
    cgwire_project = gazu.project.all_projects()[0]

    assert avalon_project["name"] == cgwire_project["name"]
    assert str(avalon_project["_id"]) == cgwire_project["data"]["id"]


# Avalon project to CGWire project. Name, tasks, ID.
# Avalon asset to CGWire asset. Name, task, ID.
# Avalon sequence to CGWire sequence. Name, ID.
# Avalon sequence/shot to CGWire sequence/shot. Name, tasks, ID.
# Avalon episode to CGWire episode. Name, ID.
# Avalon episode/sequence to CGWire episode/sequence. Name, ID.
# Avalon episode/sequence/shot to CGWire episode/sequence/shot. Name, tasks, ID.
