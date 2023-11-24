from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(DyndbDynamics)
admin.site.register(DyndbProtein)
admin.site.register(DyndbModel) 
admin.site.register(DyndbSubmission)

admin.site.register(DyndbCannonicalProteins)
admin.site.register(DyndbModeledResidues)
admin.site.register(DyndbProteinSequence)
admin.site.register(DyndbProteinMutations)
admin.site.register(DyndbComplexExp)
admin.site.register(DyndbFiles)
admin.site.register(DyndbReferences)
admin.site.register(DyndbComplexMolecule)
admin.site.register(DyndbMolecule)
admin.site.register(DyndbUniprotSpecies) 
admin.site.register(DyndbSubmissionDynamicsFiles)
admin.site.register(DyndbCompound)
admin.site.register(DyndbFilesMolecule)