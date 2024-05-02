import pandas as pd
import re

from django.core.management.base import BaseCommand, CommandError

from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from modules.corplots.models import Corplots
from modules.dynadb.models import DyndbDynamics, DyndbModel, DyndbFilesDynamics

class Command(BaseCommand):
    help = "Update corplots table to relate the points with the structures."
    
    def add_arguments(self, parser):
        parser.add_argument(
        '--relate',
            nargs='*',
            action='store',
            default=False,
            help='Gets the structures of corplots tool and related their name to a dynamic. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
          
    def handle(self, *args, **kwargs):
               
        if kwargs["relate"]:
            recs = ['5ht1a','5ht1b','5ht1d','5ht2a','5ht2b','5ht2c','5ht4','5ht6','5ht7a','5ht7b','d1','d2','d3','d4','d5','h1','m1','m2','m3','m4','m5','α1a','α2a','α2b','α2c']            
            
            kwargs["relate"] = [ele.replace(",","") for ele in kwargs["relate"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {kwargs['relate']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in kwargs['relate']:
                if "-" in dyn_id: #To avoid write every number we incorporate ranges using min-max structure
                    dyn_id = dyn_id.replace(" ","")
                    l_dyn_id = dyn_id.split("-")
                    l_dyn_id = [int(x) for x in l_dyn_id]
                    l_dyn_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_dyn_id = range(l_dyn_id[0],l_dyn_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_dyn_id:
                        #Get data
                        dynaobj=DyndbDynamics.objects.select_related('id_dynamics_solvent_types','id_dynamics_membrane_types').get(pk=x)
                        
                        #Get name
                        name = dynaobj.id_model.name
                        mod_name = name.lower()
                        
                        #Get receptor
                        if "5-hydroxytryptamine" in mod_name:
                            mod_name = mod_name.replace("5-hydroxytryptamine receptor ", "5ht")
                        if "alpha" in mod_name:
                            mod_name = mod_name.replace("alpha-", "α")
                        l_name = mod_name.split("in complex with")
                        
                        for r in recs: 
                            if r in l_name[0]:
                                receptor = r
                                break
                            else:
                                receptor = ""     
                            
                        #Get drug
                        l_text2 = l_name[1].strip().split(" ")
                        drug = l_text2[0].replace(" ","") #Reclean
                        
                        #Add data to table Corplots
                        try:
                            query = Corplots(
                                dyn_id = x,
                                drug = drug,
                                name = name,
                                receptor = receptor,
                            )
                            query.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    #Get data
                    dynaobj=DyndbDynamics.objects.select_related('id_dynamics_solvent_types','id_dynamics_membrane_types').get(pk=dyn_id)
                    
                    #Get name
                    name = dynaobj.id_model.name
                    mod_name = name.lower()
                    
                    #Get receptor
                    if "5-hydroxytryptamine" in mod_name:
                        mod_name = mod_name.replace("5-hydroxytryptamine receptor ", "5ht")
                    if "alpha" in mod_name:
                        mod_name = mod_name.replace("alpha-", "α")
                    l_name = mod_name.split("in complex with")
                    
                    for r in recs: 
                        if r in l_name[0]:
                            receptor = r
                            break
                        else:
                            receptor = ""                            
                    
                    #Get drug
                    l_text2 = l_name[1].strip().split(" ")
                    drug = l_text2[0].replace(" ","") #Reclean
                    
                    #Add data to table Corplots
                    try:
                        query = Corplots(
                            dyn_id = dyn_id,
                            drug = drug,
                            name = name,
                            receptor = receptor,
                        )
                        query.save()
                        object_ready.append(dyn_id)
                    except:
                        object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are READY: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are UNREADY: {object_unready}'))