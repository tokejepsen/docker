import os
import json

import pymongo
from bson import json_util
import gazu


def get_project(avalon_project):
    for project in gazu.project.all_projects():
        if project["data"].get("avalon_id", "") == str(avalon_project["_id"]):
            print("Found existing project by id. Project: {}".format(project))
            return project

    print(
        "Creating new project:\nProject Name: {}".format(
            avalon_project["name"]
        )
    )
    return gazu.project.new_project(avalon_project["name"])


def update_project(avalon_project):
    """Update CGWire project with Avalon project data.

    Args:
        project (dict): Avalon project.
    """
    cgwire_project = get_project(avalon_project)

    # Update task data.
    task_types = [x["name"] for x in gazu.task.all_task_types()]
    for task in avalon_project["config"]["tasks"]:
        if task["name"].title() in task_types:
            continue
        gazu.task.new_task_type(task["name"].title())

    avalon_project["config"].pop("tasks")

    # Update project data.
    data = json.loads(json_util.dumps(avalon_project["data"]))
    data.update(avalon_project["config"])
    data["avalon_id"] = str(avalon_project["_id"])

    cgwire_project.update({
        "code": avalon_project["name"].replace(" ", "_").lower(),
        "data": data,
        "name": avalon_project["name"]
    })
    gazu.project.update_project(cgwire_project)

    return cgwire_project


def get_asset(cgwire_project, avalon_asset):
    cgwire_asset = None
    for asset in gazu.asset.all_assets_for_project(cgwire_project):
        # Search for existing asset with id.
        if asset["data"].get("avalon_id", "") == str(avalon_asset["_id"]):
            print("Found existing asset by id.")
            cgwire_asset = asset
            break

        # Search for existing asset with label/name.
        name = avalon_asset["data"].get("label", avalon_asset["name"])
        if asset["name"] == name:
            print("Found existing asset by label/name.")
            cgwire_asset = asset

    if cgwire_asset is None:
        print(
            "Creating new asset:\nProject: {}\nAsset Type: {}"
            "\nAsset Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                gazu.asset.all_asset_types()[0],
                avalon_asset["name"]
            )
        )
        cgwire_asset = gazu.asset.new_asset(
            cgwire_project,
            gazu.asset.all_asset_types()[0],  # There are no default asset type
            # in Avalon, so we take the first available asset type.
            avalon_asset["name"]
        )

    return cgwire_asset


def update_asset(cgwire_project, avalon_asset):
    cgwire_asset = get_asset(cgwire_project, avalon_asset)

    # Update task data.
    task_types = {x["name"]: x for x in gazu.task.all_task_types()}
    for task_name in avalon_asset["data"].get("tasks", []):
        gazu.task.new_task(
            cgwire_asset, task_types[task_name.title()], name=task_name
        )
    avalon_asset["data"].pop("tasks", None)

    # Update asset data.
    data = json.loads(json_util.dumps(avalon_asset["data"]))
    data["avalon_id"] = str(avalon_asset["_id"])

    cgwire_asset.update({
        "data": data,
        "name": avalon_asset["data"].get("label", avalon_asset["name"])
    })
    gazu.asset.update_asset(cgwire_asset)

    return cgwire_asset


def get_sequence(cgwire_project, avalon_asset, episode=None):
    sequences = []
    if episode:
        sequences = gazu.shot.all_sequences_for_episode(episode)
    else:
        sequences = gazu.shot.all_sequences_for_project(cgwire_project)

    cgwire_sequence = None
    for sequence in sequences:
        # Search for existing sequence with id.
        if sequence["data"].get("avalon_id", "") == str(avalon_asset["_id"]):
            print("Found existing sequence by id.")
            cgwire_sequence = sequence
            break

        # Search for existing sequence with label/name.
        name = avalon_asset["data"].get("label", avalon_asset["name"])
        if sequence["name"] == name:
            print("Found existing sequence by label/name.")
            cgwire_sequence = sequence

    if cgwire_sequence is None:
        print(
            "Creating new sequence:\nProject: {}\nName: {}"
            "\nEpisode: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                avalon_asset["name"],
                json.dumps(episode, sort_keys=True, indent=4)
            )
        )
        cgwire_sequence = gazu.shot.new_sequence(
            cgwire_project,
            avalon_asset["name"],
            episode=episode
        )

    return cgwire_sequence


def update_sequence(cgwire_project, avalon_asset, episode=None):
    cgwire_sequence = get_sequence(cgwire_project, avalon_asset, episode)

    # Update asset data.
    data = json.loads(json_util.dumps(avalon_asset["data"]))
    data["avalon_id"] = str(avalon_asset["_id"])

    cgwire_sequence.update({
        "data": data,
        "name": avalon_asset["data"].get("label", avalon_asset["name"])
    })
    gazu.shot.update_sequence(cgwire_sequence)

    return cgwire_sequence


def get_episode(cgwire_project, avalon_asset):
    cgwire_episode = None
    for episode in gazu.shot.all_episodes_for_project(cgwire_project):
        # Search for existing sequence with id.
        if episode["data"]:
            if episode["data"].get("avalon_id", "") == str(avalon_asset["_id"]):
                print("Found existing episode by id.")
                cgwire_episode = episode
                break

        # Search for existing sequence with label/name.
        name = avalon_asset["data"].get("label", avalon_asset["name"])
        if episode["name"] == name:
            print("Found existing episode by label/name.")
            cgwire_episode = episode

    if cgwire_episode is None:
        print(
            "Creating new episode:\nProject: {}\nEpisode Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                avalon_asset["name"]
            )
        )
        cgwire_episode = gazu.shot.new_episode(
            cgwire_project,
            avalon_asset["name"]
        )

    return cgwire_episode


def update_episode(cgwire_project, avalon_asset):
    cgwire_episode = get_episode(cgwire_project, avalon_asset)

    # Update asset data.
    data = json.loads(json_util.dumps(avalon_asset["data"]))
    data["avalon_id"] = str(avalon_asset["_id"])

    cgwire_episode.update({
        "data": data,
        "name": avalon_asset["data"].get("label", avalon_asset["name"])
    })
    gazu.shot.update_episode(cgwire_episode)

    return cgwire_episode


def get_shot(cgwire_project, cgwire_sequence, avalon_asset):
    cgwire_shot = None
    for shot in gazu.shot.all_shots_for_sequence(cgwire_sequence):
        # Search for existing sequence with id.
        if shot["data"].get("avalon_id", "") == str(avalon_asset["_id"]):
            print("Found existing shot by id.")
            cgwire_shot = shot
            break

        # Search for existing sequence with label/name.
        name = avalon_asset["data"].get("label", avalon_asset["name"])
        if shot["name"] == name:
            print("Found existing shot by label/name.")
            cgwire_shot = shot

    if cgwire_shot is None:
        print(
            "Creating new shot:\nProject: {}\nSequence: {}"
            "\nShot Name: {}".format(
                json.dumps(cgwire_project, sort_keys=True, indent=4),
                json.dumps(cgwire_sequence, sort_keys=True, indent=4),
                avalon_asset["name"]
            )
        )
        cgwire_shot = gazu.shot.new_shot(
            cgwire_project,
            cgwire_sequence,
            avalon_asset["name"]
        )

    return cgwire_shot


def update_shot(cgwire_project, cgwire_sequence, avalon_asset):
    cgwire_shot = get_shot(cgwire_project, cgwire_sequence, avalon_asset)

    # Update task data.
    task_types = {x["name"]: x for x in gazu.task.all_task_types()}
    for task_name in avalon_asset["data"].get("tasks", []):
        gazu.task.new_task(
            cgwire_shot, task_types[task_name.title()], name=task_name
        )
    avalon_asset["data"].pop("tasks", None)

    # Update asset data.
    data = json.loads(json_util.dumps(avalon_asset["data"]))
    data["avalon_id"] = str(avalon_asset["_id"])

    cgwire_shot.update({
        "data": data,
        "name": avalon_asset["data"].get("label", avalon_asset["name"])
    })
    gazu.shot.update_shot(cgwire_shot)

    return cgwire_shot


def get_visual_child_ids(database, asset, children=[]):
    for child in database.find({"data.visualParent": asset["_id"]}):
        children.append(child["_id"])
        return get_visual_child_ids(database, child, children)
    return children


def get_visual_children(database, asset):
    ids = get_visual_child_ids(database, asset)
    children = []
    for id in ids:
        child = database.find_one({"_id": id})
        if child:
            children.append(child)
    return children


def full_sync():
    gazu.client.set_host("http://127.0.0.1/api")
    gazu.log_in("admin@example.com", "mysecretpassword")

    # Mapping.
    silo_mapping = {"film": "shot", "assets": "asset"}

    # Collect all projects data in Mongo.
    client = pymongo.MongoClient(os.environ["AVALON_MONGO"])
    db = client["avalon"]

    for name in db.collection_names():
        cgwire_project = update_project(db[name].find_one({"type": "project"}))
        for asset in db[name].find({"type": "asset"}):
            if silo_mapping[asset["silo"]] == "asset":
                update_asset(cgwire_project, asset)

            if silo_mapping[asset["silo"]] == "shot":
                # If the asset has a visual parent skip.
                if asset["data"].get("visualParent", None):
                    print("Skipping {} due to visual parent.".format(asset))
                    continue

                # Query visual children for hierarchy.
                children = get_visual_children(db[name], asset)

                # One visual child == sequence.
                if len(children) == 1:
                    cgwire_sequence = update_sequence(
                        cgwire_project, asset
                    )
                    update_shot(cgwire_project, cgwire_sequence, children[0])

                # Two visual children == episode/sequence.
                if len(children) == 2:
                    cgwire_episode = update_episode(
                        cgwire_project, asset
                    )
                    cgwire_sequence = update_sequence(
                        cgwire_project,
                        children[0],
                        episode=cgwire_episode
                    )
                    update_shot(cgwire_project, cgwire_sequence, children[1])
