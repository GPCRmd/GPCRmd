from django.contrib import admin
from .models import DyndbModeledResidues, DyndbProtein, DyndbOtherProteinNames, DyndbProteinSequence, AuthGroup, AuthUser, DyndbModel

# Register your models here.
admin.site.register(DyndbModeledResidues)
admin.site.register(DyndbProtein)
admin.site.register(DyndbModel)
admin.site.register(DyndbOtherProteinNames)
admin.site.register(DyndbProteinSequence)
admin.site.register(AuthUser)
