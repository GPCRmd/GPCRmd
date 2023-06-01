from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
import os
from os import path
import pandas as pd
import json
import datetime
import re
from modules.view.obtain_gpcr_numbering import generate_gpcr_pdb
from modules.view.views import compute_interaction, obtain_all_chains, relate_atomSerial_mdtrajIndex
from modules.view.data import change_lig_name
from modules.dynadb.models import DyndbProtein, DyndbFilesDynamics, DyndbSubmissionMolecule, DyndbDynamicsComponents,DyndbModeledResidues, DyndbDynamics
from modules.protein.models import Protein
from modules.view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from modules.dynadb.pipe4_6_0 import *
from modules.view.views import obtain_prot_chains , obtain_DyndbProtein_id_list, obtain_seq_pos_info, findGPCRclass, obtain_rel_dicts, translate_all_poslists_to_ourclass_numb,obtain_predef_positions_lists,find_missing_positions
import copy
import operator
from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from django.conf import settings


class Command(BaseCommand):
    help = "Creates precomputed datafiles of ligand-residue interactons in the GPCRs stored at the database for posterior creation of comparaive plots. Only considers published data."
    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already stored data, calculating again the interactions for all the public dynamics stored at the DB.',
        )
        parser.add_argument(
            '--do_classdict',
            action='store_true',
            dest='do_classdict',
            default=False,
            help='If selected, adds positions of the protein of the computed simulations to the GPCRnomenclatures dictionary',
        )

#        parser.add_argument(
#           '-dyn_id',
#            dest='dyn_id',
#            nargs='*',
#            action='store',
#            default=False,
#            help='Dynamics id(s) for which lihand-residue interactions will be precomputed. All dynamics which are "ready for publication" and were not precumputed before will be admitted if no #id(s) are provided.'
#        )
#        parser.add_argument(
#            '-str',
#            dest='stride', 
#            nargs='?',
#            action='store',
#            default=1,
#            type=int,
#            help='Stride the trajectories.'
#        )
        
    def handle(self, *args, **options):
    
        def json_dict(path):
            """Converts json file to pyhton dict."""
            json_file=open(path)
            json_str = json_file.read()
            json_data = json.loads(json_str)
            return json_data

        def create_class_position_dict(classdict_gpcr, class_gpcr):
            """
            Reorganizes data in classdict_gpcr (Being GPCR of class B, the structure of this dictionary is something like: 
            1.34 : { C: 1.37, A: 1.38, F: 1.40  }). 
            The data is stored in a Json with four dictionaries, one for each GPCRclass, with its equivalences in the other classes
            """

            #Declaring variables
            class_letters = set(('A','B','C','F'))

            #Open and load existing dictionary, if any
            classdict_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files/GPCRnomenclatures_dict.json"
            if os.path.isfile(classdict_path):
                classdict = json_dict(classdict_path)
            else:
                classdict = {'A' : {}, 'B' : {}, 'C' : {}, 'F' : {}}

            #For every position in the processed gpcr
            pos_equivalents = {}
            for pos in classdict_gpcr:

                #For every class not of the current GPCR's class, assign an equivalent
                for class_letter in class_letters:
                    if class_letter == class_gpcr:
                        continue
                    pos_equivalents[class_letter] = classdict_gpcr[pos][class_letter]  
                pos_equivalents[class_gpcr] = pos

                # Create dictionary to print in json: class_letter -> position -> equivalentA & equivalentB & equivalentC & equivalentF
                for class_letter in class_letters:
                    joint_eqs_with_helix = '&'.join((pos_equivalents['A'],pos_equivalents['B'],pos_equivalents['C'],pos_equivalents['F']))
                    classdict[class_letter][pos_equivalents[class_letter]] = re.sub('&\d+x','x', joint_eqs_with_helix)

            #Store modified dictionary as Json file
            with open(classdict_path, 'w') as outfile:
                json.dump(classdict, outfile, sort_keys=True, indent=4)

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
            p=re.compile("(" + settings.MEDIA_ROOT + ")(.*)")
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
            allfiles_path=settings.MEDIA_ROOT + ""
            model=dyn.id_model
            model_id=model.id
            pdb_id=model.pdbid
            user=dyn.submission_id.user_id.username
            is_gpcrmd_community=dyn.submission_id.is_gpcrmd_community

            #IF no protein assigned
            if not (model.id_protein_id or model.id_complex_molecule_id):
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
                pdb_name = settings.MEDIA_ROOT + ""+structure_file
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
                    "user": user,
                    "is_gpcrmd_community" : is_gpcrmd_community
                    }

            return(data_dict)

        def update_time(upd,upd_now):
            year=upd_now.year
            month=upd_now.month
            day=upd_now.day
            hour=upd_now.hour
            minute=upd_now.minute
            second=upd_now.second
            microsecond =upd_now.microsecond
            updtime=upd["ligres_int"]
            updtime["year"]=year
            updtime["month"]=month
            updtime["day"]=day
            updtime["hour"]=hour
            updtime["minute"]=minute
            updtime["second"]=second
            updtime["microsecond"]=microsecond
            
        def obtain_datetime(upd):
            u=upd["ligres_int"]
            last_upd_dt=datetime.datetime(u["year"], u["month"], u["day"], u["hour"], u["minute"], u["second"], u["microsecond"])
            return last_upd_dt
    
        cra_path=settings.MEDIA_ROOT + "Precomputed/get_contacts_files"
        if not os.path.isdir(cra_path):
            os.makedirs(cra_path)
        upd_now=datetime.datetime.now()
        compl_file_path=path.join(cra_path,"compl_info.json")
        upd_file_path=path.join(cra_path,"last_update.json")
        if options['overwrite']:
            compl_data={}
            upd={"ligres_int":{}}
        else: 
            compl_file_pathobj = Path(compl_file_path)
            try:
                compl_abs_path = compl_file_pathobj.resolve()
                compl_data = json_dict(compl_file_path)
            except FileNotFoundError:
                compl_data={}       
            upd_file_pathobj = Path(upd_file_path)
            try:
                upd_abs_path = upd_file_pathobj.resolve()
                upd=json_dict(upd_file_path)
                last_upd_dt=obtain_datetime(upd)
            except FileNotFoundError:
                upd={"ligres_int":{}}

        #Annotate shortname alternatives
        dynobjs=DyndbDynamics.objects.filter(is_published=True)
        dynobjs=dynobjs.annotate(entry=F('id_model__id_protein__receptor_id_protein__entry_name'))
        dynobjs=dynobjs.annotate(entry2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__entry_name'))

        i=1
        for dyn in dynobjs:
            try:
                self.stdout.write(self.style.NOTICE("Computing dictionary for dynamics with id %d (%d/%d) ...."%(dyn.id,i , len(dynobjs))))
                retrieve_info(self,dyn,compl_data,change_lig_name)
            except FileNotFoundError:
                self.stdout.write(self.style.NOTICE("Files for dynamics with id %d are not avalible. Skipping" % (dyn.id)))
            i+=1

        update_time(upd,upd_now)
        with open(upd_file_path, 'w') as outfile:
            json.dump(upd, outfile)
        with open(compl_file_path, 'w') as outfile:
            json.dump(compl_data, outfile)