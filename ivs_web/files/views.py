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

@login_required
def index(request):
        out= []    # this will be sent to page for output
        client = pm.MongoClient()
#	print request.GET['db']  + ' A key was found '
#	print request.GET.db+ '   This is the name of the db  '
       # db = client[request.GET.db]
	try:
		settings.user_name 
	except:
		return redirect('login.views.index')

	conn=pm.Connection()
        db_users=conn["users"]
	# set the value of the db

	if 'db' in request.GET.keys() :
		db= client[request.GET['db']]
	else:
		a = db_users.users.find_one( {'user_name':settings.user_name } )
		return render( request , 'repos.html', {'repos':a['repo'] } )
        files = db.files.find()
        for x in files:
                out.append( { 'name':x['name'] , 'path':x['path'] } )

        print files
        return render( request , 'files.html', { 'files': out } )




