import requests
import pandas as pd
import io
from tqdm import tqdm
from os import path 
import sys
import re
import json

from modules.protein.models import Species
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

class Command(BaseCommand):
    help = "Get species information from GPCRdb and update the table on GPCRmd database."
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data on ../modules/protein/management/tools/species_data.json',
        )

    def handle(self, *args, **kwargs):

        #Get data from GPCRdb services
        url = "https://gpcrdb.org/services/species/"
        l_errors = {} #Store possible errors & warnings to display them at the end
        j_file = f"{MODULES_ROOT}/protein/management/tools/species_data.json"
        
        try:
            # urlData = requests.get(url).json()
            urlData = requests.get(url)
            urltext = urlData.text
        except:
            l_errors["connection"] = "Request to GPCRdb fails."
        html_cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')#Clean tags and some not enclosed elements like &nsbm  
        
        # Opening JSON file
        try:
            with open(j_file) as json_file:
                species_dic = json.load(json_file)
        except:
            species_dic = ""

        if kwargs['update'] or species_dic == "": 
            print("     - UPDATE FILES STEP...")
            if species_dic == "":
                print("         > Dictionary of families on prot_fam_data,py not found... Refreshing data...")
            else:
                print("         > Refreshing data...")

            # Write information into data.py file on dynadb main directory
            print("     > Writing info into ../modules/protein/management/tools/species_data.json...")
            dic_species_file = open(mode="w", file=f"{MODULES_ROOT}/protein/management/tools/species_data.json")
            dic_species_file.write(urltext)
            dic_species_file.close()
        
        with open(j_file) as json_file:
            species_dic = json.load(json_file)
        # Read information from table Species     
       
        print("     - READING STEP...")
        print("         > Reading table Species from database...")
        data_spe = Species.objects.all() # latin_name, common_name     

        # Update table Species
        print("     - UPDATE STEP...")
        # Add new entries to Species
        print("         > Search of new entries for table Species...")
        l_errors['new_spec'] = []
        l_latin_names = list(Species.objects.values_list("latin_name",flat=True))     
        for key in tqdm(species_dic, total=len(species_dic)):
            if key["latin_name"] not in l_latin_names:
                # print(f"        - New specie {key['latin_name']} found on GPCRdb...")
                latin_name = key["latin_name"]
                common_name = key["common_name"]
                query = Species(latin_name = latin_name, common_name = common_name)
                query.save()
                l_errors['new_spec'].append(key['latin_name'])
            else:
                continue

        # Errors
        if l_errors['new_spec'] == [] and "connection" not in l_errors.keys():
            print("     - ERRORS & WARNINGS...")
        if "connection" in l_errors.keys():                        
            print("         > Url problem:")
            print(f"    {l_errors['connection']}")
        if l_errors["new_spec"] != []:                        
            print("         > New species found on GPCRdb...")
            print(f"    {l_errors['new_spec']}")


        
