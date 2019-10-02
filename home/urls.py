from django.conf.urls import url
from django.views.generic.base import RedirectView
#from home import views
from django.views.generic import TemplateView
from django.conf import settings

from home import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/home/', permanent=False), name='index'), 
    url(r'^home/$', views.gpcrmd_home, name='gpcrmd_home'),
    #url(r'^hometest/$', views.gpcrmd_home, name='gpcrmd_home'),
    #url(r'^mhometest/$', views.gpcrmd_hometest, name='gpcrmd_hometest'),
    url(r'^gpcrtree/$', views.gpcrtree, name='gpcrtree'),
]
