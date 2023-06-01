from django.core.management.base import BaseCommand, CommandError
from modules.dynadb.models import *
import os 
import csv
from django.conf import settings

class Command(BaseCommand):
    def handle(self, *args, **options):
        def obtain_prot(model):
            if model.id_protein:
                return model.id_protein
            else:
                all_prot=[]
                dprot_li_all=DyndbProtein.objects.filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
                for dprot in dprot_li_all:
                    gprot= dprot.receptor_id_protein
                    if gprot:
                        all_prot.append(dprot)
                return all_prot[0]
        out_path=settings.MEDIA_ROOT + "Precomputed/Summary_info/"
        if not os.path.isdir(out_path):
            os.makedirs(out_path)
        dynobj=DyndbDynamics.objects.all()
        with open(os.path.join(out_path,"simulated_pdbs_pubinfo_allinfo.csv"),"w") as outfile:
            mywriter = csv.writer(outfile,delimiter=';')
            mywriter.writerow(["PDB id","Dyn id","is apo","is_published","uniprot","is_mut","name","description"])
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
                is_published=dyn.is_published
                try:
                    prot=obtain_prot(model)
                except:
                    mywriter.writerow([pdb_id,dyn_id,is_apo,is_published,"-","-","-","-"])
                else:
                    is_mut=prot.is_mutated
                    uniprot=prot.uniprotkbac
                    mywriter.writerow([pdb_id,dyn_id,is_apo,is_published, uniprot,is_mut,model.name,model.description])
