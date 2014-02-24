from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import DevClear.views
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_change
from DevClearSite import settings
from django.conf.urls.static import static

admin.autodiscover()




urlpatterns = patterns('',
                       url(r'^$', 'DevClear.views.main', name='main'),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
                       url(r'^logout/$', logout, {'next_page': '/'}, name='logout'),
                       url(r'^change_password/', password_change,
                           {'post_change_redirect': 'home/settings'}, name='password_change'),
                       url(r'^register/$', 'DevClear.views.register', name= 'register'),
                       url(r'^home/$', 'DevClear.views.home', name='home'),
                       url(r'^home/settings/$', 'DevClear.views.settings', name='settings'),
                       url(r'^home/inbox/$', 'DevClear.views.inbox', name='inbox'),
                       url(r'^(?P<org_name>[\w|\W]+)/create_project/$', 'DevClear.views.create_project', name='inbox'),
                       url(r'^home/register_org/$', 'DevClear.views.register_org', name='register_org'),
                       url(r'^profile/(?P<org_name>[\w|\W]+)/(?P<proj_name>[\w|\W]+)/$',
                           'DevClear.views.view_project_profile', name='view_project_profile'),
                       url(r'^profile/(?P<org_name>[\w|\W]+)/$', 'DevClear.views.view_profile', name='view_profile'),
                       #url(r'^messages/', include('postman.urls')),


)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
