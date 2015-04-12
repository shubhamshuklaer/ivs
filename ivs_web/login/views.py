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
import sys
#sys.path.append('home/vibhanshu/Desktop/ivs/')

from django.conf import settings
import pymongo as pm


# Create your views here.

#@login_required
def index(request):
	return render( request , 'registration/login.html', { 'auth_failure':False } )


def auth(request):
#	print request.POST.get('username','')
#	print request.POST.get('password','')

	conn=pm.Connection()
	db_users=conn["users"]
	if db_users.users.find( { 'user_name': request.POST.get('username','') } ).count() <1 :  # no user
		return render( request , 'registration/login.html', { 'auth_failure':True } )
	else:    # if such a user exist
		a = db_users.users.find_one( {'user_name':request.POST.get('username','') } )
		if a['passwd']==request.POST.get('password',''):  # grant access
			settings.user_name = request.POST.get('username','')   # the currently logged in username
			return render( request, 'repos.html', {'repos': a['repo'] } )
		return render( request, 'registration/login.html' , {'auth_failure':True } )
