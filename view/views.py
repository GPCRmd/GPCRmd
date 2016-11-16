from django.shortcuts import render
from django.http import HttpResponse
from dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents
from view.assign_generic_numbers_from_DB import obtain_gen_numbering
from dynadb.pipe4_6_0 import *
from view.data import *
import re
import json
from Bio.PDB import *
from Bio import PDB                                                     

def find_range_from_cons_pos(my_pos, gpcr_pdb):
    """Given a position in GPCR generic numbering, returns the range that consist in the residue number at the same +1. This is because NGL selections requires a range, not a single number."""
    (pos_range_l,chain)=gpcr_pdb[my_pos]
    pos_range_r=int()
    pos_range=""
    n=1
    pdb_positions_all = gpcr_pdb.values()
    pdb_positions_inchain = [p[0] for p in pdb_positions_all if p[1]==chain]
    while pos_range=="":
        if pos_range_l + n in pdb_positions_inchain:
            pos_range = (str(pos_range_l)+"-"+str(pos_range_l +n))
            break
        else:
            n+=1
        if n > len(pdb_positions_inchain):  
            return False
    return pos_range
 
def create_conserved_pos_list(gpcr_pdb,gpcr_aa, i,my_pos, cons_pos_li, add,multiple_chains,chain_name):
    """Given the GPCR num of a position of our seq, checks if it's one of the conserved residues, and if it has been mutated"""
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

def find_missing_pos(cons_pos_li):
    """Given a list of conserved positions, where the positions found at our sequence are indicated, modifies the list to indicate the positions not found."""
    for e in cons_pos_li:
        if e[2]=="":
            i=cons_pos_li.index(e)
            cons_pos_li[i][2]="None"

def find_missing_pos_in_motif(motifs, motname_li):
    """Given a list of positions in conserved motifs, where the positions found at our sequence are indicated, creates a list of motifs where the positions found at our sequence, are indicated, showing if they have the conserves AA or another one."""
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

def obtain_dyn_files(paths_list):
    """Given a list of files related to a dynamic, separates them in structure files and trajectory files."""
    structure_file=""
    structure_name=""
    traj_list=[]
    p=re.compile("(/protwis/sites/files/)(.*)")
    p2=re.compile("[\.\w]*$")
    for path in paths_list:
        myfile=p.search(path).group(2)
        myfile_name=p2.search(path).group()
        if myfile_name.endswith(".pdb"): #, ".ent", ".mmcif", ".cif", ".mcif", ".gro", ".sdf", ".mol2"))
            structure_file=myfile
            structure_name=myfile_name
        elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append((myfile, myfile_name))    
    return (structure_file,structure_name, traj_list)

def obtain_prot_chains(pdb_name):
    """Given a structure file, returns a list of protein chains"""
    pdb = PDBParser(PERMISSIVE=True, QUIET=True).get_structure("ref", pdb_name)
    chain_name_li=[]
    for chain in pdb.get_chains(): 
        a=chain.get_residues()
        ex=list(a)[0]
        if PDB.is_aa(ex): 
            chain_name_li.append(chain.id)
    return chain_name_li

def obtain_predef_positions_lists(result,numbers,mol_sw,cons_classA,motifs,gpcr_pdb,gpcr_aa,multiple_chains,chain_name):
    """Takes the predefined lists of positions/motifs that will appear as predefined views and modifies them so that they match the sequence of our protein."""
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            db_pos=pos[1][1]
            if numbers[db_pos][1]: #If exist GPCR num for this position
                gpcr_pdb[numbers[db_pos][1]]=[pos[0][2],chain_name]
                gpcr_aa[numbers[db_pos][1]]=[numbers[db_pos][0], chain_name]

    # Obtain list for the predefined views of important positions
    chain_pos = [pos for pos in gpcr_aa if gpcr_aa[pos][1]==chain_name]
    for my_pos in chain_pos:
        i=id_start_pos=0
        create_conserved_pos_list(gpcr_pdb, gpcr_aa,i,my_pos,mol_sw, id_start_pos,multiple_chains,chain_name)
        id_start_pos2=len(mol_sw)
        create_conserved_pos_list(gpcr_pdb, gpcr_aa,i,my_pos,cons_classA, id_start_pos2,multiple_chains,chain_name)
        j=0
        create_conserved_motif_list(gpcr_pdb,gpcr_aa,j,my_pos,motifs,multiple_chains,chain_name)

def find_missing_positions(mol_sw,cons_classA,motifs):
    "Completes the conserved position lists to indicate the positions that are missing in our prot"
    find_missing_pos(mol_sw)
    find_missing_pos(cons_classA)
    motifs_def=find_missing_pos_in_motif(motifs, motname_li)
    return motifs_def

def obtain_compounds(dyn_id):
    """Creates a list of the ligands, ions, lipids, water molecules, etc found at the dynamic"""
    comp=DyndbModelComponents.objects.filter(id_model__dyndbdynamics=dyn_id)
    comp_dict={}
    for c in comp:
        dc=DyndbCompound.objects.get(dyndbmolecule__dyndbmodelcomponents=c.id).name #Ligands, water (and ions)
        comp_dict[dc] = c.resname
    ddc=DyndbDynamicsComponents.objects.filter(id_dynamics=dyn_id) # Lipids and ions
    for c in ddc:
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
    return(comp_li)

def index(request):
    dyn_id =1 #EXAMPLE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    if len(dynfiles) ==0:
        error="Structure file not found."
        return render(request, 'view/index_error.html', {"error":error} )
    else:
        comp_li=obtain_compounds(dyn_id)
        paths_list=[e.id_files.filepath for e in dynfiles]
        (structure_file,structure_name, traj_list)=obtain_dyn_files(paths_list)
        # structure_file="Dynamics/test.pdb"########################### REMOVE
        # structure_name="test.pdb" ################################### REMOVE
        pdb_name = "/protwis/sites/files/"+structure_file   
        chain_name_li=obtain_prot_chains(pdb_name)
        multiple_chains=False
        chain_str=""
        if len(chain_name_li) > 1:
            multiple_chains=True
            chain_str="(Chains: "+", ".join(chain_name_li)+")"        
        if len(obtain_gen_numbering(dyn_id))==3:
            (numbers, num_scheme, db_seq) = obtain_gen_numbering(dyn_id) 
            gpcr_n_ex=""
            if "gpcr" in num_scheme: 
                for e in numbers:
                    gpcr_n_ex= numbers[e][1]
                    if gpcr_n_ex: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                        break
                if "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                    gpcr_pdb={}
                    gpcr_aa={}
                    for chain_name in chain_name_li:
                        checkpdb_res=checkpdb(pdb_name, segid="",start=-1,stop=99999, chain=chain_name)
                        if isinstance(checkpdb_res, tuple):
                            tablepdb,pdb_sequence,hexflag=checkpdb_res
                            result=matchpdbfa(db_seq,pdb_sequence, tablepdb, hexflag)
                            if isinstance(result, list):
                                obtain_predef_positions_lists(result,numbers,mol_sw,cons_classA,motifs,gpcr_pdb,gpcr_aa,multiple_chains,chain_name)                                              
                    motifs_def=find_missing_positions(mol_sw,cons_classA,motifs)
                    gpcr_pdb_js=json.dumps(gpcr_pdb) 
                    context={
                        "structure_file":structure_file, 
                        "structure_name":structure_name , 
                        "traj_list":traj_list, 
                        "compounds" : comp_li,
                        "mol_sw" : mol_sw,
                        "cons_classA" : cons_classA,
                        "motifs_def" : motifs_def,
                        "chains" : chain_str,
                        "gpcr_pdb": gpcr_pdb_js}
                    return render(request, 'view/index.html', context)
       #Cannot use gpcr numbering:
        context={
            "structure_file":structure_file, 
            "structure_name":structure_name , 
            "traj_list":traj_list, 
            "compounds" : comp_li,
            "chains" : chain_str,            
            "gpcr_pdb": "no"}
        return render(request, 'view/index.html', context)

