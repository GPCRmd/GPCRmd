import re
import os
import numpy as np
import argparse as ap
from json import loads, dump
import traceback
import MDAnalysis as mda
from multiprocessing import Pool
import multiprocessing as mp

###########
##Functions
###########

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = loads(json_str)
    return json_data

def merge_dynamic_files(dynfiles, outfile):
    """
    Merge the dynamic contacts tabular files of a simulation into a single one, adding them as new frames
    """

    print("merging dynamic files")
    lines = []
    accum_frames = 0
    # Parse all dynamic files apported
    for dynfile in dynfiles:
        
        # Open each dynamics file and iterate througt lines
        with open(dynfile, "r") as f:
            for line in f: 
                # Omit headers
                if line[0] == '#':
                    continue
                # in our new line, we will modify the frame number taking into account the accumulated files 
                # (e.g.: 122 frame of 2nd file is now 2622)
                tabline = line.split("\t")
                frame = int(tabline[0])+accum_frames
                tabline[0] = str(frame)
                lines.append("\t".join(tabline))

        # Update accumulated frames per file
        accum_frames = frame+1

    # header for new file
    header = "# total_frames:%s beg:0 end:%s stride:1 interaction_types:hp,sb,pc,ps,ts,vdw,hb" % (accum_frames+1, accum_frames )
    lines.insert(0,header)

    with open(outfile, "w") as file:
        # Iterate through the list and write each string to the file
        for line in lines:
            file.write(line)

def obtain_universal_gennum(GPCRdb_gennums, dyn_gennum, gclass):
    """
    Obtain multi-class GPCR generic numbering, using alignments previously made by GPCRdb
    """
    dyn_gennum_u = {}
    for (gennum,pos) in dyn_gennum.items():
        if gennum in GPCRdb_gennums[gclass]:
            gennum_u = GPCRdb_gennums[gclass][gennum]
            dyn_gennum_u[gennum_u] = pos
    return(dyn_gennum_u)


def create_labelfile(gennum_dict, outfile, strucfile, gpcr_class, peplig_chain=False, lig_resname=False):
    """
    Create a labelfile for getcontacts frequencies of this dynamic
    """

    # Skip if already exist
    if os.path.exists(outfile):
        print("labelfile already exists. Skipping...")
        # return

    # Open label file
    out = open(outfile,'w')

    # Iterate throught dictionary of generic numbering, and write its contents into labelfile
    for (gennum,pos_sel) in gennum_dict.items():
        gennum_r = gennum.replace('.','_') # Getcontacts doesnt like dots 
        (resid,chainid,resname) = pos_sel.split('-')
        out.write("%s:%s:%s\t%s\n"%(chainid,resname,resid,gennum_r))

    # If peptide ligand, parse its residues and assign them the 'Ligand' label 
    if peplig_chain or lig_resname:
        u = mda.Universe(strucfile)

        # Peptide ligands. All residues will have the "Ligand" label
        if peplig_chain:
            peplig_atoms = u.select_atoms(f"chainid {peplig_chain}")
            for residue in peplig_atoms.residues:
                out.write("%s:%s:%d\tLigand\n"%(peplig_chain,residue.resname,residue.resid))

        # small molecule ligands
        if lig_resname:
            smalmol_atoms = u.select_atoms(f"chainid {lig_resname}")
            for residue in smalmol_atoms.residues:
                out.write("%s:%s:%d\tLigand\n"%(residue.chainID,residue.resname,residue.resid))


    out.close()

def run_line(com, fake_arg):
    """
    For paralelization purpouses
    """
    os.system(com)

#######
## Main
#######

# Arguments
parser = ap.ArgumentParser(description="this calculates interaction frequencies for given simulation")
parser.add_argument(
    '--dynids',
    dest='dynids',
    type=str,
    nargs='*',
    action='store',
    default=[],
    help='Dynamics IDs to compute.'
)
parser.add_argument(
    '--overwrite',
    dest='overwrite',
    action='store_true',
    default=False,
    help='Compute interactions even if it has previoulsy been done already'
)
parser.add_argument(
    '--cores',
    dest='cores',
    action='store',
    default=4,
    help='number of cores to use in get_dynamic_contacts'
)
args = parser.parse_args()

# Set paths
overwrite = args.overwrite
cores = int(args.cores)
dynids = args.dynids
get_contacts_path = "/users/gpcr/daranda/doctorat/getcontacts/"
# filespath = "/GPCRmd/media/files/"DEBUGGG!!!
filespath = "/home/daranda/files_kasparov/"
precompath = filespath+"Precomputed/"
resultspath = precompath + "gpcr_gprot/"
os.makedirs(resultspath, exist_ok=True)
interta_path = resultspath+"inter_tables/"
os.makedirs(interta_path, exist_ok=True)

#Reading GPCRnomenclatures Json: the json with the equivalences between different GPCR scales (Wooten, Ballesteros, Pi, ...)
GPCRdb_gennums = json_dict(precompath + "/get_contacts_files/GPCRnomenclatures_dict.json")

# Load Database information from compl_info.json file
db_dict = json_dict(precompath + "compl_info2.json")

# If required, keep only dynids specified as input option
db_dict_all = db_dict.copy()
if len(dynids):
    db_dict = { k : v for (k,v) in db_dict.items() if k.replace('dyn','') in dynids}

#Interaction multi-types dictionary: we need an all-hydrogenbonds table, as well as an all-waterbridges
multi_itypes = {
    'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
    'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
    'wb2':'wb2 lwb2',
}
itypes = ['hb','wb','wb2',"vdw","all","sb", "pc", "ts", "ps", "hp", "hbbb", "hbsb", "hbss"]

##############################
# Part 1: calculate interaction frequencies for each simulation
##############################
dyncounter = 0
dyntotal = len(db_dict.keys())
for (dyn_id,entry) in db_dict.items():

    try: 
        dyncounter += 1
        print("Computing dictionary for  %s (%d/%d) ...."%(dyn_id, dyncounter, dyntotal))
    
        # Skip if dynamic has no GPCR or GProt
        gprot_chain = entry['gprot_chain']
        gpcr_chain = entry['gpcr_chain']
        if (not gprot_chain) or (not gpcr_chain):
            print("Dynamic with id %s has no GPCR/Gprot. Skipping..."%(dyn_id))
            continue 
        
        # Info from db_dict
        lig_resname = entry['lig_sname']
        peplig_chain = entry['peplig']

        # Generic numberings
        gclass = entry['class']
        gpcr_gennum = entry['gpcr_pdb']
        gprot_gennum = entry['gprot_pdb']

        gpcr_gennum_u = obtain_universal_gennum(GPCRdb_gennums, gpcr_gennum, gclass) 
        gennum_dict = {**gpcr_gennum_u, **gprot_gennum}

        # Paths to simulation files
        strucpath = filespath+entry['struc_f']
        trajpaths = [ filespath+traj for traj in entry['traj_f'] ]

        # Filepaths to results
        resultspath_dyn = resultspath+dyn_id+'/'
        os.makedirs(resultspath_dyn,exist_ok=True)
    
        # Create labelfile 
        labelfile = resultspath_dyn+'labelfile.tsv'
        create_labelfile(gennum_dict, labelfile, strucpath, db_dict, peplig_chain, lig_resname)

        # For every trajectory of this simulation, calculate all dynamic interactions between GPCR and G protein alpha unit
        # using GetContacts
        inter_file_merged = str("%s%s_inter.tsv" % (resultspath_dyn, dyn_id))
        inter_files = []
        rep=0
        for trajfile in trajpaths: 
            rep +=1
            inter_file = "%s%s-%d_inter.tsv" % (resultspath_dyn, dyn_id, rep)
            if (os.path.exists(inter_file) or os.path.exists(inter_file_merged)) and not overwrite:
                print("Dynamic interactions for %s-%d already computed. Skipping..."%(dyn_id,rep))
            else:
                os.system("source /opt/gpcrmdenv/bin/activate; python %sget_dynamic_contacts.py         \
                --topology %s  \
                --trajectory %s       \
                --cores %s \
                --sele \"chain %s\"  \
                --sele2 \"chain %s\"  \
                --itypes all    \
                --output %s"  % (get_contacts_path, strucpath, trajfile, cores, gpcr_chain, gprot_chain, inter_file)
                )
            inter_files.append(inter_file)

        # Merge all individual trajectory files    
        if not os.path.exists(inter_file_merged) or overwrite:
            merge_dynamic_files(inter_files, inter_file_merged)

        # Frequencies output folder
        freqpath = resultspath_dyn+"frequency_tables/"
        os.makedirs(freqpath,exist_ok=True)

        # Calculate interaction frequencies
        pool = mp.Pool(cores)
        for itype in itypes:

            #Omit already computed frequencies
            freqfile = "%sfrequency_tables/%s.tsv" % (resultspath_dyn, itype)
            if os.path.exists(freqfile):
                pass
                # continue
            print("computing %s frequencies for %s" % (itype,dyn_id))

            # If itype corresponds to one of the "multi-itypes" kind
            if itype in multi_itypes:
                itype = multi_itypes[itype]

            # Calculate interaction frequencies
            comand_line = "source /opt/gpcrmdenv/bin/activate;python %sget_contact_frequencies.py \
                --input_files %s \
                --itypes %s \
                --label_file %s \
                --output %s" % (get_contacts_path, inter_file_merged, itype, labelfile, freqfile)
            x = pool.apply_async(run_line, args=(comand_line,False))
            # print(x.get()) # Print errors when activated, but also removes paralelization

        pool.close()
        pool.join() 

    except Exception as e:
        print("Could not process %s because of %s" % (dyn_id,e))
        print(traceback.format_exc())

#####################
# Part 2: Get an all-simulations interaction table by itype
#####################

pool = mp.Pool(cores)
for itype in itypes:

    try: 
        #Creating list of frequency files for calculating fingerprint
        infreqs = ""
        dynid_headers = ""
        for dyn_id in db_dict_all:
            freqpath = resultspath+dyn_id+'/frequency_tables/%s.tsv'%itype
            if os.path.exists(freqpath):
                dynid_headers += "\t"+dyn_id 
                infreqs += " "+freqpath
                #TODO: do something with multi-trajectory submissions

        #Getting fingerprint info by type
        table_output = str("%s%s.tsv" % (interta_path, itype))
        comand_line = "/opt/gpcrmdenv/bin/activate;python %sget_contact_fingerprints.py \
                    --input_frequencies %s \
                    --frequency_cutoff 0.00 \
                    --column_headers %s \
                    --table_output %s" % (get_contacts_path, infreqs, dynid_headers, table_output)
        x = pool.apply_async(run_line, args=(comand_line,False))
        # print(x.get()) # Print errors when activated, but also removes paralelization

    except Exception as e:
        print("Interaction type %s table failed because of %s" % (itype,e))
        print(traceback.format_exc())

pool.close()
pool.join() 
