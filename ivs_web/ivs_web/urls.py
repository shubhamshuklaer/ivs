from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ivs_web.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
	url(r'^login/','django.contrib.auth.views.login',name='login'),
	url(r'^admin/',include(admin.site.urls)),
	url(r'^files/','files.views.index',name='files'),
	url(r'^branches/','branches.views.index',name='files'),
	url(r'^commits/','commits.views.index',name='commits'),
	url(r'^params/','params.views.index',name='params'),
	url(r'^patches/','patches.views.index',name='patches'),
	url(r'^main/','main.views.index',name='main'),

)
