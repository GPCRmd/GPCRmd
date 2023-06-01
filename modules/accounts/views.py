from django.shortcuts import render, redirect
from django.template import RequestContext
from django.contrib.auth import login as django_login , authenticate, logout as django_logout, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse, path
#from django.contrib.auth.views import password_reset, password_reset_confirm, password_reset_done, password_reset_complete
from django.contrib.auth import views as auth_views
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.conf import settings
from django.db.models import F

from modules.dynadb.models import DyndbSubmission, DyndbDynamics, DyndbSubmissionDynamicsFiles
from modules.accounts.models import User
from .forms import AuthenticationForm, RegistrationForm, ChangeForm, ChangePassw, ChangeMailForm, PasswordResetForm

import datetime
from .complete import deprecate_current_app

@login_required
def memberpage(request):
    context={'username':request.user.username}
    if request.user.has_privilege_covid:
        context["user_covid"]=True
    return render(request, 'accounts/memberpage.html',context)

def login(request):
    """allows active users to log in and enter to the memberpage"""
    # get the webpage to redirect on successful login from GET query string
    next_url = None
    mytemplate='accounts/login.html'
    if 'next' in request.GET:
        next_url = request.GET['next']
    is_covid=False
    if 'is_covid' in request.GET:
        is_covid = request.GET['is_covid']
        if is_covid:
            mytemplate='covid19/login_covid.html'
    # if user is already logged in redirect to GET query string 'next' key value or
    # to user main menu
    if request.user.is_authenticated:
        if next_url is not None:
            return redirect(next_url)
        else:
            return redirect('accounts:memberpage')
    if request.method == 'POST':
        # get the webpage to redirect on successful login from POST for redirect
        # or preserving the value on unsuccessful login after page reload
        if 'next' in request.POST:
            next_url = request.POST['next']
        if 'is_covid' in request.POST:
            is_covid = request.POST['is_covid']
            if is_covid:
                mytemplate='covid19/login_covid.html'
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    django_login(request, user)
                    if next_url is not None:
                        return redirect(next_url)
                    else:
                        return redirect('accounts:memberpage')
    elif request.method == 'GET':
        
        form = AuthenticationForm()
    # add webpage to redirect on login form as a hidden HTML input element for POST requests   
    return render(request, mytemplate, {
        'form': form,
        'next_url': next_url,
        "is_covid":is_covid
    })

###################### REGISTER AND USER ACTIVATION
@deprecate_current_app
@csrf_protect
@login_required
def register(request,
       email_template_name='accounts/act/act_email.html', 
       subject_template_name='accounts/act/act_subject.txt', 
       password_reset_form=RegistrationForm,
       token_generator=default_token_generator,
       from_email=None,
       html_email_template_name=None, ##*
       extra_email_context=None, 
       ):     
    if request.user.is_staff:
        """The user is registered and an activation email is sent"""
        if request.method == 'POST':
            form = RegistrationForm(data=request.POST)
            email = form.fields["email"].to_python(form.data["email"])
            User.objects.filter(email=email,is_active=False,last_login=None).delete()

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
        return render(request, 'accounts/register.html', {
            'form': form,
            'username':request.user.username,
        })

def reg_mail(request):
    """Indicates to the user that they will receive a mail for activation"""
    return render(request, 'accounts/reg_mail.html')

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
        uid = force_str(urlsafe_base64_decode(uidb64))
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
    return render(request, 'accounts/mail/mail_done.html', context={'email': request.user.email})



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
        uid = force_str(urlsafe_base64_decode(uidb64))
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
    return render(request, 'accounts/change_data.html', context={
        'form': form, 'user_mail':request.user.email,
    })


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
    return render(request, 'accounts/change_passw.html', context={
        'form': form,
    })


##### Reset password
def reset_confirm(request, uidb64=None, token=None):
    """The user is recognized with the url token and can enter the new password"""
    return auth_views.PasswordResetConfirmView.as_view(request, 
        template_name='accounts/registration/password_reset_confirm.html',
        uidb64=uidb64, 
        token=token,
        succes_url=reverse('accounts:password_reset_complete')         
        )

@login_required
def user_submissions(request):
    submission_table = []
    submissionq = DyndbSubmission.objects.order_by('-pk',)
    submissionq = submissionq.annotate(dynamics_id=F('dyndbdynamics__pk'))
    values = []
    if request.user.is_superuser:
        values = ['user_id__username']
    else:
        values = []
        submissionq = submissionq.filter(user_id=request.user.pk)
    
    values += ['pk','dynamics_id','is_closed','is_ready_for_publication','is_published']
    submissionq = submissionq.values(*values)
    for subinfo in submissionq:
        if subinfo['is_published']:
            state = 'Published'
        elif subinfo['is_ready_for_publication']:
            state = 'Ready for publication'
        elif subinfo['is_closed']:
            state = 'Closed'
        else:
            state = 'Open'
        # To check if submission is completed, check if it has trajectories. We wont allow its closeness otherwise
        is_completed = len(DyndbSubmissionDynamicsFiles.objects.filter(submission_id=subinfo['pk'],type=2)) 
        row_dict = {'submission_id':subinfo['pk'], 'dynamics_id': subinfo['dynamics_id'], 'state':state, 'is_completed':is_completed}
        if request.user.is_superuser:
            row_dict['username'] = subinfo['user_id__username']
        submission_table.append(row_dict)
    return render(request, 'accounts/user_submissions.html', context={'submission_table':submission_table,'username':request.user.username,'superuser':request.user.is_superuser})
