from django.conf.urls import url

from protein import views


urlpatterns = [
    url(r'^$', views.BrowseSelection.as_view(), name='index'),
    url(r'^autocomplete', views.SelectionAutocomplete, name='autocomplete'),
    url(r'^gproteins', views.g_proteins, name='g_proteins'),
    url(r'^(?P<slug>[-\w]+)/$', views.detail, name='detail'),
]