from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps

def get_data_for_commits(db_name,commit_uid_list):
    mongo_conn=Connection()
    db=mongo_conn[db_name]
    for i in range(len(commit_uid_list)):
        commit_uid_list[i]=ObjectId(commit_uid_list[i])

    print("hell"+str(commit_uid_list))

    selected_commits=db.commits.find({'uid':{'$in': commit_uid_list}})

    patch_ids=[]
    selected_commits_list=[]
    selected_patches_list=[]

    for entity in selected_commits:
        patch_ids.append(entity["patch_ids"])
        selected_commits_list.append(entity)
        
    selected_patches=db.patched.find({'uid':{'$in':patch_ids}})

    for entity in selected_patches:
        selected_patches_list.append(entity)


    result={"commits":selected_commits_list,"patches":selected_patches_list}
    print(result)

    return dumps(result)
