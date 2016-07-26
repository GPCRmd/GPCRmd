from django.shortcuts import render_to_response, redirect, render
from django.template import RequestContext, Context
from django.contrib.auth import login as django_login , authenticate, logout as django_logout, get_user_model
from .forms import AuthenticationForm, RegistrationForm, ChangeForm, ChangePassw, ActivationConfirmForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.contrib.auth import update_session_auth_hash
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.core.mail import send_mail, EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
import datetime


@login_required(login_url='/accounts/login/')
def memberpage(request):
    return render_to_response('accounts/memberpage.html',{'username':request.user.username},  context_instance=RequestContext(request))

@user_passes_test(lambda user: not user.username, login_url='/accounts/memberpage', redirect_field_name=None)
def login(request):
    """allows active users to log in and enter to the memberpage"""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    return HttpResponseRedirect("/accounts/memberpage/")
    else:
        form = AuthenticationForm()
    return render_to_response('accounts/login.html', {
        'form': form,
    }, context_instance=RequestContext(request))


def register(request):
    """User registration + sends to the user a mail to activate their account. Users are sent to a page where they are told so."""
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            send_confirmation_mail(request,user)
            return HttpResponseRedirect("/accounts/reg_mail/")
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {
        'form': form,
    }, context_instance=RequestContext(request))



def send_confirmation_mail(request,user):
    """Function to sent the activation mail, not associated to any url. The mail contains a random code (which is created for the user when it iis registered) which will later be used to identify the user."""
    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain
    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user.act_code)),
        'protocol': 'http',  #### https ?
  }
    subject="Account activation"
    message= get_template("accounts/activation_email.html").render(Context(context))
    msg = EmailMessage(subject, message, to=[user.email] , from_email="from_email@mail.com")
    msg.content_subtype = 'html'
    msg.send()


def confirm(request, uidb64=None):
    """identifies the user related to the act_code, if exists. Checks if he registered as much a day ago. Checks if the code corresponds to the username and password introduced in a form. If so, activates the user."""
    try:
        act_code = force_text(urlsafe_base64_decode(uidb64))
        user=get_user_model().objects.get(act_code=act_code)
    except Exception:
        user=None 
    else: 
        d=user.date_joined
        d=datetime.datetime(d.year, d.month, d.day)
    if user is not None and (datetime.datetime.now()-datetime.timedelta(days=1)) < d < datetime.datetime.now():
# form:
        if request.method == 'POST':
            form = ActivationConfirmForm(data=request.POST, act_code=act_code) 
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if act_code == user.act_code:
                        user.is_active = True
                        user.act_code="act"
                        user.save()
                        django_login(request, user)
                        return HttpResponseRedirect("/accounts/memberpage/") 
        else:
            form = ActivationConfirmForm()
        return render_to_response('accounts/activation_conf.html', {
            'form': form,
        }, context_instance=RequestContext(request))

    else:
        error_message= "Sorry, this activation link is not valid."
        return render_to_response('accounts/errorpage.html',  {'error_message':error_message}, context_instance=RequestContext(request))





def reg_mail(request):
    """Indicates to the user that they will receive a mail for activation"""
    return render_to_response('accounts/reg_mail.html',  context_instance=RequestContext(request))


@login_required(login_url='/accounts/login/')
def logout(request):
    django_logout(request)
    return redirect('/accounts/login')


@login_required(login_url='/accounts/login/')
def change_data(request):
    """change user data"""
    if request.method == 'POST':
        form = ChangeForm(data=request.POST, instance=request.user)
        form.actual_user = request.user
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/accounts/memberpage/")
    else:
        form = ChangeForm(initial={'first_name':request.user.first_name,'last_name':request.user.last_name,'username':request.user.username,'email':request.user.email, 'country':request.user.country, 'institution':request.user.institution, 'department':request.user.department, 'lab':request.user.lab})
    return render_to_response('accounts/change_data.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def change_passw(request):
    """a logged-in user can change its password"""
    if request.method=='POST':
        form = ChangePassw(data=request.POST, instance=request.user)
        form.user = request.user
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect("/accounts/memberpage/")
    else:
        form = ChangePassw()
    return render_to_response('accounts/change_passw.html', {
        'form': form,
    }, context_instance=RequestContext(request))


##### Reset password

def reset_confirm(request, uidb64=None, token=None):
    return password_reset_confirm(request, template_name='accounts/registration/password_reset_confirm.html',
         uidb64=uidb64, token=token,
         post_reset_redirect=reverse('accounts:password_reset_complete')         
         )


def reset(request):
    return password_reset(request,
        template_name='accounts/registration/password_reset_form.html',
        email_template_name='accounts/registration/password_reset_email.html',
        post_reset_redirect='/accounts/password_reset/done'
        )

def reset_done(request):
    return password_reset_done(request, template_name = 'accounts/registration/password_reset_done.html'
    )

def reset_complete(request):
    return password_reset_complete(request, template_name = 'accounts/registration/password_reset_complete.html'
    )
