from django.conf.urls import url,patterns,include
from django.conf import settings
from . import views

app_name = "view"

urlpatterns = [
    url(r'^(?P<dyn_id>[0-9]+)/$', views.index, name='index'),
  #  url(r'^distances/(?P<dist_str>[0-9]+-[0-9]+(a[0-9]+-[0-9]+)*)/(?P<struc_id>[0-9]+)/(?P<traj_id>[0-9]+)$', views.distances, name='distances'),
  #  url(r'^rmsd/$', views.rmsd, name='rmsd'),
    url(r'^dwl/(?P<dist_id>dist_[0-9]+)/$', views.download_dist, name="download_dist"),
    url(r'^dwl/(?P<rmsd_id>rmsd_[0-9]+)/$', views.download_rmsd, name="download_rmsd"),
    url(r'^dwl/(?P<int_id>int_[0-9]+)/$', views.download_int, name="download_int"),
    url(r'^docs/$', views.viewer_docs, name='viewer_docs'),
]

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^files/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
)
