from django.conf import settings
from django import forms
from modules.accounts.models import User
from django.forms import ModelForm, PasswordInput
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import  get_template
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.forms import PasswordResetForm as PasswordResetForm_default


from modules.accounts.models import User

class RegistrationForm(forms.ModelForm):
    """
    When a user registers, saves his data and sends him an email to activate the account.
    """
    username = forms.CharField(widget=forms.widgets.TextInput,label="Username")
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,
                                label="Confirm password")
    class Meta:
        model = User
        fields = ['first_name','last_name', 'username', 'email','country','institution','department','lab' ,'password1', 'password2']
        labels = {'lab':'Laboratory / Group / Unit'}

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()    
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two passwords did not match.")
        return self.cleaned_data

    def send_mail(self, subject_template_name, 
             email_template_name,
             context, from_email, to_email, 
             html_email_template_name=None):
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        to_email = to_email.split(",")
        email_message = EmailMultiAlternatives(subject, body, from_email, to_email,headers=settings.EMAIL_TRANSACTIONAL_HEADERS)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()



    def save(self, commit=True,
             subject_template_name='accounts/act/act_subject.txt',
             email_template_name='accounts/act/act_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None,
             ):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()

        #### Generates a one-use only link for activating the user
        email = self.cleaned_data["email"]
        user=get_user_model().objects.get(email=email)
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
        context = {
            'email': user.email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'user': user,
            'token': token_generator.make_token(user),
            'protocol': 'https' if use_https else 'http',
        }
        self.send_mail(
            subject_template_name, email_template_name, 
            context, from_email, user.email, 
            html_email_template_name=html_email_template_name,
        )
        return user


class AuthenticationForm(forms.Form): #Login
    username = forms.CharField(widget=forms.widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        fields = ['username', 'password']
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            if username is not None and password is not None:
                raise forms.ValidationError("Invalid login.")
        return self.cleaned_data


class ChangeForm(forms.ModelForm):
    """Form to change the personal data of a user"""
    class Meta:
        model=User
        fields = ['first_name','last_name','country','institution','department','lab']
        labels = {'lab':'Laboratory / Group / Unit'}


class ChangePassw(forms.ModelForm):
    """Change password"""
    password1 = forms.CharField(widget=forms.PasswordInput,
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,label="Confirm password")    
    class Meta:
        model=User
        fields = ['password1','password2']
    def clean(self):
        cleaned_data = super(ChangePassw, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two passwords did not match.")
        return self.cleaned_data
    def save(self, commit=True):
        user = super(ChangePassw, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

 
## Change email

class ChangeMailForm(forms.ModelForm):
    """If the new email introduced is not used by anyone in the DB, sets it to the field 'email_new' and sends a mail to this address for confirmation"""
    def __init__(self, *args, **kwargs):                               
        self.email_old = kwargs.pop('email_old', None)                   
        super(ChangeMailForm, self).__init__(*args, **kwargs)   
    class Meta:
        model=User
        fields = ['email_new']

    def clean(self):
        email_new = self.cleaned_data['email_new']
        email_old = self.email_old
        if email_new == email_old: # Maybe this will not work..! 
            raise forms.ValidationError("This email is already associated with your account.")
        else:
            if User.objects.filter(email=email_new).exists(): 
                raise forms.ValidationError("This email is already taken.")
        return self.cleaned_data

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        email_message = EmailMultiAlternatives(subject, body, from_email, to_email,headers=settings.EMAIL_TRANSACTIONAL_HEADERS)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')
        email_message.send()


    def save(self, username, commit=True,
             subject_template_name='accounts/mail/mail_subject.txt',
             email_template_name='accounts/mail/mail_email.html', 
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """
        Generates a one-use only link for activating the new mail and sends it to the
        user.
        """
        user = super(ChangeMailForm, self).save(commit=False)
        if commit:
            user.save()
          # email_new = self.cleaned_data["email_new"]        
            user=get_user_model().objects.get(username=username)
            current_site = get_current_site(request)           
            site_name = current_site.name
            domain = current_site.domain
            context = {
                'username': user.username,
                'email': user.email_new,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }
            self.send_mail(
                subject_template_name, email_template_name, context, from_email,
                user.email_new, html_email_template_name=html_email_template_name,
            )


class PasswordResetForm(PasswordResetForm_default):
    def send_mail(self, subject_template_name, email_template_name,
                context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, to_email,headers=settings.EMAIL_TRANSACTIONAL_HEADERS)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

