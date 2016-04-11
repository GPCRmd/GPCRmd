from django.contrib import admin
from .models import Formup,Question,DyndbAssayTypes


admin.site.register(DyndbAssayTypes)
admin.site.register(Question)
admin.site.register(Formup)

# Register your models here.
