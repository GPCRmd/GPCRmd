from django.core.management.base import BaseCommand, CommandError
from modules.dynadb.models import DyndbSubmission, DyndbProtein, DyndbCompound, DyndbDynamics, DyndbMolecule,  DyndbComplexExp, DyndbComplexMolecule, DyndbModel
from modules.dynadb.models import DyndbSubmissionProtein, DyndbSubmissionMolecule, DyndbSubmissionModel, DyndbFilesMolecule, DyndbFilesModel , DyndbFilesDynamics, DyndbFiles
from modules.dynadb.views import get_file_name, get_file_name_dict, get_file_paths
from django.db.models import Count, F, Value as V, SmallIntegerField
from django.db.models import TextField
import re
from os import path, rename as os_rename
import shutil
import time 

class Command(BaseCommand):
    help = 'Prepare the files into Ori for the precompute processing.'
    
    def add_arguments(self, parser):
        parser.add_argument(
           'dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Sets dynamics ids as_published=True on DyndbDynamics. This action marks as ready for precomputation process.',
        )       
    
    def handle(self, *args, **options):
        
        if options["dynamics_id"]:
            options["dynamics_id"] =[ele.replace(",","") for ele in options["dynamics_id"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {options['dynamics_id']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in options['dynamics_id']:
                try:
                    obj = DyndbDynamics.objects.get(id=dyn_id)
                    if obj.is_published == False:
                        obj.is_published = True
                        obj.save()
                    object_ready.append(dyn_id)
                except:
                    object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are READY for precomputing: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are UNREADY for precomputing: {object_unready}'))

                    
        print("Exit!")