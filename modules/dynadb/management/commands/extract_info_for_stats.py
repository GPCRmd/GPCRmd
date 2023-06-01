import requests
from modules.dynadb.models import DyndbDynamics
from django.db.models import F
import pickle
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = "Creates a pickle file with a list of number of active, inactive and intermediate published simulaitons (according to PDB used)."
    def handle(self, *args, **options):
        struc=requests.get('http://gpcrdb.org/services/structure/').json()
        pdb_act={d["pdb_code"]:d["state"] for d in struc}

        dynall=DyndbDynamics.objects.filter(is_published=True)
        dynann=dynall.annotate(dyn_id=F("id"))
        dynann=dynann.annotate(pdb_namechain=F("id_model__pdbid"))
        dynall_values=dynann.values("dyn_id","pdb_namechain")

        active_set=set()
        inactive_set=set()
        interm_set=set()
        for dyn in dynall_values:
            dyn_id= dyn["dyn_id"]
            if dyn_id == 7:
                dyn["pdb_namechain"]="2YDO"
            pdb_namechain=dyn["pdb_namechain"]
            pdb = pdb_namechain.split(".")[0].upper()
            if dyn_id==4:
                pdb="4N6H"
            act_state=pdb_act[pdb]
            if act_state=="Active":
                active_set.add(dyn_id)
            elif act_state=="Inactive":
                inactive_set.add(dyn_id)
            elif act_state=="Intermediate":
                interm_set.add(dyn_id)
            else:
                self.stdout.write(self.style.NOTICE("State not regognized for dyn %s: %s" %(dyn_id,act_state)))
        act_stats=[["Active",len(active_set)],
                   ["Inactive",len(inactive_set)],
                   ["Intermediate",len(interm_set)],
                  ]
        out_file=settings.MEDIA_ROOT + "Precomputed/Summary_info/dyn_stats.data"
        with open(out_file, 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(act_stats, filehandle)
        self.stdout.write(self.style.SUCCESS("Output file successfully created: %s" % (out_file)))
