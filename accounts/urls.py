from django.conf.urls import patterns, include, url
from . import views
from django.contrib.auth import views as auth_views
import django

app_name = "accounts"

urlpatterns = [
   url(r'^register/$', views.register, name='register'),
   url(r'^login/$', views.login, name='login'),
   url(r'^logout/$', views.logout, name='logout'),
   url(r'^memberpage/$', views.memberpage, name='memberpage'),
   url(r'^change_data/$', views.change_data, name='change_data'),
   url(r'^change_passw/$', views.change_passw, name='change_passw'),       
# Reset password:
   url(r'^password_reset/$', views.reset, name='password_reset'),
   url(r'^password_reset/done/$', views.reset_done, name='password_reset_done'),
   url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.reset_confirm, name='password_reset_confirm'),
   url(r'^reset/done/$', views.reset_complete, name='password_reset_complete'),
# Confirmation_mail
   url(r'^reg_mail/$', views.reg_mail, name='reg_mail'),
   url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$', views.confirm, name='confirm'), # This will get the code, ask for username and passw (like login) and check if they match
]

