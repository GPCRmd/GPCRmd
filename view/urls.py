from django.conf.urls import url
from . import views

app_name = "view"

urlpatterns = [
    url(r'^(?P<dyn_id>[0-9]+)/$', views.index, name='index'),
    url(r'^previewer/$', views.pre_viewer, name='pre_viewer'),
  #  url(r'^distances/(?P<dist_str>[0-9]+-[0-9]+(a[0-9]+-[0-9]+)*)/(?P<struc_id>[0-9]+)/(?P<traj_id>[0-9]+)$', views.distances, name='distances'),
    url(r'^rmsd/$', views.rmsd, name='rmsd'),
    url(r'^dwl/(?P<dist_id>dist_[0-9]+)/$', views.download_dist, name="download_dist"),
]
