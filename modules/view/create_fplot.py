from modules.dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents,DyndbDynamics, DyndbModel, DyndbProtein,DyndbProteinSequence, DyndbModeledResidues
from modules.view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from modules.view.traj2flare_modified_wn import * #[!] Now it's the wn version (new version that uses MDtraj wernet_nilsson function)
from modules.view.views import findGPCRclass, obtain_all_chains, obtain_DyndbProtein_id_list, obtain_seq_pos_info
from modules.dynadb.pipe4_6_0 import *
from modules.view.data import *
import re
import json
from Bio.PDB import *
from Bio import PDB
import itertools
import mdtraj as md 
import numpy as np
import copy
import csv


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
   

    
def create_fplot(self,dyn_id,newpath,pdbpath=None,trajpath=None,traj_id=None,stride=1):# Not sure what will happen in pdbs with more than 1 gpcr . Use traj 14 or 15 for dyn 1
    """Generates the json files necessary to visualize flare plots."""
    gpcr_mode=True
    if (trajpath==None and traj_id):
        trajpath=DyndbFiles.objects.get(id=traj_id)
    if (pdbpath==None):
        pdbpath=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__extension="pdb")[0].filepath
       
    chain_name_li=obtain_all_chains(pdbpath)
    if (len(chain_name_li)==0):
        error="Protein chains not found."
        self.stdout.write(self.style.NOTICE(error))
        return

    prot_li_gpcr, dprot_li_all,dprot_li_all_info,pdbid=obtain_DyndbProtein_id_list(dyn_id)
    dprot_chains={}
    chains_taken=set()
    prot_seq_pos={}
    seq_pos_n=1
    for prot_id, prot_name, prot_is_gpcr, prot_seq in dprot_li_all_info: #To classify chains by protein (dprot_chains is a dict:for each protein, has a list of each chain with its matchpdbfa results + the protein seq_pos)
        seq_pos=[]
        dprot_chains[prot_id]=[[],[]]  
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
                        dprot_chains[prot_id][0].append((chain_name,result))
                        (seq_pos,seq_pos_n)=obtain_seq_pos_info(result,seq_pos,seq_pos_n,chain_name,True)
                        dprot_chains[prot_id][1]=seq_pos
        prot_seq_pos[prot_id]=(prot_name,seq_pos)
    keys_to_rm=set()
    for key, val in dprot_chains.items():
        if val==([],[]):
            keys_to_rm.add(key)
    for key in keys_to_rm:
        del dprot_chains[key]

    if chains_taken: # To check if some result have been obtained               
        for gpcr_DprotGprot in prot_li_gpcr:
            gpcr_Dprot=gpcr_DprotGprot[0]
            gpcr_Gprot=gpcr_DprotGprot[1]
            dprot_id=gpcr_Dprot.id
            dprot_name=gpcr_Dprot.name
            gen_num_res=obtain_gen_numbering(dyn_id, gpcr_Dprot,gpcr_Gprot) 
            if len(gen_num_res) > 2:
                (numbers, num_scheme, db_seq, current_class) = gen_num_res
                current_class=findGPCRclass(num_scheme)
                gpcr_n_ex=""
                for pos_gnum in numbers[current_class].values():
                    if pos_gnum[1]: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                        gpcr_n_ex=pos_gnum[1]
                        break
                if not "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                    error="Error obtaining GPCR generic numbering."
                    self.stdout.write(self.style.NOTICE(error))
                    return

                (dprot_chain_li, dprot_seq) = dprot_chains[dprot_id] 
                for chain_name, result in dprot_chain_li:
                    (resi_to_group,resi_to_name,cluster_dict)=obtain_fplot_input(result,numbers,chain_name,current_class)
                model_res=DyndbModeledResidues.objects.filter(id_model__dyndbdynamics__id=dyn_id)
                seg_to_chain={mr.segid : mr.chain for mr in model_res}
                if gpcr_mode:
                    for (pos, gnum) in resi_to_name.items():
                        if gnum != "None":
                            chain=gnum.split("x",1)[0]
                            resi_to_name[pos]=chain+"."+gnum
                    create_json(self,True,trajpath,pdbpath,resi_to_group,resi_to_name,newpath,stride,seg_to_chain)
                else:
                    create_json(self,False,trajpath,pdbpath,resi_to_group,resi_to_name,newpath,stride,seg_to_chain)
                out_file  = re.search("(\w*)(\.\w*)$" , newpath).group()
                self.stdout.write(self.style.SUCCESS('JSON file '+out_file+' successfully created'))
            else:
                error="Error obtaining GPCR generic numbering."
                self.stdout.write(self.style.NOTICE(error))
                return
    else:
        error="Error assigning the GPCR generic numbering to the PDB"
        self.stdout.write(self.style.NOTICE(error))
        return


