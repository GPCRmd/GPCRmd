
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.conf import settings
from dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents,DyndbDynamics, DyndbModel, DyndbProtein,DyndbProteinSequence,DyndbReferences,DyndbModeledResidues
from django.db.models import F
from protein.models import Protein
from mutation.models import Mutation,MutationExperiment
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
from pathlib import Path
import pandas as pd

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

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

def create_conserved_motif_list(dyn_id,gpcr_pdb,gpcr_aa,j,my_pos,motifs,multiple_chains,chain_name):
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


def obtain_dyn_files(dynfiles,get_framenum=False):
    """Given a list of files related to a dynamic, separates them in structure files and trajectory files."""
    structure_file=""
    structure_name=""
    traj_list=[]
    trajidToFramenum={}
    p=re.compile("(/protwis/sites/files/)(.*)")
    p2=re.compile("[\.\w]*$")
    for e in dynfiles:
        f_id=e.id_files.id
        path=e.id_files.filepath
        myfile=p.search(path).group(2)
        myfile_name=p2.search(path).group()
        if myfile_name.endswith(".pdb"): #, ".ent", ".mmcif", ".cif", ".mcif", ".gro", ".sdf", ".mol2"))
            structure_file=myfile
            structure_file_id=f_id
            structure_name=myfile_name
        elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append([myfile, myfile_name, f_id])
            framenum=e.framenum
            if framenum < 5000:
                strideto=10
            elif framenum < 10000:
                strideto=50
            else:
                strideto=100
            trajidToFramenum[f_id]=[framenum,strideto]
    if get_framenum:
        return (structure_file,structure_file_id,structure_name, traj_list,trajidToFramenum)
    else:
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


def obtain_wholeModel_seg_to_chain(pdb_name):
    whole_seg_to_chain={}
    fpdb=open(pdb_name,'r')
    first=True
    for line in fpdb:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            chain_name=line[21]
            seg_name=line[72:76].strip()
            if first:
                first=False
                seg_name_pre=seg_name
                whole_seg_to_chain[seg_name]=chain_name
            elif (seg_name != seg_name_pre):
                seg_name_pre=seg_name
                whole_seg_to_chain[seg_name]=chain_name
    return whole_seg_to_chain

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

def obtain_rel_dicts(result,numbers,chain_name,current_class,seq_pos,seq_pos_n,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,simplified=False,add_aa=False,seq_pdb=False,all_struc_num=False):
    """Creates a series of dictionaries that will be useful for relating the pdb position with the gpcr number (pos_gnum) or AA (pos_gnum); and the gpcr number for the different classes (in case the user wants to compare)"""
    chain_nm_seq_pos=""
    rs_by_seg={1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: [], 13: [], 14: [], 15: [], 16: [], 17: []}
    if multiple_chains:
        chain_nm_seq_pos=":"+chain_name
    pos_gnum = numbers[current_class]
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            db_pos=pos[1][1]
            if db_pos:
                gnum_or_nth=""
                this_gnum = pos_gnum[db_pos][1]
                if this_gnum: #If exist GPCR num for this position
                    if simplified:
                        (chain_num,bw,gpcrdb)=re.split('\.|x', this_gnum)
                        this_gnum=chain_num+"x"+gpcrdb
                        if add_aa:
                            this_pdb=str(pos[0][1])+"-"+chain_name+"-"+pos_gnum[db_pos][0]
                        else:
                            this_pdb=str(pos[0][1])+"-"+chain_name
                    else:
                        if add_aa:
                            this_pdb=[pos[0][1],chain_name,pos_gnum[db_pos][0]]
                        else:
                            this_pdb=[pos[0][1],chain_name]
                    gpcr_pdb[this_gnum]=this_pdb
                    gpcr_aa[this_gnum]=[pos_gnum[db_pos][0], chain_name]
                    gnum_or_nth=this_gnum
                    rs_by_seg[pos_gnum[db_pos][2]].append(pos[0][1]+chain_nm_seq_pos) #Chain!!
                if type(seq_pdb)==dict:
                    seq_pdb[db_pos]={"pdb":[pos[0][1],chain_name],"gnum":gnum_or_nth}
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
                    if all_struc_num:
                        (chain_num,bw,gpcrdb)=re.split('\.|x',gnum)
                        my_num=chain_num+"x"+gpcrdb
                        (achain_num,abw,agpcrdb)=re.split('\.|x',gnum_altclass)
                        alt_gnum=achain_num+"x"+agpcrdb
                    else:
                        my_num=gnum.split("x")[0]
                        alt_gnum=gnum_altclass.split("x")[0]
                    gnum_classes_rel[class_name][alt_gnum]=my_num
    if type(seq_pdb)==dict:
        return(gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,seq_pos,seq_pos_n,seg_li,seq_pdb)
    else:
        return(gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,seq_pos,seq_pos_n,seg_li)

def translate_all_poslists_to_ourclass_numb(motifs_dict,gnum_classes_rel,cons_pos_dict,current_class,other_classes_ok):
    """Takes all the lists of conserved residues and translates to the GPCR numbering of the class of the protein to visualize the conserved positions of the rest of classes."""
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
                if bw_pos in gnum_classes_rel[gpcr_class]:
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


def obtain_predef_positions_lists(dyn_id,current_poslists,current_motif,other_classes_ok,current_class,cons_pos_dict,motifs,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,chain_name,motifs_dict):
    """Takes the predefined lists of positions/motifs that will appear as predefined views and modifies them so that they match the sequence of our protein."""
    # Obtain list for the predefined views of important positions
    chain_pos = [pos for pos in gpcr_aa if gpcr_aa[pos][1]==chain_name]
    for my_pos in chain_pos:
        for cons_pos_li in current_poslists:
            create_conserved_pos_list(gpcr_pdb, gpcr_aa,0,my_pos,cons_pos_li,multiple_chains,chain_name)
        if current_motif:
            create_conserved_motif_list(dyn_id,gpcr_pdb,gpcr_aa,0,my_pos,current_motif[0],multiple_chains,chain_name)
        for gpcr_class in other_classes_ok:
            for cons_pos_li in cons_pos_dict[gpcr_class]:                     
                create_conserved_pos_list_otherclass(gpcr_pdb,gpcr_aa, 0,my_pos, cons_pos_li, multiple_chains,chain_name,gnum_classes_rel,gpcr_class,current_class)
            alt_class_motif=motifs_dict[gpcr_class]
            if alt_class_motif:
                create_conserved_motif_list_otherclass(gpcr_pdb,gpcr_aa,0,my_pos,alt_class_motif[0],multiple_chains,chain_name)


def find_missing_positions(motifs_dict_def,current_motif,current_poslists,other_classes_ok,current_class,cons_pos_dict,motifs,motname_li,motifs_dict):
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

def sort_by_myorderlist(my_order,word):
    number=my_order.index(word)
    return(number)
def str_len_limit(mystr):
    if len(mystr)>50:
        mystr=mystr[:47]+"..."
    return mystr

def obtain_prot_lig(dyn_id):
    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
    if model.id_protein:
        dprot_li_all=[model.id_protein]
    else:
        dprot_li_all=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
    protlig_all=[]
    for dprot in dprot_li_all:
        if not dprot.receptor_id_protein:
            name=dprot.name
            sel_s= {":%s" % res.chain.upper() for res in DyndbModeledResidues.objects.filter(id_protein=dprot.id)}
            sel=" or ".join(sel_s)
            protlig_all.append({"sel":sel,"name":name})
    return(protlig_all)

def load_heavy_tag(mol_type):
    if mol_type in [ 'Lipid', 'Water']:
        return "load_heavy"
    else:
        return ""


def obtain_compounds(dyn_id):
    """Creates a list of the ligands, ions, lipids, water molecules, etc found at the dynamic.
    Arguments:
    
    dyn_id      Dynamics ID to query.
    
    Returns:
    
    comp_li     list of [component_name,component_residue_name,component_type_str].
    lig_li      list of ligand [component_name,component_residue_name].
    lig_li_s    list of ligands residue names.
    
    """
    molecule_type = dict(DyndbDynamicsComponents.MOLECULE_TYPE)
    
    comp=DyndbModelComponents.objects.filter(id_model__dyndbdynamics=dyn_id)
    comp_dict={}
    lig_li=[]
    lig_li_s=[]
    changed_res=[]
    for c in comp:
        ctype=c.type
        if ctype == 2:
            dc = c.resname
        else:
            dc=DyndbCompound.objects.get(dyndbmolecule__dyndbmodelcomponents=c.id).name #Ligands, water (and ions)
        if (int(dyn_id) in change_lig_name) and (change_lig_name[int(dyn_id)]["orig_resname"]==c.resname):
            changed_res.append(c.resname)
            lname=change_lig_name[int(dyn_id)]["longname"]
            resname=change_lig_name[int(dyn_id)]["resname"]
            comp_dict[lname] = [resname,"Ligand"]
            add_twice=change_lig_name[int(dyn_id)]["add_twice"]
            if (add_twice):
                comp_dict[dc] = [c.resname,add_twice]
            if ctype ==1:
                    lig_li.append([lname,resname])
                    lig_li_s.append(resname)
        else:
            comp_dict[dc] = [c.resname,molecule_type.get(ctype,"Other")]
            if ctype ==1:
                lig_li.append([dc,c.resname])
                lig_li_s.append(c.resname)
    ddc=DyndbDynamicsComponents.objects.filter(id_dynamics=dyn_id) # Lipids and ions
    for c in ddc:
        ctype=c.type
        if ctype == 2:
            dc = c.resname
        else:
            dc=DyndbCompound.objects.get(dyndbmolecule__dyndbdynamicscomponents=c.id).name
        resn=c.resname
        if (int(dyn_id) in change_lig_name) and (change_lig_name[int(dyn_id)]["orig_resname"]==resn):
            if resn not in changed_res:
##############################
                lname=change_lig_name[int(dyn_id)]["longname"]
                resname=change_lig_name[int(dyn_id)]["resname"]
                comp_dict[lname] = [resname,"Ligand"]
                add_twice=change_lig_name[int(dyn_id)]["add_twice"]
                if ctype ==1:
                        lig_li.append([lname,resname])
                        lig_li_s.append(resname)
                if (not add_twice):
                    continue
##############################
        if (dc not in comp_dict) and (c.resname not in changed_res):
            comp_dict[dc]=[resn,molecule_type.get(ctype,"Other")]
        else:
            saved_comp=[ sname for (sname,ctype) in comp_dict.values()]
            if resn not in saved_comp:
                new_resn= comp_dict[dc][0] + " OR " + resn
                comp_dict[dc]= [new_resn ,molecule_type.get(ctype,"Other")]
    comp_li=[[name,sname,ctype] for (name,(sname,ctype)) in comp_dict.items()]
    comp_li=sorted(comp_li, key=lambda x:x[0].lower())
    comp_li=sorted(comp_li, key=lambda x: sort_by_myorderlist(['Ligand','Lipid','Ions','Water','Other'],x[2]))
    comp_li=[[str_len_limit(lname),sname,mtype,load_heavy_tag(mtype)]  for lname,sname,mtype in comp_li]

    lig_li==[[str_len_limit(lname),sname]  for lname,sname in lig_li]

    protlig_all=obtain_prot_lig(dyn_id)
    for protlig in protlig_all:
        protlig_name=protlig["name"]
        protlig_sel=protlig["sel"]
        lig_li.append([protlig_name,protlig_sel])
        lig_li_s.append(protlig_sel)
        comp_li.append([protlig_name,protlig_sel,"Prot_ligand",""])
    return(comp_li,lig_li,lig_li_s)

def findGPCRclass(num_scheme):
    """Uses the numbering scheme name to determine the GPCR family (A, B, C or F). Also sets the values of a dict that will determine the class shown at the template."""
    if num_scheme == "gpcrdba" or num_scheme == "gpcrdb":
        current_class ="A"
        #active_class["A"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbb":
        current_class ="B"
        #active_class["B"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbc":
        current_class ="C"
        #active_class["C"]=["active gpcrbold","in active"]
    elif num_scheme == "gpcrdbf":
        current_class ="F"
        #active_class["F"]=["active gpcrbold","in active"]
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
        return (False,None, "Error loading input files.")    
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


def retrieve_prot_info(dprot,prot_li_gpcr,dprot_li_all_info):
    is_gpcr = False
    gprot= dprot.receptor_id_protein
    if gprot:
        is_gpcr=True
        prot_li_gpcr.append((dprot,gprot))
    dprot_seq=DyndbProteinSequence.objects.get(id_protein=dprot.id).sequence
    dprot_li_all_info.append((dprot.id, dprot.name, is_gpcr, dprot_seq))
    return (prot_li_gpcr,dprot_li_all_info)


def obtain_DyndbProtein_id_list(dyn_id):
    """Given a dynamic id, gets a list of the dyndb_proteins and proteins associated to it that are GPCRs + a list of all proteins (GPCRs or not)"""
    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
    pdbid=model.pdbid
    prot_li_gpcr=[]
    dprot_li_all=[]
    dprot_li_all_info=[]
    if model.id_protein:
        dprot=model.id_protein
        dprot_li_all=[dprot]
        (prot_li_gpcr,dprot_li_all_info)=retrieve_prot_info(dprot,prot_li_gpcr,dprot_li_all_info)
    else:
        dprot_li_all=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
        for dprot in dprot_li_all:
            (prot_li_gpcr,dprot_li_all_info)=retrieve_prot_info(dprot,prot_li_gpcr,dprot_li_all_info)
    return (prot_li_gpcr, dprot_li_all, dprot_li_all_info,pdbid)


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

def pdbChain_to_mdtrajChainid_li(chain,seg_to_chain,struc):
    """
    Takes a chain name (1 letter, as defined in PDB), transforms it to the list of segments in tis chain, 
    and then gives the mdtraj id of each of these segments. Returns them as a list. 
    We need this because mdtraj chain id is actually segment id.
    """
    chain = chain.upper()
    chain_segments=[seg for seg,chainval in seg_to_chain.items() if chainval==chain]
    if chain_segments:
        structable, bonds=struc.topology.to_dataframe()
        chainid_li=[]
        for segname in chain_segments:
                seg_chainid_li=structable.loc[structable['segmentID'] == segname].chainID.unique()
                chainid_li+=list(seg_chainid_li)
        chainid_li=list(set(chainid_li))
        return chainid_li
    else:
        return False


def res_to_atom(seg_to_chain,struc,res, chain, atm):
    chainid_li=pdbChain_to_mdtrajChainid_li(chain,seg_to_chain,struc)
    if chainid_li:
        chains_sel_li=[]
        for chainid in chainid_li:
            chains_sel_li.append("chainid "+ str(chainid))

        chain_sel_str=" or ".join(chains_sel_li)
        atm_index_arr = struc.topology.select("residue "+str(res)+" and ("+chain_sel_str+") and name "+atm)
        if atm_index_arr:
            return (str(atm_index_arr[0]))
        else:
            return False
    else: 
        return False

def distances_Wtraj(dist_str,struc_path,traj_path,strideVal,seg_to_chain,gpcr_chains):
    struc_path = "/protwis/sites/files/"+struc_path
    traj_path = "/protwis/sites/files/"+traj_path
    dist_li=dist_str.split(",")
    #serial_mdInd=relate_atomSerial_mdtrajIndex(struc_path) 
    frames=[]
    axis_lab=[["Frame"]]
    atom_pairs=np.array([]).reshape(0,2)
    small_error=[]
    dist_pair_new=[]
    if len(dist_li) > 20:
        dist_li =dist_li[:20]
        small_error.append("Too much distances to compute. Some have been omitted.")        
    try:
        itertraj=md.iterload(filename=traj_path,chunk=10, top=struc_path , stride = strideVal)
    except Exception:
        return (False,None, "Error loading input files.",True,"")
    count=0
    for itraj in itertraj:
        if count==0:
            for dist_pair in dist_li:
                if ":" in dist_pair:
                    (inf_from,inf_to)=dist_pair.split("-")
                    (resF, chainF, atmF)= inf_from.split(":")
                    (resT, chainT, atmT)= inf_to.split(":")
                    pos_from=res_to_atom(seg_to_chain,itraj,resF, chainF, atmF)
                    pos_to=res_to_atom(seg_to_chain,itraj,resT, chainT, atmT)
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
            dist=np.array([]).reshape((0,len(atom_pairs))) 
        try:
            d=md.compute_distances(itraj, atom_pairs)*10
        except Exception:
            num_atoms=itraj.n_atoms
            error_msg="Atom indices must be between 0 and "+str(num_atoms)
            return (False, None, error_msg,True,"")
        dist=np.append(dist,d,axis=0)
        count +=1
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

def get_fplot_data(dyn_id,traj_list):
    show_fp=False
    int_type_l=['hbonds', 'hb', 'sb', 'pc', 'ps', 'ts', 'vdw', 'wb', 'wb2',"hp"]
    int_name_d={"hbonds":"Wernet Nilsson criteria (MDTraj)",
                "hb":"GetContacts criteria",
                "sb": "Salt bridges",
                "pc": "Pi-cation",
                "ps": "Pi-stacking",
                "ts": "T-stacking",
                "vdw": "Van der Waals",
                "wb": "Water bridges",
                "wb2": "Extended water bridges",
                "hp" : "Hydrophobic"}
    for ind, (trajfile, trajfile_name, f_id) in enumerate(traj_list):
        fpfilename_pre = get_file_name(objecttype="dynamics",fileid=f_id,objectid=dyn_id,ext="json",forceext=True,subtype="trajectory")##[!] Change if function is changed!!!        
        fp_data=[]
        for int_type in int_type_l:
            ###########[!] Change get_file_name() to obtain it automatically
            (pre,post)=fpfilename_pre.split(".")
            fpfilename= "%s_%s.%s" % (pre,int_type,post) 
            ###########
            fpdir = get_precomputed_file_path('flare_plot',int_type ,url=False)
            fppath = path.join(fpdir,fpfilename)
            exists=path.isfile(fppath)
            if exists:
                fpdir_url = get_precomputed_file_path('flare_plot',int_type ,url=True)
                fppath_url = path.join(fpdir_url,fpfilename)
                fp_data.append([int_type,int_name_d[int_type],fppath_url])
                show_fp=True
            else:
                fp_data.append([int_type,int_name_d[int_type],""])
        traj_list[ind].append(fp_data)
    return (traj_list, show_fp)


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

def extract_var_info_file(pdb_vars,gpcr_Gprot,seq_pdb):
    mypath="/protwis/sites/files/Precomputed/muts_vars_info"
    vars_filepath=os.path.join(mypath,"gpcr_vars.json")
    filepath_obj = Path(vars_filepath)
    try:
        filepath_res = filepath_obj.resolve()
        json_file=open(vars_filepath)
        json_str = json_file.read()
        all_vars=pd.io.json.loads(json_str)
        entry_name=gpcr_Gprot.entry_name
        seq_vars_pre=all_vars.get(entry_name)
        if seq_vars_pre:
            seq_vars=seq_vars_pre
        else:
            seq_vars={}
    except FileNotFoundError:
        seq_vars={}
    for seqN,pos_var_info_li in seq_vars.items():
        seqN=int(seqN)
        if seqN in seq_pdb: 
            pdb_pos_l=seq_pdb[seqN]["pdb"]
            gnum=seq_pdb[seqN]["gnum"]
            if gnum:
                (chain_num,bw,gpcrdb)=re.split('\.|x', gnum)
                gnum=chain_num+"x"+gpcrdb
            pdb_pos=pdb_pos_l[0]+":"+pdb_pos_l[1]
            pos_vars={}
            for pos_var_info in pos_var_info_li:
                consequence_nm={"frameshift_variant":"Frameshift","missense_variant":"Missense","stop_gained":"Stop gain","synonymous_variant":"Synonymous"}
                #consequence=pos_var_info["consequence"].replace("_"," ").capitalize()
                consequence=consequence_nm[pos_var_info["consequence"]]
                aafrom=pos_var_info["from"]
                aato=pos_var_info["to"]
                if consequence=="Frameshift":
                    fs_info=aafrom+str(seqN)+aato
                    consequence=consequence+" (%s)"%fs_info
                    aato="FS"
                fromto=aafrom+","+aato
                allele_freq='{:.3e}'.format(pos_var_info["allele_freq"])
                info={"seq_pos":str(seqN),"consequence":consequence,"exac_id":pos_var_info["exac_var_id"],"allele_freq":allele_freq}
                if fromto in pos_vars:
                    pos_vars[fromto].append(info)
                else:
                    pos_vars[fromto]=[info]
            pdb_vars[pdb_pos]={}
            pdb_vars[pdb_pos]["gnum"]=gnum
            pdb_vars[pdb_pos]["vars"]=pos_vars
    return pdb_vars

def extract_mut_info(pdb_muts,gpcr_Gprot,seq_pdb):
    muts=Mutation.objects.filter(protein_id=gpcr_Gprot.id)
    for mut in muts:
        seqN=mut.residue.sequence_number
        if seqN in seq_pdb: 
            pdb_pos_l=seq_pdb[seqN]["pdb"]
            gnum=seq_pdb[seqN]["gnum"]
            if gnum:
                (chain_num,bw,gpcrdb)=re.split('\.|x', gnum)
                gnum=chain_num+"x"+gpcrdb
            pdb_pos=pdb_pos_l[0]+":"+pdb_pos_l[1]
            aafrom=mut.residue.amino_acid
            aato=mut.amino_acid
            experiments=MutationExperiment.objects.filter(mutation=mut.id)
            pdb_muts[pdb_pos]={}
            pdb_muts[pdb_pos]["gnum"]=gnum
            pos_muts={}
            for exp in experiments:
                #exp_fun
                exp_fun_obj=exp.exp_func
                if exp_fun_obj:
                    exp_fun=exp_fun_obj.func
                else:
                    exp_fun=""
                #ligand
                lig_obj=exp.ligand
                if lig_obj:
                    lig=lig_obj.name
                else:
                    lig=""
                #measure
                measure_obj=exp.exp_type
                if measure_obj:
                    measure=measure_obj.type
                else:
                    measure=""
                #Qualitative res
                qual_obj=exp.exp_qual
                if qual_obj:
                    qual=qual_obj.qual 
                else:
                    qual=""
                info={"exp":exp_fun,"fchange":exp.foldchange,"lig":lig,"unit":exp.wt_unit,"measure":measure,"pub_ref":exp.refs.web_link.index,"qual":qual,"seq_pos":str(seqN)}
                fromto=aafrom+","+aato
                if fromto in pos_muts:
                    pos_muts[fromto].append(info)
                else:
                    pos_muts[fromto]=[info]
            
            pdb_muts[pdb_pos]["vars"]=pos_muts
    return pdb_muts

def obtain_tunnel_data(dyn_id,traj_list):
    """
    Returns, for static cluster files (timeless):
        list of files related to each cluster: each element of the list corresponds to a cluster and contains a list of pdb files of said cluster.
    for dynamic cluster files:
        list of files related to each cluster: each element of the list corresponds to a cluster and contains a list of pdb+xtc sets of said cluster.
    The static and dynami lists are ordered so that element 1 of static list corresponds to element 1 of dynamic list. Which corresponds to cluster 1.
    """
    root = settings.MEDIA_ROOT
    tun_path=os.path.join(root,"Precomputed/tunnels/output_files")
    tunnels={}
    traj_clust_rad={}
    clust_rep_avail=False
    for mytraj in traj_list:
        traj_id=mytraj[2]
        traj_tun_path=os.path.join(tun_path,"dyn%s/traj_%s"%(dyn_id,traj_id))
        traj_static=os.path.join(traj_tun_path,"data/clusters_timeless")
        radius_path=os.path.join(traj_tun_path,"data/cluster_radii")
        #traj_dyn=os.path.join(traj_tun_path,"data/clusters_merge")
        traj_rep=os.path.join(traj_tun_path,"data/clusters_rep")
        statics_d={}
        rep_d={}
        if os.path.isdir(traj_static):
            for filenm in os.listdir(traj_static):
                cluster_num=int(filenm.split("_")[2])
                if cluster_num not in statics_d:
                    statics_d[cluster_num]=[]
                statics_d[cluster_num].append(filenm)
        statics=[  statics_d[k] for k in sorted(statics_d.keys())]

        radius_d={}
        clust_rad={}
        if os.path.isdir(radius_path):
            for filenm in os.listdir(radius_path):
                cluster_num=int(filenm.replace(".r","").split("_")[2])
                frame_radius=[]
                with open(os.path.join(radius_path,filenm)) as fp:
                    for line in fp:
                        n=4
                        line=line.rstrip("\n")
                        radius_atoms=[line[i:i+n] for i in range(0, len(line), n)]
                        frame_radius.append(radius_atoms)
                radius_d[cluster_num]=frame_radius
        if os.path.isdir(traj_rep):
            for filenm in os.listdir(traj_rep):
                cluster_num=int(filenm.split("_")[2])
                vals_in_nm=re.findall('[0-9]+',filenm)
                rep_cl=vals_in_nm[0]
                rep_fr=vals_in_nm[1]
                if len(vals_in_nm)>2:
                    tun_strideVal=int(vals_in_nm[2])
                else:
                    tun_strideVal=25
                traj_fr=int(rep_fr)*tun_strideVal
                repfr_rads=radius_d[cluster_num][int(rep_fr)]
                rep_d[cluster_num]=[[filenm],traj_fr]
                clust_rad[cluster_num]=repfr_rads
        clust_rep=[  rep_d[k] for k in sorted(rep_d.keys())]

        if clust_rad:
            traj_clust_rad[traj_id]=clust_rad
        if statics:
            if clust_rep:
                clust_rep_avail=True
                if len(statics)==len(clust_rep):
                    tunnels[traj_id]=list(zip(statics,clust_rep))
                else:
                    tunnels[traj_id]=list(zip(statics,[[]]*len(statics)))
            else:
                tunnels[traj_id]=list(zip(statics,[[]]*len(statics)))
    if tunnels:
        return (tunnels,clust_rep_avail,traj_clust_rad)
    else:
        return (False,False,traj_clust_rad)
#        dyn_clu_pairs_d={}
#        if os.path.isdir(traj_dyn):
#            dyn_cluster_files=os.listdir(traj_dyn)
#            file_combos=itertools.combinations(dyn_cluster_files,2)
#            for (a,b) in file_combos:
#                if a=="info.txt" or b=="info.txt":
#                    continue
#                num_a=int(re.split('_|\.',a)[-2])
#                num_b=int(re.split('_|\.',b)[-2])
#                if num_a==num_b:
#                    if ".pdb" in a:
#                        struc_dt=a;
#                        traj_dt=b;
#                    else:
#                        struc_dt=b;
#                        traj_dt=a;
#                    dyn_clu_pairs_d[num_a]=(struc_dt,traj_dt)
#            dyn_tun_info_file=os.path.join(traj_dyn,"info.txt")
#            if not dyntunnel_stride:
#                if os.path.isfile(dyn_tun_info_file):
#                    with open(dyn_tun_info_file) as f:
#                        stridestr=f.read()
#                    dyntunnel_stride=int( stridestr.split(" ")[1])
#        dyn_clu_pairs=[ dyn_clu_pairs_d[k] for k in sorted(dyn_clu_pairs_d.keys())]

def obtain_ed_align_matrix(dyn_id,traj_list):
#    if dyn_id=="4":
#        r_angl=[0.09766122750587349, -0.058302789675214316, 0.1389009096961483]
#        trans=[  9.21,74.12,-80.74]
#        return(r_angl,trans)
#    else:
    root = settings.MEDIA_ROOT
    EDmap_path=os.path.join(root,"Precomputed/ED_map")
    ed_mats={}
    for mytraj in traj_list:
        traj_id=mytraj[2]
        matrix_file="transfmatrix_%s_%s.data" % (dyn_id,traj_id)
        matrix_filepath=os.path.join(EDmap_path,matrix_file)
        exists=os.path.isfile(matrix_filepath)
        if exists:
            with open(matrix_filepath, 'rb') as filehandle:  
                (r_angl,trans) = pickle.load(filehandle)
            ed_mats[traj_id]=(list(r_angl),list(trans))
    if ed_mats:
        return json.dumps(ed_mats)
    else:
        return False

"""This function takes the dyn_id as argument and returns 2 dictionaries with the traj_id as key and the filepath as value. If the map does not exist, the key gets the value: None (string)"""
def obtain_volmaps(dyn_id):

    root = settings.MEDIA_ROOT
    occupancy_path = os.path.join(root, "Precomputed/WaterMaps")    #change this if the watermaps are in another folder! 
    # density_path = os.path.join(root, "Precomputed/WaterMaps")

    trajfiles = DyndbFiles.objects.annotate(dynid=F('dyndbfilesdynamics__id_dynamics'))
    trajfiles = trajfiles.filter(dynid=dyn_id, id_file_types__is_trajectory=True)
    trajfiles = trajfiles.annotate(file_id=F('dyndbfilesdynamics__id_files_id'))
    trajfiles = trajfiles.values('file_id')

    occupancy_files = {}
    # density_files = {}

    for i in trajfiles:
        traj_id = i['file_id']
        if i['file_id'] not in occupancy_files:
            occupancy_file = os.path.join(occupancy_path, '%s_occupancy_%s.dx' %(traj_id, dyn_id))
            if os.path.isfile(occupancy_file):
                occupancy_files[traj_id] = occupancy_file
            else:
                #occupancy_files[traj_id] = None
                continue

        # if i['file_id'] not in density_files:
        #     density_file = os.path.join(density_path, '%s_density_%s.dx' %(traj_id, dyn_id))
        #     if os.path.isfile(density_file):
        #         density_files[traj_id] = density_file
        #     else:
        #         #density_files[traj_id] = None
        #         continue

    return (occupancy_files)

@ensure_csrf_cookie
def index(request, dyn_id, sel_pos=False,selthresh=False):
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
            if request.session.get('main_strc_data', False):
                session_data=request.session["main_strc_data"][dyn_id]
                seg_to_chain=session_data["seg_to_chain"]
                if request.session.get('rmsd_data', False):
                    rmsd_data_all=request.session['rmsd_data']
                    if dyn_id in rmsd_data_all:
                        rmsd_data=rmsd_data_all[dyn_id]
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
                else:
                    new_rmsd_id=1
                    rmsd_dict={}
                
                if len(rmsd_dict) < 15:
                    (success,data_fin, errors)=compute_rmsd(struc_p,traj_p,traj_frame_rg,ref_frame,ref_traj_p,traj_sel,int(strideVal),seg_to_chain)
                    if success:
                        data_frame=data_fin
                        data_store=copy.deepcopy(data_frame)
                        data_store[0].insert(1,"Time")
                        data_time=[data_store[0][1:]]
                        for row in data_store[1:]:
                            frame=row[0]
                            time=(frame+1)*delta
                            row.insert(1,time)
                            d_time=row[1:]
                            data_time.append(d_time)  
                        p=re.compile("\w*\.\w*$")
                        struc_filename=p.search(struc_p).group(0)
                        traj_filename=p.search(traj_p).group(0)
                        rtraj_filename=p.search(ref_traj_p).group(0)
                        rmsd_dict["rmsd_"+str(new_rmsd_id)]=(data_store,struc_filename,traj_filename,traj_frame_rg,ref_frame,rtraj_filename,traj_sel,strideVal)
                        
                        rmsd_data_dyn={"rmsd_dict":rmsd_dict, "new_rmsd_id":new_rmsd_id+1}
                        if request.session.get('rmsd_data', False):
                            rmsd_data_all=request.session["rmsd_data"]
                        else:
                            rmsd_data_all={}
                        rmsd_data_all[dyn_id]= rmsd_data_dyn
                        request.session['rmsd_data']=rmsd_data_all

                        data_rmsd = {"result_t":data_time,"result_f":data_frame,"rmsd_id":"rmsd_"+str(new_rmsd_id),"success": success, "msg":errors , "strided":strideVal}
                    else: 
                        data_rmsd = {"result":data_fin,"rmsd_id":None,"success": success, "msg":errors , "strided":strideVal}
                else:
                    data_rmsd = {"result":None,"rmsd_id":None,"success": False, "msg":"Please, remove some RMSD results to obtain new ones." , "strided":strideVal}
            else:
                data_rmsd = {"result":None,"rmsd_id":None,"success": False, "msg":"Session error." , "strided":strideVal}
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
            if request.session.get('main_strc_data', False):
                session_data=request.session["main_strc_data"][dyn_id]
                #num_prots=session_data["prot_num"]
                #serial_mdInd=session_data["serial_mdInd"]
                gpcr_chains=session_data["gpcr_chains"]
                seg_to_chain=session_data["seg_to_chain"]
                if request.session.get('dist_data', False):
                    dist_data_all=request.session['dist_data']
                    if dyn_id in dist_data_all:
                        dist_data=dist_data_all[dyn_id]
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
                else:
                    new_id=1
                    dist_dict={}
            else:
                data = {"result":None,"dist_id":None,"success": False, "msg":"Session error.", "strided":strideVal, "isEmpty":True, "dist_pair_new":""}
            if len(dist_dict) < 15:
                
                (success,data_fin, msg, isEmpty,dist_pair_new)=distances_Wtraj(dist_ids,dist_struc_p,dist_traj_p,int(strideVal),seg_to_chain,gpcr_chains)
                if success and not isEmpty:
                    data_frame=data_fin
                    data_store=copy.deepcopy(data_frame)
                    data_store[0].insert(1,"Time")
                    data_time=[data_store[0][1:]]
                    for row in data_store[1:]:
                        frame=row[0]
                        time=(frame+1)*delta
                        row.insert(1,time)
                        d_time=row[1:]
                        data_time.append(d_time)                 
                    p=re.compile("\w*\.\w*$")
                    struc_filename=p.search(dist_struc_p).group(0)
                    traj_filename=p.search(dist_traj_p).group(0)
                    dist_dict["dist_"+str(new_id)]=(data_store,struc_filename,traj_filename,strideVal)
                    dist_data_dyn={"dist_dict":dist_dict, "new_id":new_id+1 ,"traj_filename":traj_filename, "struc_filename":struc_filename}
                    if request.session.get('dist_data', False):
                        dist_data_all=request.session['dist_data']
                    else:
                        dist_data_all={}
                    dist_data_all[dyn_id]=dist_data_dyn
                    request.session['dist_data']=dist_data_all               
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
                session_data=request.session["main_strc_data"][dyn_id]
                num_prots=session_data["prot_num"]
                serial_mdInd=session_data["serial_mdInd"]
                gpcr_chains=session_data["gpcr_chains"]
                seg_to_chain=session_data["seg_to_chain"]
                
                if request.session.get('int_data', False):
                    int_data_all=request.session['int_data']
                    if dyn_id in int_data_all:
                        int_data=int_data_all[dyn_id]
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
                else:
                    new_int_id=1
                    int_info={}
                
                if len(int_info) < 15:
                    # remove chain_names
                    (success,int_dict,errors)=compute_interaction(res_li,int_struc_p,int_traj_p,num_prots,float(thresh),serial_mdInd,gpcr_chains,dist_scheme, int(strideVal),seg_to_chain)
                    int_id = None
                    if success:
                        p=re.compile("\w*\.\w*$")
                        struc_fileint=p.search(int_traj_p).group(0)
                        traj_fileint=p.search(int_struc_p).group(0)
                        int_id="int_"+str(new_int_id)
                        int_info[int_id]=(int_dict,thresh,traj_fileint,struc_fileint,dist_scheme, strideVal)
                        int_data_dyn={"int_info":int_info, "new_int_id":new_int_id+1 }
                        if request.session.get('int_data', False):
                            int_data_all=request.session["int_data"]
                        else:
                            int_data_all={}
                        int_data_all[dyn_id]=int_data_dyn
                        request.session['int_data']=int_data_all
                    data = {"result":int_dict,"success": success, "e_msg":errors, "int_id":int_id ,"strided":strideVal}
                else:
                    data = {"result":None,"success": False, "e_msg":"Please, remove some interaction results to obtain new ones.","int_id":None ,"strided":strideVal}
            else:
                data = {"result":None,"success": False, "e_msg":"Session error.","int_id":None ,"strided":strideVal}
            return HttpResponse(json.dumps(data), content_type='view/'+dyn_id)
        elif request.POST.get("warning_type"):
            warning_type=request.POST.get("warning_type")
            if request.session.get('warning_load', False):
                warning_load=request.session["warning_load"]
            else:
                warning_load={"trajload":True,"heavy":True}
            warning_load[warning_type]=False;
            request.session['warning_load']=warning_load
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    if len(dynfiles) ==0:
        error="Structure file not found."
        return render(request, 'view/index_error.html', {"error":error} )
    else:
        if request.session.get('warning_load', False):
            warning_load=request.session["warning_load"]
        else:
            warning_load={"trajload":True,"heavy":True}
##### ---- NATHALIE CODE HERE -------
# retrieving the filepaths from the database. put traj_id as key and vol/occ map as value. Then pass this variable through context variable.
        watermaps = False
        occupancy = obtain_volmaps(dyn_id)   #the variables contain dictionaries with the occupancy and density maps filepaths. CHANGE THIS! only occupancy 
        if occupancy:
            watermaps = True 
#### --------------------------------
#### ---- PHarmacophores ------------
        pharma_jsonpath = "/protwis/sites/files/Precomputed/pharmacophores/dyn"+dyn_id+'/pharmaco_itypes.json'
        if os.path.exists(pharma_jsonpath):
            has_pharmacophores = True
            pharma_json = json_dict(pharma_jsonpath)
        else: 
            has_pharmacophores = False
            pharma_json = {}
#### --------------------------------
        (comp_li,lig_li,lig_li_s)=obtain_compounds(dyn_id)
        exception_light=""
        has_exception_light=change_lig_name.get(int(dyn_id))
        if has_exception_light:
            exception_light=has_exception_light["resname"]

        heavy_comp_sel=" or ".join({e[1] for e in comp_li if e[3]})
        light_sel_s={e[1] for e in comp_li if e[2]=='Ligand' or e[2]=='Ions'}
        light_sel_s.add("protein")
        light_sel=" or ".join(light_sel_s)
        (structure_file,structure_file_id,structure_name, traj_list,trajidToFramenum)=obtain_dyn_files(dynfiles,True)
        first_strideval=trajidToFramenum[traj_list[0][2]][1]
        #structure_file="Dynamics/with_prot_lig_multchains_gpcrs.pdb"########################### [!] REMOVE
        #structure_name="with_prot_lig_multchains_gpcrs.pdb" ################################### [!] REMOVE
        pdb_name = "/protwis/sites/files/"+structure_file
        chain_name_li=obtain_prot_chains(pdb_name)
        #traj_list=sorted(traj_list,key=lambda x: x[2])
        #(traj_list,fpdir)=get_fplot_path(dyn_id,traj_list)
        (traj_list, show_fp)=get_fplot_data(dyn_id,traj_list)
        ed_mats=obtain_ed_align_matrix(dyn_id,traj_list)
        ############
        (tunnels,clust_rep_avail,traj_clust_rad)=obtain_tunnel_data(dyn_id,traj_list)
        #dyn_clu_merge,dyntunnel_stride
        #print("\n\n\n\n")
        ############
        if str(dyn_id)=="197":
            i=1
            for traj_e in traj_list:
                traj_e.append("Step %s"%i)
                i+=1
        presel_pos=""
        bind_domain=""
        if sel_pos:
            cra_path="/protwis/sites/files/Precomputed/crossreceptor_analysis_files"
            resli_file_path=path.join(cra_path,"ligres_int.csv")
            resli_file_pathobj = Path(resli_file_path)
            if resli_file_pathobj.is_file():
                df = pd.read_csv(resli_file_path,index_col=[0,1])
                thresh_li=set(df.index.get_level_values("Threshold"))
                selthresh=float(selthresh)
                if selthresh in thresh_li:
                    bind_domain_li=df.loc[selthresh].columns.values                
                    bind_domain=",".join(bind_domain_li)
                    presel_pos=sel_pos
            #Checking if call corresponds to contplots call (containts a selpos of format 12x50_2x40)
            contplots_pat = re.compile("\d+x\d+")
            if re.match(contplots_pat,sel_pos):
                presel_pos=sel_pos
                bind_domain = "none"

        if len(chain_name_li) > 0:
            multiple_chains=False
            chain_str=""
            if len(chain_name_li) > 1:
                multiple_chains=True
            (prot_li_gpcr, dprot_li_all,dprot_li_all_info,pdbid)=obtain_DyndbProtein_id_list(dyn_id)
            model_res=DyndbModeledResidues.objects.filter(id_model__dyndbdynamics__id=dyn_id)
            seg_to_chain={mr.segid : mr.chain for mr in model_res}
            session_data_dyn={"chain_name_li":chain_name_li,"prot_num":len(dprot_li_all),"serial_mdInd":relate_atomSerial_mdtrajIndex(pdb_name),"gpcr_chains":False,"seg_to_chain":seg_to_chain}
            if request.session.get('main_strc_data', False):
                session_data_all=request.session["main_strc_data"]
            else:
                session_data_all={}
            session_data_all[dyn_id]= session_data_dyn
            request.session['main_strc_data']=session_data_all
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
                request.session['main_strc_data'][dyn_id]["gpcr_chains"]=gpcr_chains
                all_gpcrs_info=[]
                seg_li_all={}
                gpcr_pdb_all={}
                gpcr_id_name={}
                pdb_muts={}
                pdb_vars={}
                TMsel_all={}
                i=1
                while i <=8:
                    TMsel_all[i]={}
                    i+=1
                for gpcr_DprotGprot in prot_li_gpcr:
                    gpcr_Dprot=gpcr_DprotGprot[0]
                    gpcr_Gprot=gpcr_DprotGprot[1]
                    dprot_id=gpcr_Dprot.id
                    dprot_name=gpcr_Dprot.name
                    gen_num_res=obtain_gen_numbering(dyn_id, gpcr_Dprot,gpcr_Gprot)  #warning!! the problem is here
                    if len(gen_num_res) > 2:
                        (numbers, num_scheme, db_seq, current_class) = gen_num_res
                        current_class=findGPCRclass(num_scheme)
                        active_class={"A":["",""],"B":["",""],"C":["",""],"F":["",""]}
                        active_class[current_class]=["active gpcrbold","in active"]
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
                            seq_pdb={}
                            (dprot_chain_li, dprot_seq) = dprot_chains[dprot_id] 
                            cons_pos_dict_mod=copy.deepcopy(cons_pos_dict)
                            motifs_mod=copy.deepcopy(motifs)
                            motname_li=["PIF","DRY","NPxxY","Sodium binding site","Ionic lock","Rotamer toggle switch"]
                            motifs_dict_mod=copy.deepcopy(motifs_dict)
                            for chain_name, result in dprot_chain_li:
                                (gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,dprot_seq,seq_pos_index,seg_li,seq_pdb)=obtain_rel_dicts(result,numbers,chain_name,current_class,dprot_seq,seq_pos_index, gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,seq_pdb=seq_pdb)
                                (show_class,current_poslists,current_motif,other_classes_ok)=translate_all_poslists_to_ourclass_numb(motifs_dict_mod,gnum_classes_rel,cons_pos_dict_mod,current_class,other_classes_ok)
                                obtain_predef_positions_lists(dyn_id,current_poslists,current_motif,other_classes_ok,current_class,cons_pos_dict_mod, motifs_mod,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,chain_name,motifs_dict_mod)
                            prot_seq_pos[dprot_id]=(dprot_name, dprot_seq)
                            motifs_dict_def={"A":[],"B":[],"C":[],"F":[]}
                            #print("\n\n\n")
                            find_missing_positions(motifs_dict_def,current_motif,current_poslists,other_classes_ok,current_class,cons_pos_dict_mod,motifs_mod,motname_li,motifs_dict_mod)
                            #gpcr_pdb_js=json.dumps(gpcr_pdb)
                            #########
                            all_gpcrs_info.append((dprot_id, dprot_name, show_class, active_class, copy.deepcopy(cons_pos_dict_mod) , motifs_dict_def))
                            gpcr_pdb_all[dprot_id]=(gpcr_pdb)
                            gpcr_id_name[dprot_id]=dprot_name
                            seg_li_all[dprot_id]=seg_li #[!] For the moment I don't use this, I consider only 1 GPCR
                            #Obtain var and mut data
                            pdb_muts=extract_mut_info(pdb_muts,gpcr_Gprot,seq_pdb)
                            pdb_vars=extract_var_info_file(pdb_vars,gpcr_Gprot,seq_pdb)
                            #TM extremes
                            last_tm=False
                            for pos in sorted(gpcr_pdb.keys()):
                                pos=pos.split("x")[0]
                                tm=int(pos.split(".")[0])
                                if tm in TMsel_all:
                                    if tm != last_tm:
                                        TMsel_all[tm][dprot_id]={"first":pos}
                                        last_tm=tm
                                    TMsel_all[tm][dprot_id]["last"]=pos

                if all_gpcrs_info:
                    TMsel_all_ok={}
                    for tm,extdict in TMsel_all.items():
                        prefix="TM"
                        if tm ==8:
                            prefix="H"
                        tmname=prefix+str(tm)
                        for gpcrid,posdict in extdict.items():
                            extdict[gpcrid]=posdict["first"]+"-"+posdict["last"]
                        TMsel_all_ok[tmname]=json.dumps(extdict)
                    #request.session['gpcr_pdb']= gpcr_pdb #[!] For the moment I consider only 1 GPCR
                    cons_pos_all_info=generate_cons_pos_all_info(copy.deepcopy(cons_pos_dict),all_gpcrs_info)
                    motifs_all_info=generate_motifs_all_info(all_gpcrs_info)
                    #Fill blanks

                    for gclass,consinfo in cons_pos_all_info[0].items():
                         for consli in consinfo:
                             for cons in consli:
                                 if cons[1]=="":
                                     cons[1]=cons[0]
                    if dyn_id=="4":
                        pdbid="4N6H"
                    #traj_list.append(['Dynamics/dyn20/tmp_trj_0_20.dcd', 'tmp_trj_0_20.dcd', 10170, '10140_trj_4_hbonds_rep.json'])#[!] REMOVE! only for Flare Plot tests
                    #traj_list.append(['Dynamics/10140_trj_4.dcd', '10140_trj_4.dcd', 10140, '10140_trj_4_hbonds_OK.json']);
                    

                    if int(dyn_id) ==29:
                        traj_list=[traj_list[0]]
                    context={
                        "dyn_id":dyn_id,
                        "mdsrv_url":mdsrv_url,
                        "structure_file":structure_file, 
                        "structure_name":structure_name, 
                        "structure_file_id":structure_file_id,
                        "traj_list":traj_list,
                        "first_strideval":first_strideval,
                        "trajidToFramenum":json.dumps(trajidToFramenum),
                        "compounds" : comp_li,
                        "heavy_comp_sel":heavy_comp_sel,
                        "light_sel":json.dumps(light_sel),
                        "exception_light":exception_light,
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
                        "show_fp" : show_fp,
                        "delta":delta,
                        "bind_domain":bind_domain,
                        "presel_pos":presel_pos,
                        "pdbid":pdbid,
                        "pdb_muts":json.dumps(pdb_muts),
                        "pdb_vars":json.dumps(pdb_vars),
                        "ed_mats":ed_mats,
                        "tunnels":tunnels,
                        "tunnels_dump":json.dumps(tunnels),
                        "tun_clust_rep_avail":clust_rep_avail,
                        "traj_clust_rad":json.dumps(traj_clust_rad),
                        "test":"HI THERE",
                        "TMsel_all":sorted(TMsel_all_ok.items(), key=lambda x:int(x[0][-1])),
                        "warning_load":json.dumps(warning_load),
                        "watermaps" : watermaps,
                        "occupancy" : json.dumps(occupancy),
                        "has_pharmacophores" : has_pharmacophores,
                        "pharma_json" : json.dumps(pharma_json)
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
                        "first_strideval":first_strideval,
                        "trajidToFramenum":json.dumps(trajidToFramenum),
                        "compounds" : comp_li,
                        "heavy_comp_sel":heavy_comp_sel,
                        "light_sel":json.dumps(light_sel),
                        "exception_light":exception_light,
                        "ligands": lig_li,
                        "ligands_short": ",".join(lig_li_s),
                        "other_prots":other_prots,
                        "chains" : chain_str,
                        "prot_seq_pos": list(prot_seq_pos.values()),
                        "gpcr_pdb": "no",
                        "all_chains": ",".join(all_chains),
                        "all_prot_names" : ", ".join(all_prot_names),
                        "show_fp" : show_fp,
                        "seg_li":"",
                        "delta":delta,
                        "bind_domain":bind_domain,
                        "presel_pos":presel_pos,
                        "pdbid":pdbid,
                        "ed_mats":ed_mats,
                        "tunnels":tunnels,
                        "tunnels_dump":json.dumps(tunnels),
                        "tun_clust_rep_avail":clust_rep_avail,
                        "traj_clust_rad":json.dumps(traj_clust_rad),
                        "warning_load":json.dumps(warning_load),
                        "watermaps" : watermaps,
                        "occupancy" : json.dumps(occupancy),
                        "has_pharmacophores" : has_pharmacophores,
                        "pharma_json" : json.dumps(pharma_json)                        
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
                        "first_strideval":first_strideval,
                        "trajidToFramenum":json.dumps(trajidToFramenum),
                        "compounds" : comp_li,
                        "heavy_comp_sel":heavy_comp_sel,
                        "light_sel":json.dumps(light_sel),
                        "exception_light":exception_light,
                        "ligands": lig_li,
                        "ligands_short": ",".join(lig_li_s),
                        "other_prots":other_prots,
                        "chains" : chain_str,            
                        "gpcr_pdb": "no",
                        "all_prot_names" : ", ".join(all_prot_names),
                        "show_fp" : show_fp,
                        "seg_li":"",
                        "delta":delta,
                        "bind_domain":bind_domain,
                        "presel_pos":presel_pos,
                        "pdbid":pdbid,
                        "ed_mats":ed_mats,
                        "tunnels":tunnels,
                        "tunnels_dump":json.dumps(tunnels),
                        "tun_clust_rep_avail":clust_rep_avail,
                        "traj_clust_rad":json.dumps(traj_clust_rad),
                        "warning_load":json.dumps(warning_load),
                        "watermaps" : watermaps,
                        "occupancy" : json.dumps(occupancy),
                        "has_pharmacophores" : has_pharmacophores,
                        "pharma_json" : json.dumps(pharma_json)
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
                    "first_strideval":first_strideval,
                    "trajidToFramenum":json.dumps(trajidToFramenum),
                    "compounds" : comp_li,
                    "heavy_comp_sel":heavy_comp_sel,
                    "light_sel":json.dumps(light_sel),
                    "exception_light":exception_light,
                    "ligands": lig_li,
                    "other_prots":[],
                    "ligands_short": ",".join(lig_li_s),                  
                    "chains" : "",            
                    "gpcr_pdb": "no",
                    "show_fp" : show_fp,
                    "seg_li":"",
                    "delta":delta,
                    "bind_domain":bind_domain,
                    "presel_pos":presel_pos,
                    "ed_mats":ed_mats,
                    "tunnels":tunnels,
                    "tunnels_dump":json.dumps(tunnels),
                    "tun_clust_rep_avail":clust_rep_avail,
                    "traj_clust_rad":json.dumps(traj_clust_rad),
                    "warning_load":json.dumps(warning_load),
                    "watermaps" : watermaps,
                    "occupancy" : json.dumps(occupancy),
                    "has_pharmacophores" : has_pharmacophores,
                    "pharma_json" : json.dumps(pharma_json)
                    }
            return render(request, 'view/index.html', context)





#########################

def compute_rmsd(rmsdStr,rmsdTraj,traj_frame_rg,ref_frame,rmsdRefTraj,traj_sel,strideVal,seg_to_chain):
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
        itertraj=md.iterload(filename=traj_path,chunk=10, skip =fr_from ,top=struc_path, stride =strideVal)
    except Exception:
        return (False,None, ["Error loading input files."])
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
            if " and " in traj_sel:
                (resname,resseqpos)=traj_sel.split(" and ")
                lig_sel="resname '"+resname+"' and residue "+resseqpos
                try:
                    selection=itraj.topology.select(lig_sel)
                except Exception:
                    error_msg="Ligand not found."
                    return (False,None, error_msg)

            elif ":" in traj_sel:
                try:
                    mytop=itraj.topology
                    structable, bonds=mytop.to_dataframe()
                    reschain_li=traj_sel.split(" or ")
                    reschain_li=[chain.replace(":","") for chain in reschain_li]
                    selection=select_prot_chains(structable,seg_to_chain,mytop,reschain_li)
                except Exception:
                    error_msg="Ligand not found."
                    return (False,None, error_msg)
            else:
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


def download_hb_sb(request, dyn_id, bond_type, traj_path):
    sbhb_save_error=False
    if request.session.get(bond_type, False):
        alldata_alldyn=request.session[bond_type]
        if dyn_id in alldata_alldyn:
            alldata=alldata_alldyn[dyn_id]
            int_res=alldata["results"]
            analysis_data=alldata["analysis_data"]
            bonds_li=[]
            for don_res,acc_li in int_res.items():
                for acc_info in acc_li:
                    acc_res=acc_info[0]
                    freq=acc_info[1]
                    atom0=acc_info[2]
                    atom1=acc_info[3]
                    chain0=acc_info[4]
                    chain1=acc_info[5]
                    pair_info=[don_res,acc_res,freq,atom0,atom1,chain0,chain1]
                    bonds_li.append(pair_info)
            int_res_ok=sorted(bonds_li,key=lambda x:float(x[2]),reverse=True)
            return_error=True
            filename_dict={"hbp":"hbonds_prot.csv" , "hbo":"hbonds_other.csv" , "sb":"saltbridges.csv"}
            dyn_id=analysis_data["dyn_id"]
            filename= "dyn%s_%s" % ( dyn_id , filename_dict[bond_type])
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
            writer = csv.writer(response)

            writer.writerow(["#Dyn ID: "+dyn_id])
            traj_p=analysis_data["traj_path"]
            traj_nm=traj_p.split("/")[-1]
            writer.writerow(["#Trajectory: "+traj_nm])
            frame_from=int(analysis_data["frameFrom"])
            frame_to=int(analysis_data["frameTo"])
            if frame_from != 0 or frame_to!= 100000000000000000000:
                if frame_to==100000000000000000000:
                    frame_to="last"
                writer.writerow(["#Frames: %s - %s"%(frame_from,frame_to)])
            else:
                writer.writerow(["#Frames: all"])
            writer.writerow(["#Threshold: %s%%" % analysis_data["cutoff"]])
            if bond_type=="hbp" or bond_type=="hbo":
                writer.writerow(["#Only side chains: %s" % analysis_data["no_backbone"]])
                writer.writerow(["#Filter out neighbour residues: %s" % analysis_data["no_neighbours"]])
                writer.writerow(["Donor residue","Donor chain","Donor atom id","Acceptor residue","Acceptor chain","Acceptor atom id","Frequency (%)"])
                for row in int_res_ok:
                    (dres,ares,freq,datom,aatom,dchain,achain)=row
                    writer.writerow([dres,dchain,datom,ares,achain,aatom,freq])

            elif bond_type=="sb":
                writer.writerow(["Residue 1","Chain 1","Atom id 1","Residue 2","Chain 2","Atom id 2","Frequency (%)"])
                for row in int_res_ok:
                    (dres,ares,freq,datom,aatom,dchain,achain)=row
                    writer.writerow([dres,dchain,int(float(datom)),ares,achain,int(float(aatom)),freq])
            else:
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="x.csv"'
                writer = csv.writer(response)
                writer.writerow(["Data not found."])
        else:
            sbhb_save_error=True
    else:
        sbhb_save_error=True
    if sbhb_save_error:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow(["Data not found."])
    return response

def download_dist(request, dyn_id, dist_id):
    save_error_dist=False
    error_txt=" "
    if request.session.get('dist_data', False):
        dist_data_s_all=request.session['dist_data']
        if dyn_id in dist_data_s_all:
            dist_data_s=dist_data_s_all[dyn_id]
            dist_dict=dist_data_s["dist_dict"]
            if dist_id in dist_dict:
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
                save_error_dist=True
                error_txt="Session data expired. Please re-load the page and try again."
        else:
            save_error_dist=True
    else:
        save_error_dist=True
    if save_error_dist:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([error_txt])
    return response
    
def download_int(request,dyn_id, int_id):
    int_save_error=False
    error_txt=" "
    if request.session.get('int_data', False):
        int_data_s_all=request.session['int_data']
        if dyn_id in int_data_s_all:
            int_data_s=int_data_s_all[dyn_id]
            int_info=int_data_s["int_info"]
            if int_id in int_info:
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
                error_txt="Session data expired. Please re-load the page and try again."
                int_save_error=True
        else:
            int_save_error=True
    else:
        int_save_error=True
    if int_save_error:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([error_txt])
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


def select_prot_chains(structable,seg_to_chain,mytop,chains):
    chains_sel_li=[]
    chainid_li=[]
    for chain in chains:
        chain_segments=[seg for seg,chainval in seg_to_chain.items() if chainval==chain]
        for segname in chain_segments:
            seg_chainid_li=structable.loc[structable['segmentID'] == segname].chainID.unique()#In princliple should be a list of 1 value but just in case I iterate
            chainid_li+=list(seg_chainid_li)
    chainid_li=list(set(chainid_li))
    for chainid in chainid_li:
        chains_sel_li.append("chainid "+ str(chainid))
    chains_sel="protein and ("+" or ".join(chains_sel_li)+")"
    mysel=mytop.select(chains_sel)
    return mysel


def compute_interaction(res_li,struc_p,traj_p,num_prots,thresh,serial_mdInd,gpcr_chains,dist_scheme,strideVal,seg_to_chain):

    struc_path = "/protwis/sites/files/"+struc_p
    traj_path = "/protwis/sites/files/"+traj_p
    itertraj=md.iterload(filename=traj_path,chunk=10, top=struc_path, stride=strideVal)
    first=True 
    structable=False
    lig_multiple_res=False
    try:
        for itraj in itertraj:
            if first:
                mytop=itraj.topology
                all_lig_res=[]
                fin_dict={}
                for res in res_li:
                    if " and " in res:
                        (resname,resseqpos)=res.split(" and ")
                        lig_sel=mytop.select("resname '"+resname+"' and residue "+resseqpos)
                        fin_dict[res]=[]
                    elif ":" in res:
                        structable, bonds=mytop.to_dataframe()
                        reschain_li=res.split(" or ")
                        reschain_li=[chain.replace(":","") for chain in reschain_li]
                        lig_sel=select_prot_chains(structable,seg_to_chain,mytop,reschain_li)
                        fin_dict["Lig"]=[]
                    else:
                        fin_dict[res]=[]
                        lig_sel=mytop.select("resname '"+res+"'")
                    if len(lig_sel)>0:
                        lig_res=[residue.index for residue in itraj.atom_slice(lig_sel).topology.residues]
                        for myres in lig_res:
                            all_lig_res.append(myres)
                if len(all_lig_res)==0:
                    return (False,None, "Error with ligand selection.")
                elif len(all_lig_res)>1 :
                    lig_multiple_res=True
                if gpcr_chains:
                    if type(structable) == bool:
                        structable, bonds=mytop.to_dataframe()
                    gpcr_sel=select_prot_chains(structable,seg_to_chain,mytop,gpcr_chains)

                else:
                    gpcr_sel=mytop.select("protein") 
                gpcr_res=[residue.index for residue in itraj.atom_slice(gpcr_sel).topology.residues]
                pairs = list(itertools.product(gpcr_res, all_lig_res))
                
                (dists,res_p)=md.compute_contacts(itraj, contacts=pairs, scheme=dist_scheme)
                alldists=dists
                allres_p=res_p
                first=False
            else:
                (dists,res_p)=md.compute_contacts(itraj, contacts=pairs, scheme=dist_scheme)
                alldists=np.append(alldists,dists,axis=0)
    except Exception:
        return (False,None, "Error loading input files.")
    contact_freq={}
    for pair in allres_p:
        mykey=tuple(pair)
        if lig_multiple_res:
            mykey=(mykey[0],"Lig")
        contact_freq[mykey]=0
    for frame_dist in alldists:
        i=0
        ligint_in_frame=set()
        while i < len(frame_dist):
            pair=allres_p[i]
            mykey=tuple(pair)
            if lig_multiple_res:
                mykey=(mykey[0],"Lig")
                if mykey in ligint_in_frame:
                    i+=1
                    continue
                else:
                    ligint_in_frame.add(mykey)
            if frame_dist[i]<(thresh/10):
                contact_freq[mykey]+=1
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
    for pair in sorted(contact_freq, key=lambda x: contact_freq[x], reverse=True):
        freq=contact_freq[pair]
        res_ind=pair[0]
        lig_ind=pair[1]
        res_topo=mytop.residue(res_ind)
        res_pdb=res_topo.resSeq
        res_name=res_topo.name
        res_chain=seg_to_chain[res_topo.segment_id]
        if lig_ind=="Lig":
            lig_nm=lig_ind
        else:
            lig_topo=mytop.residue(lig_ind)
            lig_nm=lig_topo.name
        if lig_nm in fin_dict:
            fin_dict[lig_nm].append((res_pdb,res_chain,res_name,("%.2f" % freq)))
        else:
            lig_topo=mytop.residue(lig_ind)
            lig_pdb=lig_topo.resSeq
            ligres_sel=lig_nm+" and "+str(lig_pdb)
            if (ligres_sel in fin_dict):
                fin_dict[ligres_sel].append((res_pdb,res_chain,res_name,("%.2f" % freq)))
            else: 
                return (False,None, "Error when parsing results (2).")
    return(True,fin_dict,None)

def download_rmsd(request, dyn_id,rmsd_id):
    save_error=False
    error_txt=" "
    if request.session.get('rmsd_data', False):
        rmsd_data_s_all=request.session['rmsd_data']
        if dyn_id in rmsd_data_s_all:
            rmsd_data_s=rmsd_data_s_all[dyn_id]
            rmsd_dict=rmsd_data_s["rmsd_dict"]
            if rmsd_id in rmsd_dict:
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
                save_error=True
                error_txt="Session data expired. Please re-load the page and try again."
        else:
            save_error=True
    else:
        save_error=True
    if save_error:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="x.csv"'
        writer = csv.writer(response)
        writer.writerow([error_txt])
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
        dyn_id=arrays[5]
        struc_path = "/protwis/sites/files/"+arrays[4]
        whole_seg_to_chain=obtain_wholeModel_seg_to_chain(struc_path)
        traj_shortpath=arrays[3]
        traj_path = "/protwis/sites/files/"+traj_shortpath
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
            chain0=whole_seg_to_chain[t.topology.atom(keys[0]).segment_id]
            chain1=whole_seg_to_chain[t.topology.atom(keys[2]).segment_id]
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
        analysis_data={"frameFrom":start,"frameTo":end,"cutoff":percentage_cutoff,"traj_path":traj_shortpath,"dyn_id":dyn_id,"no_backbone":backbone,"no_neighbours":neighbours}
        hbp_data_dyn={"results":hbonds_residue,"analysis_data":analysis_data}
        if request.session.get('hbp', False):
            hbp_data_all=request.session["hbp"]
        else:
            hbp_data_all={}
        hbp_data_all[dyn_id]=hbp_data_dyn
        request.session["hbp"]=hbp_data_all
        hbo_data_dyn={"results":hbonds_residue_notprotein,"analysis_data":analysis_data}
        if request.session.get('hbo', False):
            hbo_data_all=request.session["hbo"]
        else:
            hbo_data_all={}
        hbo_data_all[dyn_id]=hbo_data_dyn
        request.session["hbo"]=hbo_data_all
        return HttpResponse(data, content_type='application/json')


def saltbridges(request):#
    if request.method == 'POST':

        arrays=request.POST.getlist('frames[]')
        dyn_id=arrays[5]
        struc_path = "/protwis/sites/files/"+arrays[4]
        traj_shortpath=arrays[3]
        traj_path = "/protwis/sites/files/"+traj_shortpath
        whole_seg_to_chain=obtain_wholeModel_seg_to_chain(struc_path);
        label = lambda hbond : '%s--%s' % (mytop.atom(hbond[0]), mytop.atom(hbond[2]))
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
                mytop=t.topology
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
        bridge_dic=dict() # To separate into prot - prot and prot-others: create two separate dicts instead o bidge_dict using
                            # t.topology.atom(atomnum).residue.is_protein 
                            # where atomnum is bond[2] or bond [3]
        for bond in full_results['salt_bridges']:
            labelbond=bond[0]
            labelbond=labelbond.replace(' ','')
            labelbond=labelbond.split('--')
            donor=labelbond[0]
            acceptor=labelbond[1]
            acceptor_res=acceptor[:acceptor.rfind('-')]
            donor_res=donor[:donor.rfind('-')]
            chain0=whole_seg_to_chain[mytop.atom(int(bond[2])).segment_id]
            chain1=whole_seg_to_chain[mytop.atom(int(bond[3])).segment_id]
            if donor_res in bridge_dic:
                bridge_dic[donor_res].append([acceptor_res,bond[1],str(bond[2]),str(bond[3]),chain0,chain1])
            elif acceptor_res in bridge_dic:
                bridge_dic[acceptor_res].append([donor_res,bond[1],str(bond[2]),str(bond[3]),chain0,chain1])
            else:
               bridge_dic[donor_res]=[[acceptor_res,bond[1],str(bond[2]),str(bond[3]),chain0,chain1]]

#        if False: #warning, to implement in future, download csv with results
#            struc_path=struc_path[:-4]
#            csvfile= open(struc_path+'saltbridges.csv','w',newline='')
#            writer = csv.writer(csvfile,delimiter=' ',
#                                quotechar=',', quoting=csv.QUOTE_MINIMAL)
#
#            header=['Residue1', 'Residue2', 'Frequency', 'Atom_index', 'Atom_index_2']
#            writer.writerow(header)
#
#            for keys in bridge_dic:
#                for minilist in bridge_dic[keys]:
#                    rowlist=[keys]+minilist
#                    writer.writerow(rowlist)
#                writer.writerow(['','','','',''])

        full_results['salt_bridges']=bridge_dic
        analysis_data={"frameFrom":start,"frameTo":end,"cutoff":percentage_threshold,"traj_path":traj_shortpath,"dyn_id":dyn_id}
        sb_data_dyn={"results":bridge_dic,"analysis_data":analysis_data}
        if request.session.get('sb', False):
            sb_data_all=request.session["sb"]
        else:
            sb_data_all={}
        sb_data_all[dyn_id]=sb_data_dyn
        request.session["sb"]=sb_data_all

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
        sasa_data_all=request.session['sasa_data']
        if dyn_id in sasa_data_all:
            sasa_data=sasa_data_all[dyn_id]
            sasa_dict=sasa_data["sasa_dict"]
            new_sasa_id=sasa_data["new_sasa_id"]+1
        else:
            new_sasa_id=1
            sasa_dict={}
    else:
        new_sasa_id=1
        sasa_dict={}
            
    sasa_dict["sasa_"+str(new_sasa_id)]=sasares
    sasa_data_dyn={"sasa_dict":sasa_dict, "new_sasa_id":new_sasa_id}
    if request.session.get('sasa_data', False):
        sasa_data_all=request.session["sasa_data"]
    else:
        sasa_data_all={}
    sasa_data_all[dyn_id]=sasa_data_dyn
    request.session['sasa_data']=sasa_data_all
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
        t=trajectory
        trajectory=trajectory.atom_slice(atom_indices, inplace=False)
        atomindexes_prot=[atom.index for atom in trajectory.topology.atoms if atom.residue.is_protein]
        trajprot=trajectory.superpose(trajectory,0,atom_indices=atomindexes_prot) #works!
        trajprot=trajprot
        mintop=np.array([0,0,0])
        i=0
        for frame in range(len(trajprot)):
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

def trim_path_for_mdsrv(path):
    p=re.compile("(/protwis/sites/files/)(.*)")
    myfile=p.search(path).group(2)
    return myfile

def quickload(request,dyn_id,trajfile_id):
    #DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_trajectory=True)
    mdsrv_url=obtain_domain_url(request)
    modelfile=DyndbFiles.objects.get(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_model=True)
    trajfile=DyndbFiles.objects.get(id=trajfile_id)
    model_filepath=trim_path_for_mdsrv(modelfile.filepath)
    traj_filepath=trim_path_for_mdsrv(trajfile.filepath)
    context={
        "dyn_id":dyn_id,
        "struc_file":model_filepath,
        "traj_file":traj_filepath,
        "mdsrv_url":mdsrv_url
            }
    return render(request, 'view/quickload.html', context)

def quickloadall(request):
    #DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_trajectory=True)
    mdsrv_url=obtain_domain_url(request)
    dynobj=DyndbDynamics.objects.all()
    dynfiledata = dynobj.annotate(dyn_id=F('id'))
    #dynfiledata = dynfiledata.annotate(is_pub=F('is_published'))
    #dynfiledata = dynfiledata.annotate(sub_id=F('submission_id__id'))
    dynfiledata = dynfiledata.annotate(file_path=F('dyndbfilesdynamics__id_files__filepath'))
    #dynfiledata = dynfiledata.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
    dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynfiledata = dynfiledata.annotate(file_ext=F('dyndbfilesdynamics__id_files__id_file_types__extension'))
    dynfiledata = dynfiledata.values("dyn_id","file_path","file_is_traj","file_ext")

    dyn_dict = {}
    for dyn in dynfiledata:
        dyn_id=dyn["dyn_id"]
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["traj"]=[]
            dyn_dict[dyn_id]["pdb"]=[]
        file_info=dyn["file_path"]
        if not file_info:
            continue
        file_short=file_info[file_info.index("Dynamics"):]
        if dyn["file_is_traj"]:
            dyn_dict[dyn_id]["traj"].append(file_short)
        elif dyn["file_ext"]=="pdb":
            dyn_dict[dyn_id]["pdb"].append(file_short)

    del dynfiledata
    filesli=[[d["pdb"][0],d["traj"]] for d in dyn_dict.values() if d["pdb"]]
    context={
        "mdsrv_url":mdsrv_url,
        "filesli":json.dumps(filesli)
            }
    return render(request, 'view/quickloadall.html', context)


def metatest(request):
    mdsrv_url=obtain_domain_url(request)

    context={
        "mdsrv_url":mdsrv_url,
            }
    return render(request, 'view/metatest.html', context)
    
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

