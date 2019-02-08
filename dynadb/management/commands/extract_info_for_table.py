from django.core.management.base import BaseCommand, CommandError
from dynadb.models import *
import os 
import csv

class Command(BaseCommand):
    def handle(self, *args, **options):
        out_path="/protwis/sites/files/Precomputed/Summary_info/"
        if not os.path.isdir(out_path):
            os.makedirs(out_path)
        dynobj=DyndbDynamics.objects.all()
        first=True
        with open(os.path.join(out_path,"simulated_pdbs.csv"),"w") as outfile:
            if first:
                first=False
            else:
                mywriter = csv.writer(outfile,delimiter=';')
                mywriter.writerow(["PDB id","Dyn id","is apo"])
                for dyn in dynobj:
                    dyn_id=dyn.id
                    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
                    pdb_id=model.pdbid
                    mtype_val=model.type
                    if mtype_val==1:
                        is_apo=False
                    elif mtype_val==0:
                        is_apo=True
                    else:
                        self.stdout.write(self.style.ERROR("Unknown model type for dyn "+str(dyn_id)))
                        continue
                    mywriter.writerow([pdb_id,dyn_id,is_apo])