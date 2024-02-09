from django.urls import reverse
from django.utils.http import urlencode
from django.utils.html import format_html

from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Protein)
admin.site.register(ProteinFamily) 
admin.site.register(ProteinPDB)
admin.site.register(ProteinState)