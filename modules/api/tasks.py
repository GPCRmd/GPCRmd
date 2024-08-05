# Create your tasks here
import celery
from config.celery import app
from celery import shared_task
from celery_progress.backend import ProgressRecorder

import time
import os
from os.path import join
import shutil
# import mimetypes
import json

from wsgiref.util import FileWrapper

# from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.utils import timezone

from modules.dynadb.models import DyndbFiles, DyndbFilesDynamics, DyndbDynamics, DyndbSubmission 
from modules.api.models import AllDownloads

from config.settings import DOWNLOAD_FILES

# @shared_task(bind=True)
# def check_file(self, file, l_dyns): #, *args, **kwargs):
#     progress_recorder = ProgressRecorder(self)
#     switch = 0
#     while switch == 0:
#         if os.path.isdir(DOWNLOAD_FILES + "/" + file):
#             count = len(next(os.walk(DOWNLOAD_FILES + "/" + file))[1])
#             if os.path.isfile(DOWNLOAD_FILES + "/" + file + ".zip"):
#                 progress_recorder.set_progress(len(l_dyns), len(l_dyns) + 1, f'Preparing the zip file') 
#             else:
#                 progress_recorder.set_progress(count, len(l_dyns) + 1, f'On dyn {l_dyns[count-1]}')         
#         else:
#             switch = 1
    
#     progress_recorder.set_progress(len(l_dyns) + 1, len(l_dyns) + 1, f'Done') 
            
#     return "Done"

def get_size(path):
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} bytes"
        elif size < pow(1024,2):
            return f"{round(size/1024, 2)} KB"
        elif size < pow(1024,3):
            return f"{round(size/(pow(1024,2)), 2)} MB"
        elif size < pow(1024,4):
            return f"{round(size/(pow(1024,3)), 2)} GB"

@shared_task(bind=True)
def prepare_file(self, obj, *args, **kwargs):

    obj = json.loads(obj)
    #Log file
    progress_recorder = ProgressRecorder(self)
    os.umask(0)
    f = open(os.path.join(obj['tmp'], f'{obj["outfile"]}.log'), "w")
    f.write("LOG FILE ABOUT THE DOWNLOADED FILES: \n")
    
    # Check ids
    # progress_recorder.set_progress(step, total, "Step 0 - Preparing the request...")
    l_dyns = []
    l_ndyns = []
    dyns = obj['l_dyns'][0:5]
    for d in dyns:
        dyn_data = DyndbDynamics.objects.get(id = d)
        sub_data = DyndbSubmission.objects.get(id = dyn_data.submission_id.id)
        if sub_data.is_published:
            l_dyns.append(d)
        else:
            l_ndyns.append(d)
            
    for nd in l_ndyns:
        f.write((f"    > Dyn {nd} not found or not published yet - {timezone.now()} \n"))
                    
    # Seach the files & Counter 
    obj['dic_files'] = {}
    step = 0
    total = len(l_dyns) + 5  # 3, 0 step copy, 1 step zip and 2 step done
    for dyn in l_dyns:#Limit to first 5 dyns 
        obj['dic_files'][f"dyn_{dyn}"] = list(DyndbFilesDynamics.objects.filter(id_dynamics = dyn).values_list("id_files", flat=True)) #[10394, 10395, 10396, 10397, 10398, 10399, 10400]     10395_dyn_36.psf  |  NOT 10398_trj_36_xtc_bonds 
        total = total + len(obj['dic_files'][f"dyn_{dyn}"]) # Number of files
    
    # Check list 
    if obj['dic_files'] == []:
        return int("s") #Return an error to return error callajax   
    
    # Step 1 - Copy files
    progress_recorder.set_progress(step, total, "Step 1 - Copying the files...")
    step = step + 1

    if l_dyns != []:
        # Get the files 
        for i, dyn_key in enumerate(obj['dic_files']):
            f.write((f"    > Dyn {dyn_key} files - {timezone.now()} \n"))
            dyn_path = join(obj['tmpdir'],dyn_key)
            os.makedirs(dyn_path, mode=0o777, exist_ok=True)
            file_ids = obj['dic_files'][dyn_key]
            for f_id in file_ids:
                file_path = list(DyndbFiles.objects.filter(id = f_id).values_list("filepath", flat=True))[0]
                file_name = list(DyndbFiles.objects.filter(id = f_id).values_list("filename", flat=True))[0]
                in_file = settings.MEDIA_ROOT[:-1] + file_path
                out_file = dyn_path + "/" + file_name
                
        # Copy the files 
                try:
                    shutil.copyfile(in_file, out_file)
                    f.write((f"        > File {file_name} added. - {get_size(out_file)} - {timezone.now()} \n"))
                except:
                    f.write((f"        > File {file_name} not found. - {timezone.now()} \n"))
                    pass
                progress_recorder.set_progress(step, total, description="Step 1 - Copying the files...")
                step = step + 1

            f.write((f"        > Completed the download of {dyn_key} - {timezone.now()} \n"))
            progress_recorder.set_progress(step, total, description=f"Step 1 - Copying the files of {dyn_key} done.")
            step = step + 1
               
    else:
        step = total
        progress_recorder.set_progress(total, total, description="Done - {dyn_key} files not found or not published yet.")
        f.write((f"    > Dyns not found or not published yet - {timezone.now()} \n"))

    f.write((f"    > Success! - {timezone.now()} \n"))
    f.close()
    
    downfileobj=AllDownloads(
        tmpname = obj['zip'],
        dyn_ids = obj['dyns'],
        creation_timestamp = timezone.now(),
        created_by_dbengine = settings.DB_ENGINE,
        created_by = obj['user'],
        filepath = obj['tmpdir'] + ".zip",
    )
    downfileobj.save()
    
    progress_recorder.set_progress(step, total, description="Step 2 - Compressing files into zip...")
    step = step + 1

    shutil.make_archive(obj['tmpdir'], 'zip', obj['tmp'], obj['outfile'])      
    
    time.sleep(1)

    progress_recorder.set_progress(step, total, description="Compression done!")
    step = step + 1

    # Remove tmp directory
    shutil.rmtree(obj['tmpdir'])
    
    progress_recorder.set_progress(step, total, description="Retrieving the downloading link...")
    
    time.sleep(1)
    
    return join("/dynadb/tmp/GPCRmd_downloads/", obj['zip'])  # CHANGE URL 



