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
   url(r'^act/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.act_confirm, name='act_confirm'),

# Change_mail
   url(r'^newmail/$', views.mail_reset, name='mail_reset'),
   url(r'^newmail/done/$', views.mail_done, name='mail_done'),
   url(r'^email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.mail_confirm, name='mail_confirm'),
]

