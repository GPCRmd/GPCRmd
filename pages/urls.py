from django.conf.urls import url

from pages import views

urlpatterns = [
	url(r'^releasenotes', views.releasenotes, name='releasenotes'), 
]