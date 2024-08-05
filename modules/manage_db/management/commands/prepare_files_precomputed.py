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
           '--prepare_ids',
            nargs='*',
            action='store',
            default=False,
            help='Sets dynamics ids as is_published=True on DyndbDynamics. This action marks as ready for precomputation process. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
    
        parser.add_argument(
           '--unprepare_ids',
            nargs='*',
            action='store',
            default=False,
            help='Sets dynamics ids as is_published=False on DyndbDynamics. This action marks as unready for precomputation process. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
        
        parser.add_argument(
           '--publish_ids',
            nargs='*',
            action='store',
            default=False,
            help='Sets dynamics ids as is_published=True on DyndbSubmissions. This action marks as published the dynamic/s. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
        
        parser.add_argument(
           '--unpublish_ids',
            nargs='*',
            action='store',
            default=False,
            help='Sets dynamics ids as is_published=False on DyndbSubmissions. This action marks as unpublished the dynamic/s. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
    
        parser.add_argument(
           '--is_gpcrmd_ids',
            nargs='*',
            action='store',
            default=False,
            help='Sets submissions ids as is_gpcrmd_community=True on DyndbSubmissions. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        )  
    
    def handle(self, *args, **kwargs):
        
        if kwargs["prepare_ids"]:
            kwargs["prepare_ids"] =[ele.replace(",","") for ele in kwargs["prepare_ids"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {kwargs['prepare_ids']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in kwargs['prepare_ids']:
                if "-" in dyn_id: #To avoid write every number we incorporate ranges using min-max structure
                    dyn_id = dyn_id.replace(" ","")
                    l_dyn_id = dyn_id.split("-")
                    l_dyn_id = [int(x) for x in l_dyn_id]
                    l_dyn_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_dyn_id = range(l_dyn_id[0],l_dyn_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_dyn_id:
                        try:
                            obj = DyndbDynamics.objects.get(id=x)
                            if obj.is_published == False:
                                obj.is_published = True
                                obj.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    try:
                        obj = DyndbDynamics.objects.get(id=dyn_id)
                        if obj.is_published == False:
                            obj.is_published = True
                            obj.is_ready_for_publication = True
                            obj.save()
                        object_ready.append(dyn_id)
                    except:
                        object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are READY for precomputing: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are UNREADY for precomputing: {object_unready}'))
        
        if kwargs["unprepare_ids"]:
            kwargs["unprepare_ids"] =[ele.replace(",","") for ele in kwargs["unprepare_ids"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {kwargs['unprepare_ids']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in kwargs['unprepare_ids']:
                if "-" in dyn_id: #To avoid write every number we incorporate ranges using min-max structure
                    dyn_id = dyn_id.replace(" ","")
                    l_dyn_id = dyn_id.split("-")
                    l_dyn_id = [int(x) for x in l_dyn_id]
                    l_dyn_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_dyn_id = range(l_dyn_id[0],l_dyn_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_dyn_id:
                        try:
                            obj = DyndbDynamics.objects.get(id=x)
                            if obj.is_published == True:
                                obj.is_published = False
                                obj.is_ready_for_publication = False
                                obj.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    try:
                        obj = DyndbDynamics.objects.get(id=dyn_id)
                        if obj.is_published == True:
                            obj.is_published = False
                            obj.save()
                        object_ready.append(dyn_id)
                    except:
                        object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are UNREADY for precomputing: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are READY for precomputing: {object_unready}'))
        
        if kwargs["publish_ids"]:
            kwargs["publish_ids"] =[ele.replace(",","") for ele in kwargs["publish_ids"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {kwargs['publish_ids']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in kwargs['publish_ids']:
                if "-" in dyn_id: #To avoid write every number we incorporate ranges using min-max structure
                    dyn_id = dyn_id.replace(" ","")
                    l_dyn_id = dyn_id.split("-")
                    l_dyn_id = [int(x) for x in l_dyn_id]
                    l_dyn_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_dyn_id = range(l_dyn_id[0],l_dyn_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_dyn_id:
                        try:
                            dyn_obj = DyndbDynamics.objects.get(id=x)
                            sum_id = dyn_obj.submission_id.id
                            obj = DyndbSubmission.objects.get(id=sum_id)
                            if obj.is_published == False:
                                obj.is_published = True
                                obj.is_ready_for_publication = True
                                obj.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    try:
                        dyn_obj = DyndbDynamics.objects.get(id=dyn_id)
                        sum_id = dyn_obj.submission_id.id
                        obj = DyndbSubmission.objects.get(id=sum_id)
                        if obj.is_published == False:
                            obj.is_published = True
                            obj.is_ready_for_publication = True
                            obj.save()
                        object_ready.append(dyn_id)
                    except:
                        object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are PUBLISHED: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are UNPUBLISHED: {object_unready}'))
        
        if kwargs["unpublish_ids"]:
            kwargs["unpublish_ids"] =[ele.replace(",","") for ele in kwargs["unpublish_ids"]]#Clean commas from each element of the list 
            print(f"    - Processing the dynamics ids: {kwargs['unpublish_ids']}...")
            object_ready, object_unready = [],[]  
            for dyn_id in kwargs['unpublish_ids']:
                if "-" in dyn_id: #To avoid write every number we incorporate ranges using min-max structure
                    dyn_id = dyn_id.replace(" ","")
                    l_dyn_id = dyn_id.split("-")
                    l_dyn_id = [int(x) for x in l_dyn_id]
                    l_dyn_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_dyn_id = range(l_dyn_id[0],l_dyn_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_dyn_id:
                        try:
                            dyn_obj = DyndbDynamics.objects.get(id=x)
                            sum_id = dyn_obj.submission_id.id
                            obj = DyndbSubmission.objects.get(id=sum_id)
                            if obj.is_published == True:
                                obj.is_published = False
                                obj.is_ready_for_publication = False
                                obj.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    try:
                        dyn_obj = DyndbDynamics.objects.get(id=dyn_id)
                        sum_id = dyn_obj.submission_id.id
                        obj = DyndbSubmission.objects.get(id=sum_id)
                        if obj.is_published == True:
                            obj.is_published = False
                            obj.is_ready_for_publication = False
                            obj.save()
                        object_ready.append(dyn_id)
                    except:
                        object_unready.append(dyn_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following dynamic ids are UNPUBLISHED: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following dynamic ids are PUBLISHED: {object_unready}'))
        
        if kwargs["is_gpcrmd_ids"]:
            kwargs["is_gpcrmd_ids"] =[ele.replace(",","") for ele in kwargs["is_gpcrmd_ids"]]#Clean commas from each element of the list 
            print(f"    - Processing the submissions ids: {kwargs['is_gpcrmd_ids']}...")
            object_ready, object_unready = [],[]  
            for sub_id in kwargs['is_gpcrmd_ids']:
                if "-" in sub_id: #To avoid write every number we incorporate ranges using min-max structure
                    sub_id = sub_id.replace(" ","")
                    l_sub_id = sub_id.split("-")
                    l_sub_id = [int(x) for x in l_sub_id]
                    l_sub_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                    rang_sub_id = range(l_sub_id[0],l_sub_id[1]+1) #Need to sum one more on the second value due python range function counting 1 less alwys 1933 --> 1932
                    for x in rang_sub_id:
                        try:
                            obj = DyndbSubmission.objects.get(id=x)
                            if obj.is_gpcrmd_community == False:
                                obj.is_gpcrmd_community = True
                                obj.save()
                            object_ready.append(x)
                        except:
                            object_unready.append(x)
                else:
                    try:
                        obj = DyndbSubmission.objects.get(id=sub_id)
                        if obj.is_gpcrmd_community == False:
                            obj.is_gpcrmd_community = True
                            obj.save()
                        object_ready.append(sub_id)
                    except:
                        object_unready.append(sub_id)
                    
            self.stdout.write(self.style.SUCCESS(f'        - Following submissions ids are READY for precomputing: {object_ready} '))  
            self.stdout.write(self.style.NOTICE(f'        - Following submissions ids are UNREADY for precomputing: {object_unready}'))
             
        print("Exit!")