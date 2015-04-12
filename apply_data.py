from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps
from ivs_base import ivs


def apply_data(db_name,data,root_path):
    commits_list=data["commits"]
    patches_list=data["patches"]
    branches_list=data["branches"]
    files_list=data["files"]
    param_entry=data["params"]

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
                    "$addToSet": { "child_ids" :{"$each": commit["child_ids"]}},
                    },
                upsert=True
                )

    for patch in patches_list:
        db.patches.insert(patch)

    for branch in branches_list:
        db.branches.update({"name":branch["name"]},
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
                        "patch_ids": {"$each":entity["patch_ids"]},
                        "deleted_cids":{"$each": entity["deleted_cids"]}
                        }
                    },
                upsert=True
                )

    if len(commits_list)>0 and param_entry !=None:
        db.params.update({"path":root_path},
                {
                        "path": root_path,
                        "dbname": db_name,
                        "first_cid": param_entry["first_cid"],
                        "cur_com_num": param_entry["cur_com_num"],
                        "last_cid": param_entry["last_cid"],
                        "cur_com_level": param_entry["cur_com_level"],
                        "cur_branch": param_entry["cur_branch"],
                        "cur_patch_num": param_entry["cur_patch_num"],
                    },
                upsert=True
                )

    repo=ivs()
    repo.set_path(root_path)
    repo.set_dbname(db_name)
    repo.load_params()
    param = self.params.find_one({"path": self.path})
    if param==None or repo.cur_branch == None:
        cur_branch="master"
    else:
        cur_branch=repo.cur_branch

    cur_branch_obj=db.branches.find_one({"name":cur_branch})
    if cur_branch_obj !=None:
        head_commit_id=cur_branch_obj["head"]
        repo.rollback(head_commit_id)
