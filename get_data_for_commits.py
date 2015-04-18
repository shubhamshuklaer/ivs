from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps

db_name_coll=None
commits_coll=None
branches_coll=None
files_coll=None
params_coll=None
base_class=None
mongo_db_name="ivs"

from define_classes import define_classes

def get_data_for_commits(db_name,commit_uid_list,server=False):
	define_classes(server)
	mongo_conn=Connection()
	db=mongo_conn[db_name]
	for i in range(len(commit_uid_list)):
		commit_uid_list[i]=ObjectId(commit_uid_list[i])


	selected_commits=db.commits.find({'uid':{'$in': commit_uid_list}})

	patch_ids=[]
	selected_commits_list=[]
	selected_patches_list=[]
	selected_branches_list=[]

	branches=[]
	param_entry=None

	for entity in selected_commits:
		patch_ids=patch_ids+entity["patch_ids"]
		selected_commits_list.append(entity)

	selected_patches=db.patches.find({'uid':{'$in':patch_ids}})
	print("patch_ids")
	print(patch_ids)

	for entity in selected_patches:
		branches.append(entity["branch"])
		selected_patches_list.append(entity)

	selected_branches=db.branches.find({'name':{'$in':branches}})

	for entity in selected_branches:
		selected_branches_list.append(entity)

	if len(selected_commits_list)>0:
		param_entry=db.params.find_one()

	result={"commits":selected_commits_list,"patches":selected_patches_list,"branches":selected_branches_list,"params":param_entry}

	return dumps(result)
