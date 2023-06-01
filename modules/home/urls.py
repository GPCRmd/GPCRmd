from django.urls import re_path
from django.views.generic.base import RedirectView
#from home import views
from django.views.generic import TemplateView
from django.conf import settings

from modules.home import views

urlpatterns = [
    re_path(r'^home/$', RedirectView.as_view(url='/', permanent=False), name='index'), 
    re_path(r'^$', views.gpcrmd_home, name='gpcrmd_home'),
    re_path(r'^news/$', views.news, name='news'),
    re_path(r'^news/2ndround$', views.ndround, name='ndround'),
    #re_path(r'^hometest/$', views.gpcrmd_home, name='gpcrmd_home'),
    #re_path(r'^mhometest/$', views.gpcrmd_hometest, name='gpcrmd_hometest'),
    re_path(r'^gpcrtree/$', views.gpcrtree, name='gpcrtree'),
    re_path(r'^contact/$', views.contact, name='contact'),
    re_path(r'^community/$', views.community, name='community'),
    re_path(r'^updating/$', views.is_updating, name='is_updating'),
    re_path(r'^remove_marker/$', views.remove_marker, name='remove_marker'),
    re_path(r'^quickloadall_both/$', views.quickloadall_both, name="quickloadall_both"),
    re_path(r'^disclaimer/$', views.disclaimer, name="disclaimer"),
    re_path(r'^privacy-policy/$', views.privacy_policy, name="privacy_policy"),
    re_path(r'^terms&conditions/$', views.terms, name="terms"),
    re_path(r'^cookies-policy/$', views.cookies_policy, name="cookies_policy"),


]
