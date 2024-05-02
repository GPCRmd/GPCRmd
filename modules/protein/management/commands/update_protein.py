import requests
import pandas as pd
import json
import io
from tqdm import tqdm
from os import path 
import sys
import re

from modules.protein.models import Protein, ProteinFamily, ProteinSource, Species
from modules.residue.models import ResidueNumberingScheme
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

class Command(BaseCommand):
    help = "Get protein information from GPCRdb and update the table on GPCRmd database."
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data on ../modules/protein/management/tools/prot_data.json',
        )
    def handle(self, *args, **kwargs):
        l_errors = {} #Store possible errors & warnings to display them at the end
        j_file = f"{MODULES_ROOT}/protein/management/tools/prot_data.json"
        # Opening JSON file
        try:
            with open(j_file) as json_file:
                prot_dic = json.load(json_file)
        except:
            prot_dic = ""
        
        gpcrdb_struct = f"{MODULES_ROOT}/protein/management/tools/gpcrdb_pdb.json"
        try:
            with open(gpcrdb_struct) as json_file:
                struc_dic = json.load(json_file)
        except:
            struc_dic = ""

        if kwargs['update'] or prot_dic == "" or struc_dic == "": 
            #Get data from GPCRdb services
            #Receptorlist   
            url = "https://gpcrdb.org/services/receptorlist/"
        
            try:
                # urlData = requests.get(url).json()
                urlData = requests.get(url)
                urltext = urlData.text
            except:
                l_errors["connection"] = "Request to GPCRdb fails."
            html_cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')#Clean tags and some not enclosed elements like &nsbm  
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
            
            #Structure 
            print("         > Writing info into ../modules/protein/management/tools/gpcrdb_pdb.json...")
            
            url = "https://gpcrdb.org/services/structure/"
            json_info = open(mode="w", file=f"{MODULES_ROOT}/protein/management/tools/gpcrdb_pdb.json")
            urlData = requests.get(url)
            urltext = urlData.text
            json_info.write(urltext)
            json_info.close()
                
        # Read information from table Protein   
        print("     - READING STEP...")
        print("         > Reading json data from GPCRdb...")
        
        # data_prot = Protein.objects.all() 
        with open(j_file) as json_file:
            prot_dic = json.load(json_file)
            
        with open(gpcrdb_struct) as json_file:
            struc_dic = json.load(json_file)

        # entry_name, accession, name, sequence, family_id, parent_id, residue_numbering_scheme_id, 
        # sequence_type_id, source_id, species_id      

        # Update table Protein
        print("     - UPDATE STEP...")
        print("         > Update table Protein...")
        l_errors['new_prot'], l_errors['prot_nf'] = [], []
        
        # Get list of entries on GPCRmd
        l_entry_names = list(Protein.objects.values_list("entry_name",flat=True))   
        
        # For every entry on GPCRdb check if is already in GPCRmd or not  
        for key in tqdm(prot_dic, total=len(prot_dic)):
            gpcrdb_entry_name = key["entry_name"]
            try:
                gpcrdb_url = f"https://gpcrdb.org/services/protein/{gpcrdb_entry_name}/"
                urlData = requests.get(gpcrdb_url).json()
            except:
                l_errors["connection"] = "Request to GPCRdb fails."
                break
            
            if gpcrdb_entry_name not in l_entry_names:
                try:
                    #Get family id:
                    family_id = list(ProteinFamily.objects.filter(slug=urlData["family"]).values_list("id"))[0]
                    #Get residue_numbering_scheme id
                    res_num_sch = list(ResidueNumberingScheme.objects.filter(short_name=urlData["residue_numbering_scheme"]).values_list("id"))[0]
                    #Get source_id: 
                    source_id = list(ProteinSource.objects.filter(name=urlData["source"]).values_list("id"))[0]
                    #Get species id:
                    species_id = list(Species.objects.filter(latin_name=urlData["species"]).values_list("id"))[0]
                    
                    # Parameters on Protein table
                    accession = urlData["accession"]
                    name = urlData["name"]
                    sequence = urlData["sequence"]
                    parent_id = ""
                    family_id = family_id[0]
                    residue_numbering_scheme_id = res_num_sch[0] 
                    sequence_type_id = 1
                    source_id = source_id[0]
                    species_id = species_id[0]
                    
                    query = Protein(
                        entry_name = gpcrdb_entry_name, 
                        accession = accession, 
                        name = name, 
                        sequence = sequence, 
                        family_id = family_id, 
                        parent_id = parent_id, 
                        residue_numbering_scheme_id = residue_numbering_scheme_id, 
                        sequence_type_id = sequence_type_id, 
                        source_id = source_id, 
                        species_id = species_id)
                    query.save()
                    l_errors["new_prot"].append(gpcrdb_entry_name)
                except:
                    l_errors["prot_nf"].append(gpcrdb_entry_name)
            else:
                try:
                    #Get family id:
                    family_id = list(ProteinFamily.objects.filter(slug=urlData["family"]).values_list("id"))[0]
                    #Get residue_numbering_scheme id
                    res_num_sch = list(ResidueNumberingScheme.objects.filter(short_name=urlData["residue_numbering_scheme"]).values_list("id"))[0]
                    #Get source_id: 
                    source_id = list(ProteinSource.objects.filter(name=urlData["source"]).values_list("id"))[0]
                    #Get species id:
                    species_id = list(Species.objects.filter(latin_name=urlData["species"]).values_list("id"))[0]
                    
                    # Parameters on Protein table
                    accession = urlData["accession"]
                    name = urlData["name"]
                    sequence = urlData["sequence"]
                    family_id = family_id[0]
                    residue_numbering_scheme_id = res_num_sch[0] 
                    source_id = source_id[0]
                    species_id = species_id[0]
                    
                    # Update info
                    query = Protein.objects.filter(entry_name = gpcrdb_entry_name)
                    query.update(
                        accession = accession, 
                        name = name, 
                        sequence = sequence, 
                        family_id = family_id,
                        residue_numbering_scheme_id = residue_numbering_scheme_id,
                        source_id = source_id, 
                        species_id = species_id
                        )
                except:
                    l_errors["prot_nf"].append(gpcrdb_entry_name)

        # Errors
        if l_errors['new_prot'] == [] and l_errors['prot_nf'] == [] and "connection" not in l_errors.keys():
            print("     - ERRORS & WARNINGS...")
        if "connection" in l_errors.keys():                        
            print("         > Url problem:")
            print(f"    {l_errors['connection']}")
        if l_errors["new_prot"] != []:                        
            print("         > New proteins found on GPCRdb...")
            print(f"    {l_errors['new_prot']}")
        if l_errors["prot_nf"] != []:                        
            print("         > Protein not found on GPCRdb...")
            print(f"    {l_errors['prot_nf']}")


        
