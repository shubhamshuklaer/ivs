from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps


def apply_data(db_name,data):
    commits_list=data["commits"]
    patches_list=data["patches"]
    branches_list=data["branches"]
    files_list=data["files"]

    mongo_conn=Connection()
    db=mongo_conn[db_name]

    for commit in commits_list:
        db.commits.update({"uid":commit["uid"]},
                {
                    "$set":{
                        "uid":commit["uid"],
                        "patch_ids": commit["patch_ids"],
                        "ts": commit["ts"],
                        "msg": commit["msg"],
                        "added": commit["added"],
                        "deleted": commit["deleted"],
                        "parent_id": commit["parent_id"],
                        "branch": commit["branch"],
                        "num": commit["num"],
                        "level": commit["level"]
                    },
                    "$addToSet": { "child_ids" : commit["child_ids"]},
                    },
                upsert=True
                )

    for patch in patches_list:
        db.patches.insert(patch)

    for branch in branches_list:
        db.branch.update({"name":branch["name"]},
                {
				"name": branch["name"],
				"commit_ids": branch["commit_ids"],
				"head": branch["head"],
				"tail": branch["tail"],
				"parent_branches": branch["parent_branches"],
                    },
                upsert=True
                )

    for entity in files_list:
        db.files.update({"path":entity["path"]},
                {
                    "$set":{
                        "name": entity["name"],
                        "path": entity["path"],
                        "staged": entity["staged"],
                        "staged_ts": entity["staged_ts"],
                        "is_present": entity["is_present"],
                        "to_remove": entity["to_remove"],
                        "to_add": entity["to_add"],
                        "added_cids": entity["added_cids"],
                    },
                    "$addToSet":{
                        "patch_ids": entity["patch_ids"],
                        "deleted_cids": entity["deleted_cids"]
                        }
                    },
                upsert=True
                )
