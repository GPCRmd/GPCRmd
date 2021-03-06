import re
import os
import glob
import numpy as np
import argparse as ap
import pandas as pd
from json import loads, dump
from sys import stdout
from shutil import copyfile,copyfileobj
import time

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
    compl_data = json_dict("/protwis/sites/files/Precomputed/get_contacts_files/compl_info.json")
    dictfile = compl_data[outname]['gpcr_pdb']
    gpcr_class = compl_data[outname]['class']

    #Reading GPCRnomenclatures Json: the json with the equivalences between different GPCR scales (Wooten, Ballesteros, Pi, ...)
    GPCRnomenclatures = json_dict("/protwis/sites/files/Precomputed/get_contacts_files/GPCRnomenclatures_dict.json")

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

def pharmacophores(dynname, outfile, itype, dyn_contacts_file, lig_resname = ""):
    """
    Get the list of atoms interacting with the ligand of this simulation every 10 frames
    """
    print('computing pharmacophores for ', itype)
    # Set array itype if necessari
    if itype == 'hb':
        itype = 'hblb hbls'
    elif itype in ['wb', 'wb2']:
        itype = 'l' + itype
    elif itype == 'all':
        itype = "vdw hbls hblb lwb lwb2 hp"

    # Skipping whole step if pharmacophore file already exists
    if os.path.exists(outfile):
        print('pharmacophore file for itype '+itype+' already exists. Step omitted')
        return
    
    # Skip if no ligand apported.
    if not bool(lig_resname):
        return 
    
    # Open dynamic interaction data and itereate
    filtered_array = []
    with open(dyn_contacts_file, 'r') as infile:

        # If we have a list of itypes, like in hb (hbbb, hblb, hbsb, hbsl)
        if ' ' in itype:
            for row in infile: 
                row_array = row.split('\t')[0:4]

                # Get interaction lines of our interaction type and where the ligand is one of the interacting parts
                if (row_array[1] in itype):
                    if ((lig_resname in row_array[3]) or (lig_resname in row_array[2])):
                        filtered_array.append(row_array)
        else:
            for row in infile: 
                row_array = row.split('\t')[0:4]
                # Get interaction lines of our interaction type and where the ligand is one of the interacting parts
                if (row_array[1] == itype):
                    if ((lig_resname in row_array[3]) or (lig_resname in row_array[2])):
                        filtered_array.append(row_array)

    if filtered_array.size == 0:
        print('no ligand-receptor interactions for itype '+itype)
        return

    # Convert previous array to pandas dataframe
    df = pd.DataFrame(np.array(filtered_array), columns=['frame', 'itype', 'Position1', 'Position2'])
    df['frame'] = pd.to_numeric(df['frame'])

    # Conserve only interacting atoms each 10th frame
    df10th = df[(df['frame'] % 10) == 0]
    
    # Take interacting atom codes and separate between ligand and receptor atoms
    pharmacophore_atoms = pd.unique(df10th['Position1'].append(df10th['Position2']))
    pharmacophore_receptor = set()
    pharmacophore_ligand = set()
    for atom in pharmacophore_atoms:
        if lig_resname in atom:
            pharmacophore_ligand.add(atom)
        else:
            pharmacophore_receptor.add(atom)

    #Save pharmacophoric atoms
    with open(outfile,'w') as outf: 
        dump({ 'ligand' : list(pharmacophore_ligand), 'receptor' : list(pharmacophore_receptor) }, outf)

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

    #if no files to merge exist, and the merged file already exists, skip this whole step
    non_merged_file = str("%s%s-%s_dynamic.tsv" % (files_path, dynname, "1"))
    merged_file = str("%s%s_dynamic.tsv" % (files_path, dynname))
    if (not os.path.isfile(non_merged_file)) and (os.path.isfile(merged_file)):
        return merged_file

    print("merging dynamic files")
    dynfiles = glob.glob(str("%s%s-%s_dynamic.tsv" % (files_path, dynname, "*")))
    merged_file_noheader = "%s%s_dynamic_noheader.tsv" % (files_path, dynname)
    outfile = open(merged_file_noheader, 'w')
    for dynfile in dynfiles:
        if "1_dynamic.tsv" in dynfile:
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

        # Remove file after merge
        os.remove(dynfile)

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
ligfile = args.ligfile
repeat_dynamics = args.repeat_dynamics
cores = args.cores
get_contacts_path = "~/bin/"
files_path = "/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/" + dynname + "/"
files_basepath="/protwis/sites/files/Precomputed/get_contacts_files/"

print("\ncomputing " + dynname + " dynamic contacts")

#Interaction multi-types dictionary
multi_itypes = {
    'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
    'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
    'wb2':'wb2 lwb2',
}

#Ligand information extracting
ligand_sel = read_ligandfile(ligfile)

#Creating labelfile if it does not exists
print("computing labelfile")
create_labelfile(dynname, files_path, ligfile)

#Computing dynamic contacts
if ligand_sel:
    ligand_text1 = " or %s" % (ligand_sel)
    ligand_text2 = "--ligand \"%s\" " % (ligand_sel)
    lig_resname = re.search("resname (\w+)", ligand_sel).groups()[0]
else:
    ligand_text1 = ""
    ligand_text2 = ""
    lig_resname = ""

dyn_contacts_file = str("%s%s-%s_dynamic.tsv" % (files_path, dynname, mytrajid))
dyn_contacts_file_merged = str("%s%s_dynamic.tsv" % (files_path, dynname))
if (not os.path.exists(dyn_contacts_file) and not os.path.exists(dyn_contacts_file_merged)) or repeat_dynamics:
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

    no_ligand = set(("sb", "pc", "ts", "ps", "hp", "hbbb", "hbsb", "hbss"))

    # Calculate frequencies and pharmacophores for each type
    for itype in set(("sb","hp","pc","ps","ts","vdw", "wb", "wb2", "hb", "hbbb","hbsb","hbss","hbls","hblb","all")):
    #for itype in {"wb2"}: # For debugging

        #Calculate pharmacophores for this interaction type
        pharmacofolder = files_path+'pharmacophores/' 
        os.makedirs(pharmacofolder, exist_ok=True)

        if itype not in no_ligand:
            pharmacophores(dynname, pharmacofolder+itype+'.json', itype, dyn_contacts_file, lig_resname)

    	#Calculate pharmacophores for this interaction type
    	pharmacofolder = files_path+'pharmacophores/' 
		os.makedirs(pharmacofolder, exists_ok=True)
    	def pharmacophores(dynname, outfile, itype, dyn_contacts_file):
    		"""
			Get the list of atoms interacting with the ligand of this simulation every 10 frames
    		"""
    		
    		# Put interaction data into dataframe
    		df = pd.read_csv(dyn_contacts_file, skiprows=1, sep=' ', names=['frame', 'itype', 'Position1', 'Position2'])
    		
    		# Filter out not interesting ligand types
    		df_itype = df[df['itype'] == itype]

    		# Filter no-ligand interactions
		    compl_data = json_dict("/protwis/sites/files/Precomputed/get_contacts_files/compl_info.json")
		    ligname = compl_data[dynname]['lig_sname']
		    df_itype_filtered = df_itype[ligname in (df_itype['Position1'] or df['Position2'])]

		    print(df_itype_filtered)
		pharmacophores(dynname, pharmacofolder+itype+'.tsv', itype, dyn_contacts_file)


        #Omit already computed frequencies
        outfile = str("%sfrequency_tables/%s_freqs_%s.tsv" % (files_path, dynname, itype))
        labelfile = str("%s%s_labels.tsv" % (files_path, dynname))
        if os.path.exists(outfile):
            continue
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

