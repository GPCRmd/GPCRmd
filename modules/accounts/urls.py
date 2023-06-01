from django.urls import include, re_path
from . import views
from django.contrib.auth import views as auth_views 
from .forms import AuthenticationForm, RegistrationForm, ChangeForm, ChangePassw, ChangeMailForm, PasswordResetForm

import django

app_name = "accounts"

urlpatterns = [
   re_path(r'^register/$', views.register, name='register'),
  # re_path(r'^logincovid/$', views.login,{"is_covid":True}, name='login'),
   re_path(r'^login/$', views.login, name='login'),
   re_path(r'^logout/$', views.logout, name='logout'),
   re_path(r'^memberpage/$', views.memberpage, name='memberpage'),
   re_path(r'^change_data/$', views.change_data, name='change_data'),
   re_path(r'^change_passw/$', views.change_passw, name='change_passw'),       
# Reset password:
   re_path(r'^password_reset/$', views.auth_views.PasswordResetView.as_view(
        template_name='accounts/registration/password_reset_form.html',
        html_email_template_name='accounts/registration/password_reset_email.html',
        email_template_name='accounts/registration/password_reset_email.html',
        success_url='/accounts/password_reset/done',
        form_class=PasswordResetForm
        ), name='password_reset'),
   re_path(r'^password_reset/done/$', views.auth_views.PasswordResetDoneView.as_view( 
         template_name = 'accounts/registration/password_reset_done.html'
         ), name='password_reset_done'),
   re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', views.reset_confirm, name='password_reset_confirm'),
   re_path(r'^reset/done/$', views.auth_views.PasswordResetDoneView.as_view( 
        template_name = 'accounts/registration/password_reset_complete.html'
        ), name='password_reset_complete'),
# Confirmation_mail
   re_path(r'^reg_mail/$', views.reg_mail, name='reg_mail'),
   re_path(r'^act/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', views.act_confirm, name='act_confirm'),

# Change_mail
   re_path(r'^newmail/$', views.mail_reset, name='mail_reset'),
   re_path(r'^newmail/done/$', views.mail_done, name='mail_done'),
   re_path(r'^email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', views.mail_confirm, name='mail_confirm'),
   re_path(r'^submissions/$', views.user_submissions, name='user_submissions'),
   
   
]

