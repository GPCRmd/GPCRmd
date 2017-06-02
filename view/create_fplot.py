from dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents,DyndbDynamics, DyndbModel, DyndbProtein,DyndbProteinSequence
from view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from view.traj2flare_modified import * #[!]
from view.views import findGPCRclass, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_seq_pos_info
from dynadb.pipe4_6_0 import *
from view.data import *
import re
import json
from Bio.PDB import *
from Bio import PDB
import itertools
import mdtraj as md 
import numpy as np
import copy
import csv


def obtain_fplot_input(result,numbers,chain_name,current_class,chain_name_li):
    resi_to_group = {}
    resi_to_name = {}
    cluster_dict={}
    chain_index=str(chain_name_li.index(chain_name))
    pos_gnum = numbers[current_class]
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            db_pos=pos[1][1]
            pdb_pos=pos[0][1]
            #gnum_or_nth=""
            this_gnum = pos_gnum[db_pos][1]
            this_segm = pos_gnum[db_pos][2]
            resi_to_group[(pdb_pos,chain_index)]=str(this_segm)
            if this_gnum:#If exist GPCR num for this position
                this_gnum=this_gnum[:this_gnum.find(".")]+this_gnum[this_gnum.find("x"):]
                cluster_dict[this_gnum]=[chain_name+"."+pdb_pos,""]
            resi_to_name[(pdb_pos,chain_index)]=str(this_gnum)
    return(resi_to_group,resi_to_name,cluster_dict)            
   

    
def create_fplot(dyn_id,traj_id):# Not sure what will happen in pdbs with more than 1 gpcr . Use traj 14 or 15 for dyn 1
    gpcr_mode=True
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    if len(dynfiles) ==0:
        error="Structure file not found."
        #return render(request, 'view/index_error.html', {"error":error} )
        print("\n", error, "\n")
    else:
        trajs_dict={}
        structure_file=""
        p=re.compile("(/protwis/sites/files/)(.*)")
        p2=re.compile("[\.\w]*$")
        for e in dynfiles:
            f_id=e.id_files.id
            f_path=e.id_files.filepath
            #trajs_dict[f_id]=f_path
            myfile=p.search(f_path).group(2)
            myfile_name=p2.search(f_path).group()
            if myfile_name.endswith(".pdb"):
                structure_file=myfile
            elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
                trajs_dict[f_id]=(myfile, myfile_name)
        if traj_id in trajs_dict:
            traj_file=trajs_dict[traj_id][0]
            traj_name=trajs_dict[traj_id][1]
            p3=re.compile("(\w*)(\.\w*)$")
            traj_name_ok=p3.search(traj_name).group(1)
            trj_file="/protwis/sites/files/"+traj_file # For the moment I only use the 1st traj or it would be reaaally slow
            top_file="/protwis/sites/files/"+structure_file            
            chain_name_li=obtain_prot_chains(top_file)
            if (len(chain_name_li)==0):
                error="Protein chains not found."
                #return render(request, 'view/index_error.html', {"error":error} )
                print("\n", error, "\n")
      
            (prot_li_gpcr, dprot_li_all,dprot_li_all_info)=obtain_DyndbProtein_id_list(dyn_id)
            dprot_chains={}
            chains_taken=set()
            prot_seq_pos={}
            seq_pos_n=1
            for prot_id, prot_name, prot_is_gpcr, prot_seq in dprot_li_all_info: #To classify chains by protein (dprot_chains is a dict:for each protein, has a list of each chain with its matchpdbfa results + the protein seq_pos)
                seq_pos=[]
                dprot_chains[prot_id]=[[],[]]  
                for chain_name in chain_name_li:
                    checkpdb_res=checkpdb_ngl(top_file, segid="",start=-1,stop=9999999999999999999, chain=chain_name)
                    if isinstance(checkpdb_res, tuple):
                        tablepdb,pdb_sequence,hexflag=checkpdb_res 
                        result=matchpdbfa_ngl(prot_seq,pdb_sequence, tablepdb, hexflag)
                        type(result)
                        if isinstance(result, list):
                            #chain_results[chain_name]=result
                            if chain_name not in chains_taken:
                                chains_taken.add(chain_name)
                                dprot_chains[prot_id][0].append((chain_name,result))
                                seq_pos,seq_pos_n=(seq_pos,seq_pos_n)=obtain_seq_pos_info(result,seq_pos,seq_pos_n,chain_name,True)
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
                            #return render(request, 'view/index_error.html', {"error":error} ) 
                            print("\n", error, "\n")
                        (dprot_chain_li, dprot_seq) = dprot_chains[dprot_id] 
                        for chain_name, result in dprot_chain_li:
                            (resi_to_group,resi_to_name,cluster_dict)=obtain_fplot_input(result,numbers,chain_name,current_class,chain_name_li)
                        ###
                        trj_file="/protwis/sites/files/Dynamics/14_trj_1_strid10.dcd"
                        traj_name_ok="14_trj_1_strid10"
                        ###
                        if gpcr_mode:
                            for (pos, gnum) in resi_to_name.items():
                                if gnum != "None":
                                    chain=gnum.split("x",1)[0]
                                    resi_to_name[pos]=chain+"."+gnum
                            create_json_GPCR(trj_file,traj_name_ok,top_file,resi_to_group,resi_to_name)
                        else:
                            create_json(trj_file,traj_name_ok,top_file,resi_to_group,resi_to_name)
                        #gpcr_fplot_info[dprot_id]=(resi_to_group,resi_to_name)
                        #json_name=traj_name_ok+"_HT2b.json"
                        #context={"json_name":json_name}
                        #return render(request, 'view/flare_plot_test.html', context)
                        print("\nJSON file created\n")
                    else:
                        error="Error obtaining GPCR generic numbering."
                        #return render(request, 'view/index_error.html', {"error":error} )
                        print("\n", error, "\n")
            else:
                error="Unexpected error."
                #return render(request, 'view/index_error.html', {"error":error} )
                print("\n", error, "\n")
        else:
            error="Trajectory not found."
            #return render(request, 'view/index_error.html', {"error":error} )    
            print("\n", error, "\n")

