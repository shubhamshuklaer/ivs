# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import pymongo as pm

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'),wrong=False)

def auth():
	session['db']=''    # the name of the database
	if 'logged' in session.keys() and session['logged']==True:
		return 'Already logged in'
	#redirect(URL('index'))
	#return str(request.vars['username'])
	conn=pm.MongoClient()
        db_users=conn["users"]
        if db_users.users.find( { 'user_name': request.vars['username'] } ).count() <1 :  # no user
    		return dict(message=T('Welcome to web2py!'),wrong=True)
                #return render( request , 'registration/login.html', { 'auth_failure':True } )
        else:    # if such a user exist
                a = db_users.users.find_one( {'user_name':request.vars['username'] } )
                if a['passwd']==request.vars['password']:  # grant access
                        session['prefix']=''
                        session['username']=request.vars['username']
			session['logged']=True
			redirect(URL('repo'))
    		return dict(message=T('Welcome to web2py!'),wrong=True)

def repo():
#	return 'list of repos'
	if 'username' not in session.keys() or session['username']=='': # user not logged in
		redirect(URL('index'))
        conn=pm.MongoClient()
        db_users=conn["users"]
        a = db_users.users.find_one( {'user_name':session['username'] } )
        session['prefix']=''
        session['db']=''
	if 'repo' in a.keys():
		return dict(repos=a['repo'])
	else:
		return dict(repos=list())



def files():

#	return 'Files for the db = ' + request.vars['db']

	out= []    # this will be sent to page for output
        client = pm.MongoClient()
	
	if 'username' not in session.keys() or session['username']==0 :
		redirect(URL('index'))

	conn=client
        db_users=conn["users"]
	# set the value of the db

	if 'db' in request.vars.keys() :
		db= client[request.vars['db']]
		session['db']=request.vars['db']
		session['prefix']=''
	else:
		if session['db'] == '' :
			a = db_users.users.find_one( {'user_name':session['username'] } )
			#return render( request , 'repos.html', {'repos':a['repo'] } )
			redirect(URL('repo'))
	#print 'The selected DB is : ' + request.session['db']
	db= client[session['db']]
        files = db.files.find()
	
	if session['db']=='':   # i.e. no db selected
		redirect(URL('repo'))

        for x in files:
                out.append( { 'name':x['name'] , 'path':x['path'] } )

	if  'prefix' in session.keys():
		prefix=session['prefix']
	else:
		prefix=''
		session['prefix']=prefix

	if 'folder' in request.vars.keys():
		prefix=prefix+request.vars['folder']+'/'
		session['prefix']=prefix

	if 'up' in request.vars.keys():
		sp = prefix.split('/')
		prefix = '/'.join(sp[:-2])
		if prefix!='':
			prefix=prefix+'/'
		session['prefix']=prefix
# return render( request , 'files.html', { 'files': out } )

# segregate files and folders
	folder = set()   # a list of folders
	files = list()
	out2 = list()

	# remove the prefix
	for x in out:
		if prefix==x['path'][0:len(prefix)]:
			out2.append( { 'name':x['name'] , 'path': x['path'][len(prefix):] } )
	out=out2
	for x in out:
		if len(x['name'])==len(x['path']):
			files.append( { 'name': x['name'] , 'path' : x['path'] } )
		else:
			# extract the folder name
			k=x['path'].split('/')
			folder.add(k[0])


	return dict(folders=list(folder), files=files )
			
	
def branches():
  	out= []    # this will be sent to page for output
        client = pm.MongoClient()
        if 'username' not in session.keys() or session['username']=='':
       #         print 'Redirecting to login'
       #         return HttpResponseRedirect('../login')
		redirect(URL('index'))	

        conn=client
        if 'db' not in session.keys() or session['db']=='':
		redirect(URL('repo'))
        db=conn[session['db']]
        # set the value of the db

        if 'db' in request.vars.keys() :
          #      print 'Database is : ' + request.GET['db']
                db= conn[request.vars['db']]
        #       return render( request , 'repos.html', {'repos':a['repo'] } )
        branches = db.branches.find()
        for x in branches:
                out.append( { 'name':x['name'] , 'parent':x['parent_branches'] } )
	return dict(branches=out)
#        return render( request , 'branches.html', { 'branches': out } )




def commits():
        out= []    # this will be sent to page for output
        client = pm.MongoClient()

        if 'username' not in session.keys() or session['username']=='':
		redirect(URL('index'))

        conn=client
        if 'db' not in session.keys() or session['db']=='':
		redirect(URL('repo'))
        db=conn[session['db']]
        # set the value of the db

        commits = db.commits.find()
        for x in commits:
                out.append( { 'id':str(x['_id']) , 'parent_id':str(x['parent_id']), 'added':x['added'] , 'deleted':x['deleted'], 'level':x['level'], 'ts':x['ts'], 'branch':x['branch'], 'msg':x['msg'], 'child_ids': [ str(k) for k in x['child_ids'] ]  } )

	return dict(commits=out)
#        return render( request , 'commits.html', { 'commits': out } )





def patches():

        out= []    # this will be sent to page for output
        client = pm.MongoClient()

        if 'username' not in session.keys() or session['username']=='':
		redirect(URL('index'))

        conn=client
        if 'db' not in session.keys() or session['db']=='':
		redirect(URL('repo'))
        db=conn[session['db']]
        files = db.patches.find()
        for x in files:
                out.append( { 'id':str(x['_id']) , 'dict':x['dict'], 'branch':x['branch'], 'file_path':x['file_path']  } )

	return dict( patches= out)




def logout():
        session['prefix']=''
        session['username']=''
	session['logged']=False
	redirect(URL('index'))


def register():
	conn =pm.MongoClient()
        db_users=conn['users']
	if 'username' in request.vars.keys() and 'password' in request.vars.keys():
                db_users.users.insert( { 'user_name': request.vars['username'] , 'passwd': request.vars['password'], 'repo': [] } )
		redirect(URL('index'))
        else:
		return dict()



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


