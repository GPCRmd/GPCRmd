from django.conf.urls import url
from . import views

app_name = "view"

urlpatterns = [
    url(r'^(?P<dyn_id>[0-9]+)/$', views.index, name='index'),
    url(r'^previewer/$', views.pre_viewer, name='pre_viewer'),
]
