import sys
condapath = ['', '/env/lib/python3.4', '/env/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/lib-dynload', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/site-packages']
sys.path = sys.path + condapath
import re
import string
import os
import shutil
import csv
from django.conf import settings
from view.obtain_gpcr_numbering import generate_gpcr_pdb
from view.data import change_lig_name
from view.views import obtain_compounds, sort_by_myorderlist, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_rel_dicts, obtain_seq_pos_info, compute_interaction, obtain_all_chains, relate_atomSerial_mdtrajIndex
from django.db import models
from django.forms import ModelForm, Textarea
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from pathlib import Path
import pandas as pd
import json
import datetime
from dynadb.models import DyndbProtein, DyndbFilesDynamics, DyndbSubmissionMolecule, DyndbDynamicsComponents,DyndbModeledResidues, DyndbDynamics
from protein.models import Protein
from view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from dynadb.pipe4_6_0 import *

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

def json_dict(path):
    """Converts json file to pyhton dict."""
    json_file=open(path)
    json_str = json_file.read()
    json_data = json.loads(json_str)
    return json_data

def prot_from_model(model):
    """Given a db model obj, gets the GPCR protein object"""
    model_prot=model.id_protein
    if model_prot:
        if not model_prot.receptor_id_protein:
            self.stdout.write(self.style.ERROR("Protein ID:%d UniprotKB AC:%s is not a GPCR or has no GPCRdb ID set.") % (model_prot.id,model_prot.uniprotkbac))
            raise CommandError("FATAL: error. There is no GPCR in the simulation. Cannot continue.")
        prot=model_prot
        total_num_prot=1
    else:
        prot = DyndbProtein.objects.filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
        if not list(prot.values_list("receptor_id_protein",flat=True)):
            prot = prot.values('id','uniprotkbac')
            prot0 = prot[0]
            self.stdout.write(self.style.ERROR("Protein ID:%d UniprotKB AC:%s is not a GPCR or has no GPCRdb ID set.") % (prot0['id'],prot0['uniprotkbac']))
            raise CommandError("FATAL: error. There is no GPCR in the simulation. Cannot continue.") 
        protli=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
        total_num_prot=len(protli)
        prot=""
        for p in protli:
            if p.receptor_id_protein:
                prot=p
    return (prot,total_num_prot)

def obtain_dyn_files(dyn_id):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    traj_list=[]
    traj_name_list=[]
    structure_file = None
    structure_file_name = None
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

def get_orthostericlig_resname(dyn_id,change_lig_name):
    """Returns a list with the the resname of the orthosteric ligamd(s) of a dynamics"""
    ortholig_li=DyndbSubmissionMolecule.objects.filter(submission_id__dyndbdynamics=dyn_id,type=0)
    if len(ortholig_li) == 0:
        return (False,False,False)
    comp_set_all=set()
    for ortholig in ortholig_li:
        comp_li=DyndbDynamicsComponents.objects.filter(id_molecule=ortholig.molecule_id.id)
        comp_set=set(map(lambda x: x.resname ,comp_li)) 
        comp_set_all.update(comp_set)
    comp_obj=ortholig_li[0].molecule_id.id_compound #[!] For now I only consider 1 orthosteric ligand for each dyn!
    comp_id=comp_obj.id 
    comp_name=comp_obj.name
    if (dyn_id in change_lig_name):
        comp_name=change_lig_name[dyn_id]["longname"]
        comp_set_all=[change_lig_name[dyn_id]["resname"]] 
    return (comp_id,comp_name,list(comp_set_all))
        
def retrieve_info(self,dyn,data_dict,change_lig_name):
    """
    Retrieves all the necessary info of the dyn obj for the analysis and computes it.
    """

    #Getting information from model
    dyn_id=dyn.id
    identifier="dyn"+str(dyn_id)
    allfiles_path="/protwis/sites/files/"
    model=dyn.id_model
    model_id=model.id
    pdb_id=model.pdbid
    user=dyn.submission_id.user_id.username

    #IF no protein assigned
    if not (model.id_protein or model.id_complex_molecule):
        self.stdout.write(self.style.NOTICE("Model has no protein or complex assigned. Skipping."))
        return
    (prot,total_num_prot)=prot_from_model(model)
    prot_id=prot.id 
    uniprot_id=prot.uniprotkbac
    uniprot_name=Protein.objects.get(accession=uniprot_id).entry_name
    (structure_file,structure_file_name,traj_list,traj_name_list)=obtain_dyn_files(dyn_id)
    if not structure_file:
        self.stdout.write(self.style.NOTICE("No structure file found. Skipping."))
    (comp_id,comp_name,res_li)=get_orthostericlig_resname(dyn_id,change_lig_name) 

    # If there's no ligand
    if not bool(res_li):
        res_li = ['']
        copm_name = ''

    #Assign short name
    if dyn.entry:
        shortname = dyn.entry
    elif dyn.entry2:
        shortname = dyn.entry2
    else:
        shortname = ""

    if len(traj_list) == 0:
        self.stdout.write(self.style.NOTICE("No trajectories found. Skipping."))
    else:
        traj_files = [ i[0] for i in traj_list ]
        pdb_name = "/protwis/sites/files/"+structure_file
        (gpcr_pdb,classes_dict,current_class)=generate_gpcr_pdb(dyn_id, pdb_name, True)
        pdb_to_gpcr = {v: k for k, v in gpcr_pdb.items()}
        delta=DyndbDynamics.objects.get(id=dyn_id).delta
        data_dict[identifier]={
            "dyn_id": dyn_id,
            "class" : current_class,
            "prot_id": prot_id, 
            "comp_id": comp_id,
            "lig_lname":comp_name,
            "lig_sname":res_li[0],
            "prot_lname":prot.name,
            "prot_sname":shortname,
            "up_name":uniprot_name,
            "pdb_id":pdb_id,
            "struc_f":structure_file,
            "struc_fname":structure_file_name,
            "traj_f":traj_files,
            "traj_fnames":traj_name_list,
            "delta":delta,
            "gpcr_pdb":gpcr_pdb,
            "user":user,
            }
    dyn_dict = data_dict[identifier]

    return(dyn_dict,data_dict)

def get_ligand_file(dyn_id, identifier, directory, mypdbpath):
    """
    Write the required ligand file, a one-line tabular file with four columns:
    ResNUM   ChainID     ResID  LigName
    """
    # Obtain ligand by dynID
    (comp_li,lig_li,lig_li_s) = obtain_compounds(dyn_id)

    """    
    comp_li     list of [component_name,component_residue_name,component_type_str].
    lig_li      list of ligand [component_name,component_residue_name].
    lig_li_s    list of ligands residue names.
    """

    # Open out file
    ligfile_name = os.path.join(directory, identifier + "_ligand.txt")
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
        return(ligfile_name)


class Command(BaseCommand):
    help=""
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
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already stored data, calculating again the interactions for all the public dynamics stored at the DB.',
        )

    def handle(self, *args, **options):

        #################################################
        ## Trajectory, PDB files and JSON compl_data file
        #################################################
        
        if options['dynid'] or options['alldyn']:
            dynid = options['dynid']
            alldyn = options['alldyn']
        else:
            raise CommandError("Neither dynid(s) nor --all options have been specified. Use --help for more details.")

        # In this file will be stored all commands to run in ORI (for the computer-spending steps, you know)
        commands_path = "/protwis/sites/files/Precomputed/get_contacts_files/dyn_freq_commands.sh"

        #Prepare compl_data json file and the "last time modified" upd file
        cra_path="/protwis/sites/files/Precomputed/get_contacts_files"
        dyncounter = 1
        if not os.path.isdir(cra_path):
            os.makedirs(cra_path)
        compl_file_path=os.path.join(cra_path,"compl_info.json")
        compl_file_pathobj = Path(compl_file_path)
        try:
            compl_abs_path = compl_file_pathobj.resolve()
            compl_data = json_dict(compl_file_path)
        except FileNotFoundError:
            compl_data={}       
        
        # Extract dynamics information from database 
        if alldyn:
            dynobjs = DyndbDynamics.objects.filter(is_published=True)
        else:
            dynobjs = DyndbDynamics.objects.filter(id__in=dynid, is_published=True)

        #Annotate shortname alternatives
        dynobjs=dynobjs.annotate(entry=F('id_model__id_protein__receptor_id_protein__entry_name'))
        dynobjs=dynobjs.annotate(entry2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__entry_name'))

        #Open CSV file with already-done dynids, and loaded on a set
        dyn_list_file = os.path.join(cra_path, "processed_dyns.csv")
        if os.path.isfile(dyn_list_file):
            with open(dyn_list_file, "r") as file:
                dyn_set = set(file.readline().replace('\n','').split(","))
        else:
            dyn_set = set()

        ##################
        ###Begin iteration
        ##################

        for dyn in dynobjs:

            #Take dynamic identifiers (both dynX and X)
            dyn_id=dyn.id
            identifier="dyn"+str(dyn_id)

            #Unless user want to overwrite, omit already done dynids
            if (identifier in dyn_set) and not (options['overwrite']):
                self.stdout.write("%s has already been done. Skippping..." % dynid)
                continue
            else:
                dyn_set.add(identifier)

            #Compute compl_data fuke
            try:
                self.stdout.write(self.style.NOTICE("Computing dictionary for dynamics with id %d (%d/%d) ...."%(dyn_id, dyncounter, len(dynobjs))))
                dyncounter += 1
                dyn_dict,compl_data = retrieve_info(self,dyn,compl_data,change_lig_name)
            except FileNotFoundError:
                self.stdout.write(self.style.NOTICE("Files for dynamics with id %d are not avalible. Skipping" % (dyn_id)))
                continue

            if not dyn_dict['traj_fnames']:
                self.stdout.write("%s has no trajectory file. Skippping..." % dynid)
                continue
            structure_file = dyn_dict['struc_f']
            structure_file_name = dyn_dict['struc_fname']

            #Create directory for dynamic simulation id if it doesn't exists yet
            directory = os.path.join(settings.MEDIA_ROOT,"Precomputed/get_contacts_files/dynamic_symlinks/dyn" + str(dyn_id))
            if not os.path.exists(directory):
                os.makedirs(directory,exist_ok=True)

            #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
            basepath = settings.MEDIA_ROOT
            pdbpath = os.path.join(basepath,structure_file)
            
            #TO DO: idenfity structure files with an "struc" suffix, not only by extension
            #TO DO: add id_files number to the filename
            mypdbpath =  os.path.join(directory, identifier + os.path.splitext(structure_file)[1])
            if not os.path.lexists(mypdbpath):
                os.symlink(pdbpath, mypdbpath)
            
            #Links for trajectories
            traj_counter = 0
            for traj_name,traj_file in zip(dyn_dict['traj_fnames'],dyn_dict['traj_f']):
                #Create symbolic links also for trajectory file list
                #TO DO: add id_files number to the filename
                trajpath = os.path.join(basepath,traj_file)
                mytrajpath = os.path.join(directory,identifier + "_" + str(traj_counter) + os.path.splitext(trajpath)[1])
                if not os.path.lexists(mytrajpath):
                    os.symlink(trajpath, mytrajpath)
                traj_counter += 1

            #Ligand files
            try:
                ligfile_name = get_ligand_file(dyn_id, identifier, directory, mypdbpath)    
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
            with open(commands_path,"a") as commands_file:
                numtraj = len(dyn_dict['traj_fnames'])
                traj_counter = 0
                for traj_name,traj_file in zip(dyn_dict['traj_fnames'],dyn_dict['traj_f']):

                    trajpath = os.path.join(basepath,traj_file)
                    mytrajpath = os.path.join(directory,identifier + "_" + str(traj_counter) + os.path.splitext(trajpath)[1])
                    traj_counter += 1

                    if numtraj == traj_counter:
                        tail_comand = "--merge_dynamics \n"
                    else:
                        tail_comand = "\n"

                    commands_file.write(str("python /protwis/sites/protwis/contact_maps/scripts/get_contacts_dynfreq.py \
                        --dynid %s \
                        --traj %s \
                        --traj_id %s \
                        --topology %s \
                        --ligandfile %s \
                        --cores 4 %s" % (dyn_id, mytrajpath, traj_counter, mypdbpath, ligfile_name, tail_comand))
                    )  

        # Save compl_data.json
        with open(compl_file_path, 'w') as outfile:
            json.dump(compl_data, outfile)
            
        # Save dynnames in dynfile
        with open(dyn_list_file, 'w') as csvfile:
            csvfile.write(",".join(dyn_set))