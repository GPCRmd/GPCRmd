import re
import os
import glob
import numpy as np
import argparse as ap
import pandas as pd
from random import sample
from json import loads, dump
from sys import stdout
from shutil import copyfile,copyfileobj
import time
import MDAnalysis as md

from django.conf import settings

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = loads(json_str)
    return json_data

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def read_ligandfile(ligfile):
    """
    Read information contained in ligandfile, and create a VMD selection line for this ligand. It will be used in --ligand and --sel from 
    get_dynamic_interactions.py
    """
    # Omit if file is empty
    ligand_sel = ""
    lig_list = set()
    if os.path.getsize(ligfile) == 0:
        return ("","",[])
    # Else open and parse the file
    ligfile = open(ligfile, 'r')
    first_line = True
    for line in ligfile:
        line = line.rstrip()
        lig_list.add(line)
        linetab = line.split(":")
        if first_line: 
            ligand_sel += str("( chain %s and resname %s and resid %s)" % (linetab[0],linetab[1],linetab[2]))
            first_line = False
            lig_res = linetab[1]
        else:
            ligand_sel += str(" or (chain %s and resname %s and resid %s)" % (linetab[0],linetab[1],linetab[2]))
    ligfile.close()
    ligand_apendsel = " or %s" % (ligand_sel)
    ligand_option = "--ligand \"%s\" " % (ligand_sel)
    return(ligand_apendsel, ligand_option, lig_list)

def create_labelfile(outname, outfolder = "./", ligand = None):
    """
    The idea of this function is to create a label file (get_contacts format) with the ballesteros GPCR id's as labels for a certain model.
    The optional argument "ligand" corresponds to a file with the PDB identifier of the molecule ligand and its label. Example
    NUMBER CHAIN RESIDUE Ligand
    """

    # If labelfile already exists, skip
    outfile_name = outfolder + outname + "_labels.tsv"
    if os.path.exists(outfile_name):
        print('labelfile already exists. Step omitted')
        return

    #open a output label file. It's name will be the same as the pdb, but with a _label.tsv at the end
    outfile = open(outfile_name,'w')
    outdict = {}

    #Dictionary with aminoacid codes (label files require 3-letter code)
    AAs =  {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN', 
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP', 
     'A': 'ALA', 'V': 'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}

    #Reading dictionary file with the GPCR numeration for this protein sequence
    compl_data = json_dict(settings.MEDIA_ROOT + "Precomputed/get_contacts_files/compl_info.json")
    dictfile = compl_data[outname]['gpcr_pdb']
    gpcr_class = compl_data[outname]['class']

    #Reading GPCRnomenclatures Json: the json with the equivalences between different GPCR scales (Wooten, Ballesteros, Pi, ...)
    GPCRnomenclatures = json_dict(settings.MEDIA_ROOT + "Precomputed/get_contacts_files/GPCRnomenclatures_dict.json")

    #Iterate over residues in the dictionary, and extract its corresponding aminoacid type from the PDB
    pattern = re.compile("-\d\d")
    for ballesteros_id in dictfile:
        AA = dictfile[ballesteros_id]
        #Split by the dash that separates chainame and AA number
        AA_splited = AA.split("-")
        number = AA_splited[0]
        chain = AA_splited[1]
        type_res = AAs[AA_splited[2]]
        ballesteros_id = ballesteros_id.replace(".","-")
        ballesteros_id_cuted = re.sub(pattern,"",ballesteros_id)
        universal_id = GPCRnomenclatures[gpcr_class][ballesteros_id_cuted] 
        outdict[int(number)] = ("%s:%s:%s\t%s\n" %(chain, type_res,number, universal_id))

    #Print a new label file with the results
    for AA in sorted(outdict):
        outfile.write(outdict[AA])

    # If there's a ligandfile specified, add its content as a label at the end of the labelfile
    if ligand is not None:
        ligandfile = open(ligand, "r")

        # Iterate over lines. Split by :, catch second element as label and first as residue name
        for line in ligandfile:
            line = line.rstrip()
            outfile.write("%s\tLigand\n" %(line))

    #Close output file
    outfile.close()


def add_dyn_to_dynfile(dynname, files_basepath):
    """
    Adds new dynname to list of dynnames if it is not present yet
    """
    dyn_csv = files_basepath + "dyn_list.csv"
    if os.path.exists(dyn_csv):
        dyn_csv_file = open(dyn_csv, "r")
        col_line = dyn_csv_file.readline()
        col_names = col_line.split(",")
        col_names = set(col_names)
        dyn_csv_file.close()
    else:
        col_names = set()

    col_names.add(dynname)
    col_csv = ",".join(col_names)
    dyn_csv_file = open(dyn_csv, "w")
    dyn_csv_file.write(col_csv)
    dyn_csv_file.close()

def get_contact_frequencies(get_contacts_path, dyn_contacts_file, itype, labelfile, outfile, repeat_dynamics): 
    """
    Execute script get_contact frequencies for the given parameters
    """
    os.system(str("/opt/gpcrmdenv/bin/activate;python %sget_contact_frequencies.py \
        --input_files %s \
        --itypes %s \
        --label_file %s \
        --output %s" % (get_contacts_path, dyn_contacts_file, itype, labelfile, outfile))
    )

def remove_ligand_lines(filename): 
    """
    Remove ligand lines from a file
    """
    freqfile_with_ligand = open(filename, "r")
    lines = freqfile_with_ligand.readlines()
    freqfile_no_ligand = open(filename, "w")
    for line in lines:
        if not "Ligand" in line:
            freqfile_no_ligand.write(line)

def pharmacophores(dynname, path, dyn_contacts_file, trajfile, topfile, mytrajid, lig_list = []):
    """
    Compute pharmacopohres PDB files
    """

    def pdb_line(atomnum, atomname, coords, elname):
        """
        Prepare a pdb-format-like line for the input atom parameters
        """

        j = {}
        j[0] = 'HETATM'.ljust(6)#atom
        j[1] = str(atomnum).rjust(5)#atomnum
        j[2] = 'DUM'.center(4)#atomname$
        j[3] = elname.rjust(3)#resname
        j[4] = ' '.rjust(1) #Chainname (I put here element name instead, for NGL reasons)
        j[5] = str(atomnum).rjust(4) #resnum
        j[6] = str('%8.3f' % (float(coords[0]))).rjust(8) #x
        j[7] = str('%8.3f' % (float(coords[1]))).rjust(8)#y
        j[8] = str('%8.3f' % (float(coords[2]))).rjust(8) #z
        j[9] =str('%6.2f'%(float("0.00"))).rjust(6)#occ
        j[10]=str('%6.2f'%(float("0.00"))).ljust(6)#temp
        j[11]= ' '.rjust(12)#elname
        return str("%s%s %s %s %s%s    %s%s%s%s%s%s\n" % (j[0],j[1],j[2],j[3],j[4],j[5],j[6],j[7],j[8],j[9],j[10],j[11]))

    def add_atom(inter_dict, row_array, lig_list, total_lines):
        """
        Organize interacting ligand and atom lines inside the inter_dict dictionary
        """
        frame = row_array[0]
        atom1 = row_array[2]
        atom2 = row_array[3]
        res1 = atom1.rsplit(":",1)[0]
        res2 = atom2.rsplit(":",1)[0]
        ligres1 = False
        ligres2 = False

        # Locate the ligand, if any. Else return
        if res1 in lig_list:
            ligatom = atom1
            recatom = atom2
            ligres1 = True
        if res2 in lig_list:
            ligatom = atom2
            recatom = atom1
            ligres2 = True

        # Skip within-ligand or no-ligand interactions
        if (ligres1 == ligres2):
            return (inter_dict, total_lines)

        # Assign atoms
        total_lines += 1
        if ligatom not in inter_dict['ligand']:
            inter_dict['ligand'][ligatom] = set()
        if recatom not in inter_dict['receptor']: 
            inter_dict['receptor'][recatom] = set()

        inter_dict['ligand'][ligatom].add(frame)
        inter_dict['receptor'][recatom].add(frame)
    
        return (inter_dict, total_lines)

    # Skip if no ligand apported.
    if not bool(lig_list):
        print('simulation '+dynname+'has no ligand. Pharmacophore step omitted')
        return 

    # Take original trajectory fileid from compl_data
    compl_data = json_dict(settings.MEDIA_ROOT + "Precomputed/get_contacts_files/compl_info.json")

    #Load trajectory into mdAnalysis object
    u = md.Universe(topfile, trajfile)
    traj_object = u.trajectory

    # Create pharmacophores-itype-exist dictionary, or open from json if already exists
    json_itypes = path+dynname+"/pharmaco_itypes.json"
    if os.path.exists(json_itypes):
        itype_dict = json_dict(json_itypes)
    else:
        itype_dict = {}

    # For every itype with ligand-receptor interactions:
    for itype in set(("hb", "hblb", "hbls", "wb", "wb2", "vdw", "all")):
    #for itype in {"vdw"}:

        original_itype = itype

        # Set as false by default
        if mytrajid in itype_dict:
            itype_dict[mytrajid][original_itype] = False 
        else:
            itype_dict[mytrajid] = { original_itype : False }

        # Skipping whole step if pharmacophore file already exists
        pharmacofolder = path + dynname + '/' + itype + '/'
        if os.path.exists(pharmacofolder):
            print('pharmacophore file for itype '+itype+' already exists. Omitted')
            continue
        else: 
            os.makedirs(pharmacofolder, exist_ok=True)
    
        # Set array itype if necessari
        if itype == 'hb':
            itype = 'hblb hbls'
        elif itype in ['wb', 'wb2']:
            itype = 'l' + itype
        elif itype == 'all':
            itype = "vdw hbls hblb lwb lwb2 hp"

        print('computing pharmacophores for ', original_itype)
        
        # Open dynamic interaction data and itereate
        inter_dict = {'ligand' : {}, 'receptor' : {}}
        total_lines = 0
        with open(dyn_contacts_file, 'r') as infile:

            # If we have a list of itypes, like in hb (hbbb, hblb, hbsb, hbsl)
            if ' ' in itype:
                for row in infile:
                    if row.startswith('#'):
                        continue
                    row_array = row.rstrip().split('\t')
                    if row_array[1] in itype:
                        (inter_dict, total_lines) = add_atom(inter_dict, row_array, lig_list, total_lines)
            else:
                for row in infile: 
                    if row.startswith('#'):
                        continue
                    row_array = row.rstrip().split('\t')
                    if row_array[1] == itype:
                        (inter_dict, total_lines) = add_atom(inter_dict, row_array, lig_list, total_lines)

        # If there are no ligand-receptor interactions for this type, there's no need of going on
        if len(inter_dict['receptor'].keys()) == 0:
            print('no ligand-receptor interactions for itype '+original_itype)
            continue
        
        for ligrec in inter_dict:

            # Set initial counters
            linecounter = 0
            atomcounter = 0
            
            # If we have more atom lines than the max allowed, delete a random set of lines to eliminate the excedent
            max_lines = 6000
            total_lines = sum(len(v) for v in inter_dict[ligrec].values())
            line_excedent = total_lines-max_lines
            if line_excedent > 0:
                kill_lines = set(sample(range(1,total_lines), line_excedent))
            else:
                kill_lines = []

            # Iterate througth interacting atoms, extract coordinates and write them in a pdb
            with open(pharmacofolder+ligrec+"_"+mytrajid+".pdb", 'w') as outfile:
                for atom in inter_dict[ligrec]:
                    atom_array = atom.split(':')
                    resname = atom_array[1]
                    resid = atom_array[2]
                    name = atom_array[3]
                    element = name[0]
                    selection = u.select_atoms("resid %s  and resname %s and name %s"  % (resid, resname,  name))
                    if len(selection) == 0:
                        print("atom %s from residue %s%s not found. Skipping..." % (name, resname, resid))
                        continue
                    atomid = selection[0].id
                    for frame in inter_dict[ligrec][atom]:
                        linecounter += 1
                        # if line is inside the killing set, omit it
                        if linecounter in kill_lines:
                            continue
                        coords = traj_object[int(frame)-1][int(atomid)-1]
                        line = pdb_line(atomcounter, element, coords, element)
                        outfile.write(line)
                        atomcounter +=1

        # If pharmacophore file has been correctly computed, annotate true
        itype_dict[mytrajid][original_itype] = True

    # Save json once all itypes are done
    with open(json_itypes, "w") as out:
        dump(itype_dict, out)


def merge_dynamic_files(dynname, files_path):
    """
    Merge the dynamic contacts tabular files of a simulation into a single one, adding them as new frames
    """

    #if no files to merge exist, and the merged file already exists, skip this whole step
    non_merged_file = str("%s%s-%s_dynamic.tsv" % (files_path, dynname, "1"))
    merged_file = str("%s%s_dynamic.tsv" % (files_path, dynname))
    if (not os.path.isfile(non_merged_file)) and (os.path.isfile(merged_file)):#Debugging
        return merged_file

    print("merging dynamic files")
    dynfiles = glob.glob(str("%s%s-%s_dynamic.tsv" % (files_path, dynname, "*")))
    merged_file_noheader = "%s%s_dynamic_noheader.tsv" % (files_path, dynname)
    outfile = open(merged_file_noheader, 'w')
    first_file = True
    for dynfile in dynfiles:
        if first_file:
            with open(dynfile, "r") as f:
                for line in f: 
                    if line[0] == '#':
                        continue
                    outfile.write(line)
                frame = int(line.split("\t")[0]) + 1
            first_file = False

        else:
            with open(dynfile, "r") as f:
                for line in f: 
                    if line[0] == '#':
                        continue
                    tabline = line.split("\t")
                    tabline[0] = str(int(int(tabline[0]) + frame))
                    outfile.write("\t".join(tabline))
                frame = int(tabline[0]) + 1

        # Remove file after merge
        #os.remove(dynfile)

    outfile.close()

    #Paste header
    header = "# total_frames:%s beg:0 end:%s stride:1 interaction_types:hp,sb,pc,ps,ts,vdw,hb" % (frame, frame-1 )
    from_file = open(merged_file_noheader, 'r') 
    to_file = open(merged_file, "w")

    to_file.write(header)
    copyfileobj(from_file, to_file)

    from_file.close()
    to_file.close()
    os.remove(merged_file_noheader)

    return merged_file

# Arguments
parser = ap.ArgumentParser(description="this calculates interaction frequencies for given simulation")
parser.add_argument(
    '--dynid',
    dest='dynid',
    action='store',
    help=' (int) dynamic id of the simulation on database'
)
parser.add_argument(
    '--merge_dynamics',
    dest='merge_dynamics',
    action='store_true',
    default=False,
    help=' (bool) merges resulting dynamic file with previous dynamic files of same simulation'
)
parser.add_argument(
    '--traj',
    dest='trajfile',
    action='store',
    help='Trajectory file to process'
)
parser.add_argument(
    '--topology',
    dest='topology',
    action='store',
    help='Topology file to process'
)
parser.add_argument(
    '--ligandfile',
    dest='ligfile',
    action='store',
    help='Ligand file for this simulation'
)
parser.add_argument(
    '--repeat_dynamics',
    dest='repeat_dynamics',
    action='store_true',
    default=False,
    help='(bool) repeat get_dynamic_contacts even if there already exists a results file for this files'
)
parser.add_argument(
    '--cores',
    dest='cores',
    action='store',
    default=1,
    help='number of cores to use in get_dynamic_contacts'
)

args = parser.parse_args()

# Set paths and files
merge_dynamics = args.merge_dynamics
dynname = "dyn" + args.dynid
mytrajpath = args.trajfile
mypdbpath = args.topology
ligfile = args.ligfile
repeat_dynamics = args.repeat_dynamics
cores = args.cores
get_contacts_path = "~/bin/"
basepath = settings.MEDIA_ROOT + "Precomputed/"
pharma_path = basepath + "pharmacophores/"
files_basepath=basepath + "get_contacts_files/"
files_path = files_basepath + "dynamic_symlinks/" + dynname + "/"
mytrajid = re.search("_(\d+).\w+$", mytrajpath).group(1)
print("\ncomputing " + dynname + " dynamic contacts")

#Interaction multi-types dictionary
multi_itypes = {
    'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
    'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
    'wb2':'wb2 lwb2',
}

#Ligand information extracting
(ligand_sel, ligand_option, lig_list) = read_ligandfile(ligfile)

#Creating labelfile if it does not exists
print("computing labelfile")
create_labelfile(dynname, files_path, ligfile)

#Computing dynamic contacts
dyn_contacts_file = str("%s%s-%s_dynamic.tsv" % (files_path, dynname, mytrajid))
dyn_contacts_file_merged = str("%s%s_dynamic.tsv" % (files_path, dynname))
if (not os.path.exists(dyn_contacts_file) and not os.path.exists(dyn_contacts_file_merged)) or repeat_dynamics:
    os.system(str("/opt/gpcrmdenv/bin/activate;python %sget_dynamic_contacts.py         \
    --topology %s  \
    --trajectory %s       \
    --cores %s \
    --sele \"protein%s\"  \
    --itypes all    " % (get_contacts_path, mypdbpath, mytrajpath, cores, ligand_sel) 
    +ligand_option+
    "--output %s" % (dyn_contacts_file)
    ))

# Computing pharmacophores
pharmacophores(dynname, pharma_path, dyn_contacts_file, mytrajpath, mypdbpath, mytrajid, lig_list)

# Merge dynamic files of this dyn if option says so, and calculate frequencies from this merged dynamic file
if merge_dynamics:

    dyn_contacts_file = merge_dynamic_files(dynname, files_path)
    
    # Create files_path for freqeuncy files
    mkdir_p(str(files_path + "frequency_tables"))

    no_ligand = set(("sb", "pc", "ts", "ps", "hp", "hbbb", "hbsb", "hbss"))

    # Calculate frequencies and pharmacophores for each type
    #for itype in set(("sb","hp","pc","ps","ts","vdw", "wb", "wb2", "hb", "hbbb","hbsb","hbss","hbls","hblb","all")):
    for itype in set(("all", "vdw")):


        #Omit already computed frequencies
        outfile = str("%sfrequency_tables/%s_freqs_%s.tsv" % (files_path, dynname, itype))
        labelfile = str("%s%s_labels.tsv" % (files_path, dynname))
        if os.path.exists(outfile):
            pass
            #continue
        print(str("computing %s frequencies") % (itype))
        
        # HB and wb have to be calculated in a special way
        if  itype in multi_itypes:
            get_contact_frequencies(get_contacts_path, dyn_contacts_file, multi_itypes[itype], labelfile, outfile, repeat_dynamics)

        else:

            #Obtain contact frequencies
            get_contact_frequencies(get_contacts_path, dyn_contacts_file, itype, labelfile, outfile, repeat_dynamics)

            # Filter ligand interactions if itype is one of the interaction types unable to deal correctly with ligands
            if itype in no_ligand:
                remove_ligand_lines(outfile)

    #Add dynname to dyn-list-file and get new full list name
    add_dyn_to_dynfile(dynname, files_basepath)
