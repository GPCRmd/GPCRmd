from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.conf import settings
from dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents,DyndbDynamics, DyndbModel, DyndbProtein,DyndbProteinSequence,DyndbReferences
from protein.models import Protein
from view.assign_generic_numbers_from_DB import obtain_gen_numbering 
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
import pickle
import math
from os import path
from dynadb.views import  get_precomputed_file_path, get_file_name , get_file_name_dict, get_file_paths
from django.shortcuts import redirect
import os


def find_range_from_cons_pos(my_pos, gpcr_pdb):
    """Given a position in GPCR generic numbering, returns the residue number."""
    (ext_range,chain)=gpcr_pdb[my_pos]
    pos_range=str(ext_range)
    #pos_range=ext_range+"-"+ext_range
    return pos_range
                              
def create_conserved_pos_list(gpcr_pdb,gpcr_aa, i,my_pos, cons_pos_li, multiple_chains,chain_name):
    """Given the GPCR num of a position of our seq, checks if it's one of the GPCR conserved residues, and if it has been mutated"""
    my_pos_bw=my_pos.split("x")[0]
    add_chain_name=""
    if multiple_chains:
        add_chain_name=":"+chain_name
    while i < len(cons_pos_li):
        cons_pos = cons_pos_li[i][0]
        cons_pos_bw=cons_pos[1:]
        cons_aa=cons_pos[0]
        if my_pos_bw==cons_pos_bw:
            pos_range=find_range_from_cons_pos(my_pos, gpcr_pdb)
            if pos_range:
                cons_pos_li[i][2]=pos_range + add_chain_name
                (my_aa,chain)=gpcr_aa[my_pos]
                if my_aa != cons_aa:
                    cons_pos_li[i][0]=cons_pos+my_aa
        i+=1
                                    
def create_conserved_pos_list_otherclass(gpcr_pdb,gpcr_aa, i,my_pos, cons_pos_li, multiple_chains,chain_name,gnum_classes_rel,dict_class,current_class):
    """Given the GPCR num of a position of our seq, checks if it's one of the conserved residues, and if it has been mutated"""
    my_pos_bw=my_pos.split("x")[0]
    add_chain_name=""
    if multiple_chains:
        add_chain_name=":"+chain_name
    while i < len(cons_pos_li):
        cons_pos_bw_ourclass = cons_pos_li[i][1]
        if my_pos_bw==cons_pos_bw_ourclass:
            pos_range=find_range_from_cons_pos(my_pos, gpcr_pdb)
            if pos_range:
                cons_pos_li[i][2]=pos_range + add_chain_name
                cons_pos_li[i][1]="Correspods to "+cons_pos_bw_ourclass +  current_class.lower()
        i+=1

def create_conserved_motif_list(gpcr_pdb,gpcr_aa,j,my_pos,motifs,multiple_chains,chain_name):
    """Given the GPCR num of a position of our seq, checks if it's one of the residues of a conserved motif, and if it has been mutated"""
    my_pos_bw=my_pos.split("x")[0]
    (my_aa,chain)=gpcr_aa[my_pos]
    add_chain_name=""
    if multiple_chains:
        add_chain_name=":"+chain_name    
    while j < len(motifs):
        cons_pos = motifs[j][1]
        cons_pos_bw=cons_pos[1:]
        cons_aa=cons_pos[0]
        if my_pos_bw==cons_pos_bw:
            pos_range=find_range_from_cons_pos(my_pos, gpcr_pdb)
            if pos_range:
                motifs[j][2]=True
                motifs[j][3]=pos_range + add_chain_name
                if cons_aa != "x" and my_aa != cons_aa:
                    motifs[j][1]+=my_aa
        j+=1

def create_conserved_motif_list_otherclass(gpcr_pdb,gpcr_aa,j,my_pos,motifs,multiple_chains,chain_name):
    """Given the GPCR num of a position of our seq, checks if it's one of the residues of a conserved motif, and if it has been mutated"""
    my_pos_bw=my_pos.split("x")[0]
    (my_aa,chain)=gpcr_aa[my_pos]
    add_chain_name=""
    if multiple_chains:
        add_chain_name=":"+chain_name    
    while j < len(motifs):
        cons_pos_bw = motifs[j][4]
        if my_pos_bw==cons_pos_bw:
            pos_range=find_range_from_cons_pos(my_pos, gpcr_pdb)
            if pos_range:
                motifs[j][2]=True
                motifs[j][3]=pos_range + add_chain_name
        j+=1


def find_missing_pos(cons_pos_li, alt_class=False):
    """Given a list of conserved positions, where the positions found at our sequence are indicated, modifies the list to indicate the positions not found."""
    i=0
    while i < len(cons_pos_li):
        if cons_pos_li[i][2]=="":
            cons_pos_li[i][2]="None"
        # if alt_class:
        #     cons_pos_li[i][0] += alt_class.lower() 
        i+=1


def find_missing_pos_in_motif(motifs, motname_li):
    """Given a list of positions in conserved motifs, where the positions found at our sequence are indicated, creates a list of motifs where the positions found at our sequence are indicated, showing if they have the conserves AA or another one."""
    motifs_def=[]
    n=0
    for motname in motname_li:
        found=[]
        found_ranges=[]
        not_found=[]
        for e in motifs:
           if e[0]==motname:
               if not e[2]:
                   not_found.append(e[1])
               else:
                   found.append(e[1])
                   found_ranges.append(e[3])
                   
        num_nf=len(not_found)
        ranges_all=",".join(found_ranges)
        if num_nf ==0:
            motifs_def.append([motname," , ".join(found),(ranges_all)])
        elif num_nf ==3:
            motifs_def.append([motname,"Motif not found","None"])
        else:
            motifs_def.append([motname,(" , ".join(not_found)+" not found"),(ranges_all)])
        n+=1
    return motifs_def

def find_missing_pos_in_motif_otherclass(motifs, motname_li,dict_class,current_class):
    """Given a list of positions in conserved motifs, where the positions found at our sequence are indicated, creates a list of motifs where the positions found at our sequence are indicated, showing if they have the conserves AA or another one."""
    motifs_def=[]
    n=0
    for motname in motname_li:
        found=[]
        found_ranges=[]
        not_found=[]
        for e in motifs:
            if e[0]==motname:
                if not e[2]:
                    not_found.append(e[1])
                else:
                    motpos= e[1] + current_class.lower() + " = " + e[4] +dict_class.lower()
                    found.append(motpos)
                    found_ranges.append(e[3])
                   
        num_nf=len(not_found)
        ranges_all=",".join(found_ranges)
        if num_nf ==0:
            motifs_def.append([motname," ; ".join(found),(ranges_all)])
        elif num_nf ==3:
            motifs_def.append([motname,"Motif not found","None"])
        else:
            motifs_def.append([motname,(" ; ".join(found) + " (" + " , ".join(not_found) + " not found)"),(ranges_all)])
        n+=1
    return motifs_def


def obtain_dyn_files(paths_dict):
    """Given a list of files related to a dynamic, separates them in structure files and trajectory files."""
    structure_file=""
    structure_name=""
    traj_list=[]
    p=re.compile("(/protwis/sites/files/)(.*)")
    p2=re.compile("[\.\w]*$")
    for f_id , path in paths_dict.items():
        myfile=p.search(path).group(2)
        myfile_name=p2.search(path).group()
        if myfile_name.endswith(".pdb"): #, ".ent", ".mmcif", ".cif", ".mcif", ".gro", ".sdf", ".mol2"))
            structure_file=myfile
            structure_file_id=f_id
            structure_name=myfile_name
        elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append([myfile, myfile_name, f_id])
    return (structure_file,structure_file_id,structure_name, traj_list)

def obtain_prot_chains(pdb_name):
    chain_name_s=set()
    fpdb=open(pdb_name,'r')
    for line in fpdb:
        if useline2(line):
            chain_name_s.add(line[21])
    return list(chain_name_s)


def obtain_all_chains(pdb_name):
    chain_name_l=[]
    fpdb=open(pdb_name,'r')
    first=True
    for line in fpdb:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            chain_name=line[21]
            if first:
                first=False
                chain_name_pre=chain_name
                chain_name_l.append(line[21])
            elif (chain_name != chain_name_pre):
                chain_name_pre=chain_name
                chain_name_l.append(line[21])
    return list(chain_name_l)

def obtain_seq_pos_info(result,seq_pos,seq_pos_n,chain_name,multiple_chains):
    """Creates a list of all the important info of prot sequence positions"""
    chain_nm_seq_pos=""
    if multiple_chains:
        chain_nm_seq_pos=chain_name
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            seq_pos.append([pos[0][0],pos[0][1],"",chain_nm_seq_pos,seq_pos_n]);
            seq_pos_n+=1
    return (seq_pos,seq_pos_n)

def obtain_rel_dicts(result,numbers,chain_name,current_class,seq_pos,seq_pos_n,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains):
    """Creates a series of dictionaries that will be useful for relating the pdb position with the gpcr number (pos_gnum) or AA (pos_gnum); and the gpcr number for the different classes (in case the user wants to compare)"""
    chain_nm_seq_pos=""
    rs_by_seg={1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: []}
    if multiple_chains:
        chain_nm_seq_pos=":"+chain_name
    pos_gnum = numbers[current_class]
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            db_pos=pos[1][1]
            gnum_or_nth=""
            this_gnum = pos_gnum[db_pos][1]
            if this_gnum: #If exist GPCR num for this position
                gpcr_pdb[this_gnum]=[pos[0][1],chain_name]
                gpcr_aa[this_gnum]=[pos_gnum[db_pos][0], chain_name]
                gnum_or_nth=this_gnum
                rs_by_seg[pos_gnum[db_pos][2]].append(pos[0][1]+chain_nm_seq_pos) #Chain!!
            seq_pos[seq_pos_n][2]=gnum_or_nth
            seq_pos_n+=1
    #######
    seg_li=[]
    for seg in range(2,17):
        slen=len(rs_by_seg[seg])
        if slen==0:
            seg_li.append([])
        elif slen==1:
            seg_li.append([rs_by_seg[seg][0]])
        else:
            seg_li.append([rs_by_seg[seg][0],rs_by_seg[seg][-1]])
    #######
    other_classes=list({"A","B","C","F"} - set(current_class))
    other_classes_ok=[]
    for name in other_classes:
        if numbers[name]:
            other_classes_ok.append(name)
            gnum_classes_rel[name]={}
    for pos, (res,gnum,segm) in pos_gnum.items():
        if gnum:
            for class_name in other_classes_ok:
                gnum_altclass=numbers[class_name][pos][1]
                if gnum_altclass:
                    gnum_classes_rel[class_name][gnum_altclass.split("x")[0]]=gnum.split("x")[0]
    return(gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,seq_pos,seq_pos_n,seg_li)

def traduce_all_poslists_to_ourclass_numb(motifs_dict,gnum_classes_rel,cons_pos_dict,current_class,other_classes_ok):
    """Takes all the lists of conserved residues and traduces to the GPCR numbering of the class of the protein to visualize the conserved positions of the rest of classes."""
    current_poslists=cons_pos_dict[current_class]
    current_motif = motifs_dict[current_class]
    show_class={"A":True,"B":True,"C":True,"F":True}
    for gpcr_class in other_classes_ok:
        for cons_pos_li in cons_pos_dict[gpcr_class]:
            for el in cons_pos_li:
                pos_nm=el[0]
                s=re.search("([A-Z]?)([\d\.]+)",pos_nm)
                AA=s.group(1)
                bw_pos_ok=s.group(2)
                try:
                    current_bw_pos=gnum_classes_rel[gpcr_class][bw_pos_ok]
                except Exception:
                    current_bw_pos="Position not found"
                    el[2]="None"
                el[0]=AA + bw_pos_ok + gpcr_class.lower()
                el[1]=current_bw_pos
        motif_info = motifs_dict[gpcr_class]
        if motif_info:
            for el in motif_info[0]:
                bw_pos=el[1][1:]
                current_bw_pos=gnum_classes_rel[gpcr_class][bw_pos]
                el[4]=current_bw_pos
    none_classes=list({"A","B","C","F"} - set(other_classes_ok + list(current_class)))
    for n_class in none_classes:
        show_class[n_class]=False
        i=0
        while i < len(cons_pos_dict[n_class]):
            cons_pos_dict[n_class][i]=None
            i+=1
        motifs_dict[n_class]=[]
    return (show_class,current_poslists,current_motif,other_classes_ok)


def obtain_predef_positions_lists(current_poslists,current_motif,other_classes_ok,current_class,cons_pos_dict,motifs,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,chain_name):
    """Takes the predefined lists of positions/motifs that will appear as predefined views and modifies them so that they match the sequence of our protein."""
    # Obtain list for the predefined views of important positions
    chain_pos = [pos for pos in gpcr_aa if gpcr_aa[pos][1]==chain_name]
    for my_pos in chain_pos:
        for cons_pos_li in current_poslists:
            create_conserved_pos_list(gpcr_pdb, gpcr_aa,0,my_pos,cons_pos_li,multiple_chains,chain_name)
        if current_motif:
            create_conserved_motif_list(gpcr_pdb,gpcr_aa,0,my_pos,current_motif[0],multiple_chains,chain_name)
        for gpcr_class in other_classes_ok:
            for cons_pos_li in cons_pos_dict[gpcr_class]:                     
                create_conserved_pos_list_otherclass(gpcr_pdb,gpcr_aa, 0,my_pos, cons_pos_li, multiple_chains,chain_name,gnum_classes_rel,gpcr_class,current_class)
            alt_class_motif=motifs_dict[gpcr_class]
            if alt_class_motif:
                create_conserved_motif_list_otherclass(gpcr_pdb,gpcr_aa,0,my_pos,alt_class_motif[0],multiple_chains,chain_name)


def find_missing_positions(motifs_dict_def,current_motif,current_poslists,other_classes_ok,current_class,cons_pos_dict,motifs):
    """Completes the conserved position lists to indicate the positions that are missing in our prot"""
    for cons_pos_li in current_poslists:
        find_missing_pos(cons_pos_li)
    if current_motif:
        motifs_def=find_missing_pos_in_motif(current_motif[0], current_motif[1])
        motifs_dict_def[current_class] = motifs_def
    for dict_class in other_classes_ok:
        for cons_pos_li in cons_pos_dict[dict_class]:
            find_missing_pos(cons_pos_li,dict_class)
        alt_class_motif=motifs_dict[dict_class]
        if alt_class_motif:
            motifs_def=find_missing_pos_in_motif_otherclass(motifs, motname_li,dict_class,current_class)
            motifs_dict_def[dict_class] = motifs_def

def obtain_compounds(dyn_id):
    """Creates a list of the ligands, ions, lipids, water molecules, etc found at the dynamic"""
    comp=DyndbModelComponents.objects.filter(id_model__dyndbdynamics=dyn_id)
    comp_dict={}
    lig_li=[]
    lig_li_s=[]
    for c in comp:
        if c.type == 2:
            dc = c.resname
        else:
            dc=DyndbCompound.objects.get(dyndbmolecule__dyndbmodelcomponents=c.id).name #Ligands, water (and ions)
        comp_dict[dc] = c.resname
        if c.type ==1:
            lig_li.append([dc,c.resname])
            lig_li_s.append(c.resname)
    ddc=DyndbDynamicsComponents.objects.filter(id_dynamics=dyn_id) # Lipids and ions
    for c in ddc:
        if c.type == 2:
            dc = c.resname
        else:
            dc=DyndbCompound.objects.get(dyndbmolecule__dyndbdynamicscomponents=c.id).name
        resn=c.resname
        if dc not in comp_dict:
            comp_dict[dc]=resn
        else:
            if resn not in comp_dict.values():
                new_resn= comp_dict[dc] + " OR " + resn
                comp_dict[dc]= new_resn 
    comp_li=list(map(list, comp_dict.items()))
    comp_li=sorted(comp_li, key=lambda x: x[0])
    return(comp_li,lig_li,lig_li_s)

def findGPCRclass(num_scheme):
    """Uses the numbering scheme name to determine the GPCR family (A, B, C or F). Also sets the values of a dict that will determine the class shown at the template."""
    if num_scheme == "gpcrdba" or num_scheme == "gpcrdb":
        current_class ="A"
        active_class["A"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbb":
        current_class ="B"
        active_class["B"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbc":
        current_class ="C"
        active_class["C"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbf":
        current_class ="F"
        active_class["F"]=["active gpcrbold","in active"]
    return current_class

def generate_motifs_all_info(all_gpcrs_info):
    """Generates a dictionary which, for each GPCR class, shows the conserved motifs info of all the GPCRs opened with the viewer."""
    for prot_info in all_gpcrs_info:
        prot_motifs = prot_info[5]
        for gpcr_class, motifs_li in prot_motifs.items():
            if motifs_li:
                motif_num = 0
                while motif_num < len(motifs_li):
                    motif_info = motifs_li[motif_num]
                    if motif_info[2] != "None":
                        motifs_all_info[gpcr_class][motif_num][2]+=(motif_info[2]+",")
                    motif_num+=1
    for gpcr_class, motifs_li in motifs_all_info.items():
        for motif_info in motifs_li:
            if motif_info[2]:
                motif_info[2]=motif_info[2].rstrip(",")
            else:
                motif_info[1]="Motif not found."
                motif_info[2]="None"
            
    return (motifs_all_info)
    
def generate_cons_pos_all_info(cons_pos_all,all_gpcrs_info):
    """Generates a dictionary which, for each GPCR class, shows the conserved position info of all the GPCRs opened with the viewer. Also generates active_class and show_class which are needed for the template"""
    for prot_info in all_gpcrs_info:
        cons_pos_prot = prot_info[4]
        for gpcr_class, cons_class_lists in cons_pos_prot.items():
           if cons_class_lists:
               list_num=0 # list 0 or 1
               while list_num < len(cons_class_lists):
                   cons_pos_li=cons_class_lists[list_num]
                   cons_pos_num = 0
                   while cons_pos_num < len(cons_pos_li):
                       cons_pos_info=cons_pos_li[cons_pos_num]
                       if cons_pos_info[2] != "None":
                           cons_pos_all[gpcr_class][list_num][cons_pos_num][2]+=(cons_pos_info[2]+",")
                       cons_pos_num +=1
                   list_num+=1
    show_class={}
    for gpcr_class, cons_pos_class in cons_pos_all.items():
        for cons_pos_li in cons_pos_class:
            for cons_pos in cons_pos_li:
                if cons_pos[2]:
                    cons_pos[2]=cons_pos[2].rstrip(",")
                else:
                    cons_pos[1]="Position not found."
                    cons_pos[2]="None"
        show_class[gpcr_class]=True
    active_class_all=  {'A': ['', ''], 'C': ['', ''], 'F': ['', ''], 'B': ['', '']}
    classes=sorted(cons_pos_all)
    active_class_all[classes[0]]=['active', 'in active']
    return (cons_pos_all,show_class,active_class_all)

def relate_atomSerial_mdtrajIndex(pdb_path):
    serial_mdInd={}
    line_num=0
    readpdb=open(pdb_path,'r')
    for line in readpdb:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            serial=line[6:11].strip()
            serial_mdInd[serial]=line_num
            line_num+=1
    return(serial_mdInd)


def distances_notraj(dist_struc,dist_ids):
    struc_path = "/protwis/sites/files/"+dist_struc
    try:
        strc=md.load(struc_path)
    except Exception:
        return (False,None, "Error loading the file.")    
    dist_li=re.findall("\d+-\d+",dist_ids)
    #serial_mdInd=relate_atomSerial_mdtrajIndex(struc_path)
    dist_result={}
    for dist_pair in dist_li:
        pos_from,pos_to=dist_pair.split("-") 
        #from_to=np.array([[serial_mdInd[pos_from],serial_mdInd[pos_to]]]) 
        from_to=np.array([[pos_from,pos_to]]) 
        try:
            dist=float(md.compute_distances(strc, from_to)*10)
        except Exception:
            num_atoms=strc.n_atoms
            error_msg="Atom indices must be between 0 and "+str(num_atoms)
            return (False, None, error_msg)
        dist_result[dist_pair]=dist
    return(True, dist_result, None)


def obtain_DyndbProtein_id_list(dyn_id):
    """Given a dynamic id, gets a list of the dyndb_proteins and proteins associated to it that are GPCRs + a list of all proteins (GPCRs or not)"""
    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
    prot_li_gpcr=[]
    dprot_li_all=[]
    dprot_li_all_info=[]
    if model.id_protein:
        is_gpcr = False
        gprot= model.id_protein.receptor_id_protein
        if gprot:
            prot_li_gpcr=[(model.id_protein, gprot)]
            is_gpcr=True
        dprot_li_all=[model.id_protein]
        dprot_seq=DyndbProteinSequence.objects.get(id_protein=model.id_protein.id).sequence
        dprot_li_all_info=[(model.id_protein.id, model.id_protein.name, is_gpcr , dprot_seq )]     
    else:
        dprot_li_all=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
        for dprot in dprot_li_all:
            is_gpcr = False
            gprot= dprot.receptor_id_protein
            if gprot:
                is_gpcr = True
                prot_li_gpcr.append((dprot,gprot))
            dprot_seq=DyndbProteinSequence.objects.get(id_protein=dprot.id).sequence
            dprot_li_all_info.append((dprot.id, dprot.name, is_gpcr, dprot_seq))
    return (prot_li_gpcr, dprot_li_all, dprot_li_all_info)

def obtain_protein_names(dyn_id):
    """Given a dynamic id, gets a list of the GPCR names"""
    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
    prot_li_names=[]
    if model.id_protein:
        gprot= model.id_protein.receptor_id_protein
        if gprot:#it means it is a GPCR
            prot_li_names.append(model.id_protein.name)
    else:
        dprot_li_all=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
        for dprot in dprot_li_all:
            gprot= dprot.receptor_id_protein
            if gprot:#it means it is a GPCR
                prot_li_names.append(dprot.name)
    return ",".join(prot_li_names)


def res_to_atom(chain_names,struc,res, chain, atm):
    chain = chain.upper()
    if chain in chain_names:
        chain_ind=chain_names.index(chain)
        atm_index_arr = struc.topology.select("residue "+str(res)+" and chainid "+str(chain_ind)+" and name "+atm)
        if atm_index_arr:
            return (str(atm_index_arr[0]))
        else:
            return False
    else:
        return False


def distances_Wtraj(dist_str,struc_path,traj_path,strideVal):
    struc_path = "/protwis/sites/files/"+struc_path
    traj_path = "/protwis/sites/files/"+traj_path
    dist_li=dist_str.split(",")
    #serial_mdInd=relate_atomSerial_mdtrajIndex(struc_path) 
    frames=[]
    axis_lab=[["Frame"]]
    atom_pairs=np.array([]).reshape(0,2)
    small_error=[]
    # If some dist needs re -> atom traduction:
    chain_names=obtain_all_chains(struc_path)
    if (":" in dist_str):
        struc=md.load(struc_path)
    dist_pair_new=[]
    if len(dist_li) > 20:
        dist_li =dist_li[:20]
        small_error.append("Too much distances to compute. Some have been omitted.")
    for dist_pair in dist_li:
        if ":" in dist_pair:
            (inf_from,inf_to)=dist_pair.split("-")
            (resF, chainF, atmF)= inf_from.split(":")
            (resT, chainT, atmT)= inf_to.split(":")
            pos_from=res_to_atom(chain_names,struc,resF, chainF, atmF)
            pos_to=res_to_atom(chain_names,struc,resT, chainT, atmT)
            var_lab="dist "+resF +":"+ chainF+"("+atmF+")-"+resT +":"+ chainT+"("+atmT+")"
            skip=False
            if not pos_from:
                small_error.append("Selection "+resF+":"+chainF+" "+atmF+" not found")
                skip=True
            if not pos_to:
                small_error.append("Selection "+resT+":"+chainT+" "+atmT+" not found")
                skip=True
            if skip:
                continue
            
        else:
            pos_from,pos_to=re.findall("\d+",dist_pair)
            var_lab="dist "+pos_from+"-"+pos_to
        dist_pair_new.append(dist_pair)
        axis_lab[0].append(var_lab) 
        #from_to=np.array([[serial_mdInd[pos_from],serial_mdInd[pos_to]]])
        from_to=np.array([[pos_from,pos_to]])        
        atom_pairs=np.append(atom_pairs,from_to, axis=0)
    if (len(atom_pairs) ==0):
        return (True,[], small_error, True, ",".join(dist_pair_new))
        
    try:
        itertraj=md.iterload(filename=traj_path,chunk=(50/strideVal), top=struc_path , stride = strideVal)
    except Exception:
        return (False,None, "Error loading the file.",True,"")
    dist=np.array([]).reshape((0,len(atom_pairs))) 
    for itraj in itertraj:
        try:
            d=md.compute_distances(itraj, atom_pairs)*10
        except Exception:
            num_atoms=itraj.n_atoms
            error_msg="Atom indices must be between 0 and "+str(num_atoms)
            return (False, None, error_msg,True,"")
        dist=np.append(dist,d,axis=0)
    frames=np.arange(0,len(dist)*strideVal, strideVal,dtype=np.int32).reshape((len(dist),1))
    data=np.append(frames,dist, axis=1).tolist()
    data_fin=axis_lab + data
    if not small_error:
        small_error=None
    return (True,data_fin, small_error,False,",".join(dist_pair_new))

def obtain_domain_url(request):
    current_host = request.get_host()
    domain=current_host.rsplit(':',1)[0]
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
        
    if hasattr(settings, 'MDSRV_PORT'):
        port = settings.MDSRV_PORT
    else:
        port = 80
        
    if hasattr(settings, 'MDSRV_URL'):
        mdsrv_url = settings.MDSRV_URL.strip()
        if mdsrv_url.find('/') == len(mdsrv_url) - 1:
           mdsrv_url = mdsrv_url[:-1]
    else:
        mdsrv_url = protocol+'://'+domain+':'+str(port)
    return(mdsrv_url)

def get_fplot_path(dyn_id,traj_list):
    fpdir = get_precomputed_file_path('flare_plot',"hbonds",url=False)
    fpdir_url=""
    fp_exist=False
    li_n=0
    for (trajfile, trajfile_name, f_id) in traj_list:
        fpfilename = get_file_name(objecttype="dynamics",fileid=f_id,objectid=dyn_id,ext="json",forceext=True,subtype="trajectory")##[!] Change if function is changed!!!        
        ###########[!] Change get_file_name() to obtain it automatically
        (pre,post)=fpfilename.split(".")
        fpfilename=pre+"_hbonds."+post
        ###########
        fppath = path.join(fpdir,fpfilename)
        exists=path.isfile(fppath)
        addname=""
        if exists:
            fp_exist=True
            addname=fpfilename
            #fplot_path.append([f_id,fpfilename,trajfile_name])
        traj_list[li_n].append(addname)
        li_n+=1
    if fp_exist:
        fpdir_url = get_precomputed_file_path('flare_plot',"hbonds",url=True)
    return (traj_list,fpdir_url)
        
    

@ensure_csrf_cookie
def index(request, dyn_id):
#    if request.session.get('dist_data', False):
#        dist_data=request.session['dist_data']
#        dist_dict=dist_data["dist_dict"]
#        print("\n\n",len(dist_dict))
    request.session.set_expiry(0) 
    mdsrv_url=obtain_domain_url(request)
    delta=DyndbDynamics.objects.get(id=dyn_id).delta
    if request.is_ajax() and request.POST:
        if request.POST.get("rmsdStr"):
            struc_p= request.POST.get("rmsdStr")
            traj_p= request.POST.get("rmsdTraj")
            traj_frame_rg= request.POST.get("rmsdFrames")
            ref_frame= request.POST.get("rmsdRefFr")
            ref_traj_p= request.POST.get("rmsdRefTraj")
            traj_sel= request.POST.get("rmsdSel")
            no_rv=request.POST.get("no_rv")
            strideVal=request.POST.get("stride")
                       
            if request.session.get('rmsd_data', False):
                rmsd_data=request.session['rmsd_data']
                rmsd_dict=rmsd_data["rmsd_dict"]
                new_rmsd_id=rmsd_data["new_rmsd_id"]
                no_rv_l=no_rv.split(",")
                to_rv=[];
                for r_id in rmsd_dict.keys():
                    if (r_id not in no_rv_l):
                        to_rv.append(r_id)
                for r_id in to_rv:
                    del rmsd_dict[r_id]   
            else:
                new_rmsd_id=1
                rmsd_dict={}
            
            if len(rmsd_dict) < 15:
                (success,data_fin, errors)=compute_rmsd(struc_p,traj_p,traj_frame_rg,ref_frame,ref_traj_p,traj_sel,int(strideVal))
                if success:
                    data_frame=data_fin
                    data_store=copy.deepcopy(data_frame)
                    data_store[0].insert(1,"Time")
                    data_time=[data_store[0][1:]]
                    for row in data_store[1:]:
                        frame=row[0]
                        time=frame*delta
                        row.insert(1,time)
                        d_time=row[1:]
                        data_time.append(d_time)  
                    p=re.compile("\w*\.\w*$")
                    struc_filename=p.search(struc_p).group(0)
                    traj_filename=p.search(traj_p).group(0)
                    rtraj_filename=p.search(ref_traj_p).group(0)
                    rmsd_dict["rmsd_"+str(new_rmsd_id)]=(data_store,struc_filename,traj_filename,traj_frame_rg,ref_frame,rtraj_filename,traj_sel,strideVal)
                    request.session['rmsd_data']={"rmsd_dict":rmsd_dict, "new_rmsd_id":new_rmsd_id+1}
                    data_rmsd = {"result_t":data_time,"result_f":data_frame,"rmsd_id":"rmsd_"+str(new_rmsd_id),"success": success, "msg":errors , "strided":strideVal}
                else: 
                    data_rmsd = {"result":data_fin,"rmsd_id":None,"success": success, "msg":errors , "strided":strideVal}
            else:
                data_rmsd = {"result":None,"rmsd_id":None,"success": False, "msg":"Please, remove some RMSD results to obtain new ones." , "strided":strideVal}
            return HttpResponse(json.dumps(data_rmsd), content_type='view/'+dyn_id)   
        elif request.POST.get("distStr"):
            dist_struc=request.POST.get("distStr")
            dist_ids=request.POST.get("dist_resids")
            (success,dist_result, msg)=distances_notraj(dist_struc,dist_ids)
            data = {"result":dist_result,"success": success, "msg":msg}
            return HttpResponse(json.dumps(data), content_type='view/'+dyn_id)
        elif request.POST.get("distStrWT"):
            dist_struc_p=request.POST.get("distStrWT")
            dist_ids=request.POST.get("dist_atmsWT")
            dist_traj_p=request.POST.get("distTraj")
            no_rv=request.POST.get("no_rv")
            strideVal=request.POST.get("stride")
            if request.session.get('dist_data', False):
                dist_data=request.session['dist_data']
                dist_dict=dist_data["dist_dict"]
                new_id=dist_data["new_id"]
                no_rv_l=no_rv.split(",")
                to_rv=[];
                for d_id in dist_dict.keys():
                    if (d_id not in no_rv_l):
                        to_rv.append(d_id)
                for d_id in to_rv:
                    del dist_dict[d_id]   
            else:
                new_id=1
                dist_dict={}
                
            if len(dist_dict) < 15:
                
                (success,data_fin, msg, isEmpty,dist_pair_new)=distances_Wtraj(dist_ids,dist_struc_p,dist_traj_p,int(strideVal))
                if success and not isEmpty:
                    data_frame=data_fin
                    data_store=copy.deepcopy(data_frame)
                    data_store[0].insert(1,"Time")
                    data_time=[data_store[0][1:]]
                    for row in data_store[1:]:
                        frame=row[0]
                        time=frame*delta
                        row.insert(1,time)
                        d_time=row[1:]
                        data_time.append(d_time)                 
                    p=re.compile("\w*\.\w*$")
                    struc_filename=p.search(dist_struc_p).group(0)
                    traj_filename=p.search(dist_traj_p).group(0)
                    dist_dict["dist_"+str(new_id)]=(data_store,struc_filename,traj_filename,strideVal)
                    request.session['dist_data']={"dist_dict":dist_dict, "new_id":new_id+1 ,
                         "traj_filename":traj_filename, "struc_filename":struc_filename}
                    data = {"result_t":data_time,"result_f":data_frame,"dist_id":"dist_"+str(new_id),"success": success, "msg":msg , "strided":strideVal , "isEmpty":isEmpty , "dist_pair_new":dist_pair_new}
                else: 
                    data = {"result":data_fin,"dist_id":None,"success": success, "msg":msg , "strided":strideVal, "isEmpty":isEmpty, "dist_pair_new":dist_pair_new}
            else:
                data = {"result":None,"dist_id":None,"success": False, "msg":"Please, remove some distance results to obtain new ones.", "strided":strideVal, "isEmpty":isEmpty, "dist_pair_new":dist_pair_new}
            return HttpResponse(json.dumps(data), content_type='view/'+dyn_id)       
        elif request.POST.get("all_ligs"):
            all_ligs=request.POST.get("all_ligs")
            thresh=request.POST.get("thresh")
            int_traj_p=request.POST.get("traj_p")
            int_struc_p=request.POST.get("struc_p")
            dist_scheme = request.POST.get("dist_scheme")
            no_rv=request.POST.get("no_rv")
            strideVal=request.POST.get("stride")
            res_li=all_ligs.split(',')
            if request.session.get('main_strc_data', False):
                session_data=request.session["main_strc_data"]
                #chain_names=session_data["chain_name_li"]
                chain_names=obtain_all_chains("/protwis/sites/files/"+int_struc_p)
                num_prots=session_data["prot_num"]
                serial_mdInd=session_data["serial_mdInd"]
                gpcr_chains=session_data["gpcr_chains"]
                
                
                if request.session.get('int_data', False):
                    int_data=request.session['int_data']
                    int_info=int_data["int_info"]
                    new_int_id=int_data["new_int_id"]
                    no_rv_l=no_rv.split(",")
                    to_rv=[];
                    for i_id in int_info.keys():
                        if (i_id not in no_rv_l):
                            to_rv.append(i_id)
                    for i_id in to_rv:
                        del int_info[i_id]   
                else:
                    new_int_id=1
                    int_info={}
                
                if len(int_info) < 15:
                    (success,int_dict,errors)=compute_interaction(res_li,int_struc_p,int_traj_p,num_prots,chain_names,float(thresh),serial_mdInd,gpcr_chains,dist_scheme, int(strideVal))
                    int_id = None
                    if success:
                        p=re.compile("\w*\.\w*$")
                        struc_fileint=p.search(int_traj_p).group(0)
                        traj_fileint=p.search(int_struc_p).group(0)
                        int_id="int_"+str(new_int_id)
                        int_info[int_id]=(int_dict,thresh,traj_fileint,struc_fileint,dist_scheme, strideVal)
                        request.session['int_data']={"int_info":int_info, "new_int_id":new_int_id+1 }
                    data = {"result":int_dict,"success": success, "e_msg":errors, "int_id":int_id ,"strided":strideVal}
                else:
                    data = {"result":None,"success": False, "e_msg":"Please, remove some interaction results to obtain new ones.","int_id":None ,"strided":strideVal}
            else:
                data = {"result":None,"success": False, "e_msg":"Session error.","int_id":None ,"strided":strideVal}
            return HttpResponse(json.dumps(data), content_type='view/'+dyn_id)
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    if len(dynfiles) ==0:
        error="Structure file not found."
        return render(request, 'view/index_error.html', {"error":error} )
    else:
        (comp_li,lig_li,lig_li_s)=obtain_compounds(dyn_id)
        paths_dict={}
        for e in dynfiles:
            paths_dict[e.id_files.id]=e.id_files.filepath
        (structure_file,structure_file_id,structure_name, traj_list)=obtain_dyn_files(paths_dict)
        #structure_file="Dynamics/with_prot_lig_multchains_gpcrs.pdb"########################### [!] REMOVE
        #structure_name="with_prot_lig_multchains_gpcrs.pdb" ################################### [!] REMOVE
        pdb_name = "/protwis/sites/files/"+structure_file
        chain_name_li=obtain_prot_chains(pdb_name)
        (traj_list,fpdir)=get_fplot_path(dyn_id,traj_list)

        if len(chain_name_li) > 0:
            multiple_chains=False
            chain_str=""
            if len(chain_name_li) > 1:
                multiple_chains=True
            (prot_li_gpcr, dprot_li_all,dprot_li_all_info)=obtain_DyndbProtein_id_list(dyn_id)            
            request.session['main_strc_data']={"chain_name_li":chain_name_li,"prot_num":len(dprot_li_all),"serial_mdInd":relate_atomSerial_mdtrajIndex(pdb_name),"gpcr_chains":False}
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
            other_prots=[]
            #receptor_sel="protein"
            if non_gpcr_chains:
                non_gpcr_chains_str=",".join(non_gpcr_chains)
                non_gpcrs_str="protein and (:"+non_gpcr_chains[0]
                for chain_n in non_gpcr_chains[1:]:
                    non_gpcrs_str+=" or :"+chain_n
                non_gpcrs_str+=")"
                if len(non_gpcr_chains)>1:
                    other_prots_title="Chains "+non_gpcr_chains_str
                else:
                    other_prots_title="Chain "+non_gpcr_chains[0]
                other_prots=[non_gpcrs_str,other_prots_title,non_gpcr_chains_str]
                #if gpcr_chains:
                #    receptor_sel+="and (:"+gpcr_chains[0]
                #    for chain_n in gpcr_chains[1:]:
                #        receptor_sel+=" or :"+chain_n
                #    receptor_sel+=")"
            if multiple_chains:
                if len(gpcr_chains) ==1:
                    chain_str="GPCR chain: "+gpcr_chains[0]
                elif len(gpcr_chains) > 1:
                    chain_str="GPCR chains: "+", ".join(gpcr_chains)
                
            if chains_taken: # To check if some result have been obtained
                request.session['main_strc_data']["gpcr_chains"]=gpcr_chains
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
                            cons_pos_dict_mod=copy.deepcopy(cons_pos_dict)
                            for chain_name, result in dprot_chain_li:
                                (gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,dprot_seq,seq_pos_index,seg_li)=obtain_rel_dicts(result,numbers,chain_name,current_class,dprot_seq,seq_pos_index, gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains)
                                (show_class,current_poslists,current_motif,other_classes_ok)=traduce_all_poslists_to_ourclass_numb(motifs_dict,gnum_classes_rel,cons_pos_dict_mod,current_class,other_classes_ok)
                                obtain_predef_positions_lists(current_poslists,current_motif,other_classes_ok,current_class,cons_pos_dict_mod, motifs,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,chain_name)                                
                            prot_seq_pos[dprot_id]=(dprot_name, dprot_seq)
                            motifs_dict_def={"A":[],"B":[],"C":[],"F":[]}
                            find_missing_positions(motifs_dict_def,current_motif,current_poslists,other_classes_ok,current_class,cons_pos_dict_mod,motifs)
                            #gpcr_pdb_js=json.dumps(gpcr_pdb)
                            all_gpcrs_info.append((dprot_id, dprot_name, show_class, active_class, copy.deepcopy(cons_pos_dict_mod) , motifs_dict_def))
                            gpcr_pdb_all[dprot_id]=(gpcr_pdb)
                            gpcr_id_name[dprot_id]=dprot_name
                            seg_li_all[dprot_id]=seg_li #[!] For the moment I don't use this, I consider only 1 GPCR
                            

                if all_gpcrs_info:
                    request.session['gpcr_pdb']= gpcr_pdb #[!] For the moment I consider only 1 GPCR
                    cons_pos_all_info=generate_cons_pos_all_info(copy.deepcopy(cons_pos_dict),all_gpcrs_info)
                    motifs_all_info=generate_motifs_all_info(all_gpcrs_info)
                    #traj_list.append(['Dynamics/dyn20/tmp_trj_0_20.dcd', 'tmp_trj_0_20.dcd', 10170, '10140_trj_4_hbonds_rep.json'])#[!] REMOVE! only for Flare Plot tests
                    #traj_list.append(['Dynamics/10140_trj_4.dcd', '10140_trj_4.dcd', 10140, '10140_trj_4_hbonds_OK.json']);
                    context={
                        "dyn_id":dyn_id,
                        "mdsrv_url":mdsrv_url,
                        "structure_file":structure_file, 
                        "structure_name":structure_name, 
                        "structure_file_id":structure_file_id,
                        "traj_list":traj_list,
                        "compounds" : comp_li,
                        "ligands": lig_li,
                        "ligands_short": ",".join(lig_li_s),
                        "all_gpcrs_info" : all_gpcrs_info,
                        "cons_pos_all_info" : cons_pos_all_info,
                        "motifs_all_info" :motifs_all_info,
                        "gpcr_id_name_js" : json.dumps(gpcr_id_name),
                        "gpcr_id_name" : gpcr_id_name,
                        "gpcr_pdb": json.dumps(gpcr_pdb_all),
                        "prot_seq_pos": list(prot_seq_pos.values()),
                        "other_prots":other_prots,#["protein and (:A or :B or :C)" , "Chains A, B, C" , "A, B,C"]
                        "chains" : chain_str, # string defining GPCR chains. If empty, GPCR chains = protein
                        "all_chains": ",".join(all_chains),
                        "all_prot_names" : ", ".join(all_prot_names),
                        "seg_li":",".join(["-".join(seg) for seg in seg_li]),
                        "fpdir" : fpdir,
                        "delta":delta
                         }
                    return render(request, 'view/index.html', context)
                else:
                    context={
                        "dyn_id":dyn_id,
                        "mdsrv_url":mdsrv_url,
                        "structure_file":structure_file, 
                        "structure_name":structure_name , 
                        "structure_file_id":structure_file_id,
                        "traj_list":traj_list, 
                        "compounds" : comp_li,
                        "ligands": lig_li,
                        "ligands_short": ",".join(lig_li_s),
                        "other_prots":other_prots,
                        "chains" : chain_str,
                        "prot_seq_pos": list(prot_seq_pos.values()),
                        "gpcr_pdb": "no",
                        "all_chains": ",".join(all_chains),
                        "all_prot_names" : ", ".join(all_prot_names),
                        "fpdir" : fpdir,
                        "seg_li":"",
                        "delta":delta
                        }
                    return render(request, 'view/index.html', context)
            else: #No checkpdb and matchpdb
                context={
                        "dyn_id":dyn_id,
                        "mdsrv_url":mdsrv_url,
                        "structure_file":structure_file, 
                        "structure_name":structure_name , 
                        "structure_file_id":structure_file_id,
                        "traj_list":traj_list, 
                        "compounds" : comp_li,
                        "ligands": lig_li,
                        "ligands_short": ",".join(lig_li_s),
                        "other_prots":other_prots,
                        "chains" : chain_str,            
                        "gpcr_pdb": "no",
                        "all_prot_names" : ", ".join(all_prot_names),
                        "fpdir" : fpdir,
                        "seg_li":"",
                        "delta":delta
                        }
                return render(request, 'view/index.html', context)
        else: #len(chain_name_li) <= 0
            context={
                    "dyn_id":dyn_id,
                    "mdsrv_url":mdsrv_url,
                    "structure_file":structure_file, 
                    "structure_name":structure_name , 
                    "structure_file_id":structure_file_id,
                    "traj_list":traj_list, 
                    "compounds" : comp_li,
                    "ligands": lig_li,
                    "other_prots":[],
                    "ligands_short": ",".join(lig_li_s),                  
                    "chains" : "",            
                    "gpcr_pdb": "no",
                    "fpdir" : fpdir,
                    "seg_li":"",
                    "delta":delta
                    }
            return render(request, 'view/index.html', context)





#########################

def compute_rmsd(rmsdStr,rmsdTraj,traj_frame_rg,ref_frame,rmsdRefTraj,traj_sel,strideVal):
    i=0
    struc_path = "/protwis/sites/files/" + rmsdStr
    traj_path = "/protwis/sites/files/" + rmsdTraj
    ref_traj_path = "/protwis/sites/files/" + rmsdRefTraj
    small_errors=[]
    set_sel=None
    if traj_sel == "bck":
        set_sel="alpha"
    elif traj_sel == "noh":
        set_sel="heavy"
    elif traj_sel == "min":
        set_sel="minimal"
    #elif traj_sel == "all_atoms":
    #    set_sel="all"
    if traj_frame_rg == "all_frames":
        fr_from=0
        fr_to="num_frames"
    else:
        fr_li=traj_frame_rg.split("-")
        fr_from=int(fr_li[0])
        fr_to=int(fr_li[1])+1
    try:
        ref_traj_fr=md.load_frame(ref_traj_path,int(ref_frame),top=struc_path)
        itertraj=md.iterload(filename=traj_path,chunk=50/strideVal, skip =fr_from ,top=struc_path, stride =strideVal)
    except Exception:
        return (False,None, ["Error loading the file."])
    if len(ref_traj_fr)==0:
        error_msg="Frame "+str(ref_frame)+" does not exist at refference trajectory."
        return (False,None, error_msg)          
    rmsd_all=np.array([])
    if fr_to=="num_frames":
        max_n_frames=False
    else:
        max_n_frames=fr_to
    fr_count=fr_from
    for itraj in itertraj:
        fr_count+=(itraj.n_frames)*strideVal
        if max_n_frames and fr_count > max_n_frames:
            if i == 0:
                fr_max=math.ceil(( max_n_frames-(fr_count - (itraj.n_frames)*strideVal))/strideVal)
            else:
                fr_max=max_n_frames-(fr_count - (itraj.n_frames)*strideVal)
        else:
            fr_max=itraj.n_frames
        i+=fr_max
        if traj_sel =="all_prot":
            selection=itraj.topology.select("protein")
        elif (traj_sel not in ["bck","noh","min"]):
            lig_sel="resname "+traj_sel
            try:
                selection=itraj.topology.select(lig_sel)
            except Exception:
                error_msg="Ligand not found."
                return (False,None, error_msg)
            if (len(selection)==0):
                error_msg="Ligand not found."
                return (False,None, error_msg)
        else:
            selection=itraj.topology.select_atom_indices(set_sel)
        try:
            rmsd = md.rmsd(itraj[:fr_max], ref_traj_fr, 0,atom_indices=selection)
            rmsd_all=np.append(rmsd_all,rmsd,axis=0)
        except Exception:
            error_msg="RMSD can't be calculated."
            return (False,None, error_msg)
        if max_n_frames and fr_from+ (i*strideVal) >= max_n_frames:
            break
    if fr_from >= fr_count:
        error_msg ="The trajectory analysed has no frame " + str(fr_from) +"."
        return (False,None, error_msg)
    if max_n_frames and max_n_frames > fr_count:
        small_error ="The trajectory analysed has no frame " + str(max_n_frames-1) +". The final frame has been set to "+ str(fr_count - 1) +", the last frame of that trajectory."
        small_errors.append(small_error)            
    rmsd_all=np.reshape(rmsd_all,(len(rmsd_all),1))
    frames=np.arange(fr_from,fr_from+(len(rmsd_all)*strideVal),strideVal,dtype=np.int32).reshape((len(rmsd_all),1))
    data=np.append(frames,rmsd_all, axis=1).tolist()
    data_fin=[["Frame","RMSD"]] + data
    return(True, data_fin, small_errors)




def download_dist(request, dist_id):
    if request.session.get('dist_data', False):
        dist_data_s=request.session['dist_data']
        dist_dict=dist_data_s["dist_dict"]
        dist_data_all=dist_dict[dist_id]
        (dist_data,struc_filename,traj_filename,strideVal)=dist_data_all
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_filename).group(1)+"_"+dist_id+'.csv"'
        writer = csv.writer(response)
        writer.writerow(["#Structure: "+struc_filename])
        writer.writerow(["#Trajectory: "+traj_filename])
        if (int(strideVal) > 1):
            writer.writerow(["#Strided: "+strideVal])
        header=[]
        for name in dist_data[0]:
            header.append("'"+name+"'")
        writer.writerow(header)
        for row in dist_data[1:]:
            rowcol=[]
            for col in row:
                rowcol.append(col)
            writer.writerow(rowcol) 
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([" "])
    return response
    
def download_int(request, int_id):
    if request.session.get('int_data', False):
        int_data_s=request.session['int_data']
        int_info=int_data_s["int_info"]
        int_data_all=int_info[int_id]
        (int_dict,thresh,traj_fileint,struc_fileint,dist_scheme,strideVal)=int_data_all
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_fileint).group(1)+"_"+int_id+'_interact.csv"'
        writer = csv.writer(response)
        if (dist_scheme=="closest"):
            dist_scheme_name="All atoms";
        else:
            dist_scheme_name="Heavy atoms only";

        writer.writerow(["#Structure: "+struc_fileint])
        writer.writerow(["#Trajectory: "+traj_fileint])
        if (int(strideVal) > 1):
            writer.writerow(["#Strided: "+strideVal])
        if (dist_scheme=="closest"):
            dist_scheme_name="All atoms";
        else:
            dist_scheme_name="Heavy atoms only";

        writer.writerow(["#Threshold: "+thresh+ " angstroms ("+dist_scheme+")"])
        writer.writerow(["'Ligand'","'Position'" ,"'Residue'", "'Chain'", "'Frequency (%)'"])
        for (lig, lig_int) in int_dict.items():
            (pos,chain,res,freq)=lig_int[0]
            all_first=["'"+lig+"'", pos,"'"+res+"'","'"+chain+"'",freq]
            writer.writerow(all_first)
            for inter in lig_int[1:]:
                (pos,chain,res,freq)=inter
                writer.writerow(["", pos,"'"+res+"'","'"+chain+"'",freq])

    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([" "])
    return response
    


    
def proper_name(traj_sel):
    if traj_sel == "bck":
        set_sel="protein CA"
    elif traj_sel == "noh":
        set_sel="non-hydrogen protein atoms"
    elif traj_sel == "min":
        set_sel="protein CA, CB, C, N, O"
    elif traj_sel == "all_prot":
        set_sel="all protein atoms"
    else:
        set_sel = traj_sel
    return set_sel  
    

def obtain_pdb_atomInd_from_chains(gpcr_chains,struc_path,serial_mdInd):
    readpdb=open(struc_path,'r')
    gpcr_atomInd=[]
    for line in readpdb:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            trykey=line[17:21].strip()
            if trykey in d.keys():
                if line[21:22].strip() in gpcr_chains:
                    serial=line[6:11].strip()
                    gpcr_atomInd.append(serial_mdInd[serial])
    return(np.array(gpcr_atomInd))



def compute_interaction(res_li,struc_p,traj_p,num_prots,chain_name_li,thresh,serial_mdInd,gpcr_chains,dist_scheme,strideVal):
    struc_path = "/protwis/sites/files/"+struc_p
    traj_path = "/protwis/sites/files/"+traj_p
    try:
        struc=md.load(struc_path)
    except Exception:
        return (False,None, "Error loading the file.")
    all_lig_res=[]
###
    for res in res_li:
        lig_sel=struc.topology.select("resname '"+res+"'")
        if len(lig_sel)>0:
            lig_res=[residue.index for residue in struc.atom_slice(lig_sel).topology.residues]
            all_lig_res.append(lig_res[0])
####
    if len(all_lig_res)>0:
        if gpcr_chains:
            gpcr_chains_sel=""
            for chain in gpcr_chains:
                gpcr_chains_sel+="chainid "+ str(chain_name_li.index(chain)) +" or "
            gpcr_chains_sel="protein and ("+gpcr_chains_sel[:-4]+")"
            gpcr_sel=struc.topology.select(gpcr_chains_sel)
        else:
            gpcr_sel=struc.topology.select("protein") 
        gpcr_res=[residue.index for residue in struc.atom_slice(gpcr_sel).topology.residues]
        pairs = list(itertools.product(gpcr_res, all_lig_res))
        itertraj=md.iterload(filename=traj_path,chunk=(50/strideVal), top=struc_path, stride=strideVal)
        first=True 
        try:
            for itraj in itertraj:
                (dists,res_p)=md.compute_contacts(itraj, contacts=pairs, scheme=dist_scheme)
                if first:
                    alldists=dists
                    allres_p=res_p
                    first=False
                else:
                    alldists=np.append(alldists,dists,axis=0)
        except Exception:
            return (False,None, "Error loading the file.")
        contact_freq={}
        for pair in allres_p:
            contact_freq[tuple(pair)]=0
        for frame_dist in alldists:
             i=0
             while i < len(frame_dist):
                 if frame_dist[i]<(thresh/10):
                     contact_freq[tuple(allres_p[i])]+=1
                 i+=1
        num_frames=len(alldists)
        to_delete=[]
        for allres_p , freq in contact_freq.items():
             if freq ==0:               
                 to_delete.append(allres_p)
             else:                    
                 contact_freq[allres_p]=(freq/num_frames)*100
        for key in to_delete:
            del contact_freq[key]
        fin_dict={}
        for r in res_li:
             fin_dict[r]=[]
        for pair in sorted(contact_freq, key=lambda x: x[0]):
            freq=contact_freq[pair]
            res_ind=pair[0]
            lig_ind=pair[1]
            lig_nm=struc.topology.residue(lig_ind).name
            res_topo=struc.topology.residue(res_ind)
            res_pdb=res_topo.resSeq
            res_chain_ind=res_topo.chain.index
            res_name=res_topo.name
            res_chain=chain_name_li[res_chain_ind]
            fin_dict[lig_nm].append((res_pdb,res_chain,res_name,("%.2f" % freq)))
        return(True,fin_dict,None)
    else:
        return (False,None, "Error with ligand selection.")

def download_rmsd(request, rmsd_id):
    if request.session.get('rmsd_data', False):
        rmsd_data_s=request.session['rmsd_data']
        rmsd_dict=rmsd_data_s["rmsd_dict"]
        rmsd_data_all=rmsd_dict[rmsd_id]
        (rmsd_data,struc_filename,traj_filename,traj_frame_rg,ref_frame,rtraj_filename,traj_sel,strideVal)=rmsd_data_all        
        response = HttpResponse(content_type='text/csv')
        
        response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_filename).group(1)+"_"+rmsd_id+'.csv"'
        writer = csv.writer(response)
        writer.writerow(["#Structure: "+struc_filename])
        writer.writerow(["#Trajectory: "+traj_filename])
        if (int(strideVal) > 1):
            writer.writerow(["#Strided: "+strideVal])
        writer.writerow(["#Reference: frame "+ref_frame+" of trajectory "+rtraj_filename])
        writer.writerow(["#Selection: "+proper_name(traj_sel)])
        header=[]
        for name in rmsd_data[0]:
            header.append("'"+name+"'")
        writer.writerow(header)
        for row in rmsd_data[1:]:
            rowcol=[]
            for col in row:
                rowcol.append(col)
            writer.writerow(rowcol) 
    else:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([" "])
    return response
    
def viewer_docs(request):
    return render(request, 'view/viewer_docs.html', {} )


def parser(filename):
    #'dynadb/b2ar_isoprot/b2ar.psf'
    chargesfh=open(filename,'r')
    atom_flag=0
    atoms=dict()
    for line in chargesfh:
        if '!NBOND' in line:
            atom_flag=0
        if atom_flag==1 and line.strip(): #line.strip() prevents using empty lines bc empty string evaluates to False
            fields=line.split()
            charge=fields[6]
            if 'E' in charge:
                charge= float(charge[:charge.rfind('E')]) * 10**float(charge[charge.rfind('E')+1:])
            atoms[fields[0]]=[float(charge),fields[5],fields[3],fields[2]] # charge, atom type, resname, resid
        if '!NATOM' in line:
            atom_flag=1

    return atoms

def hbonds(request):
    if request.method == 'POST':
        arrays=request.POST.getlist('frames[]')
        full_results=dict()
        struc_path = "/protwis/sites/files/"+arrays[4]
        all_chains=obtain_all_chains(struc_path)
        traj_path = "/protwis/sites/files/"+arrays[3]
        start=int(arrays[0])
        end=int(arrays[1])
        backbone=arrays[6]=='true'
        if end<0:
            end=10**20
        percentage_cutoff=int(arrays[2])
        label = lambda hbond : '%s--%s' % (t.topology.atom(hbond[0]), t.topology.atom(hbond[2]))
        histhbond=dict()
        hbonds_residue=dict()
        hbonds_residue_notprotein=dict()
        hbonds_ks=[]
        nframes=0
        chunksize=50
        neighbours=arrays[7]=='true'
        traj_name=traj_path[traj_path.rfind('/'):].replace('.','_')
        bonds_path=traj_path[:traj_path.rfind('/')]+traj_name+'_bonds'
        if neighbours:
            resid_dist=4
        else:
            resid_dist=0
        try:
            with open (bonds_path, 'rb') as fp:
                precomputed_bonds = pickle.load(fp)
            precomputed=True
        except:
            precomputed=False

        print('Is it precomputed?',precomputed)

        if not precomputed:
            precomputed_bonds=[]
            for t in md.iterload(traj_path, top=struc_path,chunk=chunksize,skip=start):
                hbonds_ks+=md.wernet_nilsson(t, exclude_water=True, periodic=True, sidechain_only=False) # i could save this precomputed matrix
            with open(bonds_path, 'wb') as fp:
                pickle.dump(hbonds_ks, fp)

            hbonds_ks=hbonds_ks[start:end]
            nframes=len(hbonds_ks)
            for frameres in hbonds_ks:
                for hbond in frameres:
                    try:
                        histhbond[tuple(hbond)]+=1
                    except KeyError:
                        histhbond[tuple(hbond)]=1

        else:
            precomputed_bonds=precomputed_bonds[start:end]
            nframes=len(precomputed_bonds)
            for frameres in precomputed_bonds:
                for hbond in frameres:
                    try:
                        histhbond[tuple(hbond)]+=1
                    except KeyError:
                        histhbond[tuple(hbond)]=1

        t=md.load_frame(traj_path, index=0, top=struc_path)

        for keys in histhbond:
            chainpair0,chainpair1=[int(t.topology.atom(keys[0]).residue.chain.index),int(t.topology.atom(keys[2]).residue.chain.index)]
            chain0,chain1=[all_chains[chainpair0],all_chains[chainpair1]]
            histhbond[keys]= round(histhbond[keys]/nframes,3)*100
            is_not_neighbour=abs(t.topology.atom(keys[0]).residue.index-t.topology.atom(keys[2]).residue.index)>resid_dist
            if backbone:
                if histhbond[keys]>percentage_cutoff and is_not_neighbour: #the hbond is not between neighbourd atoms and the frecuency across the traj is more than 10%
                    labelbond=label([keys[0],histhbond[keys],keys[2]])
                    labelbond=labelbond.replace(' ','')
                    labelbond=labelbond.split('--')
                    donor=labelbond[0]
                    acceptor=labelbond[1]
                    acceptor_res=acceptor[:acceptor.rfind('-')]
                    donor_res=donor[:donor.rfind('-')]
                    if donor_res!=acceptor_res: #do not consider hbond inside the same residue.
                        histhbond[keys]=str(histhbond[keys])[:4]
                        if (not t.topology.atom(keys[0]).residue.is_protein) or (not t.topology.atom(keys[2]).residue.is_protein): #other hbonds
                            try:
                                if t.topology.atom(keys[1]).residue.is_protein: #donor is protein
                                    hbonds_residue_notprotein[donor_res].append([acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]) # HBONDS[donor]=[acceptor,freq,atom1index,atom2index]
                                else: #acceptor is protein
                                    hbonds_residue_notprotein[acceptor_res].append([donor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain1,chain0])          
                            except KeyError:
                                if t.topology.atom(keys[1]).residue.is_protein: #donor is protein
                                    hbonds_residue_notprotein[donor_res]=[[acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]]
                                else: #acceptor is protein
                                    hbonds_residue_notprotein[acceptor_res]=[[donor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain1,chain0]]

                        else: #intraprotein hbonds
                            try:
                                hbonds_residue[donor_res].append([acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1])
                            except KeyError:
                                hbonds_residue[donor_res]=[[acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]]
            else:
                if histhbond[keys]>percentage_cutoff:
                    if t.topology.atom(keys[0]).residue.is_protein:
                        a1=t.topology.atom(keys[0]).is_sidechain
                    else:
                        a1=True
                    if t.topology.atom(keys[2]).residue.is_protein:
                        a2=t.topology.atom(keys[2]).is_sidechain
                    else:
                        a2=True    
                    if a1 and a2 and is_not_neighbour:
                        labelbond=label([keys[0],histhbond[keys],keys[2]])
                        labelbond=labelbond.replace(' ','')
                        labelbond=labelbond.split('--')
                        donor=labelbond[0]
                        acceptor=labelbond[1]
                        acceptor_res=acceptor[:acceptor.rfind('-')]
                        donor_res=donor[:donor.rfind('-')]
                        if donor_res!=acceptor_res: #do not consider hbond inside the same residue.
                            histhbond[keys]=str(histhbond[keys])[:4]
                            if (not t.topology.atom(keys[0]).residue.is_protein) or (not t.topology.atom(keys[2]).residue.is_protein): #other hbonds
                                try:
                                    if t.topology.atom(keys[1]).residue.is_protein: #donor is protein
                                        hbonds_residue_notprotein[donor_res].append([acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]) # HBONDS[donor]=[acceptor,freq,atom1index,atom2index]
                                    else: #acceptor is protein
                                        hbonds_residue_notprotein[acceptor_res].append([donor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain1,chain0])          
                                except KeyError:
                                    if t.topology.atom(keys[1]).residue.is_protein: #donor is protein
                                        hbonds_residue_notprotein[donor_res]=[[acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]]
                                    else: #acceptor is protein
                                        hbonds_residue_notprotein[acceptor_res]=[[donor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain1,chain0]]

                            else: #intraprotein hbonds
                                try:
                                    hbonds_residue[donor_res].append([acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1])
                                except KeyError:
                                    hbonds_residue[donor_res]=[[acceptor_res,histhbond[keys],str(keys[1]),str(keys[2]),chain0,chain1]]

        if False: #warning, to implement download of csv file

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="'+re.search("(\w*)\.\w*$",struc_filename).group(1)+"_"+rmsd_id+'.csv"'
            writer = csv.writer(response)
            writer.writerow(["#Structure: "+struc_filename])
            writer.writerow(["#Trajectory: "+traj_filename])
            if (int(strideVal) > 1):
                writer.writerow(["#Strided: "+strideVal])
            writer.writerow(["#Reference: frame "+ref_frame+" of trajectory "+rtraj_filename])
            writer.writerow(["#Selection: "+proper_name(traj_sel)])
            struc_path=struc_path[:-4]
            csvfile= open(struc_path+'hbonds.csv','w',newline='')
            writer = csv.writer(csvfile,delimiter=' ',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)
            header=['Donor_residue', 'Acceptor_Residue', 'Frequency', 'Atom_index', 'Atom_index_2']
            writer.writerow(header)
            for keys in hbonds_residue:
                for minilist in hbonds_residue[keys]:
                    rowlist=[keys]+minilist[:-2]
                    writer.writerow(rowlist)
                writer.writerow(['','','','',''])

            csvfile= open(struc_path+'hbonds_notprotein.csv','w',newline='')
            writer = csv.writer(csvfile,delimiter=' ',quotechar=',', quoting=csv.QUOTE_MINIMAL)
            header=['Residue1_(protein)', 'Residue2_(other)', 'Frequency', 'Atom_index', 'Atom_index_2']
            writer.writerow(header)
            for keys in hbonds_residue_notprotein:
                for minilist in hbonds_residue_notprotein[keys]:
                    rowlist=[keys]+minilist[:-2]
                    writer.writerow(rowlist)
                writer.writerow(['','','','',''])
        
        full_results['hbonds'] = hbonds_residue
        full_results['hbonds_notprotein'] = hbonds_residue_notprotein
        data = json.dumps(full_results)
        return HttpResponse(data, content_type='application/json')


def saltbridges(request):
    if request.method == 'POST':
        arrays=request.POST.getlist('frames[]')
        struc_path = "/protwis/sites/files/"+arrays[4]
        traj_path = "/protwis/sites/files/"+arrays[3]
        label = lambda hbond : '%s--%s' % (t.topology.atom(hbond[0]), t.topology.atom(hbond[2]))
        full_results=dict()
        chunksize=50
        start=int(arrays[0])
        end=int(arrays[1])
        if end<0:
            end=10**20
        nframes=0
        counter=0
        percentage_threshold=int(arrays[2])/100
        distance_threshold=0.4 #4 angstroms/0.4nm
        for t in md.iterload(traj_path, top=struc_path,chunk=chunksize,skip=start):
            rframes=end-nframes 
            if rframes==0:
                break
            if rframes<chunksize:
                t=t[:rframes] #maybe the user does not want the full chunk.
            nframes+=len(t)
            salt_bridges_atoms=[]
            salt_bridges_residues=[]
            cdis=[]
            if counter==0:
                number_hatoms=0
                for residue in t.topology.residues:
                    if residue.name=='HIS':
                        number_hatoms= len([atom.index for atom in residue.atoms if atom.element.name=='hydrogen'])
                    if residue.name in ['ASP','GLU','ARG','LYS'] or number_hatoms>7:
                        caindex= [atom.index for atom in residue.atoms if atom.name == 'CA'][0]
                        for atom in residue.atoms:
                            cdis.append([caindex,atom.index])

                        for atom in residue.atoms:
                            if residue.name=='ARG' and (atom.name=='NH1' or atom.name=='NH2'):
                                salt_bridges_atoms.append(atom.index+1)
                            if residue.name=='GLU' and (atom.name=='OE2' or atom.name=='OE1' ):
                                salt_bridges_atoms.append(atom.index+1)
                            if residue.name=='ASP' and (atom.name=='OD2' or atom.name=='OD1'):
                                salt_bridges_atoms.append(atom.index+1)
                            if residue.name=='HIS' and (atom.name=='NE2' or atom.name=='ND1'):
                                salt_bridges_atoms.append(atom.index+1)
                            if residue.name=='LYS' and atom.name=='NZ':
                                salt_bridges_atoms.append(atom.index+1)

                if False:
                    distance=md.compute_distances(t, np.array(cdis),periodic=False) #shape=(n_frames, num_pairs)
                    distancedic=dict()
                    for f in range(len(t)):
                        for i in range(len(cdis)): #iterate for each ca-atom.index pair
                            try:
                                if distance[f][i]>distancedic[cdis[i][0]][0]: #if distance from another atom is bigger, pick that atom index and distance
                                    distancedic[cdis[i][0]]=[distance[f][i],cdis[i][1]]
                            except KeyError:
                                distancedic[cdis[i][0]]=[distance[f][i],cdis[i][1]] # distance['ca']=[maxdis,atom_index]

                    for keys in distancedic:
                        salt_bridges_atoms.append(int(distancedic[keys][1])) #+1before

                combinations=[]
                for atom_index in range(len(salt_bridges_atoms)):
                    for atom_index2 in range(atom_index+1,len(salt_bridges_atoms)):
                        resname1=t.topology.atom(salt_bridges_atoms[atom_index]).residue.name #-1bef
                        resname2=t.topology.atom(salt_bridges_atoms[atom_index2]).residue.name #-1bef
                        chained=abs(t.topology.atom(salt_bridges_atoms[atom_index]).residue.index-t.topology.atom(salt_bridges_atoms[atom_index2]).residue.index)<4 #-1bef
                        if {resname1,resname2} in [{'ASP','ARG'},{'ASP','LYS'},{'GLU','LYS'},{'GLU','ARG'},{'GLU','HIS'},{'ASP','HIS'}] and not chained: #is this a correct combination?
                            combinations.append([salt_bridges_atoms[atom_index],salt_bridges_atoms[atom_index2]])

                combinations=np.array(combinations)
                distances=md.compute_distances(t,combinations) #shape=(n_frames, num_pairs)
                frequency= np.sum(distances < distance_threshold,axis=0) #number of times the distance is lower than threshold in the current chunk

            else:
                distances=md.compute_distances(t,combinations)
                frequency+=np.sum(distances < distance_threshold,axis=0)

            counter+=1

        frequency=frequency/nframes
        distances= frequency> percentage_threshold #[True, False, True, True, ...]
        combfreq=np.concatenate((combinations,np.array([frequency]).T),axis=1) # atom1,atom2, freq
        salt_bridges_residues=combfreq[distances] #logical mask to combinationcs [[10,34],[11,90],[42,666],[],...][True, False, True, True, ...]
        full_results['salt_bridges'] = salt_bridges_residues
        full_results['salt_bridges'] = [(label([int(saltb[0])-1,'-',int(saltb[1])-1]),str(round(saltb[2],3)*100)[:4], saltb[0]-1,saltb[1]-1 ) for saltb in full_results['salt_bridges']] 
        #-1 to return to zero indexing.
        bridge_dic=dict()
        for bond in full_results['salt_bridges']:
            labelbond=bond[0]
            labelbond=labelbond.replace(' ','')
            labelbond=labelbond.split('--')
            donor=labelbond[0]
            acceptor=labelbond[1]
            acceptor_res=acceptor[:acceptor.rfind('-')]
            donor_res=donor[:donor.rfind('-')]
            if donor_res in bridge_dic:
                bridge_dic[donor_res].append([acceptor_res,bond[1],str(bond[2]),str(bond[3])])
            elif acceptor_res in bridge_dic:
                bridge_dic[acceptor_res].append([donor_res,bond[1],str(bond[2]),str(bond[3])])
            else:
               bridge_dic[donor_res]=[[acceptor_res,bond[1],str(bond[2]),str(bond[3])]]

        if False: #warning, to implement in future, download csv with results
            struc_path=struc_path[:-4]
            csvfile= open(struc_path+'saltbridges.csv','w',newline='')
            writer = csv.writer(csvfile,delimiter=' ',
                                quotechar=',', quoting=csv.QUOTE_MINIMAL)

            header=['Residue1', 'Residue2', 'Frequency', 'Atom_index', 'Atom_index_2']
            writer.writerow(header)

            for keys in bridge_dic:
                for minilist in bridge_dic[keys]:
                    rowlist=[keys]+minilist
                    writer.writerow(rowlist)
                writer.writerow(['','','','',''])

        full_results['salt_bridges']=bridge_dic
        data = json.dumps(full_results)
        return HttpResponse(data, content_type='application/json')

def sasa(request):
    zatoms=[]
    arrays=request.POST.getlist('frames[]')
    struc_path = "/protwis/sites/files/"+arrays[4]
    traj_path = "/protwis/sites/files/"+arrays[3]
    sel=arrays[6]
    residue_indexes=arrays[7].split(',')
    traj_name=traj_path[traj_path.rfind('/'):].replace('.','_')
    sasa_path=traj_path[:traj_path.rfind('/')]+traj_name+'.npy'
    try:
        sasa=np.load(sasa_path)
        precomputed=True
    except:
        precomputed=False
    chunksize=50
    start=int(arrays[0])
    end=int(arrays[1])
    nframes=0
    counter=0
    zpos_dic=dict()
    for t in md.iterload(traj_path, top=struc_path,chunk=chunksize):
        notwatatoms=t.topology.select("not water")
        t=t.atom_slice(notwatatoms)
        if counter==0:
            tfind=t.atom_slice(t.topology.select("protein"))
            cter=tfind.topology.residue(-1).atom(0).index
            nter=tfind.topology.residue(0).atom(0).index
            if tfind.xyz[0][nter][2]>tfind.xyz[0][cter][2]:
                normal=True
            else:
                normal=False
            tori=t
            patoms=t.topology.select("symbol P and (not protein)")
            tmod=t.atom_slice(patoms)
            zetas_p=[]
            for i in range(tmod.xyz[0].shape[0]): #this is the FIRST frame, not the original PDB! equal to put 1 in the VMD Main window.
                zetas_p.append(tmod.xyz[0][i][2])
            zetas_p=sorted(zetas_p)
            zetahalf=np.mean(zetas_p)
            maxjump=0
            for i in range(len(zetas_p)-1):
                if abs(zetas_p[i]-zetas_p[i+1])>maxjump:
                    lastp=i
                    maxjump=abs(zetas_p[i]-zetas_p[i+1])
            zleaftop=np.mean(zetas_p[lastp:])
            zleafbottom=np.mean(zetas_p[:lastp])

            atoms_prot_bootom=[]
            atoms_half=[]
            atoms_receptor=[]
            atoms_up=[]
            atoms_uphalf=[]
            for i in range(tori.xyz[0].shape[0]):
                if normal:
                    if tori.xyz[0][i][2]<zleafbottom and tori.topology.atom(i).residue.is_protein:
                        atoms_prot_bootom.append(i)
                    if tori.xyz[0][i][2]<zetahalf and tori.topology.atom(i).residue.is_protein:
                        atoms_half.append(i)
                    if tori.topology.atom(i).residue.is_protein:
                        atoms_receptor.append(i)
                    if tori.xyz[0][i][2]>zleaftop and tori.topology.atom(i).residue.is_protein:
                        atoms_up.append(i)
                    if tori.xyz[0][i][2]>zetahalf and tori.topology.atom(i).residue.is_protein:
                        atoms_uphalf.append(i)
                else:
                    if tori.xyz[0][i][2]>zleaftop and tori.topology.atom(i).residue.is_protein:
                        atoms_prot_bootom.append(i)
                    if tori.xyz[0][i][2]>zetahalf and tori.topology.atom(i).residue.is_protein:
                        atoms_half.append(i)
                    if tori.xyz[0][i][2]<zetahalf and tori.topology.atom(i).residue.is_protein:
                        atoms_uphalf.append(i)
                    if tori.topology.atom(i).residue.is_protein:
                        atoms_receptor.append(i)
                    if tori.xyz[0][i][2]<zleafbottom and tori.topology.atom(i).residue.is_protein:
                        atoms_up.append(i)

            if not precomputed:
                sasa=md.shrake_rupley(tori)

        elif counter>0 and not precomputed:
            sasa=np.concatenate((sasa,md.shrake_rupley(t)))

        else:
            break

        counter+=1

    if not precomputed:
        traj_name=traj_path[traj_path.rfind('/'):].replace('.','_')
        sasa_path=traj_path[:traj_path.rfind('/')]+traj_name
        np.save(sasa_path,sasa)

    sasa=sasa[start:end]
    selected_resids=[]
    if sel=='half':
        sasaours=sasa[:,atoms_half] #pick only the sasa columns of our atoms.
        for atom_index in atoms_half:
            selected_resids.append(tori.topology.atom(atom_index).residue)
    elif sel=='bottom':
        sasaours=sasa[:,atoms_prot_bootom] #pick only the sasa columns of our atoms.
        for atom_index in atoms_prot_bootom:
            selected_resids.append(tori.topology.atom(atom_index).residue)
    elif sel=='receptor':
        sasaours=sasa[:,atoms_receptor] #pick only the sasa columns of our atoms.
        for atom_index in atoms_receptor:
            selected_resids.append(tori.topology.atom(atom_index).residue)
    elif sel=='all':
        sasaours=sasa[:] #pick only the sasa columns of our atoms.
        selected_resids=[]
    elif sel=='sequence':
        sequence_atoms=[]
        for resid in residue_indexes:
            resid=int(resid)-1
            selected_resids.append(tori.topology.residue(resid))
            for atom in tori.topology.residue(resid).atoms:
                sequence_atoms.append(atom.index)

        sasaours=sasa[:,sequence_atoms] #pick only the sasa columns of our atoms.

    elif sel=='up':
        sasaours=sasa[:,atoms_up] #pick only the sasa columns of our atoms.
        for atom_index in atoms_up:
            selected_resids.append(tori.topology.atom(atom_index).residue)

    elif sel=='up_half':
        sasaours=sasa[:,atoms_uphalf] #pick only the sasa columns of our atoms.
        for atom_index in atoms_uphalf:
            selected_resids.append(tori.topology.atom(atom_index).residue)

    sasaours_peratom=sasaours.sum(axis=0)
    sasaours_perframe=sasaours.sum(axis=1)
    final_resids=[]
    for res in selected_resids:
        final_resids.append(int(re.search(r'\d+', str(res)).group()))

    final_resids=list(set(final_resids))
    if sel=='all':
        final_resids='all'

    sasaours_perframe=sasaours_perframe.tolist()
    time=sasa.shape[0] #number of frames
    time=[i for i in range(time)]
    result=zip(time,sasaours_perframe)
    result=[list(i) for i in result]
    sasares={'sasa':result,'selected_residues':final_resids}
    if request.session.get('sasa_data', False):
        sasa_data=request.session['sasa_data']
        sasa_dict=sasa_data["sasa_dict"]
        new_sasa_id=sasa_data["new_sasa_id"]+1

    else:
        new_sasa_id=1
        sasa_dict={}
            
    sasa_dict["sasa_"+str(new_sasa_id)]=sasares
    request.session['sasa_data']={"sasa_dict":sasa_dict, "new_sasa_id":new_sasa_id}
    sasares={'sasa':result,'selected_residues':final_resids,'sasa_id':new_sasa_id}
    data = json.dumps(sasares)
    return HttpResponse(data, content_type='application/json')

def grid(request):
    if request.method == 'POST':
        arrays=request.POST.getlist('frames[]')
        percentage_cutoff=int(arrays[2])
        struc_path = "/protwis/sites/files/"+arrays[4]
        traj_path = "/protwis/sites/files/"+arrays[3]
        #t = md.load(traj_path,top=struc_path)
        trajectory = md.load('dynadb/b2ar_isoprot/b2ar.dcd',top='dynadb/b2ar_isoprot/build.pdb')
        trajectory=trajectory[0:10]
        atom_indices_prot = [a.index for a in trajectory.topology.atoms if a.residue.is_protein]
        atom_indices_ligand = [a.index for a in trajectory.topology.atoms if a.residue.name=='5FW']
        atom_indices= atom_indices_prot+atom_indices_ligand
        print(atom_indices_ligand)
        t=trajectory
        trajectory=trajectory.atom_slice(atom_indices, inplace=False)
        atomindexes_prot=[atom.index for atom in trajectory.topology.atoms if atom.residue.is_protein]
        trajprot=trajectory.superpose(trajectory,0,atom_indices=atomindexes_prot) #works!
        trajprot=trajprot
        mintop=np.array([0,0,0])
        print('ck1')
        print(str(len(trajprot)))
        i=0
        for frame in range(len(trajprot)):
            print("frame: ",i)
            i+=1
            for atom in trajprot.xyz[frame]:
                if atom[0]<mintop[0]:
                    mintop[0]=atom[0]
                if atom[1]<mintop[1]:
                    mintop[1]=atom[1]
                if atom[2]<mintop[2]:
                    mintop[2]=atom[2]
        mintop-=1
        max_xyz=[0,0,0]
        atomxyz=trajprot.xyz
        for frame in range(len(trajprot)):
            for atomindex in range(len(trajprot.xyz[frame])):
                atomxyz[frame][atomindex]=atomxyz[frame][atomindex]+(mintop*-1) #ensure that atom coordinates are in positive area with a translation
                if atomxyz[frame][atomindex][0]>max_xyz[0]:
                    max_xyz[0]=atomxyz[frame][atomindex][0]
                if atomxyz[frame][atomindex][1]>max_xyz[1]:
                    max_xyz[1]=atomxyz[frame][atomindex][1]
                if atomxyz[frame][atomindex][2]>max_xyz[2]:
                    max_xyz[2]=atomxyz[frame][atomindex][2]
        #now create a grid with appropiate dimensions to hold all the atoms
        max_xyz=[int(round((i*10)+2)) for i in max_xyz] #nanometers to angstroms.
        grid=np.zeros(max_xyz)
        for frame in range(len(trajprot)):
            for atomindex in range(len(trajprot.xyz[frame])):
                xc=int(round(atomxyz[frame][atomindex][0]*10))#nanometers to angstroms.
                yc=int(round(atomxyz[frame][atomindex][1]*10))
                zc=int(round(atomxyz[frame][atomindex][2]*10))
                grid[xc,yc,zc]+=1 #add 0.5 to neighbours?
        shape=grid.shape
        grid=grid.tolist()
        full_results={'grid':grid,'shape':shape,'indexes':atom_indices}
        print('Analysis done')
        data = json.dumps(full_results)
        return HttpResponse(data, content_type='application/json')

#def fplot_test(request, filename):
#    context={"json_name":filename+".json"}
#    return render(request, 'view/flare_plot_test.html', context)
    
#def fplot_gpcr(request, dyn_id, filename,seg_li):
#    """
#    View of flare plot with pv representation of the pdb
#    """
#    nameToResiTable={}
#    if request.session.get('gpcr_pdb', False):
#        gpcr_pdb=request.session['gpcr_pdb']
#        nameToResiTable={}
#        for (gnum,posChain) in gpcr_pdb.items():
#            gnumOk=gnum[:gnum.find(".")]+gnum[gnum.find("x"):]
#            nameToResiTable[gnumOk]=[posChain[1]+"."+posChain[0],""]
#    #seg_li_ok=[seg.split("-") for seg in seg_li.split(",")]
#    fpdir = get_precomputed_file_path('flare_plot',"hbonds",url=True)
#    pdbpath=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__extension="pdb")[0].filepath
#    pdbpath=pdbpath.replace("/protwis/sites", "/dynadb")
#    prot_names=obtain_protein_names(dyn_id)
#    traj_id=int(re.match("^\d+",filename).group())
#    traj_name=DyndbFiles.objects.get(id=traj_id).filename
#    
#    comp=DyndbModelComponents.objects.filter(id_model__dyndbdynamics=dyn_id)
#    lig_li=[]
#    for c in comp:
#        if c.type ==1:
#            lig_li.append(c.resname)
#
#    context={"json_path":fpdir + filename,
#             "pdb_path": pdbpath,
#             "prot_names": prot_names,
#             "traj_name" :traj_name,
#             "lig_li" : lig_li,
#             "seg_li":seg_li,
#             "nameToResiTable":json.dumps(nameToResiTable),
#             "dyn_id":dyn_id
#            }
#    return render(request, 'view/flare_plot.html', context)
    
    
def fplot_gpcr_slide(request, dyn_id, filename,seg_li):
    """
    View of flare plot with the new slide but without representation of the pdb
    """
    fpdir = get_precomputed_file_path('flare_plot',"hbonds",url=True)
    prot_names=obtain_protein_names(dyn_id)
    traj_id=int(re.match("^\d+",filename).group())
    traj_name=DyndbFiles.objects.get(id=traj_id).filename
    
    context={"json_path":fpdir + filename,
             "prot_names": prot_names,
             "traj_name" :traj_name,
             "dyn_id":dyn_id
            }
    return render(request, 'view/flare_plot_slide.html', context)
    
    
def view_reference(request, dyn_id ):
    """
    Now only opens structure & traj of adenosine receptor with colesterol.
    """
    mdsrv_url=obtain_domain_url(request)
    refobj=DyndbReferences.objects.get(dyndbreferencesdynamics__id_dynamics=dyn_id)
    doi=refobj.doi
    authors=refobj.authors
    title=refobj.title
    pmid=refobj.pmid
    journal=refobj.journal_press
    issue=refobj.issue
    vol=refobj.volume
    pgs=refobj.pages
    pub_year=refobj.pub_year
    dbname=refobj.dbname
    url=refobj.url

    context={
         "mdsrv_url":mdsrv_url,
         "doi":doi,
         "authors": authors,
         "title":title,
         "pmid":pmid,
         "journal":journal,
         "issue":issue,
         "vol":vol,
         "pgs":pgs,
         "pub_year":pub_year,
         "dbname":dbname,
         "url":url
    }
    return render(request, 'view/reference.html', context )


def view_session(request , session_name):
    """
    Now only opens structure & traj of adenosine receptor with colesterol.
    """
    sessions_path="/protwis/sites/files/Sessions"
    s_li=os.listdir(sessions_path)
    if session_name+".ngl" in s_li:
    
        mdsrv_url=obtain_domain_url(request)
        redirect_url='/html/session.html?load=pufa.ngl'

        return redirect(mdsrv_url+redirect_url)

    
    
############ TEST #############
def fplot_test(request, dyn_id, filename):
    fpdir = get_precomputed_file_path('flare_plot',"hbonds",url=True)
    prot_names=obtain_protein_names(dyn_id)
    traj_id=int(re.match("^\d+",filename).group())
    traj_name=DyndbFiles.objects.get(id=traj_id).filename
    
    context={"json_path":fpdir + filename,
             "prot_names": prot_names,
             "traj_name" :traj_name,
             "dyn_id":dyn_id
            }
    return render(request, 'view/fplot_test.html', context)

