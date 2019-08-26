from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from dynadb.models import DyndbDynamics
import gc
import pickle

class Command(BaseCommand):
    help = "Retrieves the transformation matrix corresponding to the alignment between our model PDBs and the x-ray PDBs. This will be used to align the ED map of the x-ray structure to our model and simulation."
    def add_arguments(self, parser):
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.',
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) for which the matrix will be precomputed. '
        )
    def handle(self, *args, **options):
        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))


        dynfiledata = dynobj.annotate(dyn_id=F('id'))
        dynfiledata = dynfiledata.annotate(file_path=F('dyndbfilesdynamics__id_files__filepath'))
        dynfiledata = dynfiledata.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
        dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
        dynfiledata = dynfiledata.annotate(file_ext=F('dyndbfilesdynamics__id_files__id_file_types__extension'))
        dynfiledata = dynfiledata.values("dyn_id","file_path","file_id","file_is_traj","file_ext")

        dyn_dict = {}
        for dyn in dynfiledata:
            dyn_id=dyn["dyn_id"]
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]={}
                dyn_dict[dyn_id]["dyn_id"]=dyn_id
                dyn_dict[dyn_id]["files"]={"traj":[], "pdb":[]}
                dyn_dict[dyn_id]["pdb_namechain"]=False
                dyn_dict[dyn_id]["chains"]=set()
                dyn_dict[dyn_id]["segments"]=set()
                dyn_dict[dyn_id]["lig_li"]=set()
                dyn_dict[dyn_id]["uniprot"]=[]
            file_info={"id":dyn["file_id"],"path":dyn["file_path"]}
            if dyn["file_is_traj"]:
                dyn_dict[dyn_id]["files"]["traj"].append(file_info)
            elif dyn["file_ext"]=="pdb":
                dyn_dict[dyn_id]["files"]["pdb"].append(file_info)
        
        del dynfiledata

        dynmols = dynobj.annotate(dyn_id=F('id'))
        dynmols = dynmols.annotate(pdb_namechain=F("id_model__pdbid"))
        dynmols = dynmols.annotate(chain=F("id_model__dyndbmodeledresidues__chain"))
        dynmols = dynmols.annotate(seg=F("id_model__dyndbmodeledresidues__segid"))
        dynmols = dynmols.annotate(comp_resname=F("id_model__dyndbmodelcomponents__resname"))
        dynmols = dynmols.annotate(comp_type=F("id_model__dyndbmodelcomponents__type"))
        dynmols = dynmols.values("dyn_id","pdb_namechain","chain","seg","comp_resname","comp_type")

        for dyn in dynmols:
            dyn_id=dyn["dyn_id"]
            dyn_dict[dyn_id]["pdb_namechain"]=dyn["pdb_namechain"]
            if dyn["chain"]:
                dyn_dict[dyn_id]["chains"].add(dyn["chain"])
            if dyn["seg"]:
                dyn_dict[dyn_id]["segments"].add(dyn["seg"])
            if dyn["comp_type"]==1:
                dyn_dict[dyn_id]["lig_li"].add(dyn["comp_resname"])

        del dynmols
        gc.collect()

        dyn_li=DyndbDynamics.objects.filter(is_published=True)


        dynprot=dynobj.annotate(dyn_id=F('id'))
        dynprot=dynprot.annotate(uniprot=F('id_model__id_protein__uniprotkbac'))
        dynprot=dynprot.annotate(uniprot2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__uniprotkbac'))
        dynprot = dynprot.values("dyn_id","uniprot","uniprot2")
        
        for dyn in dynprot:
            dyn_id=dyn["dyn_id"]
            up=dyn["uniprot"]
            if not up:
                up=dyn["uniprot2"]
            if not up:
                self.stdout.write(self.style.NOTICE("UniProt ID not found for dyn %s" % (dyn_id)))
                continue
            dyn_dict[dyn_id]["uniprot"].append(up)

        with open("/protwis/sites/files/Precomputed/Summary_info/dyn_dict.data", 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(dyn_dict, filehandle)