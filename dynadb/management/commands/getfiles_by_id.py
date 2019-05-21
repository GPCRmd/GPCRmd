import sys
condapath = ['', '/env/lib/python3.4', '/env/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/lib-dynload', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/site-packages']
sys.path = sys.path + condapath
import time
start_time = time.time()
import re
import string
import os
import shutil
from json import dumps
from django.conf import settings
from view.obtain_gpcr_numbering import generate_gpcr_pdb
from view.data import change_lig_name
from view.views import obtain_compounds, sort_by_myorderlist, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_seq_pos_info
from django.db import models
from django.forms import ModelForm, Textarea
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from dynadb.models import DyndbFilesDynamics


def obtain_dyn_files_from_id(dyn_ids,alldyn=False):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    
    traj_counter = {} 
    dynfiles = DyndbFilesDynamics.objects.select_related("id_files").filter(id_dynamics__is_published=True)
    dynfiles = dynfiles.annotate(file_name=F("id_files__filename"),file_path=F("id_files__filepath"))
    dynfiles = dynfiles.values("id_dynamics","id_files","file_name","file_path")
    if not alldyn:
        dynfiles = dynfiles.filter(id_dynamics__in = dyn_ids)
    dynfiles_struct = dynfiles.filter(type=[ft[0] for ft in DyndbFilesDynamics.file_types if ft[1] == 'Input coordinates'][0])
    dynfiles_traj = dynfiles.filter(type=[ft[0] for ft in DyndbFilesDynamics.file_types if ft[1] == 'Trajectory'][0])

    dyn_dict = {}    
        
    for dynobj in dynfiles_struct:
        if not dynobj["id_files"]:
            continue
        c_dyn_id = dynobj['id_dynamics']
        dyn_dict[c_dyn_id] = {}
        dyn_dict[c_dyn_id]['structure'] = {'name':dynobj['file_name'],'path':dynobj['file_path'],'id_files':dynobj["id_files"]}
        dyn_dict[c_dyn_id]['trajectory'] = []
    
    for dynobj in dynfiles_traj:
        if not dynobj["id_files"]:
            continue
        c_dyn_id = dynobj['id_dynamics']
        if c_dyn_id not in dyn_dict:
            continue

        if c_dyn_id in traj_counter:
            traj_counter[c_dyn_id] += 1  
        else:
            traj_counter[c_dyn_id] = 0 

        dyn_dict[c_dyn_id]['trajectory'].append({
            'name':dynobj['file_name'],
            'path':dynobj['file_path'],
            'id_files':dynobj["id_files"],
            'number':traj_counter[c_dyn_id]
            })
            
    return dyn_dict


def parse_pdb(residue_id, pdbfile, residue_num = None):
    """ 
    Finds chain number/s and residue number/s for a given residue_id, and returns it as a set of tuples chain-residue
    """
    sel_chain_id = ""
    sel_residue_num = ""
    residues = set()
    with open(pdbfile, "r") as f:
        for line in f:
            if line.startswith("END"): 
                break
            if line.startswith("ATOM") or line.startswith("HETATM"):
                line_residue_id = line[17:21].strip()
                line_chain_id = line[21].strip()
                line_residue_num = line[22:26].strip()
                if residue_id == line_residue_id:
                    if ((residue_num is not None) and (residue_num == line_residue_num)) or residue_num is None:
                        sel_chain_id = line_chain_id
                        sel_residue_num = line_residue_num
                        residues.add((sel_chain_id, sel_residue_num))
    return(residues)

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
    with open(outfile_name,'w') as outfile:
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
            ligandnames_count = {}

            # Iterate over lines. Split by blank, catch second element as label and first as residue name
            for line in ligandfile:
                ligand_splited = line.split()
                number = ligand_splited[0]
                chain = ligand_splited[1]
                type_res = ligand_splited[2]
                name_ligand = ligand_splitted[3]

                if name_ligand in ligandnames_count:
                    ligandnames_count[name_ligand] = 1
                else:
                    ligandnames_count[name_ligand] += 1

                outfile.write("%s:%s:%s\tLigand_%s_%d\n" %(chain, type_res, number, name_ligand, ligandnames_count[name_ligand]))

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'dynid',
            type=int,
            nargs='*',
            action='store',
            default=False,
            help='Dynamics IDs to compute.'
        )
        
        parser.add_argument(
            '--all',
            dest='alldyn',
            action='store_true',
            default=False,
            help='Compute all dynamics. Ignores dynid(s).',
        )
        parser.add_argument(
            '--ligresid',
            dest='ligresid',
            action='store',
            help='Residue id of the main ligand molecule. Use when more than one ligand'
        )
        parser.add_argument(
            '--ligresname',
            dest='ligresname',
            action='store',
            help='Residue name of the main ligand molecule. Use when more than one ligand'
        )

    def handle(self, *args, **options):

        ###########################
        ## Trajectory and PDB files
        ###########################
        
        if options['dynid'] or options['alldyn']:
            dynids = options['dynid']
        else:
            raise CommandError("Neither dynid(s) nor --all options have been specified. Use --help for more details.")
        # Obtain filenames
        dyn_dict = obtain_dyn_files_from_id(dynids,options['alldyn'])

        # In this file will be stored all commands to run in ORI (for the computer-spending steps, you know)
        commands_path = "/protwis/sites/protwis/contact_maps/scripts/dyn_freq_commands.sh"

        if dyn_dict:
            with open(commands_path,"w") as commands_file:
                for dynid in dyn_dict:
                    if not dyn_dict[dynid]['trajectory']:
                        continue
                    structure_file = dyn_dict[dynid]['structure']['path']
                    structure_file_name = dyn_dict[dynid]['structure']['name']

                    #Create directory for dynamic simulation id if it doesn't exists yet
                    directory = os.path.join(settings.MEDIA_ROOT,"Precomputed/get_contacts_files/dynamic_symlinks/dyn" + str(dynid))
                    os.makedirs(directory,exist_ok=True)

                    #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
                    basepath = settings.MEDIA_ROOT
                    pdbpath = os.path.join(basepath,structure_file)
                    
                    #TO DO: idenfity structure files with an "struc" suffix, not only by extension
                    #TO DO: add id_files number to the filename
                    mypdbpath =  os.path.join(directory, "dyn" + str(dynid) + os.path.splitext(structure_file)[1])
                    if not os.path.lexists(mypdbpath):
                        os.symlink(pdbpath, mypdbpath)
                    self.stdout.write("Created symlink "+pdbpath+" -> "+mypdbpath)
                    
                    for i,traj_dict in enumerate(dyn_dict[dynid]['trajectory']):
                        #Create symbolic links also for trajectory file list
                        #TO DO: add id_files number to the filename
                        traj_name = traj_dict['name']
                        trajpath = os.path.join(basepath,traj_dict['path'])
                        mytrajpath = os.path.join(directory,"dyn" + str(dynid) + "_" + str(i) + os.path.splitext(trajpath)[1])
                        if os.path.islink(mytrajpath):
                            os.remove(mytrajpath)
                        os.symlink(trajpath, mytrajpath)
                        traj_dict['local_path'] = mytrajpath
                        
                    try:
                        ############
                        #Ligand file
                        ############

                        # Obtain ligand by dynID
                        (comp_li,lig_li,lig_li_s) = obtain_compounds(dynid)

                        """    
                        comp_li     list of [component_name,component_residue_name,component_type_str].
                        lig_li      list of ligand [component_name,component_residue_name].
                        lig_li_s    list of ligands residue names.
                        """

                        # Open out file
                        ligfile_name = os.path.join(directory, "dyn" + str(dynid) + "_ligand.txt")
                        with open(ligfile_name, "w") as ligfile:
                            # Print each ligand in a ligand file, after finding out its chain and residue id in the PDB
                            for ligand_info in lig_li:

                                ligand_name = ligand_info[0].replace(" ","_")
                                ligres = ligand_info[1]

                                # If we have the dyn7 exception of ligand being one cholesterol among others
                                # isma: this makes no sense
                                # david: it is a very puntual exception for a very puntual case
                                if "and" in ligres: # If its like 'CHL1 and 59'
                                    ligpos_list = ligres.split(" and ")
                                    ligres = ligpos_list[0]
                                    lignum_prov = ligpos_list[1]
                                    lig_chains_resnums = list(parse_pdb(ligres, mypdbpath, lignum_prov))
                                    ligchain = lig_chains_resnums[0][0]
                                    lignum = lig_chains_resnums[0][1]

                                else:
                                    # TO DO: there is the possibility that there is more than one molecule
                                    # of ligand in the same system (but not in our simulations)
                                    if len(lig_li) > 1:
                                        lignum = options['ligresid']
                                        ligres = options['ligresname'] 
                                        lig_chains_resnums = list(parse_pdb(ligres, mypdbpath, lignum))
                                        ligchain = lig_chains_resnums[0][0]

                                    else:
                                        lig_chains_resnums = list(parse_pdb(ligres, mypdbpath))
                                        ligchain = lig_chains_resnums[0][0]
                                        lignum = lig_chains_resnums[0][1]
                                    
                                print("%s\t%s\t%s\t%s" % (lignum,ligchain,ligres,ligand_name),file=ligfile)

                        ##################
                        ## Dictionary file
                        ##################
                        dictfile_name = os.path.join(directory, "dyn" + str(dynid) + "_dict.txt")
                        with open(dictfile_name, "w") as dictfile:
                            mydict = generate_gpcr_pdb(dynid, mypdbpath)
                            print(dumps(mydict),file=dictfile)
                                       
                    except IndexError:
                        self.stdout.write(self.style.WARNING("Ligand error: options --ligresname and --ligresid are mandatory when more than one ligand molecule is present on the database. Skipping and cleaning up."))
                        shutil.rmtree(directory)
                        continue

                    except Exception:
                         self.stdout.write(self.style.WARNING("Error while processing dynamics "+str(dynid)+". Skipping and cleaning up."))
                         shutil.rmtree(directory)
                    
                    ###########################################
                    ## Compute frequencies and dynamic contacts
                    ###########################################

                    # for each trajectory file, write a run-in-ORI command
                    numtraj = len(dyn_dict[dynid]['trajectory'])
                    for i,traj_dict in enumerate(dyn_dict[dynid]['trajectory']):
                        
                        # Put option to merge all dynamics from this simulation, if all trajectories are already computed
                        trajcounter = traj_dict['number'] + 1 
                        if numtraj == trajcounter:
                            tail_comand = "--merge_dynamics \n"
                        else:
                            tail_comand = "\n"

                        commands_file.write(str("python /protwis/sites/protwis/contact_maps/scripts/get_contacts_dynfreq.py \
                            --dynid %s \
                            --traj %s \
                            --traj_id %s \
                            --topology %s \
                            --dict %s \
                            --ligandfile %s \
                            --cores 4 %s" % (dynid, traj_dict['local_path'], traj_dict['number'], mypdbpath, dictfile_name, ligfile_name, tail_comand))
                        )  
