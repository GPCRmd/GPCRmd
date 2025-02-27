from django.urls import include, re_path, path
from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.conf import settings
from config import views
from modules.dynadb import views as dyn_views

urlpatterns = [
    re_path(r'^', include('modules.home.urls')),
    re_path(r'^maintenance/', views.error503, name='maintenance'),
    path('admin/', admin.site.urls),
    path('admin_panel/', include('modules.admin_panel.urls')),
    re_path(r'^accounts/', include('modules.accounts.urls')),
    re_path(r'^api/', include('modules.api.urls')),
    re_path(r'^cancer/', include('modules.cancer.urls')),
    path('celery-progress/', include('celery_progress.urls')),
    re_path(r'^contmaps/', include('modules.contact_maps.urls')),
    re_path(r'^common/', include('modules.common.urls')),
    re_path(r'^covid19/', include('modules.covid19.urls')),
    re_path(r'^dynadb/', include('modules.dynadb.urls')),
    re_path(r'^figview/', include('modules.figview.urls')),
    re_path(r'^gpcr_gprot/', include('modules.gpcr_gprot.urls')),
    re_path(r'^gpcr_arr/', include('modules.gpcr_arr.urls')),
    re_path(r'^gpcrome/', include('modules.crossreceptor_analysis.urls')),
    re_path(r'^mdsrv/(?P<path>Precomputed/.*)$',dyn_views.mdsrv_redirect,name='mdsrv_redirect'),
    re_path(r'^psymd/', include('modules.corplots.urls')),
    path('temp/', include('modules.temp.urls')),
    re_path(r'^sc2md/', include('modules.sc2md.urls')),
    re_path(r'^view/', include('modules.view.urls')),
]

if not settings.FILES_NO_LOGIN:
    urlpatterns.append(re_path(r'^mdsrv/(?P<path_dir>dir/files/[^/\\]+/[^/\\]+)|mdsrv/(?P<path>.*/files/[^/\\]+/[^/\\]+/.*)$',
    dyn_views.mdsrv_redirect_prelogin,name='mdsrv_redirect_prelogin'))
urlpatterns += [ re_path(r'^mdsrv/(?P<path>.*)$', dyn_views.mdsrv_redirect,name='mdsrv_redirect'),
    re_path(r'^html/(?P<path>.*)$', dyn_views.mdsrv_redirect,name='mdsrv_redirect'),
]

urlpatterns += [path('', include('django.contrib.auth.urls'))]

handler404 = views.error404
handler500 = views.error500
# handler503 = views.error503

if settings.DEBUG:
    import debug_toolbar
    urlpatterns.append( re_path(r'^__debug__/', include(debug_toolbar.urls)) )
