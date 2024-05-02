import requests
import json
import pandas as pd
import io
from tqdm import tqdm
from os import path 
import sys
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

from modules.dynadb.models import DyndbSubmissionDynamicsFiles

class Command(BaseCommand):
    help = "Restores the filenames and filepath in table dyndb_submission_dynamics_files. "

    def add_arguments(self, parser):
        parser.add_argument(
           '--dsdfsubs',
            nargs='*',
            action='store',
            default=False,
            help='Replace the filenames and paths of a list of submission ids, separated by comma, with the correct ones in the dyndb submission dynamics files. You can use the range statement to provide range of numbers instead of write them one by one (e.g. 1594-1933).',
        ) 
    
    def handle(self, *args, **kwargs):       
        l_errors = {'not_found':[]}
        print("         > Update DyndbSubmissionDynamicsFiles.")
        kwargs["dsdfsubs"] =[ele.replace(",","") for ele in kwargs["dsdfsubs"]]#Clean commas from each element of the list 
        print(f"         > Processing the submission ids: {kwargs['dsdfsubs']}...")
        
        for sub_id in kwargs['dsdfsubs']:
            if "-" in sub_id: #To avoid write every number we incorporate ranges using min-max structure
                sub_id = sub_id.replace(" ","")
                l_sub_id = sub_id.split("-")
                l_sub_id = [int(x) for x in l_sub_id]
                l_sub_id.sort() #1594-1933 OR 1933-1594 always return range(1594,1933) to avoid max,min error
                for b in DyndbSubmissionDynamicsFiles.objects.filter(submission_id__gte=l_sub_id[0],submission_id__lte=l_sub_id[1]):     # (815,1191)
                    df = b.id_files
                    submission_id = b.submission_id
                    if df:
                        if df.filename != b.filename:
                            try:
                                url = df.url
                                filename = df.filename
                                filepath = df.filepath
                                DSDF = DyndbSubmissionDynamicsFiles.objects.filter(pk=b.id)
                                DSDF.update(url=url, filename=filename, filepath=filepath)
                                # print(filename, filename,url,' ', DF)
                                print(f"            > File Submission Id: {submission_id.id} File Id: {b.id_files.id} corrected...")
                            except Exception as e:
                                l_errors['not_found'].append(f"{b.filename}")
                                print(e)
            else:
                for b in DyndbSubmissionDynamicsFiles.objects.filter(submission_id=(sub_id)):     
                    df = b.id_files
                    if df:
                        if df.filename != b.filename:
                            try:
                                url = df.url
                                filename = df.filename
                                filepath = df.filepath
                                DSDF = DyndbSubmissionDynamicsFiles.objects.filter(pk=b.id)
                                DSDF.update(url=url, filename=filename, filepath=filepath)
                                print(f"            > {submission_id}_{b.id_files} corrected...")
                                # print(filename, filename,url,' ', DF)
                            except Exception as e:
                                l_errors['not_found'].append(f"{b.filename}")
                                print(e)

       # Errors
        if l_errors['not_found'] != []:
            print("     - ERRORS & WARNINGS...")
        if l_errors["not_found"] != []:                        
            print("         > Error in database...")
            print(f"    {l_errors['not_found']}")
        
