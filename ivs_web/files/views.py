# Create your views here.
from django.shortcuts import render
from django.shortcuts import render, render_to_response
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm
#import yrbook.models as model
from django.template.loader import get_template
from django.template import Context, RequestContext
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import *
from django.conf import settings
from django.shortcuts import *

import pymongo as pm


# Create your views here.

def index(request):
        out= []    # this will be sent to page for output
        client = pm.MongoClient()
#	print request.GET['db']  + ' A key was found '
#	print request.GET.db+ '   This is the name of the db  '
       # db = client[request.GET.db]
	try:
		settings.user_name 
	except:
		print 'User name not set : ERROR '
		return redirect('login.views.index')

	conn=pm.Connection()
        db_users=conn["users"]
	# set the value of the db

	if 'db' in request.GET.keys() :
		db= client[request.GET['db']]
		request.session['db']=request.GET['db']
	else:
		if request.session['db'] == '' :
			a = db_users.users.find_one( {'user_name':settings.user_name } )
			return render( request , 'repos.html', {'repos':a['repo'] } )
	db= client[request.session['db']]
        files = db.files.find()
        for x in files:
		print x
                out.append( { 'name':x['name'] , 'path':x['path'] } )

	if  'prefix' in request.session.keys():
		prefix=request.session['prefix']
	else:
		prefix=''

	if 'folder' in request.GET.keys():
		prefix=prefix+request.GET['folder']+'/'

	print 'The prefix is : ' + prefix
	

#        return render( request , 'files.html', { 'files': out } )

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
			print 'PATH :',
			print k
			folder.add(k[0])


	print folder
	print files
        return render( request , 'files2.html', { 'folders': list(folder), 'files':files } )
			
		
		




