from django import forms
from accounts.models import User
from django.forms import ModelForm, PasswordInput
from django.contrib.auth import authenticate



class RegistrationForm(forms.ModelForm):
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

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ChangeForm(forms.ModelForm):
    class Meta:
        model=User
        fields = ['first_name','last_name','username' , 'email','country','institution','department','lab']
        labels = {'lab':'Laboratory / Group / Unit'}


class ChangePassw(forms.ModelForm):
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


class AuthenticationForm(forms.Form): #Login
    username = forms.CharField(widget=forms.widgets.TextInput)
    password = forms.CharField(widget=forms.widgets.PasswordInput)
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


class ActivationConfirmForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.act_code = kwargs.pop('act_code', None)
        super(ActivationConfirmForm, self).__init__(*args, **kwargs)
 
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if username is not None and password is not None:
            if not user:
                raise forms.ValidationError("Invalid user.")
            else:
                if user.is_active:
                    raise forms.ValidationError("This user has already been activated.")
                else:
                    if self.act_code != user.act_code:
                        raise forms.ValidationError("Invalid user")
        return self.cleaned_data
  
