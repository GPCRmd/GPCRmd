import re
from os import path
import gc

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F

from modules.dynadb.models import DyndbSubmission, DyndbDynamics
from modules.dynadb.models import DyndbSubmissionProtein, DyndbSubmissionMolecule, DyndbSubmissionModel, DyndbFilesMolecule, DyndbFilesModel , DyndbFilesDynamics, DyndbFiles
from modules.dynadb.views import  get_precomputed_file_path, get_file_name , get_file_name_dict, get_file_paths

from modules.view.create_fplot import *
from django.conf import settings

class Command(BaseCommand):
    help = "Creates precomputed JSON files for posterior creation of flare plots. By default, all 'ready for publication' dynamics will be considered. If the json file for a given dynamics trajectory altrady exists, it is not overwritten."
    def add_arguments(self, parser):
        parser.add_argument(
           '--sub',
            dest='submission_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify submission id(s) for which json file will be precomputed.'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) for which json file will be precomputed. '
        )
        parser.add_argument(
           '--traj',
            dest='traj_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify file id(s) of trajectories for which a json file will be precomputed. '
        )
        parser.add_argument(
            '--type',
            dest='consider_comp_type', 
            nargs='?',
            choices=['hbonds','all'],
            action='store',
            default='all',
            help='Type of computation. Precomputed files for all the computation types will be created if nothing is specified.'
        )
        
        parser.add_argument(
            '--str',
            dest='stride', 
            nargs='?',
            action='store',
            default=1,
            type=int,
            help='Stride the trajectories.'
        )
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated json files.',
        )
        parser.add_argument(
            '--exit-on-error',
            action='store_true',
            dest='exit-on-error',
            default=False,
            help='Stop execution and display traceback if any error takes place while generating json files.',
        )

    def handle(self, *args, **options):
        hb_json_path=settings.MEDIA_ROOT + "Precomputed/flare_plot/hbonds"
        if not os.path.isdir(hb_json_path):
            os.makedirs(hb_json_path)
        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['submission_id']:
            dynobj=dynobj.filter(submission_id__in=options['submission_id'])
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])

        dynobj=dynobj.annotate(traj_id=F('dyndbfilesdynamics__id_files__id'))
        if options['traj_id']:
            dynobj=dynobj.filter(traj_id__in=options['traj_id'])
            
        #get trajectory filepaths
        trajfiles = dynobj.annotate(dyn_id=F('id'))
        trajfiles = trajfiles.annotate(is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
        trajfiles = trajfiles.filter(is_traj=True)
        trajfiles = trajfiles.annotate(filepath=F('dyndbfilesdynamics__id_files__filepath'))
        trajfiles = trajfiles.values('dyn_id','traj_id','filepath')
 
        #create a dictionary with needed information 
        dyn_dict = {}
        for traj in trajfiles:
            if traj['dyn_id'] not in dyn_dict:
                dyn_dict[traj['dyn_id']] = dict()
                dyn_dict[traj['dyn_id']]['dyn_id'] = traj['dyn_id']
                dyn_dict[traj['dyn_id']]['pdbpath'] = None
                dyn_dict[traj['dyn_id']]['traj_files'] = dict()
            if traj['traj_id'] is None:
                continue
            dyn_dict[traj['dyn_id']]['traj_files'][traj['traj_id']] = dict()
            dyn_dict[traj['dyn_id']]['traj_files'][traj['traj_id']]['id'] = traj['traj_id']
            dyn_dict[traj['dyn_id']]['traj_files'][traj['traj_id']]['filepath'] = traj['filepath']
        
        del trajfiles
        del dynobj
        
        gc.collect() # free memory right now!!
        
        #get PDB filepaths
        pdbfiles = DyndbFiles.objects.annotate(dyn_id=F('dyndbfilesdynamics__id_dynamics'))
        pdbfiles = pdbfiles.filter(dyn_id__in=list(dyn_dict), id_file_types=2)
        pdbfiles = pdbfiles.values('dyn_id','filepath')
       
        #add PDB filepaths to the dictionary
        for pdbfile in pdbfiles:
            dyn_dict[pdbfile['dyn_id']]['pdbpath'] = pdbfile['filepath']
        del pdbfiles
        gc.collect()
        
        if len(dyn_dict.keys()) == 0:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))
        #self.stdout.write(self.style.NOTICE("%d published dynamics found."%len(dynobj)))

        #transform dictionaries into sorted lists
        dyn_list = [dyn_dict[dyn_id] for dyn_id in sorted(list(dyn_dict))]
        del dyn_dict
        gc.collect()
        
        for dyn in dyn_list:
            dyn['traj_files'] = [dyn['traj_files'][traj_id] for traj_id in sorted(list(dyn['traj_files']))]
        gc.collect()
        


        strideVal=abs(options["stride"])
        if options['consider_comp_type']=="all" or options['consider_comp_type']=="hbonds":
            newdir = get_precomputed_file_path('flare_plot',"hbonds",url=False)
            for dyn in dyn_list:
                dyn_id = dyn['dyn_id']
                self.stdout.write(self.style.NOTICE("\nDynamics id: %d"%dyn_id))
                if len(dyn['traj_files']) == 0:
                    self.stdout.write(self.style.NOTICE("No trajectories found for dynamics ID "+str(dyn_id)+". Skipping..."))
                    continue
                pdbpath = dyn['pdbpath']
                if not pdbpath:
                    self.stdout.write(self.style.NOTICE("No PDB file found for dynamics ID "+str(dyn_id)+". Skipping..."))
                    continue
                for traj in dyn['traj_files']:
                    traj_id = traj['id']
                    trajpath=traj['filepath']
                    newfilename = get_file_name(objecttype="dynamics",fileid=traj_id,objectid=dyn_id,ext="json",forceext=True,subtype="trajectory") #suffix="_hbonds" , remove forceext=True
                    
                    ###########[!] Change get_file_name() to obtain it automatically
                    (pre,post)=newfilename.split(".")
                    add=""
                    if strideVal > 1:
                        add+="_str"+str(strideVal)
                    newfilename=pre+"_hbonds"+add+"."+post
                    ###########
                    
                    newpath = path.join(newdir,newfilename)
                    exists=path.isfile(newpath)
                    generate_json=False
                    if exists:                    
                        if options['overwrite']:
                            generate_json=True
                            self.stdout.write(self.style.NOTICE("Flareplot "+newfilename+" already exists, but will be overwritten."))
                        else:
                            self.stdout.write(self.style.NOTICE("Skipping flareplot "+newfilename+": already exists."))
                    else:
                        generate_json=True
                    if generate_json:
                        self.stdout.write(self.style.NOTICE("Creating flareplot "+newfilename+"..."))
                        try:
                            create_fplot(self,dyn_id=dyn_id,newpath=newpath,pdbpath=pdbpath,trajpath=trajpath,stride=strideVal)
                        except Exception as e:
                            if options['exit-on-error']:
                                raise
                            self.stdout.write(self.style.ERROR(type(e).__name__+': '+str(e)))
                            self.stdout.write(self.style.NOTICE("Skipping flareplot "+newfilename+": error during flareplot generation."))
                        gc.collect()
