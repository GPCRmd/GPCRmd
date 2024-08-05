import pandas as pd

from django.core.management.base import BaseCommand, CommandError

from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from modules.dynadb.models import DyndbDynamics, DyndbReferencesDynamics 

class Command(BaseCommand):
    help = "Get individual contributions."
    
    def handle(self, *args, **kwargs):
        
        def get_data(published):
            # Get published, individual dynamics 
            dynobj=DyndbDynamics.objects.filter(is_published=published, submission_id__is_closed=True)
            dynprot = dynobj.annotate(dyn_id=F('id'))
            dynprot = dynprot.annotate(is_gpcrmd_community=F('submission_id__is_gpcrmd_community'))
            
            return dynprot
        
        def get_references(dyn_ids):
            # Get references of this dynamics
            dynref=DyndbReferencesDynamics.objects.filter(id_dynamics__in = list(dyn_ids))
            dynr = dynref.annotate(pmid=F('id_references__pmid'))
            dynr = dynr.annotate(title=F('id_references__title'))
            dynref_values = dynr.values("title", "pmid").distinct()
            
            return dynref_values
            
        def get_dyn_ids(dynprot, gpcrmd_com):
            dyn_values = dynprot.values("dyn_id","is_gpcrmd_community").filter(is_gpcrmd_community=gpcrmd_com)
            dyn_ids = dyn_values.values_list("dyn_id")
            
            return dyn_ids
        
        dyn_pub_data = get_data(True)
        dyn_unpub_data = get_data(False)
        
        dyn_pub_com_dyns = get_dyn_ids(dyn_pub_data, True)
        dyn_unpub_com_dyns = get_dyn_ids(dyn_unpub_data, True)
        
        dyn_pub_ind_dyns = get_dyn_ids(dyn_pub_data, False)
        dyn_unpub_ind_dyns = get_dyn_ids(dyn_unpub_data, False)

        print(f'Community contributions - Published ({len(list(dyn_pub_com_dyns))}) - Unpublished ({len(list(dyn_unpub_com_dyns))})')
        print(f'Individual contributions - Published ({len(list(dyn_pub_ind_dyns))}) - Unpublished ({len(list(dyn_unpub_ind_dyns))})')
        
        ref_com = get_references(dyn_pub_com_dyns)
        ref_ind = get_references(dyn_pub_ind_dyns)
        
        print(f'Papers:')
        print(f'    - Community:{ref_com}')
        print(f'    - Individual: {ref_ind}')