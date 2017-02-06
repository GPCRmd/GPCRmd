from django.shortcuts import render_to_response, redirect
from accounts.models import User
from django.template import RequestContext
from django.contrib.auth import login as django_login , authenticate, logout as django_logout, get_user_model
from .forms import AuthenticationForm, RegistrationForm, ChangeForm, ChangePassw, ChangeMailForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.contrib.auth import update_session_auth_hash
from django.core.urlresolvers import reverse
from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
import datetime
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect
from .complete import deprecate_current_app
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.conf import settings

@login_required
def memberpage(request):
    return render_to_response('accounts/memberpage.html',{'username':request.user.username},  context_instance=RequestContext(request))

@user_passes_test(lambda user: not user.username,login_url='accounts:memberpage', redirect_field_name=None)
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
                    if 'next' in request.GET:
                        return redirect(request.GET['next'])
                    return redirect('accounts:memberpage')
    else:
        form = AuthenticationForm()
    return render_to_response('accounts/login.html', {
        'form': form,
    }, context_instance=RequestContext(request))



###################### REGISTER AND USER ACTIVATION
@deprecate_current_app
@csrf_protect
def register(request,
       email_template_name='accounts/act/act_email.html', 
       subject_template_name='accounts/act/act_subject.txt', 
       password_reset_form=RegistrationForm,
       token_generator=default_token_generator,
       from_email=None,
       html_email_template_name=None, ##*
       extra_email_context=None, 
       ):     
    """The user is registered and an activation email is sent"""
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            user = form.save(**opts)
            return HttpResponseRedirect("/accounts/reg_mail/")
    else:
        form = RegistrationForm()
    return render_to_response('accounts/register.html', {
        'form': form,
    }, context_instance=RequestContext(request))



def reg_mail(request):
    """Indicates to the user that they will receive a mail for activation"""
    return render_to_response('accounts/reg_mail.html',  context_instance=RequestContext(request))

@sensitive_post_parameters()
@never_cache
@deprecate_current_app
def act_confirm(request, uidb64=None, token=None,
                           template_name='accounts/act/act_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=None,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    View that recognises the user associated with the token in the url and sets the user as active
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('User Activated') # Probably I won't use this in the template, though
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        django_login(request, user)
    else:
        validlink = False
        title = _('Password reset unsuccessful')
    context = {
        'form': None, # Remove this
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)



################## EMAIL CHANGE
@deprecate_current_app
@csrf_protect
def mail_reset(request,
                   template_name='accounts/mail/mail_form.html',
                   email_template_name='accounts/mail/mail_email.html',
                   subject_template_name='accounts/mail/mail_subject.txt',
                   password_reset_form=ChangeMailForm,
                   token_generator=default_token_generator,
                   from_email=None,
                   html_email_template_name=None,
                   extra_email_context=None):
    """Saves the new mail at the email_new field and sends a mail to activate it."""
    if request.method == "POST":
        form = password_reset_form(data=request.POST, instance=request.user, email_old=request.user.email)
        form.actual_user = request.user
        if form.is_valid():
            opts = {
                'username': request.user.username, 
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return HttpResponseRedirect("/accounts/newmail/done/")
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    return TemplateResponse(request, template_name, context)

def mail_done(request):
    """a message informing that the user will receive a mail appears"""
    return render_to_response('accounts/mail/mail_done.html',{'email': request.user.email},  context_instance=RequestContext(request))



@sensitive_post_parameters()
@never_cache
@deprecate_current_app
def mail_confirm(request, uidb64=None, token=None,
                           template_name='accounts/mail/mail_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=None,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    If the user enters a correct mail activation link, the email_new is saved as the account email. email_new is set to blank again.
    """
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token) and not User.objects.filter(email=user.email_new).exists():
        validlink = True
        error_message=None
        title = _('New Email Confirmed') # Probably I won't use this in the template, though
        user.email = user.email_new
        user.email_new=""
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        django_login(request, user)
    else:
        validlink = False
        title = _('Password reset unsuccessful')
        if User is not None:
            if User.objects.exclude(pk=user.pk).filter(email=user.email_new).exists():
                error_message="Sorry, you already associated this email to another GPCRmd account."
            else:
                error_message="The activation link was invalid, possibly because it has already been used."
        else:
            error_message="The activation link was invalid, possibly because it has already been used."


    context = {
        'form': None, # Remove this
        'title': title,
        'validlink': validlink,
        'email':user.email, 
        'error_message': error_message,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)



##############################

@login_required
def logout(request):
    django_logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


@login_required
def change_data(request):
    """change user data"""
    if request.method == 'POST':
        form = ChangeForm(data=request.POST, instance=request.user)
        form.actual_user = request.user
        if form.is_valid():
            form.save()
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = ChangeForm(initial={'first_name':request.user.first_name,'last_name':request.user.last_name,'username':request.user.username, 'country':request.user.country, 'institution':request.user.institution, 'department':request.user.department, 'lab':request.user.lab})
    return render_to_response('accounts/change_data.html', {
        'form': form, 'user_mail':request.user.email,
    }, context_instance=RequestContext(request))


@login_required
def change_passw(request):
    """a logged-in user can change its password"""
    if request.method=='POST':
        form = ChangePassw(data=request.POST, instance=request.user)
        form.user = request.user
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = ChangePassw()
    return render_to_response('accounts/change_passw.html', {
        'form': form,
    }, context_instance=RequestContext(request))


##### Reset password

def reset(request):
    """Displays the form to enter the email of the account for which we want to reset the password"""
    return password_reset(request,
        template_name='accounts/registration/password_reset_form.html',
        email_template_name='accounts/registration/password_reset_email.html',
        post_reset_redirect='/accounts/password_reset/done',
        )

def reset_done(request):
    """Indicates the user that he will receive an email to reset the password. This appears even if the email introduced is not associated to any account"""
    return password_reset_done(request, template_name = 'accounts/registration/password_reset_done.html'
    )



def reset_confirm(request, uidb64=None, token=None):
    """The user is recognized with the url token and can enter the new password"""
    return password_reset_confirm(request, template_name='accounts/registration/password_reset_confirm.html',
         uidb64=uidb64, token=token,
         post_reset_redirect=reverse('accounts:password_reset_complete')         
         )

def reset_complete(request):
    """Displays a message confirming that the new password is set"""
    return password_reset_complete(request, template_name = 'accounts/registration/password_reset_complete.html'
    )
