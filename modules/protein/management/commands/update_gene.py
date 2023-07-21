import requests
import pandas as pd
import json
import io
from tqdm import tqdm
from os import path 
import sys
import re

from modules.protein.models import Protein, ProteinFamily, ProteinSource, Species, Gene
from modules.residue.models import ResidueNumberingScheme
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

class Command(BaseCommand):
    help = "Get gene information from GPCRdb and update the table on GPCRmd database."
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data on ../modules/protein/management/tools/prot_data.json',
        )
    def handle(self, *args, **kwargs):
        #Get data from GPCRdb services
        url = "https://gpcrdb.org/services/receptorlist/"
        l_errors = {} #Store possible errors & warnings to display them at the end
        j_file = f"{MODULES_ROOT}/protein/management/tools/prot_data.json"
        
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
                prot_dic = json.load(json_file)
        except:
            prot_dic = ""

        if kwargs['update'] or prot_dic == "": 
            print("     - UPDATE FILES STEP...")
            if prot_dic == "":
                print("         > Data not found... Collecting data...")
            else:
                print("         > Refreshing data...")

            # Write information into data.py file on dynadb main directory
            print("         > Writing info into ../modules/protein/management/tools/prot_data.json...")
            dic_species_file = open(mode="w", file=f"{MODULES_ROOT}/protein/management/tools/prot_data.json")
            dic_species_file.write(urltext)
            dic_species_file.close()
            
        # Read information from table Protein   
        print("     - READING STEP...")
        print("         > Reading json data from GPCRdb...")
        with open(j_file) as json_file:
            prot_dic = json.load(json_file)

        # Update table Protein
        print("     - UPDATE STEP...")
        print("         > Update table Gene...")
        l_errors['new_gene'] = []
        
        # Get list of genes on GPCRmd
        l_gene_names = list(Gene.objects.values_list("name",flat=True))   
        
        # For every entry on GPCRdb check if is already in GPCRmd or not  
        for key in tqdm(prot_dic, total=len(prot_dic)):
            gpcrdb_entry_name = key["entry_name"]
            try:
                gpcrdb_url = f"https://gpcrdb.org/services/protein/{gpcrdb_entry_name}/"
                urlData = requests.get(gpcrdb_url).json()
            except:
                l_errors["connection"] = "Request to GPCRdb fails."
                break
            # name, position, species_id      
            # gene_id, protein_id
            gpcrdb_genes = urlData["genes"]
            protein_id = list(Protein.objects.filter(entry_name=gpcrdb_entry_name).values_list("id"))[0]
            species_id = list(Species.objects.filter(latin_name=urlData["species"]).values_list("id"))[0]
            for position, name in enumerate(gpcrdb_genes):
                # Check if exists: 
                check_gene = list(Gene.objects.filter(name=name).values_list('name', flat=True))
                if check_gene == []: # Empty means not found
                    query = Gene(
                        name = name, 
                        position = position, 
                        species_id = species_id[0]
                    )
                    query.save()
                    query.proteins.set(protein_id)
                    l_errors["new_gene"].append([gpcrdb_entry_name, gpcrdb_genes])
                else:
                    query = Gene.objects.filter(name=name).filter(proteins=protein_id)
                    query.update(
                        name = name, 
                        position = position, 
                        species_id = species_id[0]
                    )

        # Errors
        if l_errors['new_gene'] == [] and "connection" not in l_errors.keys():
            print("     - ERRORS & WARNINGS...")
        if "connection" in l_errors.keys():                        
            print("         > Url problem:")
            print(f"    {l_errors['connection']}")
        if l_errors["new_gene"] != []:                        
            print("         > New genes found on GPCRdb...")
            print(f"    {l_errors['new_gene']}")


        
