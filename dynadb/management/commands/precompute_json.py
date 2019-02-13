from django.core.management.base import BaseCommand, CommandError
from dynadb.models import DyndbSubmission, DyndbDynamics
from dynadb.models import DyndbSubmissionProtein, DyndbSubmissionMolecule, DyndbSubmissionModel, DyndbFilesMolecule, DyndbFilesModel , DyndbFilesDynamics, DyndbFiles
from dynadb.views import  get_precomputed_file_path, get_file_name , get_file_name_dict, get_file_paths
import re
from os import path
from view.create_fplot import *

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
            help='Specify id(s) of trajectories for which a json file will be precomputed. '
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
    def handle(self, *args, **options):
        hb_json_path="/protwis/sites/files/Precomputed/flare_plot/hbonds"
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
        if options['traj_id']:
            dynobj=dynobj.filter(dyndbfilesdynamics__id_files__id__in=options['traj_id']).distinct()
        if dynobj == []:
            self.stdout.write(self.style.NOTICE("No published dynamics found."))
        #self.stdout.write(self.style.NOTICE("%d published dynamics found."%len(dynobj)))
        strideVal=abs(options["stride"])
        if options['consider_comp_type']=="all" or options['consider_comp_type']=="hbonds":
            newdir = get_precomputed_file_path('flare_plot',"hbonds",url=False)
            for dyn in dynobj:
                dyn_id=dyn.id
                self.stdout.write(self.style.NOTICE("\nDynamics id: %d"%dyn_id))
                trajfiles=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types__is_trajectory=True)
                if options['traj_id']:
                    trajfiles=trajfiles.filter(id__in=options['traj_id'])
                pdbfile=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics=dyn_id, id_file_types=2)
                if pdbfile:
                    pdbpath=pdbfile[0].filepath
                else:
                    continue
                for traj in trajfiles:
                    newfilename = get_file_name(objecttype="dynamics",fileid=traj.id,objectid=dyn_id,ext="json",forceext=True,subtype="trajectory") #suffix="_hbonds" , remove forceext=True
                    
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
                            create_fplot(self,dyn_id=dyn_id,newpath=newpath,pdbpath=pdbpath,trajpath=traj.filepath,stride=strideVal)
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(type(e).__name__+': '+str(e)))
                            self.stdout.write(self.style.NOTICE("Skipping flareplot "+newfilename+": error during flareplot generation."))
                        
