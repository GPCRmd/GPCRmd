from django.shortcuts import render
from django.http import HttpResponse
from dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbModelComponents, DyndbCompound, DyndbDynamicsComponents,DyndbDynamics
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
                              
def create_conserved_pos_list(gpcr_pdb,gpcr_aa, i,my_pos, cons_pos_li, multiple_chains,chain_name):
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
                cons_pos_li[i][1]=cons_pos_bw_ourclass +  current_class.lower()
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

def obtain_rel_dicts(result,numbers,chain_name,current_class):
    """Creates a series of dictionaries that will be useful for relating the pdb position with the gpcr number (pos_gnum) or AA (pos_gnum); and the gpcr number for the different classes (in case the user wants to compare)"""
    gpcr_pdb={}
    gpcr_aa={}
    gnum_classes_rel={}
    seq_pos=[]
    pos_gnum = numbers[current_class]
    for pos in result:
        if pos[0] != "-": #Consider only num in the pdb
            db_pos=pos[1][1]
            gnum_or_nth=""
            this_gnum = pos_gnum[db_pos][1]
            if this_gnum: #If exist GPCR num for this position
                gpcr_pdb[this_gnum]=[pos[0][2],chain_name]
                gpcr_aa[this_gnum]=[pos_gnum[db_pos][0], chain_name]
                gnum_or_nth=this_gnum
            seq_pos.append([pos[0][0],pos[0][2],gnum_or_nth]);
    other_classes=list({"A","B","C","F"} - set(current_class))
    other_classes_ok=[]
    for name in other_classes:
        if numbers[name]:
            other_classes_ok.append(name)
            gnum_classes_rel[name]={}
    for pos, (res,gnum) in pos_gnum.items():
        if gnum:
            for class_name in other_classes_ok:
                gnum_altclass=numbers[class_name][pos][1]
                if gnum_altclass:
                    gnum_classes_rel[class_name][gnum_altclass.split("x")[0]]=gnum.split("x")[0]
    return(gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,seq_pos)

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
                current_bw_pos=gnum_classes_rel[gpcr_class][bw_pos_ok]
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

def findGPCRclass(num_scheme):
    """Uses the numbering scheme name to determine the GPCR family (A, B, C or F). Also sets the values of a dict that will determine the class shown at the template."""
    if num_scheme == "gpcrdba" or num_scheme == "gpcrdb":
        current_class ="A"
        active_class["A"]=["active","in active"]
    elif num_scheme == "gpcrdbb":
        current_class ="B"
        active_class["B"]=["active","in active"]
    elif num_scheme == "gpcrdbc":
        current_class ="C"
        active_class["C"]=["active","in active"]
    elif num_scheme == "gpcrdbf":
        current_class ="F"
        active_class["F"]=["active","in active"]
    return current_class

def index(request, dyn_id):
    #dyn_id =1 #EXAMPLE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
        gen_num_res=obtain_gen_numbering(dyn_id)
        if isinstance(gen_num_res, tuple):
            (numbers, num_scheme, db_seq, current_class) = gen_num_res
            current_class=findGPCRclass(num_scheme)
            # current_class="B" ######## !!!!!!!!!!!!!!!!!!!!!!!!! REMOVE THIIIS!!!!!!!!!!!!!!!!!!!
            gpcr_n_ex=""
            for pos_gnum in numbers[current_class].values():
                if pos_gnum[1]: #We take the 1st instance of gpcr num as example, and check in which format it is (n.nnxnn or nxnn)
                    gpcr_n_ex=pos_gnum[1]
                    break
            if "." in gpcr_n_ex: #For the moment we only accept n.nnxnn format
                for chain_name in chain_name_li:
                    checkpdb_res=checkpdb(pdb_name, segid="",start=-1,stop=99999, chain=chain_name)
                    if isinstance(checkpdb_res, tuple):
                        tablepdb,pdb_sequence,hexflag=checkpdb_res
                        result=matchpdbfa(db_seq,pdb_sequence, tablepdb, hexflag)
                        if isinstance(result, list):
                            (gpcr_pdb,gpcr_aa,gnum_classes_rel,other_classes_ok,seq_pos)=obtain_rel_dicts(result,numbers,chain_name,current_class)
                            (show_class,current_poslists,current_motif,other_classes_ok)=traduce_all_poslists_to_ourclass_numb(motifs_dict,gnum_classes_rel,cons_pos_dict,current_class,other_classes_ok)
                            obtain_predef_positions_lists(current_poslists,current_motif,other_classes_ok,current_class,cons_pos_dict, motifs,gpcr_pdb,gpcr_aa,gnum_classes_rel,multiple_chains,chain_name)
                motifs_dict_def={"A":[],"B":[],"C":[],"F":[]}
                find_missing_positions(motifs_dict_def,current_motif,current_poslists,other_classes_ok,current_class,cons_pos_dict,motifs)
                # for gpcr_class in cons_pos_dict:
                #     print(gpcr_class)
                #     for cons_pos_li in cons_pos_dict[gpcr_class]:
                #         print(cons_pos_li)
                #     print("\n")


                gpcr_pdb_js=json.dumps(gpcr_pdb) 
                context={
                    "structure_file":structure_file, 
                    "structure_name":structure_name , 
                    "traj_list":traj_list, 
                    "compounds" : comp_li,
                    "show_class" : show_class,
                    "mol_sw" : cons_pos_dict["A"][1],
                    "cons_classA" : cons_pos_dict["A"][0],
                    "motifs_def" : motifs_dict_def["A"],
                    "cons_classB" : cons_pos_dict["B"][0],
                    "cons_classC" : cons_pos_dict["C"][0],
                    "cons_classF" : cons_pos_dict["F"][0],
                    "gpcr_class" : current_class,
                    "active_class" : active_class,
                    "chains" : chain_str,
                    "gpcr_pdb": gpcr_pdb_js,
                    "seq_pos": seq_pos}
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

#PROVA:
def pre_viewer(request):
    all_dyn=DyndbDynamics.objects.all()
    dyn_ids=[dyn.id for dyn in all_dyn]
    dyn_ids.sort()
    context={
        "dyn_ids" : dyn_ids
    }
    return render(request, 'view/pre_viewer.html', context)