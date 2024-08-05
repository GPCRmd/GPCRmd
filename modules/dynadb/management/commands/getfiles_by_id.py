import sys
condapath = ['', '/opt/gpcrmdenv/lib/python3.9', '/opt/gpcrmdenv/lib/python3.9/plat-x86_64-linux-gnu', '/opt/gpcrmdenv/lib/python3.9/lib-dynload', '/opt/gpcrmdenv/lib/python3.9/site-packages']
sys.path = sys.path + condapath
import re
import os
from django.conf import settings
from modules.view.data import change_lig_name
from modules.view.views import obtain_compounds,  get_gpcr, get_gprot, get_peptidelig, get_arr
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import json
from modules.dynadb.models import DyndbModel, DyndbProtein, DyndbFilesDynamics, DyndbSubmissionMolecule, DyndbDynamicsComponents,DyndbModeledResidues, DyndbDynamics
from modules.protein.models import Protein
from modules.dynadb.obtain_generic_numbering import obtain_class,generic_numbering 
from modules.dynadb.pipe4_6_0 import *
import traceback
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

def prot_from_model(self, model):
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

def uniprots_from_dynid(dyn_id):
    """Given a db dynamics id, returns the Uniprot Ids of the proteins present associated to it"""
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id__dyndbdynamics__pk=dyn_id)
    uniprots = [a.uniprotkbac for a in DP ]
    return(uniprots)

def gprot_within_uniprots(uniprots):
    """Given a list of uniprot ids, determine if any of its proteins is a G-alpha subunit of a G-protein"""
    has_gprot = False
    for uniprot in uniprots:
        P = Protein.objects.filter(accession=uniprot)
        if len(P) and (P[0].residue_numbering_scheme.name == 'Common G-alpha numbering scheme'):
            has_gprot=True
    return(has_gprot)

def gpcr_dyn_id(dyn_id):
    """
    Given a dyn_id, determine if any of its proteins is a GPCR. 
    Return corresponding Protein and DyndbProtein objects
    """
    gpcr_chain = False
    dp_gpcr = False
    p_gpcr = False
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id__dyndbdynamics__pk=dyn_id)
    dm = DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id__dyndbdynamics__id=dyn_id)[0]
    for dp in DP:
        if dp.prot_type==1:
            gpcr_chain=  DyndbModeledResidues.objects.filter(id_protein=dp.id,id_model=dm.pk)[0].chain.upper() 
            dp_gpcr = dp
            p_gpcr = dp.receptor_id_protein
    return(gpcr_chain,dp_gpcr,p_gpcr)

def obtain_dyn_files(dyn_id):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    traj_list=[]
    traj_name_list=[]
    structure_file = False
    structure_file_name = False
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

def obtain_files_from_dyn(dyn_id):
    """
    An easier, improved way of obtianing the paths to the files of a Dynamic
    (for christ's sake, that function above is a fucking nightmare)
    """
    # Select all files in this dynamic
    DFD = DyndbFilesDynamics.objects.filter(id_dynamics=dyn_id)
    topo_file = False
    struc_file = False
    struc_file_name = False
    traj_files = []
    traj_files_names = []
    framenums = []
    for dfd in DFD:
        file_type = dfd.type
        if file_type == 0: # If it is coordinate file
            struc_file = dfd.id_files.filepath
            struc_file_name = dfd.id_files.filename
        elif file_type == 1:
            topo_file = dfd.id_files.filepath
        elif file_type == 2: # If it is trajectory
            traj_files.append(dfd.id_files.filepath)
            traj_files_names.append(dfd.id_files.filename)
            framenums.append(dfd.framenum)
            
    return (struc_file,struc_file_name,topo_file,traj_files,traj_files_names,framenums)

def get_orthostericlig_resname(dyn_id,change_lig_name):
    """Returns a list with the the resname of the orthosteric ligamd(s) of a dynamics"""
    DSM=DyndbSubmissionMolecule.objects.filter(submission_id__dyndbdynamics=dyn_id,type=0)
    if not len(DSM):
        return (False,False,False)
    
    # For now, we only take one orthosteric ligand per system
    ddc_id = False
    lig_resname = False
    lig_name = False
    for dsm in DSM:
        ddc = DyndbDynamicsComponents.objects.get(id_molecule=dsm.molecule_id.id,id_dynamics=dyn_id)
        ddc_id = ddc.pk
        lig_resname = ddc.resname
        lig_name = ddc.id_molecule.id_compound.name

    # There are couple of exceptions (in views/data.py, systems with specific cholesterols as aligands and this stuff)
    if (dyn_id in change_lig_name):
        lig_name=change_lig_name[dyn_id]["longname"]
        lig_resname=[change_lig_name[dyn_id]["resname"]] 
    return (ddc_id,lig_name,lig_resname)

def retrieve_info(self,dyn,data_dict,change_lig_name,overwrite):
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
    (arr_name,arr_chain) = get_arr(dyn_id)
    (gprot_name_alpha, gprot_chain_a, gprot_chain_b, gprot_chain_g) = get_gprot(dyn_id)
    (gpcr_chain,dbprot_gpcr,prot_gpcr) = get_gpcr(dyn_id)
    dbprot_id = dbprot_gpcr.pk if dbprot_gpcr else False
    lname = dbprot_gpcr.name if dbprot_gpcr else False
    # (prot,total_num_prot)=prot_from_model(model)
    # Obtain uniprot name of GPCR ONLY if we have a GPCR here
    (struc_file,struc_file_name,topo_file,traj_files,traj_files_names,framenums)=obtain_files_from_dyn(dyn_id) 
    if not struc_file_name:
        self.stdout.write(self.style.NOTICE("No structure file found. Skipping."))

    # Extract Ligand information
    peplig_chain = False; lig_sel = ''; lig_name = ''
    (comp_id,lig_name,lig_sel)=get_orthostericlig_resname(dyn_id,change_lig_name)
    if not comp_id:
        (comp_id,lig_name,peplig_chain) = get_peptidelig(dyn_id)
        lig_sel = peplig_chain

    #Assign short name for dynamic
    up_name_gpcr = prot_gpcr.entry_name if prot_gpcr else False
    shortname = up_name_gpcr

    # Check if trajectories really exist
    if len(traj_files) == 0:
        self.stdout.write(self.style.NOTICE("No trajectories found. Skipping."))
        return({"traj_fnames" : False}, data_dict)
    else:
        # Find GPCR class
        gpcr_class = obtain_class(dyn_id)

        # Find GPCR numbering and class if any GPCR actually present in model 
        # Extract it from file if already calculated
        gennum = {'gpcr' : {}, 'gprot' : {}, 'arr' : {}}
        mod = False
        for prot in gennum.keys():
            gennum_path = "%s/Precomputed/gennum/dyn%d.json"%(settings.MEDIA_ROOT,dyn_id)
            if os.path.exists(gennum_path) and not overwrite:
                gennum = json_dict(gennum_path)
            elif not (prot in gennum) or not gennum[prot]:    
                mod = True
                gennum[prot] = (generic_numbering(dyn_id,prot))
        # Save gennum in a file, if not existing yet
        if mod:
            with open(gennum_path,'w') as out:
                json.dump(gennum, out, indent=4)

        # Put all the information of this dynamic entry into a big dictionary
        delta=DyndbDynamics.objects.get(id=dyn_id).delta
        data_dict[identifier]={
            "dyn_id": dyn_id,
            "class" : gpcr_class, 
            "prot_id": dbprot_id, 
            "comp_id": comp_id,
            "lig_lname": lig_name,
            "lig_sname":lig_sel,
            "prot_lname":lname,
            "arr_name" : arr_name,
            "gprot_name":gprot_name_alpha,
            "prot_sname":shortname,
            "peplig":peplig_chain,
            "arr_chain":arr_chain,
            "gprot_chain_a":gprot_chain_a,
            "gprot_chain_b":gprot_chain_b,
            "gprot_chain_g":gprot_chain_g,
            "gpcr_chain":gpcr_chain,
            "up_name":up_name_gpcr,
            "pdb_id":pdb_id,
            "topo_f":topo_file,
            "struc_f":struc_file,
            "struc_fname":struc_file_name,
            "traj_f":traj_files,
            "traj_fnames":traj_files_names,
            "framenums" : framenums,
            "delta":delta,
            "gpcr_pdb":gennum['gpcr'], 
            "gprot_pdb":gennum['gprot'],
            "arr_pdb":gennum['arr'],
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
            help='Recalculate generic numbering data for this dynamic',
        )

    def handle(self, *args, **options):

        #################################################
        ## Trajectory, PDB files and JSON compl_data file
        #################################################
        
        if options['dynid'] or options['alldyn']:
            dynid = options['dynid']
            alldyn = options['alldyn']
            overwrite = options['overwrite']
        else:
            raise CommandError("Neither dynid(s) nor --all options have been specified. Use --help for more details.")

        #Prepare compl_data json file and the "last time modified" upd file
        cra_path=settings.MEDIA_ROOT + "Precomputed/"
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
            dynobjs = DyndbDynamics.objects.all()
        else:
            dynobjs = DyndbDynamics.objects.filter(id__in=dynid)

        ##################
        ###Begin iteration
        ##################

        commands_line = ""
        for dyn in dynobjs:
            try:

                self.stdout.write(self.style.NOTICE("Computing dictionary for dynamics with id %d (%d/%d) ...."%(dyn.id, dyncounter, len(dynobjs))))
                dyncounter += 1
                dyn_dict,compl_data = retrieve_info(self,dyn,compl_data,change_lig_name,overwrite)

            except Exception as e:
                self.stdout.write(self.style.NOTICE("Could not process %s because of %s" % (dyn.id,e)))
                print(traceback.format_exc())

        # Save compl_data.json
        with open(compl_file_path, 'w') as outfile:
            json.dump(compl_data, outfile, indent=2)
