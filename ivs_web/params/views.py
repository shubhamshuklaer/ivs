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
	params = db.params.find()
	for x in params:
		out.append( { 'id':str(x['_id'])  } )

	return render( request , 'params.html', { 'files': out } )



