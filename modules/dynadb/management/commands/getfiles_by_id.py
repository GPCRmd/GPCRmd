import sys
condapath = ['', '/opt/gpcrmdenv/lib/python3.9', '/opt/gpcrmdenv/lib/python3.9/plat-x86_64-linux-gnu', '/opt/gpcrmdenv/lib/python3.9/lib-dynload', '/opt/gpcrmdenv/lib/python3.9/site-packages']
sys.path = sys.path + condapath
import re
import string
import os
import shutil
import csv
from django.conf import settings
from modules.view.obtain_gpcr_numbering import generate_gpcr_pdb
from modules.view.data import change_lig_name
from modules.view.views import obtain_compounds, sort_by_myorderlist, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_rel_dicts, obtain_seq_pos_info, compute_interaction, obtain_all_chains, relate_atomSerial_mdtrajIndex
from django.db import models
from django.forms import ModelForm, Textarea
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from pathlib import Path
import pandas as pd
import json
import datetime
from modules.dynadb.models import DyndbModel, DyndbProtein, DyndbFilesDynamics, DyndbSubmissionMolecule, DyndbDynamicsComponents,DyndbModeledResidues, DyndbDynamics
from modules.protein.models import Protein
from modules.view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from modules.dynadb.pipe4_6_0 import *

from django.conf import settings

def parse_pdb(pdbfile, chainid_list = [], resname_list = [], resid_list = []):
    """ 
    Find and annotate residues that are identified as ligands
    """
    residues = set()
    #Select active variables
    yeschains = len(chainid_list) > 0
    yesresnames = len(resname_list) > 0    
    yesresids = len(resid_list) > 0
    active_conditions = sum([yeschains, yesresnames, yesresids])
    
    # Open and parse the structure PDB in search of ligand residues
    with open(pdbfile, "r") as f:
        for line in f:
            true_conditions = 0
            if line.startswith("END"): 
                break
            if line.startswith("ATOM") or line.startswith("HETATM"):
                line_chainid = line[21].strip()
                line_resname = line[17:21].strip()
                line_resid = line[22:26].strip()

                # For each line, check which conditions are active, and from those which are met
                if yeschains:
                    if line_chainid in chainid_list:
                        true_conditions += 1

                if yesresnames:
                    if line_resname in resname_list:
                        true_conditions += 1

                if yesresids:
                    if line_resid in resid_list:
                        true_conditions += 1

                # If residue meets all conditions, add it to the set of ligand residues
                if true_conditions == active_conditions:
                    residues.add(line_chainid+":"+line_resname+":"+line_resid)
    
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
    p=re.compile(f"({settings.MEDIA_ROOT})(.*)")
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
    return (comp_id,comp_name,list(comp_set_all)[0])# At one point I should prepare this for multiple ligands
        
def get_peptidelig(dyn_id):
    model=DyndbModel.objects.select_related("id_protein","id_complex_molecule").get(dyndbdynamics__id=dyn_id)
    if model.id_protein:
        dprot_li_all=[model.id_protein]
    else:
        dprot_li_all=DyndbProtein.objects.select_related("receptor_id_protein").filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=model.id_complex_molecule.id)
    prot_id = False
    name = False
    sel_s = False
    for dprot in dprot_li_all:
        if not dprot.receptor_id_protein:
            prot_id = dprot.id
            name=dprot.name
            sel_s= ":%s" % DyndbModeledResidues.objects.filter(id_protein=dprot.id)[0].chain.upper() 
    return(prot_id, name, sel_s)

def retrieve_info(self,dyn,data_dict,change_lig_name):
    """
    Retrieves all the necessary info of the dyn obj for the analysis and computes it.
    """

    #Getting information from model
    dyn_id=dyn.id
    identifier="dyn"+str(dyn_id)
    allfiles_path=settings.MEDIA_ROOT + ""
    model=dyn.id_model
    model_id=model.id
    pdb_id=model.pdbid
    user=dyn.submission_id.user_id.username
    is_ours = dyn.submission_id.is_gpcrmd_community

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

    # Ligand information
    peptide_ligand = False
    (comp_id,comp_name,res_li)=get_orthostericlig_resname(dyn_id,change_lig_name)
    if not comp_id:
        (comp_id,comp_name,res_li) = get_peptidelig(dyn_id)
        if comp_id:
            peptide_ligand = True

    # If there's no ligand
    if not bool(res_li):
        res_li = ''
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
        return({"traj_fnames" : False}, data_dict)
    else:
        traj_files = [ i[0] for i in traj_list ]
        pdb_name = settings.MEDIA_ROOT + ""+structure_file
        try: 
            (gpcr_pdb,classes_dict,current_class)=generate_gpcr_pdb(dyn_id, pdb_name, True)
        except Exception as e:
            self.stdout.write(self.style.NOTICE("GPCR residue nomenclature for this structure could not be obtained. Skipping."))
            return({"traj_fnames" : False}, data_dict)

        pdb_to_gpcr = {v: k for k, v in gpcr_pdb.items()}
        delta=DyndbDynamics.objects.get(id=dyn_id).delta
        data_dict[identifier]={
            "dyn_id": dyn_id,
            "class" : current_class,
            "prot_id": prot_id, 
            "comp_id": comp_id,
            "lig_lname": comp_name,
            "lig_sname":res_li,
            "prot_lname":prot.name,
            "prot_sname":shortname,
            "peplig":peptide_ligand,
            "up_name":uniprot_name,
            "pdb_id":pdb_id,
            "struc_f":structure_file,
            "struc_fname":structure_file_name,
            "traj_f":traj_files,
            "traj_fnames":traj_name_list,
            "delta":delta,
            "gpcr_pdb":gpcr_pdb,
            "user":user,
            "is_gpcrmd_community" : is_ours,
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
            lig_sel = ligand_info[1]

            #Omit peptide ligands for the moment
            #if re.match(":\w", ligres) is not None:
            #    continue

            # Take resname, resname and resid of the ligand
            ligchain_list = []
            ligresid_list = []
            if ':' in lig_sel: # In NGL selections, :L is the way to select a whole chain
                ligchain_list = re.findall(":(\w)", lig_sel)
            if 'and' in lig_sel: # If there is an "and" in the selection command, odds are that resid and resname of the ligand molecule are specified
                ligresid_list = re.findall(r"\b(\d+)\b", lig_sel)
            ligresname_list = re.findall("(^[A-Z0-9]{3})", lig_sel)# Residue name is almost always the first three characters

            #Parse in search of the ligand atoms that match the parameters above
            ligline_set = parse_pdb(mypdbpath, ligchain_list, ligresname_list, ligresid_list)
            for residueline in ligline_set:
                # To avoid taking as ligands POPCs or sodiums or clorides
                if not any(word in residueline for word in ['POPC','CLA','SOD']):
                    print(residueline,file=ligfile)

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
        commands_path = settings.MEDIA_ROOT + "Precomputed/get_contacts_files/dyn_freq_commands.sh"

        #Prepare compl_data json file and the "last time modified" upd file
        cra_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files"
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

        # Open one of the input files of Contact Maps to use it as reference to know which Simulations are already present
        dyns_in_contactmaps = cra_path+"/contmaps_inputs/all/cmpl/prt_lg/name_to_dyn_dict.json"
        if os.path.isfile(dyns_in_contactmaps):
            dynsnames_list = json_dict(dyns_in_contactmaps)
            dyn_set = { identifier for (identifier, name) in dynsnames_list }
        else:
            dyn_set = set()

        ##################
        ###Begin iteration
        ##################

        commands_line = ""
        for dyn in dynobjs:

            #Take dynamic identifiers (both dynX and X)
            dyn_id=dyn.id
            identifier="dyn"+str(dyn_id)

            #Unless user want to overwrite, omit already done dynids
            if (identifier in dyn_set) and not (options['overwrite']):
                self.stdout.write("%s has already been done. Skippping..." % dyn_id)
                continue
            else:
                dyn_set.add(identifier)

            #Compute compl_data file
            try:
                self.stdout.write(self.style.NOTICE("Computing dictionary for dynamics with id %d (%d/%d) ...."%(dyn_id, dyncounter, len(dynobjs))))
                dyncounter += 1
                dyn_dict,compl_data = retrieve_info(self,dyn,compl_data,change_lig_name)
            except FileNotFoundError:
                self.stdout.write(self.style.NOTICE("Files for dynamics with id %d are not avalible. Skipping" % (dyn_id)))
                continue

            # Skip if no trajectory
            if not dyn_dict['traj_fnames']:
                self.stdout.write("%s has no trajectory file. Skippping..." % dyn_id)
                continue
            structure_file = dyn_dict['struc_f']
            structure_file_name = dyn_dict['struc_fname']

            #Create directory for dynamic simulation id if it doesn't exists yet
            directory = os.path.join(settings.MEDIA_ROOT,"Precomputed/get_contacts_files/dynamic_symlinks/dyn" + str(dyn_id))
            if not os.path.exists(directory):
                os.makedirs(directory,exist_ok=True)

            #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
            basepath = settings.MEDIA_ROOT[:-1]
            pdbpath = os.path.join(basepath,structure_file)
            
            #TO DO: idenfity structure files with an "struc" suffix, not only by extension
            #TO DO: add id_files number to the filename
            mypdbpath =  os.path.join(directory, identifier + os.path.splitext(structure_file)[1])
            if not os.path.lexists(mypdbpath):
                os.symlink(pdbpath, mypdbpath)
            
            #Links for trajectories
            for traj_name,traj_file in zip(dyn_dict['traj_fnames'],dyn_dict['traj_f']):
                #Create symbolic links also for trajectory file list
                traj_id = traj_name.split("_")[0]
                trajpath = os.path.join(basepath,traj_file)
                mytrajpath = os.path.join(directory,identifier + "_" + str(traj_id) + os.path.splitext(trajpath)[1])
                if not os.path.lexists(mytrajpath):
                    os.symlink(trajpath, mytrajpath)

            #Ligand files
            try:
                ligfile_name = get_ligand_file(dyn_id, identifier, directory, mypdbpath)
            except Exception:
                 self.stdout.write(self.style.WARNING("Error while processing dynamics "+str(dyn_id)+". Skipping and cleaning up."))
                 shutil.rmtree(directory)
                 continue

            ###########################################
            ## Compute frequencies and dynamic contacts
            ###########################################

            # for each trajectory file, write a run-in-ORI command
            numtraj = len(dyn_dict['traj_fnames'])
            traj_counter = 0
            for traj_name,traj_file in zip(dyn_dict['traj_fnames'],dyn_dict['traj_f']):

                trajpath = os.path.join(basepath,traj_file)
                traj_id = traj_name.split("_")[0]
                mytrajpath = os.path.join(directory,identifier + "_" + traj_id + os.path.splitext(trajpath)[1])
                traj_counter += 1

                if numtraj == traj_counter:
                    tail_comand = "--merge_dynamics \n"
                else:
                    tail_comand = "\n"

                commands_line += str("/opt/gpcrmdenv/bin/activate;python "+ settings.MODULES_ROOT + "/contact_maps/scripts/get_contacts_dynfreq.py \
                    --dynid %s \
                    --traj %s \
                    --topology %s \
                    --ligandfile %s \
                    --cores 4 %s\n" % (dyn_id, mytrajpath, mypdbpath, ligfile_name, tail_comand))

        # Save commands in commands file
        with open(commands_path,"w") as commands_file:
            commands_file.write(commands_line)

        # Save compl_data.json
        with open(compl_file_path, 'w') as outfile:
            json.dump(compl_data, outfile, indent=2)
            