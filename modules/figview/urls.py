from django.urls import re_path

from . import views

app_name = "figview"

urlpatterns = [
    re_path(r'^(?P<figviewname>\w+)/$', views.figviewer, name='figviewer'),
]