import re
import os
import glob
import argparse as ap
import pandas as pd
from sys import stdout
from shutil import copyfile,copyfileobj


def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def read_ligandfile(ligfile):
    """
    Read information contained in ligandfile, and create a VMD selection line for this ligand. It will be used in --ligand and --sel from 
    get_dynamic_interactions.py
    """
    ligfile = open(ligfile, 'r')
    ligand_sel = ""
    first_line = True
    for line in ligfile:
        linetab = line.split("\t")
        if first_line: 
            ligand_sel += str("(resname %s and resid %s)" % (linetab[2],linetab[0]))
            first_line = False
        else:
            ligand_sel += str(" or (resname %s and resid %s)" % (linetab[2],linetab[0]))
    ligfile.close()

    return(ligand_sel)

def create_labelfile(info_dictfile, outname, outfolder = "./", ligand = None):
    """
    The idea of this function is to create a label file (get_contacts format) with the ballesteros GPCR id's as labels for a certain model.
    info_dictfile should contain a dictionary-like text file with this format:
        {'POSITION-CHAIN-RESIDUE': BALLESTEROS_ID, ... }
    The optional argument "ligand" corresponds to a file with the PDB identifier of the molecule ligand and its label. Example
    NUMBER CHAIN RESIDUE Ligand
    """

    #Dictionary with aminoacid codes (label files require 3-letter code)
    AAs =  {'C': 'CYS', 'D': 'ASP', 'S': 'SER', 'Q': 'GLN', 'K': 'LYS',
     'I': 'ILE', 'P': 'PRO', 'T': 'THR', 'F': 'PHE', 'N': 'ASN', 
     'G': 'GLY', 'H': 'HIS', 'L': 'LEU', 'R': 'ARG', 'W': 'TRP', 
     'A': 'ALA', 'V': 'VAL', 'E': 'GLU', 'Y': 'TYR', 'M': 'MET'}

    #Reading dictionary file with the Ballesteros numeration for this protein sequence
    dictfile = eval(open(info_dictfile, 'r').read())

    #open a output label file. It's name will be the same as the pdb, but with a _label.tsv at the end
    outfile_name = outfolder + outname + "_labels.tsv"
    outfile = open(outfile_name,'w')
    outdict = {}

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
        outdict[int(number)] = ("%s:%s:%s\t%s\n" %(chain, type_res,number, ballesteros_id_cuted))

    #Print a new label file with the results
    for AA in sorted(outdict):

        outfile.write(outdict[AA])

    # If there's a ligandfile specified, add its content as a label at the end of the labelfile
    if ligand is not None:
        ligand_names = {}
        ligandfile = open(ligand, "r")

        # Iterate over lines. Split by blank, catch second element as label and first as residue name
        for line in ligandfile:
            ligand_splited = line.split()
            number = ligand_splited[0]
            chain = ligand_splited[1]
            type_res = ligand_splited[2]

            # If it doesn't have a name column,put nothing
            if len(ligand_splited) > 3:
                ligand_name = ligand_splited[3]
            else:
                ligand_name = ""

            # Number of times this ligand name has already appeared
            if ligand_name not in ligand_names:
                ligand_names[ligand_name] = 1
            else:
                ligand_names[ligand_name] += 1

            outfile.write("%s:%s:%s\tLigand\n" %(chain, type_res,number))

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
    os.system(str("python %sget_contact_frequencies.py \
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

def merge_dynamic_files(dynname, files_path):
    """
    Merge the dynamic contacts tabular files of a simulation into a single one, adding them as new frames
    """
    print("merging dynamic files")
    dynfiles = glob.glob(str("%s%s-%s_dynamic.tsv" % (files_path, dynname, "*")))
    merged_file_noheader = "%s%s_dynamic_noheader.tsv" % (files_path, dynname)
    outfile = open(merged_file_noheader, 'w')
    for dynfile in dynfiles:
        if "0_dynamic.tsv" in dynfile:
            with open(dynfile, "r") as f:
                for line in f: 
                    if line[0] == '#':
                        continue
                    outfile.write(line)
                frame = int(line.split("\t")[0]) + 1

        else:
            with open(dynfile, "r") as f:
                for line in f: 
                    if line[0] == '#':
                        continue
                    tabline = line.split("\t")
                    tabline[0] = str(int(int(tabline[0]) + frame))
                    outfile.write("\t".join(tabline))
                frame = int(tabline[0]) + 1

    outfile.close()

    #Paste header
    header = "# total_frames:%s beg:0 end:%s stride:1 interaction_types:hp,sb,pc,ps,ts,vdw,hb" % (frame, frame-1 )
    merged_file = "%s%s_dynamic.tsv" % (files_path, dynname)
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
    '--traj_id',
    dest = 'traj_id',
    action='store',
    default=0,
    help='Id of this trajectory file (over the total trajectory files for this simulation)'
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
    '--dict',
    dest='dictfile',
    action='store',
    help='Dictionary file of this simulation'
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
mytrajid = args.traj_id
mytrajpath = args.trajfile
mypdbpath = args.topology
dictfile = args.dictfile
ligfile = args.ligfile
repeat_dynamics = args.repeat_dynamics
cores = args.cores
get_contacts_path = "/protwis/sites/protwis/contact_maps/scripts/get_contacts/"
scripts_path = "/protwis/sites/protwis/contact_maps/scripts/"
files_basepath = "/protwis/sites/files/Precomputed/get_contacts_files/"
files_path = "/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/" + dynname + "/"

#Interaction multi-types dictionary
multi_itypes = {
    'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
    'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
    'wb2':'wb2 lwb2',
}

#Ligand information extracting
ligand_sel = read_ligandfile(ligfile)

#Creating labelfile
print("computing labelfile")
create_labelfile(dictfile, dynname, files_path, ligfile)

#Computing dynamic contacts
print("computing " + dynname + " dynamic contacts")
if ligand_sel:
    ligand_text1 = " or %s" % (ligand_sel)
    ligand_text2 = "--ligand \"%s\" " % (ligand_sel)
else:
    ligand_text1 = ""
    ligand_text2 = ""
dyn_contacts_file = str("%s%s-%s_dynamic.tsv" % (files_path, dynname, mytrajid))

if (not os.path.exists(dyn_contacts_file)) or repeat_dynamics:
    os.system(str("python %sget_dynamic_contacts.py         \
    --topology %s  \
    --trajectory %s       \
    --cores %s \
    --sele \"protein%s\"  \
    --itypes all    " % (get_contacts_path, mypdbpath, mytrajpath, cores, ligand_text1) 
    +ligand_text2+
    "--output %s" % (dyn_contacts_file)
    ))

# Merge dynamic files of this dyn if option says so, and calculate frequencies from this merged dynamic file
if merge_dynamics:

    dyn_contacts_file = merge_dynamic_files(dynname, files_path)
    
    # Create files_path for freqeuncy files
    mkdir_p(str(files_path + "frequency_tables"))

    no_ligand = set(("sb", "pc", "ts", "ps", "hp"))

    # Calculate frequencies for each type
    for itype in set(("sb","hp","pc","ps","ts","vdw", "wb", "wb2", "hb", "hbbb","hbsb","hbss","hbls","hblb","all")):

        print(str("computing %s frequencies") % (itype))
        labelfile = str("%s%s_labels.tsv" % (files_path, dynname))
        outfile = str("%sfrequency_tables/%s_freqs_%s.tsv" % (files_path, dynname, itype))
        
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