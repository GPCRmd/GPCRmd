import django
from django.db import models
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import UserManager
import string



class NewUserManager(BaseUserManager):
    def create_user(self,username,password):
        user=self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,username,password):
        user= self.create_user(username,password)
        user.is_staff = True
        user.is_superuser =True
        user.is_admin =True
        user.is_active =True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name=models.CharField(max_length=200)
    last_name=models.CharField(max_length=200)
    username = models.CharField(max_length=200,unique=True)
    email = models.EmailField(max_length=254, unique=True)
    country = models.CharField(max_length=200)
    institution = models.CharField(max_length=200) 
    department = models.CharField(max_length=200)
    lab = models.CharField(max_length=200)
    date_joined = models.DateField(default=django.utils.timezone.now)###
    is_active =  models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin =models.BooleanField(default=False)
    has_privilege_covid = models.BooleanField(default=False)
    email_new = models.EmailField(max_length=254, blank=True)
    objects = NewUserManager()

    USERNAME_FIELD = 'username'
      
    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.username

    class Meta:
        app_label = 'accounts'
        db_table = "user"



