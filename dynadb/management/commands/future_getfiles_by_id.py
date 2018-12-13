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
    pattern = compile("-\d\d")
    for ballesteros_id in dictfile:
        AA = dictfile[ballesteros_id]
        #Split by the dash that separates chainame and AA number
        AA_splited = AA.split("-")
        number = AA_splited[0]
        chain = AA_splited[1]
        type_res = AAs[AA_splited[2]]
        ballesteros_id = ballesteros_id.replace(".","-")
        ballesteros_id_cuted = sub(pattern,"",ballesteros_id)
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

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '-dynid',
            dest='dynid',
            nargs='*',
            action='store',
            default=False,
        )
    def handle(self, *args, **options):

        ###########################
        ## Trajectory and PDB files
        ###########################
        print(parser)

        # Obtain filenames
        structure_file,structure_file_name,traj_list,traj_name_list = obtain_dyn_files_from_id(dynid)

        #Create directory for dynamic simulation id if it doesn't exists yet
        directory = "/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/dyn" + dynid
        if not os.path.exists(directory):
            os.makedirs(directory)

        #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
        basepath = "/protwis/sites/files/"
        pdbpath = basepath + structure_file
        mypdbpath =  directory + "/dyn" + str(dynid) + ".pdb"
        if os.path.exists(mypdbpath):
            os.remove(mypdbpath)       
        os.symlink(pdbpath, mypdbpath)

        #Create symbolic links also for trajectory file list
        for i in range(0,len(traj_list)):
            trajpath = basepath + traj_list[i][0]
            mytrajpath = directory + "/dyn" + dynid + "_" + str(i) + ".dcd"
            if os.path.exists(mytrajpath):
                os.remove(mytrajpath)
            os.symlink(trajpath, mytrajpath)


        ############
        #Ligand file
        ############

        # Obtain ligand by dynID
        (comp_li,lig_li,lig_li_s) = obtain_compounds(dynid)
        # Open out file
        ligfile_name = directory + "/dyn" + dynid + "_ligand.txt"
        ligfile = open(ligfile_name, "w")

        # Print each ligand in a ligand file, after finding out its chain and residue id in the PDB
        for ligand in lig_li_s:
            # If we have the dyn7 exception of ligand being one cholesterol among others
            if "and" in ligand: # If its like 'CHL1 and 59'
                ligpos_list = ligand.split(" and ")
                ligres = ligpos_list[0]
                lignum_prov = ligpos_list[1]
                (ligchain, lignum) = parse_pdb(ligres, mypdbpath, lignum_prov)
                ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))


            else:
                ligres = ligand
                (ligchain, lignum) = parse_pdb(ligres, mypdbpath)
                ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))

        ligfile.close()

        ##################
        ## Dictionary file
        ##################
        dictfile_name = directory + "/dyn" + dynid + "_dict.txt"
        dictfile = open(dictfile_name, "w")
        mydict = generate_gpcr_pdb(dynid, mypdbpath)
        dictfile.write(dumps(mydict))
        dictfile.close()
            
        ###########################################
        ## Compute frequencies and dynamic contacts
        ###########################################

        # for each trajectory file
        for i in range(0,len(traj_list)):

            print("bash /protwis/sites/protwis/contact_plots/scripts/get_contacts_dynfreq.sh " +  
                mypdbpath + " " +
                mytrajpath + " " +
                dictfile_name + " " + 
                ligfile_name + 
                " dyn" + dynid )

            # Set paths
            dynname = "dyn" + dynid 
            mytrajpath = directory + "/" + dynname + "_" + str(i) + ".dcd"
            get_contacts_path="/protwis/sites/protwis/contact_plots/scripts/get_contacts/"
            scripts_path="/protwis/sites/protwis/contact_plots/scripts/"
            files_basepath="/protwis/sites/files/Precomputed/get_contacts_files/"
            files_path="/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/" + dynname + "/"

            # Set folder
            mkdir_p("/protwis/sites/files/Precomputed/get_contacts_files")

            #Interaction multi-types dictionary
            multi_itypes = {
                'hb' : "hbbb hbsb hbss hbls hblb", # A general category for HB is required
                'wb' : 'wb lwb', # lwb and lwb2 are not needed. I make a posterior division between ligand-residue and residue-residue interactions
                'wb2':'wb2 lwb2',
            }

            #Ligand information extracting
            print("parsing ligand file")
            ligfile = open(ligfile_name, 'r')
            ligand_sel = ""
            first_line = True
            for line in ligfile:
                linetab = line.split("\s+")
                if first_line: 
                    ligand_sel += str("(resname %s and resid %s)" % (linetab[2],linetab[0]))
                    first_line = False
                else:
                    ligand_sel += str(" or (resname %s and resid %s)" % (linetab[2],linetab[0]))
            ligfile.close()


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
            --output %s%s_dynamic.tsv" % (get_contacts_path, mypdbpath, mytrajpath, ligand_sel, ligand_sel, files_path, dynname))

            #Adding new dynname to list of dynnames if doesnt already exists, and getting dynlist;

