from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from dynadb.models import DyndbDynamics
import pickle
import requests

class Command(BaseCommand):
    help = "Retrieves info from the database to complete the dicitonary used to create the GPCRmd tree."
    def add_arguments(self, parser):
#        parser.add_argument(
#            '--overwrite',
#            action='store_true',
#            dest='overwrite',
#            default=False,
#            help='Overwrites already generated json files.',
#        )
        parser.add_argument(
           '-i',
            dest='gpcrmdtree_path',
            default="/protwis/sites/files/Precomputed/Summary_info/gpcrmdtree.data",
            action='store',
            type=str,
            help='Path to the input file containing the dicitonary-'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) of simulations to include in the plot. Otherwise all new simulations will be added.'
        )


        #Dowbload data from GPCRdb
        strucpcrdb=requests.get('http://gpcrdb.org/services/structure/').json()
        prot_info={d["protein"]:d for d in strucpcrdb}
        famgpcrdb=requests.get('http://gpcrdb.org/services/proteinfamily/').json()
        slugtofamdata={d["slug"]:d for d in famgpcrdb}

        #Load input dict
        gpcrmdtree_path=options["gpcrmdtree_path"]
        with open(gpcrmdtree_path, 'rb') as filehandle:  
            tree_data = pickle.load(filehandle)

        #Obtain dyn to be considered
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))
            return
        #Retrieve data from dyn
        dynmods = dynobj.annotate(dyn_id=F('id'))
        dynmods = dynmods.annotate(pdb_namechain=F("id_model__pdbid"))
        dynmods=dynmods.annotate(entry_name=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__entry_name'))
        dynmods=dynmods.annotate(entry_name2=F('id_model__id_protein__receptor_id_protein__entry_name'))
        vals_dynmods=dynmods.values("dyn_id","pdb_namechain","entry_name","entry_name2")

        dyn_dict = {}
        for dyn in vals_dynmods:
            dyn_id=dyn["dyn_id"]
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]={}
            pdbid=dyn["pdb_namechain"]
            if not pdbid:
                #self.stdout.write(self.style.NOTICE("!!! missing pdb in dyn %s" % dyn_id))
                print("!!! missing pdb in dyn %s" % dyn_id)
                continue
            if pdbid =="HOMO":
                continue
            pdbid=pdbid.split(".")[0].upper()

            entry_name=dyn["entry_name"]
            if not entry_name:
                entry_name=dyn["entry_name2"]
            if not entry_name:
                continue
            if entry_name not in prot_info:
                print("!!! entry name not in GPCRdb in dyn %s" % dyn_id)
                continue
            myprotd=prot_info[entry_name]
            fam_slug=myprotd["family"]
            class_slug=fam_slug.split("_")[0]
            myclass=slugtofamdata[class_slug]["name"]
            if myclass not in ['Class A (Rhodopsin)', 'Class B1 (Secretin)', 'Class C (Glutamate)', 'Class F (Frizzled)']:
                continue
            myclass=myclass[:myclass.index("(")-1]
            subtype=slugtofamdata[fam_slug]["name"]
            famname=slugtofamdata[fam_slug]["parent"]["name"]
            dyn_dict[dyn_id]["pdbid"]=pdbid
            dyn_dict[dyn_id]["class"]=myclass
            dyn_dict[dyn_id]["subtype"]=subtype
            dyn_dict[dyn_id]["fam"]=famname

        for dyn_id,dyn_data in dyn_dict.items():
            myclass=dyn_data["class"]
            class_id=["Class A","Class B1","Class F"].index(myclass)













        gpcrmdtree_path_out=options["gpcrmdtree_path_out"]
        with open(gpcrmdtree_path_out, 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(tree_data, filehandle)
