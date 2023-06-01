from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from modules.dynadb.models import DyndbDynamics,DyndbProtein
from modules.protein.models import Protein
import pickle
from modules.view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from modules.view.views import findGPCRclass
from modules.dynadb.pipe4_6_0 import checkpdb_ngl, matchpdbfa_ngl
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
        def obtain_fplot_input(result,numbers,chain_name,current_class):
            resi_to_group = {}
            resi_to_name = {}
            cluster_dict={}
            #chain_index=str(chain_name_li.index(chain_name))
            pos_gnum = numbers[current_class]
            for pos in result:
                if pos[0] != "-": #Consider only num in the pdb
                    db_pos=pos[1][1]
                    pdb_pos=pos[0][1]
                    #gnum_or_nth=""
                    this_gnum = pos_gnum[db_pos][1]
                    this_segm = pos_gnum[db_pos][2]
                    resi_to_group[(pdb_pos,chain_name)]=str(this_segm)
                    if this_gnum:#If exist GPCR num for this position
                        this_gnum=this_gnum[:this_gnum.find(".")]+this_gnum[this_gnum.find("x"):]
                        cluster_dict[this_gnum]=[chain_name+"."+pdb_pos,""]
                    resi_to_name[(pdb_pos,chain_name)]=str(this_gnum)
            return(resi_to_group,resi_to_name,cluster_dict)  

        def obtain_resi_to_dicts(dyn_id,pdbpath,chain_name_li,gpcr_Gprot,gpcr_Dprot):
            gen_num_res=obtain_gen_numbering(dyn_id, gpcr_Dprot,gpcr_Gprot) 
            if len(gen_num_res) <= 2:
                print("Error obtaining GPCR generic numbering (1).")
                return
            (numbers, num_scheme, db_seq, current_class) = gen_num_res
            current_class=findGPCRclass(num_scheme)
            gpcr_n_ex=""
            for pos_gnum in numbers[current_class].values():
                if pos_gnum[1]: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                    gpcr_n_ex=pos_gnum[1]
                    break
            if not "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                error="Error obtaining GPCR generic numbering (2)."
                print(error)
                return
            dprot_chain_res=[] #old dprot_chains[prot_id][0]
            chains_taken=set()
            seq_pos_n=1
            for chain_name in chain_name_li:
                checkpdb_res=checkpdb_ngl(pdbpath, segid="",start=-1,stop=9999999999999999999, chain=chain_name)
                if isinstance(checkpdb_res, tuple):
                    tablepdb,pdb_sequence,hexflag=checkpdb_res 
                    result=matchpdbfa_ngl(prot_seq,pdb_sequence, tablepdb, hexflag)
                    type(result)
                    if isinstance(result, list):
                        #chain_results[chain_name]=result
                        if chain_name not in chains_taken:
                            chains_taken.add(chain_name)
                            (resi_to_group,resi_to_name,cluster_dict)=obtain_fplot_input(result,numbers,chain_name,current_class)
            for (pos, gnum) in resi_to_name.items():
                if gnum != "None":
                    chain=gnum.split("x",1)[0]
                    resi_to_name[pos]=chain+"."+gnum
            return resi_to_group,resi_to_name,chains_taken


        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))


        dynfiledata = dynobj.annotate(dyn_id=F('id'))
        dynfiledata = dynfiledata.annotate(is_pub=F('is_published'))
        dynfiledata = dynfiledata.annotate(sub_id=F('submission_id__id'))
        dynfiledata = dynfiledata.annotate(file_path=F('dyndbfilesdynamics__id_files__filepath'))
        dynfiledata = dynfiledata.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
        dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
        dynfiledata = dynfiledata.annotate(file_ext=F('dyndbfilesdynamics__id_files__id_file_types__extension'))
        dynfiledata = dynfiledata.values("dyn_id","file_path","file_id","file_is_traj","file_ext","is_pub","sub_id","delta")

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
                dyn_dict[dyn_id]["is_published"]=dyn["is_pub"]
                dyn_dict[dyn_id]["delta"]=dyn["delta"]
                dyn_dict[dyn_id]["submission_id"]=dyn["sub_id"]
                dyn_dict[dyn_id]["seg_to_chain"]={}
                dyn_dict[dyn_id]["prot_lig_li"]=False
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
            dyn_dict[dyn_id]["seg_to_chain"][dyn["seg"]]=dyn["chain"]

        del dynmols


        dynprot=dynobj.annotate(dyn_id=F('id'))
        dynprot=dynprot.annotate(uniprot=F('id_model__id_protein__uniprotkbac'))
        dynprot=dynprot.annotate(uniprot2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__uniprotkbac'))
        dynprot=dynprot.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
        dynprot=dynprot.annotate(fam_slug2=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
        dynprot = dynprot.values("dyn_id","uniprot","uniprot2","fam_slug","fam_slug2")
        
        for dyn in dynprot:
            dyn_id=dyn["dyn_id"]
            prot_slug=dyn["fam_slug"]
            if not prot_slug:
                prot_slug=dyn["fam_slug2"]
            if not prot_slug:
                dyn_dict[dyn_id]["prot_lig_li"]=True
                print("\n\nHas prot lig: %s\n\n"% dyn_id)
            up=dyn["uniprot"]
            if not up:
                up=dyn["uniprot2"]
            if not up:
                self.stdout.write(self.style.NOTICE("UniProt ID not found for dyn %s" % (dyn_id)))
                continue
            dyn_dict[dyn_id]["uniprot"].append(up)

        del dynprot

        dynseq=dynobj.annotate(dyn_id=F('id'))
        dynseq=dynseq.annotate(dbprotgpcr_id=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__id'))
        dynseq=dynseq.annotate(dbprotgpcr_id2=F('id_model__id_protein__receptor_id_protein__id'))
        dynseq=dynseq.annotate(mdprot_id=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__id'))
        dynseq=dynseq.annotate(mdprot_id2=F('id_model__id_protein__id'))
        dynseq=dynseq.annotate(seq=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__dyndbproteinsequence__sequence'))
        dynseq=dynseq.annotate(seq2=F('id_model__id_protein__dyndbproteinsequence__sequence'))
        dynseq = dynseq.values("dyn_id","dbprotgpcr_id","dbprotgpcr_id2","mdprot_id","mdprot_id2","seq","seq2")

        for dyn in dynseq:
            if dyn["dbprotgpcr_id"]:
                dbprot_id=dyn["dbprotgpcr_id"]
            elif dyn["dbprotgpcr_id2"]:
                dbprot_id=dyn["dbprotgpcr_id2"]
            else:
                continue #It's not GPCR
            if dyn["mdprot_id"]:
                mdprot_id=dyn["mdprot_id"]
            elif dyn["mdprot_id2"]:
                mdprot_id=dyn["mdprot_id2"]
            else:
                continue 
            if dyn["seq"]:
                prot_seq=dyn["seq"]
            elif dyn["seq2"]:
                prot_seq=dyn["seq2"]
            else:
                continue
            dyn_id=dyn["dyn_id"]
            chain_name_li=dyn_dict[dyn_id]["chains"]
            pdbpath=dyn_dict[dyn_id]["files"]["pdb"][0]["path"]
            gpcr_Gprot=Protein.objects.get(id=dbprot_id)
            gpcr_Dprot=DyndbProtein.objects.get(id=mdprot_id)
            try:
                resi_to_dicts = obtain_resi_to_dicts(dyn_id,pdbpath,chain_name_li,gpcr_Gprot,gpcr_Dprot)
            except:
                resi_to_dicts={}
            if resi_to_dicts:
                (resi_to_group,resi_to_name,prot_chains)=resi_to_dicts
                dyn_dict[dyn_id]["resi_to_group"]=resi_to_group
                dyn_dict[dyn_id]["resi_to_name"]=resi_to_name
                dyn_dict[dyn_id]["prot_chains"]=prot_chains


        with open(settings.MEDIA_ROOT + "Precomputed/Summary_info/dyn_dict.data", 'wb') as filehandle:  
            # store the data as binary data stream
            pickle.dump(dyn_dict, filehandle)

