from json import dumps
from ivs_base import ivs
import mongo_db_name_setting



def apply_data(db_name,data,root_path,server=False):
    mongo_db_name=mongo_db_name_setting.mongo_db_name
    db_name_coll=mongo_db_name_setting.db_name_coll
    commits_coll=mongo_db_name_setting.commits_coll
    branches_coll=mongo_db_name_setting.branches_coll
    files_coll=mongo_db_name_setting.files_coll
    patches_coll=mongo_db_name_setting.patches_coll
    params_coll=mongo_db_name_setting.params_coll
    base_class=mongo_db_name_setting.base_class

    commits_list=data["commits"]
    patches_list=data["patches"]
    branches_list=data["branches"]
    param_entry=data["params"]

    for commit in commits_list:
        base_class.update(commits_coll,{"db_name":db_name,"uid":commit["uid"]},
                {
                    "$set":{
                        "uid":commit["uid"],
                        "patch_ids": commit["patch_ids"],
                        "db_name":db_name,
                        "ts": commit["ts"],
                        "msg": commit["msg"],
                        "added": commit["added"],
                        "deleted": commit["deleted"],
                        "parent_id": commit["parent_id"],
                        "branch": commit["branch"],
                        "num": commit["num"],
                        "level": commit["level"]
                    },
                    "$addToSet": { "child_ids" :{"$each": commit["child_ids"]}}
                    },
                upsert=True
                )

    for patch in patches_list:
        temp_entity=patches_coll()
        base_class.insert(temp_entity,patches_coll,{
                    "uid": patch["uid"],
                    "diff_dict": patch["diff_dict"],
                    "num": patch["num"],
                    "db_name": db_name,
                    "file_path": patch["file_path"],
                    "cid": patch["cid"],
                    "branch": patch["branch"],
            })

    for branch in branches_list:
        base_class.update(branches_coll,{"db_name":db_name,"name":branch["name"]},
                {
                    "$set":{
				"name": branch["name"],
                                "db_name":db_name,
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
        repo.set_dbname(db_name)
        repo.load_params()
        if repo.cur_branch == None:
            repo.cur_branch="master"

        if param_entry!=None:
            base_class.update(params_coll,{"db_name":db_name,"path":root_path},
                    {
                        "$set":{
                            "path": root_path,
                            "db_name": db_name,
                            "first_cid": param_entry["first_cid"],
                            "cur_com_num": param_entry["cur_com_num"],
                            "last_cid": base_class.find_one(branches_coll,{"db_name":db_name,"name":repo.cur_branch})["head"],
                            "cur_com_level": param_entry["cur_com_level"],
                            "cur_branch": repo.cur_branch,
                            "cur_patch_num": param_entry["cur_patch_num"],
                            }
                        },
                    upsert=True
                    )

        if not server:
            param = repo.params.find_one({"path": root_path})

            cur_branch_obj=base_class.find_one(branches_coll,{"db_name":db_name,"name":repo.cur_branch})
            if cur_branch_obj !=None:
                head_commit_id=cur_branch_obj["head"]
                repo.rollback(head_commit_id)
