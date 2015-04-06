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

import pymongo as pm


# Create your views here.

@login_required
def index(request):
	out= []    # this will be sent to page for output
	client = pm.MongoClient()
	db = client['test_ivs']
	commits = db.commits.find()
	for x in commits:
		out.append( { 'id':str(x['_id']) , 'parent_id':str(x['parent_id']), 'added':x['added'] , 'deleted':x['deleted'], 'level':x['level'], 'ts':x['ts'], 'branch':x['branch'], 'msg':x['msg'], 'child_ids': [ str(k) for k in x['child_ids'] ]  } )

	return render( request , 'commits.html', { 'commits': out } )



