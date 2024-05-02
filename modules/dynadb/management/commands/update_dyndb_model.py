import requests
import json
import pandas as pd
import io
from tqdm import tqdm
from os import path 
import sys
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

from modules.protein.models import ProteinPDB
from modules.dynadb.models import DyndbModel,DyndbProtein

class Command(BaseCommand):
    help = "Update dyndb_model table."

    def handle(self, *args, **options):       
        l_errors = {'not_found':[]}
        dyndb_model_table = pd.DataFrame(list(DyndbModel.objects.all().values()))
        print(dyndb_model_table.columns)
        # Create State dictionary from table 
        print("         > Update DyndbModel model.")
        dic_state = {}
        for index, row in tqdm(dyndb_model_table.iterrows(), total=dyndb_model_table.shape[0]):
            dyn_id = row["id"]
            id_protein = str(row["id_protein_id"])
            if id_protein == "nan":
                try:
                    query = DyndbModel.objects.get(id = dyn_id)
                    pdb_id = query.pdbid.replace("'","")[0:4]
                    # if pdb_id == "HOMO" or pdb_id == "ALPH" or pdb_id == "XXXX":
                    #     l_errors['not_found'].append(f"{pdb_id}")
                    #     continue
                    query_prot = ProteinPDB.objects.filter(pdb=pdb_id)  
                    l_uniprotkbac = query_prot[0].uniprotkbac.split(",")
                    for kbac in l_uniprotkbac:
                        query_dyn = DyndbProtein.objects.filter(uniprotkbac=kbac)
                        if query_dyn:
                            break
                    query.id_protein = query_dyn[0]
                    query.save()
                except:
                    l_errors['not_found'].append(f"{pdb_id}")
       # Errors
        if l_errors['not_found'] != []:
            print("     - ERRORS & WARNINGS...")
        if l_errors["not_found"] != []:                        
            print("         > Not pdb found in database...")
            print(f"    {l_errors['not_found']}")