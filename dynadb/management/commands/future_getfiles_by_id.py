import sys
condapath = ['', '/env/lib/python3.4', '/env/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/lib-dynload', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/site-packages']
sys.path = sys.path + condapath
import time
start_time = time.time()
import re
import string
import os
from json import dumps
from view.obtain_gpcr_numbering import generate_gpcr_pdb
from view.data import change_lig_name
from view.views import obtain_compounds, sort_by_myorderlist, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_seq_pos_info
from django.db import models
from django.forms import ModelForm, Textarea
from dynadb.models import DyndbFilesDynamics
from django.core.management.base import BaseCommand, CommandError
    
def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)

def obtain_dyn_files_from_id(dyn_id):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics = dyn_id)
    traj_list=[]
    traj_name_list=[]
    p=re.compile("(/protwis/sites/files/)(.*)")
    p2=re.compile("[\.\w]*$")
    for fileobj in dynfiles:
        path=fileobj.id_files.filepath
        myfile=p.search(path).group(2)
        myfile_name=p2.search(myfile).group()
        if myfile.endswith(".pdb"): 
            structure_file=myfile
            structure_file_name=myfile_name
        elif myfile.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append([myfile,fileobj.id_files.id])
            traj_name_list.append(myfile_name)
    return (structure_file,structure_file_name,traj_list,traj_name_list)


def parse_pdb(residue_id, pdbfile, residue_num = None):
    """ 
    Finds chain number and residue number for a given residue_id
    """
    sel_chain_id = ""
    sel_residue_num = ""

    for line in open(pdbfile, "r"):
        if "END" in line: 
            break
        line_residue_id = line[17:21].replace(" ","")
        line_chain_id = line[21]
        line_residue_num = line[22:26].replace(" ","")
        if residue_id == line_residue_id:
            if ((residue_num is not None) and (residue_num == line_residue_num)) or residue_num is None:
                sel_chain_id = line_chain_id
                sel_residue_num = line_residue_num
    return(sel_chain_id, sel_residue_num)

def create_ligandfile(dynid, path, pdbfile):
    """
    Create a ligand file. One line for each ligand. In tab format: 
    ligand_residue_number\tligand_chain\tligand_residue_name
    """
    # Obtain ligand by dynID
    (comp_li,lig_li,lig_li_s) = obtain_compounds(dynid)

    # Open out file
    ligfile_name = path + "dyn" + dynid + "_ligand.txt"
    ligfile = open(ligfile_name, "w")

    # Print each ligand in a ligand file, after finding out its chain and residue id in the PDB
    for ligand in lig_li_s:
        # If we have the dyn7 exception of ligand being one cholesterol among others
        if "and" in ligand: # If its like 'CHL1 and 59'
            ligpos_list = ligand.split(" and ")
            ligres = ligpos_list[0]
            lignum_prov = ligpos_list[1]
            (ligchain, lignum) = parse_pdb(ligres, pdbfile, lignum_prov)
            ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))


        else:
            ligres = ligand
            (ligchain, lignum) = parse_pdb(ligres, pdbfile)
            ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))

    ligfile.close()

    #For later uses
    return(ligfile_name)

def read_ligandfile(ligfile_name):
    """
    Read information contained in ligandfile, and create a VMD selection line for this ligand. It will be used in --ligand and --sel from 
    get_dynamic_interactions.py
    """
    ligfile = open(ligfile_name, 'r')
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
        ligandfile = open(ligand, "r")

        # Iterate over lines. Split by blank, catch second element as label and first as residue name
        for line in ligandfile:
            ligand_splited = line.split()
            number = ligand_splited[0]
            chain = ligand_splited[1]
            type_res = ligand_splited[2]
            outfile.write("%s:%s:%s\t%s\n" %(chain, type_res,number, "Ligand"))

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

def get_contact_frequencies(get_contacts_path, dyn_contacts_file, itype, labelfile, outfile): 
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

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--dynid',
            dest='dynid',
            nargs='?',
            action='store',
            default=False,
        )
    def handle(self, *args, **options):

        ###########################
        ## Trajectory and PDB files
        ###########################

        dynid = options['dynid']
        dynname = "dyn" + dynid 

        # Obtain filenames
        print("Getting simulation filenames")
        structure_file,structure_file_name,traj_list,traj_name_list = obtain_dyn_files_from_id(dynid)

        #Create files_path for dynamic simulation id if it doesn't exists yet
        files_path="/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/" + dynname + "/"
        mkdir_p(files_path)

        #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
        print("Making symbolic links for files")
        basepath = "/protwis/sites/files/"
        pdbpath = basepath + structure_file
        mypdbpath =  files_path + "dyn" + str(dynid) + ".pdb"
        if os.path.exists(mypdbpath):
            os.remove(mypdbpath)       
        os.symlink(pdbpath, mypdbpath)

        #Create symbolic links also for trajectory file list
        for i in range(0,len(traj_list)):
            trajpath = basepath + traj_list[i][0]
            mytrajpath = files_path + dynname+ "_" + str(i) + ".dcd"
            if os.path.exists(mytrajpath):
                os.remove(mytrajpath)
            os.symlink(trajpath, mytrajpath)


        #Create ligandfile, and obtain its name
        ligfile_name = create_ligandfile(dynid, files_path, pdbpath)

        # Create dictionary file
        print("writing dictionary file")
        dictfile_name = files_path + dynname + "_dict.txt"
        dictfile = open(dictfile_name, "w")
        mydict = generate_gpcr_pdb(dynid, mypdbpath)
        dictfile.write(dumps(mydict))
        dictfile.close()
            
        ###########################################
        ## Compute frequencies and dynamic contacts
        ###########################################

        # for each trajectory file
        for i in range(0,len(traj_list)):

            # Set paths
            mytrajpath = files_path + "/" + dynname + "_" + str(i) + ".dcd"
            get_contacts_path="/protwis/sites/protwis/contact_plots/scripts/get_contacts/"
            scripts_path="/protwis/sites/protwis/contact_plots/scripts/"
            files_basepath="/protwis/sites/files/Precomputed/get_contacts_files/"
            files_path="/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/" + dynname + "/"

            #Interaction multi-types dictionary
            multi_itypes = {
                'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
                'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
                'wb2':'wb2 lwb2',
            }

            #Ligand information extracting
            ligand_sel = read_ligandfile(ligfile_name)

            #Creating labelfile
            print("computing labelfile")
            create_labelfile(dictfile_name, dynname, files_path, ligfile_name)

            #Computing dynamic contacts
            print("computing dynamic contacts")
            os.system(str("python %sget_dynamic_contacts.py         \
            --topology %s  \
            --trajectory %s       \
            --sele \"protein or %s\"  \
            --itypes all    \
            --ligand %s \
            --output %s%s_dynamic.tsv" % (get_contacts_path, mypdbpath, mytrajpath, ligand_sel, ligand_sel, files_path, dynname)
            ))

            # Create files_path for freqeuncy files
            mkdir_p(str(files_path + "frequency_tables"))
            
            no_ligand = set(("sb", "pc", "ts", "ps", "hp"))

            # Calculate frequencies for each type
            for itype in set(("wb","hb","wb2","sb","hp","pc","ps","ts","vdw","hbbb","hbsb","hbss","hbls","hblb","all")):

                print(str("computing %s frequencies") % (itype))
                dyn_contacts_file = str("%s%s_dynamic.tsv" % (files_path, dynname))
                labelfile = str("%s%s_labels.tsv" % (files_path, dynname))
                outfile = str("%sfrequency_tables/%s_freqs_%s.tsv" % (files_path, dynname, itype))
                
                # HB and wb have to be calculated in a special way
                if  itype in multi_itypes:
                    get_contact_frequencies(get_contacts_path, dyn_contacts_file, multi_itypes[itype], labelfile, outfile)

                else:

                    #Obtain contact frequencies
                    get_contact_frequencies(get_contacts_path, dyn_contacts_file, itype, labelfile, outfile)

                    # Filter ligand interactions if itype is one of the interaction types unable to deal correctly with ligands
                    if itype in no_ligand:
                        remove_ligand_lines(outfile)


            #Add dynname to dyn-list-file and get new full list name
            add_dyn_to_dynfile(dynname, files_basepath)
