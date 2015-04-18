from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps
from ivs_base import ivs


db_name_coll=None
commits_coll=None
branches_coll=None
files_coll=None
params_coll=None
base_class=None
mongo_db_name="ivs"

from define_classes import define_classes

def apply_data(db_name,data,root_path,server=False):
	define_classes(server)
    commits_list=data["commits"]
    patches_list=data["patches"]
    branches_list=data["branches"]
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
                    "$set":{
				"name": branch["name"],
				"commit_ids": branch["commit_ids"],
				"head": branch["head"],
				"tail": branch["tail"],
				"parent_branches": branch["parent_branches"],
                        }
                    },
                upsert=True
                )


    if len(commits_list)>0:
        print("Generating code")
        repo=ivs()
        repo.set_path(root_path)
        repo.load_params()
        if repo.cur_branch == None:
            repo.cur_branch="master"

        if param_entry!=None:
            db.params.update({"path":root_path},
                    {
                        "$set"{
                            "path": root_path,
                            "dbname": db_name,
                            "first_cid": param_entry["first_cid"],
                            "cur_com_num": param_entry["cur_com_num"],
                            "last_cid": db.branches.find_one({"name":repo.cur_branch})["head"],
                            "cur_com_level": param_entry["cur_com_level"],
                            "cur_branch": repo.cur_branch,
                            "cur_patch_num": param_entry["cur_patch_num"],
                            }
                        },
                    upsert=True
                    )

        param = repo.params.find_one({"path": root_path})

        cur_branch_obj=db.branches.find_one({"name":repo.cur_branch})
        if cur_branch_obj !=None:
            head_commit_id=cur_branch_obj["head"]
            repo.rollback(head_commit_id)
