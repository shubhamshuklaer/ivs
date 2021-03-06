from pymongo import Connection
from bson.objectid import ObjectId
from bson.json_util import dumps

def get_data_for_commits(db_name,commit_uid_list):
	mongo_conn=Connection()
	db=mongo_conn[db_name]
	for i in range(len(commit_uid_list)):
		commit_uid_list[i]=ObjectId(commit_uid_list[i])


	selected_commits=db.commits.find({'uid':{'$in': commit_uid_list}})

	patch_ids=[]
	selected_commits_list=[]
	selected_patches_list=[]
	selected_files_list=[]
	selected_branches_list=[]

	file_paths=[]
	branches=[]
	param_entry=None

	for entity in selected_commits:
		patch_ids=patch_ids+entity["patch_ids"]
		selected_commits_list.append(entity)

	selected_patches=db.patches.find({'uid':{'$in':patch_ids}})
	print("patch_ids")
	print(patch_ids)

	for entity in selected_patches:
		file_paths.append(entity["file_path"])
		branches.append(entity["branch"])
		selected_patches_list.append(entity)

	selected_files=db.files.find({'path':{'$in':file_paths}})

	for entity in selected_files:
		selected_files_list.append(entity)

	selected_branches=db.branches.find({'name':{'$in':branches}})

	for entity in selected_branches:
		selected_branches_list.append(entity)

	if len(selected_commits_list)>0:
		param_entry=db.params.find_one()

	result={"commits":selected_commits_list,"patches":selected_patches_list,"files":selected_files_list,"branches":selected_branches_list,"params":param_entry}

	return dumps(result)
