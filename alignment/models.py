from django.db import models

# Create your models here.

class Registration(models.Model):
    name = models.CharField(max_length=200)
    username = models.CharField(max_length=200,unique=True)
    email = models.EmailField(max_length=254)
    institution = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    activation =  models.BooleanField(default=False)
    def __str__(self):
        return self.username
