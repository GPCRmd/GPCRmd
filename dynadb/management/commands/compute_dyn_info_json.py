from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import os
from os import path
import pandas as pd
import json
import datetime
import re
from view.views import compute_interaction, obtain_all_chains, relate_atomSerial_mdtrajIndex
from view.data import change_lig_name
from dynadb.models import DyndbProtein, DyndbFilesDynamics, DyndbSubmissionMolecule, DyndbDynamicsComponents,DyndbModeledResidues, DyndbDynamics
from protein.models import Protein
from view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from dynadb.pipe4_6_0 import *
from view.views import obtain_prot_chains , obtain_DyndbProtein_id_list, obtain_seq_pos_info, findGPCRclass, obtain_rel_dicts, traduce_all_poslists_to_ourclass_numb,obtain_predef_positions_lists,find_missing_positions
import copy
import operator


class Command(BaseCommand):
    help = "Creates precomputed datafiles of ligand-residue interactons in the GPCRs stored at the database for posterior creation of comparaive plots. Only considers published data."
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already stored data, calculating again the interactions for all the public dynamics stored at the DB.',
        )

#        parser.add_argument(
#           '-dyn_id',
#            dest='dyn_id',
#            nargs='*',
#            action='store',
#            default=False,
#            help='Dynamics id(s) for which lihand-residue interactions will be precomputed. All dynamics which are "ready for publication" and were not precumputed before will be admitted if no #id(s) are provided.'
#        )
#        parser.add_argument(
#            '-str',
#            dest='stride', 
#            nargs='?',
#            action='store',
#            default=1,
#            type=int,
#            help='Stride the trajectories.'
#        )
        
    def handle(self, *args, **options):

        def generate_gpcr_pdb (dyn_id, structure_file):
            """Code extracted frin view/views index"""
            pdb_name = structure_file
            chain_name_li=obtain_prot_chains(pdb_name)
            multiple_chains=False
            if len(chain_name_li) > 1:
                multiple_chains=True
            (prot_li_gpcr, dprot_li_all,dprot_li_all_info,pdbid)=obtain_DyndbProtein_id_list(dyn_id)            
            dprot_chains={}
            chains_taken=set()
            gpcr_chains=[]
            non_gpcr_chains=[]
            prot_seq_pos={}
            seq_pos_n=1
            all_chains=[]
            all_prot_names=[]
            for prot_id, prot_name, prot_is_gpcr, prot_seq in dprot_li_all_info: #To classify chains by protein (dprot_chains is a dict:for each protein, has a list of each chain with its matchpdbfa results + the protein seq_pos)
                all_prot_names.append(prot_name)
                seq_pos=[]
                dprot_chains[prot_id]=[[],[]]  
                for chain_name in chain_name_li:
                    checkpdb_res=checkpdb_ngl(pdb_name, segid="",start=-1,stop=9999999999999999999, chain=chain_name)
                    if isinstance(checkpdb_res, tuple):
                        tablepdb,pdb_sequence,hexflag=checkpdb_res
                        result=matchpdbfa_ngl(prot_seq,pdb_sequence, tablepdb, hexflag)
                        if isinstance(result, list):
                            #chain_results[chain_name]=result
                            if chain_name not in chains_taken:
                                chains_taken.add(chain_name)
                                dprot_chains[prot_id][0].append((chain_name,result))
                                seq_pos,seq_pos_n=(seq_pos,seq_pos_n)=obtain_seq_pos_info(result,seq_pos,seq_pos_n,chain_name,multiple_chains)
                                dprot_chains[prot_id][1]=seq_pos
                                all_chains.append(chain_name)
                                if prot_is_gpcr:
                                    gpcr_chains.append(chain_name)
                                else:
                                    non_gpcr_chains.append(chain_name)
                prot_seq_pos[prot_id]=(prot_name,seq_pos)
            keys_to_rm=set()
            for key, val in dprot_chains.items():
                if val==([],[]):
                    keys_to_rm.add(key)
            for key in keys_to_rm:
                del dprot_chains[key]

                
            if chains_taken: # To check if some result have been obtained
                all_gpcrs_info=[]
                seg_li_all={}
                gpcr_pdb_all={}
                gpcr_id_name={}
                for gpcr_DprotGprot in prot_li_gpcr:
                    gpcr_Dprot=gpcr_DprotGprot[0]
                    gpcr_Gprot=gpcr_DprotGprot[1]
                    dprot_id=gpcr_Dprot.id
                    dprot_name=gpcr_Dprot.name
                    gen_num_res=obtain_gen_numbering(dyn_id, gpcr_Dprot,gpcr_Gprot)  #warning!! the problem is here
                    if len(gen_num_res) > 2:
                        (numbers, num_scheme, db_seq, current_class) = gen_num_res
                        current_class=findGPCRclass(num_scheme)
                        gpcr_n_ex=""
                        for pos_gnum in numbers[current_class].values():
                            if pos_gnum[1]: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                                gpcr_n_ex=pos_gnum[1]
                                break
                        if "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                            seq_pos_index=0
                            gpcr_pdb={}
                            gpcr_aa={}
                            gnum_classes_rel={}
                            (dprot_chain_li, dprot_seq) = dprot_chains[dprot_id] 
                            for chain_name, result in dprot_chain_li:
                                (gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,dprot_seq,seq_pos_index,seg_li)=obtain_rel_dicts(result,numbers,chain_name,current_class,dprot_seq,seq_pos_index, gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,simplified=True)
                                                                
                            prot_seq_pos[dprot_id]=(dprot_name, dprot_seq)
                            gpcr_pdb_all[dprot_id]=(gpcr_pdb)
                            gpcr_id_name[dprot_id]=dprot_name
                            seg_li_all[dprot_id]=seg_li #[!] For the moment I don't use this, I consider only 1 GPCR
            return(gpcr_pdb) #[!] For now I only consider 1 GPCR, so I only need this dict

    
        def json_dict(path):
            """Converts json file to pyhton dict."""
            json_file=open(path)
            json_str = json_file.read()
            json_data = json.loads(json_str)
            return json_data

        def prot_from_model(model):
            """Given a db model obj, gets the GPCR protein object"""
            model_prot=model.id_protein
            if model_prot:
                if not model_prot.receptor_id_protein:
                    self.stdout.write(self.style.ERROR("Protein ID:%d UniprotKB AC:%s is not a GPCR or has no GPCRdb ID set.") % (model_prot.id,model_prot.uniprotkbac))
                    raise CommandError("FATAL: error. There is no GPCR in the simulation. Cannot continue.")
                prot=model_prot
                total_num_prot=1
            else:
                prot = DyndbProtein.objects.filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
                if not list(prot.values_list("receptor_id_protein",flat=True)):
                    prot = prot.values('id','uniprotkbac')
                    prot0 = prot[0]
                    self.stdout.write(self.style.ERROR("Protein ID:%d UniprotKB AC:%s is not a GPCR or has no GPCRdb ID set.") % (prot0['id'],prot0['uniprotkbac']))
                    raise CommandError("FATAL: error. There is no GPCR in the simulation. Cannot continue.") 
                protli=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
                total_num_prot=len(protli)
                prot=""
                for p in protli:
                    if p.receptor_id_protein:
                        prot=p
            return (prot,total_num_prot)


        def obtain_dyn_files(dyn_id):
            """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
            dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
            traj_list=[]
            traj_name_list=[]
            structure_file = None
            structure_file_name = None
            p2=re.compile("[\.\w]*$")
            for fileobj in dynfiles:
                path=fileobj.id_files.filepath
                myfile=path
                myfile_name=p2.search(myfile).group()
                if myfile.endswith(".pdb"):
                    structure_file=myfile
                    structure_file_name=myfile_name
                elif myfile.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
                    traj_list.append([myfile,fileobj.id_files.id])
                    traj_name_list.append(myfile_name)
            
            return (structure_file,structure_file_name,traj_list,traj_name_list)

        def get_orthostericlig_resname(dyn_id,change_lig_name):
            """Returns a list with the the resname of the orthosteric ligamd(s) of a dynamics"""
            ortholig_li=DyndbSubmissionMolecule.objects.filter(submission_id__dyndbdynamics=dyn_id,type=0)
            if len(ortholig_li) == 0:
                return (False,False,False)
            comp_set_all=set()
            for ortholig in ortholig_li:
                comp_li=DyndbDynamicsComponents.objects.filter(id_molecule=ortholig.molecule_id.id)
                comp_set=set(map(lambda x: x.resname ,comp_li)) 
                comp_set_all.update(comp_set)
            comp_obj=ortholig_li[0].molecule_id.id_compound #[!] For now I only consider 1 orthosteric ligand for each dyn!
            comp_id=comp_obj.id 
            comp_name=comp_obj.name
            if (dyn_id in change_lig_name):
                comp_name=change_lig_name[dyn_id]["longname"]
                comp_set_all=[change_lig_name[dyn_id]["resname"]] 
            return (comp_id,comp_name,list(comp_set_all))
                
        def retrieve_info(self,dyn,change_lig_name):
            """Retrieves all the necessary info of the dyn obj for the analysis and computes it."""
            dyn_id=dyn.id
            identifier="dyn"+str(dyn_id)
            allfiles_path="/protwis/sites/files/"
            model=dyn.id_model
            model_id=model.id
            pdb_id=model.pdbid
            if not (model.id_protein or model.id_complex_molecule):
                self.stdout.write(self.style.NOTICE("Model has no protein or complex assigned. Skipping."))
                return
            (prot,total_num_prot)=prot_from_model(model)
            prot_id=prot.id 
            uniprot_id=prot.uniprotkbac
            uniprot_name=Protein.objects.get(accession=uniprot_id).entry_name
            (structure_file,structure_file_name,traj_list,traj_name_list)=obtain_dyn_files(dyn_id)
            if not structure_file:
                self.stdout.write(self.style.NOTICE("No structure file found. Skipping."))
            (comp_id,comp_name,res_li)=get_orthostericlig_resname(dyn_id,change_lig_name) 

            # If there's no ligand
            if not bool(res_li):
                res_li = ['']
                copm_name = ''

            if len(traj_list) == 0:
                self.stdout.write(self.style.NOTICE("No trajectories found. Skipping."))
            else:
                traj_files = [ i[0] for i in traj_list ]
                gpcr_pdb=generate_gpcr_pdb(dyn_id, structure_file)
                pdb_to_gpcr = {v: k for k, v in gpcr_pdb.items()}
                delta=DyndbDynamics.objects.get(id=dyn_id).delta
                compl_data[identifier]={
                    "dyn_id": dyn_id,
                    "prot_id": prot_id, 
                    "comp_id": comp_id,
                    "lig_lname":comp_name,
                    "lig_sname":res_li[0],
                    "prot_lname":prot.name,
                    "up_name":uniprot_name,
                    "pdb_id":pdb_id,
                    "struc_f":structure_file,
                    "struc_fname":structure_file_name,
                    "traj_f":traj_files,
                    "traj_fnames":traj_name_list,
                    "delta":delta,
                    "gpcr_pdb":gpcr_pdb
                    }

        def update_time(upd,upd_now):
            year=upd_now.year
            month=upd_now.month
            day=upd_now.day
            hour=upd_now.hour
            minute=upd_now.minute
            second=upd_now.second
            microsecond =upd_now.microsecond
            updtime=upd["ligres_int"]
            updtime["year"]=year
            updtime["month"]=month
            updtime["day"]=day
            updtime["hour"]=hour
            updtime["minute"]=minute
            updtime["second"]=second
            updtime["microsecond"]=microsecond
            
        def obtain_datetime(upd):
            u=upd["ligres_int"]
            last_upd_dt=datetime.datetime(u["year"], u["month"], u["day"], u["hour"], u["minute"], u["second"], u["microsecond"])
            return last_upd_dt
    
        cra_path="/protwis/sites/files/Precomputed/get_contacts_files"
        if not os.path.isdir(cra_path):
            os.makedirs(cra_path)
        upd_now=datetime.datetime.now()
        compl_file_path=path.join(cra_path,"compl_info.json")
        upd_file_path=path.join(cra_path,"last_update.json")
        if options['overwrite']:
            compl_data={}
            dyn_li=DyndbDynamics.objects.filter()
            upd={"ligres_int":{}}
        else: 
            compl_file_pathobj = Path(compl_file_path)
            try:
                compl_abs_path = compl_file_pathobj.resolve()
                compl_data = json_dict(compl_file_path)
            except FileNotFoundError:
                compl_data={}       
            upd_file_pathobj = Path(upd_file_path)
            try:
                upd_abs_path = upd_file_pathobj.resolve()
                upd=json_dict(upd_file_path)
                last_upd_dt=obtain_datetime(upd)
                dyn_li=DyndbDynamics.objects.filter()#update_timestamp__gte=last_upd_dt) # TODO: activate option when on development
            except FileNotFoundError:
                upd={"ligres_int":{}}
                dyn_li=DyndbDynamics.objects.filter()

        i=1
        dyn_li = sorted(dyn_li, key=operator.attrgetter('id'))
        for dyn in dyn_li:
            try:
                self.stdout.write(self.style.NOTICE("Computing dictionary for dynamics with id %d (%d/%d) ...."%(dyn.id,i , len(dyn_li))))
                retrieve_info(self,dyn,change_lig_name)
            except FileNotFoundError:
                self.stdout.write(self.style.NOTICE("Files for dynamics with id %d are not avalible. Skipping" % (dyn.id)))
            i+=1

        update_time(upd,upd_now)
        with open(upd_file_path, 'w') as outfile:
            json.dump(upd, outfile)
        with open(compl_file_path, 'w') as outfile:
            json.dump(compl_data, outfile)

            
