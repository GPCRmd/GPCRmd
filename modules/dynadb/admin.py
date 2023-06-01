from django.contrib import admin
from .models import DyndbModeledResidues, DyndbProtein, DyndbOtherProteinNames, DyndbProteinSequence, DyndbModel, DyndbDynamics, DyndbDynamicsComponents

# Register your models here.
admin.site.register(DyndbModeledResidues)
admin.site.register(DyndbDynamics)
admin.site.register(DyndbDynamicsComponents)
admin.site.register(DyndbProtein)
admin.site.register(DyndbModel)
admin.site.register(DyndbOtherProteinNames)
admin.site.register(DyndbProteinSequence)
