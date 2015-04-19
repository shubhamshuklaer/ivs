from json import dumps
import mongo_db_name_setting



def get_data_for_commits(db_name,commit_uid_list):
        mongo_db_name=mongo_db_name_setting.mongo_db_name
        db_name_coll=mongo_db_name_setting.db_name_coll
        commits_coll=mongo_db_name_setting.commits_coll
        branches_coll=mongo_db_name_setting.branches_coll
        files_coll=mongo_db_name_setting.files_coll
        patches_coll=mongo_db_name_setting.patches_coll
        params_coll=mongo_db_name_setting.params_coll
        base_class=mongo_db_name_setting.base_class

	for i in range(len(commit_uid_list)):
		commit_uid_list[i]=commit_uid_list[i]


	selected_commits=base_class.find(commits_coll,{'uid':{'$in': commit_uid_list}})

	patch_ids=[]
	selected_commits_list=[]
	selected_patches_list=[]
	selected_branches_list=[]

	branches=[]
	param_entry=None

	for entity in selected_commits:
		patch_ids=patch_ids+entity["patch_ids"]
		selected_commits_list.append(entity)

	selected_patches=base_class.find(patches_coll,{'uid':{'$in':patch_ids}})
	print("patch_ids")
	print(patch_ids)

	for entity in selected_patches:
		branches.append(entity["branch"])
		selected_patches_list.append(entity)

	selected_branches=base_class.find(branches_coll,{'name':{'$in':branches}})

	for entity in selected_branches:
		selected_branches_list.append(entity)

	if len(selected_commits_list)>0:
            param_entry=base_class.find_one(params_coll,{"db_name":db_name})

	result={"commits":selected_commits_list,"patches":selected_patches_list,"branches":selected_branches_list,"params":param_entry}
        print(selected_commits_list)

	return dumps(result)
