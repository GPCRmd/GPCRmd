from django.contrib import admin
from .models import DyndbModeledResidues, DyndbProtein, DyndbOtherProteinNames, DyndbProteinSequence

# Register your models here.
admin.site.register(DyndbModeledResidues)
admin.site.register(DyndbProtein)
admin.site.register(DyndbOtherProteinNames)
admin.site.register(DyndbProteinSequence)
