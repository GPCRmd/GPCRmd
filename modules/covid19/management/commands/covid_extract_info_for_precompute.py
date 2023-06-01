from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from covid19.models import *
import pickle
from django.conf import settings

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
        def parse_pdb_ligand_details(pdbfile,ligresname_set):# chainid_list = [], resname_list = [], resid_list = []):
            """ 
            Find and annotate residues that are identified as ligands
            """
            residues=set()
            # Open and parse the structure PDB in search of ligand residues
            with open(pdbfile, "r") as f:
                for line in f:
                    true_conditions = 0
                    if line.startswith("END"): 
                        break
                    if line.startswith("ATOM") or line.startswith("HETATM"):
                        line_chainid = line[21].strip()
                        line_resname = line[17:21].strip()
                        line_resid = line[22:26].strip()

                        if line_resname in ligresname_set:
                            residues.add(line_chainid+":"+line_resname+":"+line_resid)
            
            return(residues)

        def get_var_data():


            found_muts=CovidMutatedPos.objects.annotate(prot_name=F("id_final_protein__name"))
            #found_muts=CovidMutatedPos.objects.annotate(prot_name=F("id_final_protein__name"))
            #found_muts=found_muts.annotate(isolate_id=F("covidsequence__covidsequencedgene__id_isolate__isolate_id"))
            found_muts_vals=found_muts.values("resid","resletter_from","resletter_to","prot_name")


#            found_muts=CovidMutations.objects.annotate(prot_name=F("id_sequence__covidsequencedgene__id_final_protein__name"))
#            found_muts=found_muts.annotate(isolate_id=F("id_sequence__covidsequencedgene__id_isolate__isolate_id"))
#            found_muts_vals=found_muts.values("resid","resletter_from","resletter_to","prot_name","isolate_id")
            var_by_finp_pos={}
            for myvar in found_muts_vals:
                prot_name=myvar["prot_name"]
                if prot_name not in var_by_finp_pos:
                    var_by_finp_pos[prot_name]={}
                resid=myvar["resid"]
                if resid not in var_by_finp_pos[prot_name]:
                    var_by_finp_pos[prot_name][resid]={}

                resletter_from=myvar["resletter_from"]
                resletter_to=myvar["resletter_to"]
                var_name="%s%s%s"%(resletter_from,resid,resletter_to)
                if var_name not in var_by_finp_pos[prot_name][resid]:
                    myvar_data={"resid":resid,"resletter_from":resletter_from,"resletter_to":resletter_to}
                    var_by_finp_pos[prot_name][resid][var_name]=myvar_data
            return var_by_finp_pos


        def get_relation_uniprot_to_finprot():
            prot_to_finalprot_obj=CovidProteinFinalprotein.objects.annotate(prot_name=F("id_finalprotein__name"))
            prot_to_finalprot_obj=prot_to_finalprot_obj.annotate(uniprotid=F("id_protein__uniprotkbac"))
            prot_to_finalprot_obj_val=prot_to_finalprot_obj.values("finalprot_seq_start","finalprot_seq_end","prot_name","uniprotid")
            up_to_finp_pos={}
            for myval in prot_to_finalprot_obj_val:
                uniprotid=myval["uniprotid"]
                if uniprotid not in up_to_finp_pos:
                    up_to_finp_pos[uniprotid]={}
                seq_interval=(myval["finalprot_seq_start"],myval["finalprot_seq_end"])
                up_to_finp_pos[uniprotid][seq_interval]=myval["prot_name"]
            return up_to_finp_pos

        def get_model_to_seq_var(up_to_finp_pos,var_by_finp_pos,model_file_id):
            model_pos_obj=CovidModelSeqPositions.objects.select_related("id_uniprotpos").filter(id_file=model_file_id)
            #model to finseq
            model_to_seq={}
            for m in model_pos_obj:
                up_pos=m.id_uniprotpos.seqpos
                model_pos=m.seqpos
                model_aa=m.aa
                model_chain=m.chainid
                model_to_seq[(model_pos,model_chain)]={}
                model_details={"seqpos":model_pos,"aa":model_aa,"chain":model_chain, "ca_atom_index":m.ca_atom_index}
                model_to_seq[(model_pos,model_chain)]["model_details"]=model_details

                up_pos=m.id_uniprotpos.seqpos
                up_aa=m.id_uniprotpos.aa
                model_to_seq[(model_pos,model_chain)]["up_seq_details"]={"seqpos":up_pos,"aa":up_aa}

                uniprotid=m.id_uniprotpos.id_protein.uniprotkbac
                seq_intervals_finalprot=up_to_finp_pos[uniprotid]
                model_to_seq[(model_pos,model_chain)]["finprot_seq_details"]={}
                for interval,protname in seq_intervals_finalprot.items():
                    if up_pos >=interval[0] and up_pos <=interval[1]:
                        fp_pos=(up_pos - interval[0]) +1
                        pos_var_data={}
                        thisprot_vars=var_by_finp_pos.get(protname)
                        if thisprot_vars:
                            thispos_vars=thisprot_vars.get(fp_pos)
                            if thispos_vars:
                                pos_var_data=thispos_vars

                        model_to_seq[(model_pos,model_chain)]["finprot_seq_details"][protname]={"seqpos":fp_pos,"var_data":pos_var_data}
            return model_to_seq



        if options['ignore_publication']:
            dynobj=CovidDynamics.objects.all()
        else:
            dynobj=CovidDynamics.objects.filter(is_published=True)
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))

        dynfiledata = dynobj.annotate(dyn_id=F('id'))
        dynfiledata = dynfiledata.annotate(is_pub=F('is_published'))
        dynfiledata = dynfiledata.annotate(pdbid=F('id_model__pdbid'))
        dynfiledata = dynfiledata.annotate(uniprotid=F('id_model__covidmodelprotein__id_protein__uniprotkbac'))
        dynfiledata = dynfiledata.annotate(framenum=F('covidfilesdynamics__framenum'))
        dynfiledata = dynfiledata.annotate(file_path=F('covidfilesdynamics__id_files__filepath'))
        dynfiledata = dynfiledata.annotate(file_id=F('covidfilesdynamics__id_files__id'))
        dynfiledata = dynfiledata.annotate(file_type=F('covidfilesdynamics__type'))
        dynfiledata = dynfiledata.values("dyn_id","file_path","file_id","file_type","is_pub","framenum","pdbid","uniprotid","delta")

        file_types={
            0 : 'Input coordinates',
            1 : 'Input topology',
            2 : 'Trajectory',
            3 : 'Parameters',
            4 : 'Others',
        }

        dyn_dict = {}
        for dyn in dynfiledata:
            dyn_id=dyn["dyn_id"]
            if dyn_id not in dyn_dict:
                dyn_dict[dyn_id]={}
                dyn_dict[dyn_id]["dyn_id"]=dyn_id
                dyn_dict[dyn_id]["pdbid"]=dyn["pdbid"]
                dyn_dict[dyn_id]["uniprotid"]=set()#dyn["uniprotid"]
                dyn_dict[dyn_id]["files"]={"traj":[], "pdb":[]}
                dyn_dict[dyn_id]["lig_li"]=set()
                dyn_dict[dyn_id]["is_published"]=dyn["is_pub"]
                dyn_dict[dyn_id]["delta"]=dyn["delta"]
            if dyn["uniprotid"]:
                dyn_dict[dyn_id]["uniprotid"].add(dyn["uniprotid"])
            file_info={"id":dyn["file_id"],"path":dyn["file_path"]}
            file_type=file_types.get(dyn["file_type"],None)
            if file_type=="Trajectory":
                file_info["framenum"]=dyn["framenum"]
                dyn_dict[dyn_id]["files"]["traj"].append(file_info)
            elif file_type=="Input coordinates":
                dyn_dict[dyn_id]["files"]["pdb"].append(file_info)        
        del dynfiledata

        dynmols = dynobj.annotate(dyn_id=F('id'))
        dynmols = dynmols.annotate(comp_resname=F("coviddynamicscomponents__resname"))
        dynmols = dynmols.annotate(is_ligand=F("coviddynamicscomponents__is_ligand"))
        dynmols = dynmols.values("dyn_id","comp_resname","is_ligand")

        for dyn in dynmols:
            dyn_id=dyn["dyn_id"]
            if dyn["is_ligand"]:
                dyn_dict[dyn_id]["lig_li"].add(dyn["comp_resname"])
        del dynmols


        up_to_finp_pos=get_relation_uniprot_to_finprot()
        var_by_finp_pos=get_var_data()        

        for dynid,dyndata in dyn_dict.items():
            ligresname_set=dyndata["lig_li"]
            if not dyndata["files"]["pdb"]:
                continue
            pdbfile=dyndata["files"]["pdb"][0]["path"]
            try:
                ligdetails_set = parse_pdb_ligand_details(pdbfile, ligresname_set)
            except:
                ligdetails_set="ERROR"
            dyndata["lig_li_details"]=ligdetails_set

            #Get model to seq map
            model_file_id=dyndata["files"]["pdb"][0]["id"]
            model_to_seq=get_model_to_seq_var(up_to_finp_pos,var_by_finp_pos,model_file_id)
            dyndata["model_to_seq"]=model_to_seq

        out_file=settings.MEDIA_ROOT + "Precomputed/Summary_info/covid_dyn_dict.data"
        print("Saving %s" % out_file)
        with open(out_file, 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(dyn_dict, filehandle)