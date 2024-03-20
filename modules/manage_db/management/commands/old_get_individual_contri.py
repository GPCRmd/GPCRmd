import pandas as pd

from django.core.management.base import BaseCommand, CommandError

from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from modules.dynadb.models import DyndbDynamics, DyndbReferencesDynamics 

class Command(BaseCommand):
    help = "Get individual contributions."
    
    def handle(self, *args, **kwargs):
        
        # Get published, individual dynamics 
        dynobj=DyndbDynamics.objects.filter(is_published=True)
        dynprot = dynobj.annotate(dyn_id=F('id'))
        dynprot = dynprot.annotate(is_gpcrmd_community=F('submission_id__is_gpcrmd_community'))
        dynall_values = dynprot.values("dyn_id","is_gpcrmd_community").filter(is_gpcrmd_community=False)
        dyn_ids = dynall_values.values_list("dyn_id")
        
        # Get references of this dynamics
        dynref=DyndbReferencesDynamics.objects.filter(id_dynamics__in = list(dyn_ids))
        dynr = dynref.annotate(pmid=F('id_references__pmid'))
        dynr = dynr.annotate(title=F('id_references__title'))
        dynref_values = dynr.values("title", "pmid").distinct()

        print(pd.DataFrame(list(dynref_values)))
