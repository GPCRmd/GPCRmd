import requests
import pandas as pd
import io
from tqdm import tqdm
from os import path 
import sys
from django.core.management.base import BaseCommand, CommandError
from config.settings import MODULES_ROOT

from modules.protein.models import ProteinPDB, ProteinState

class Command(BaseCommand):
    help = "Get state information from GPCRdb and relate it with PDBid into a dictionary."
    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            dest='update',
            default=False,
            help='Overwrites already stored data on gpcrdb_table.html.',
        )

    def handle(self, *args, **options):
        #Get data from GPCRdb 

        url = "https://gpcrdb.org/structure/"

        # If we want to update or obtain the data 
        if options['update']: 
            print("- UPDATE STEP...")
            print("     > Refreshing data...")
            table_info = open(mode="w", file=f"{MODULES_ROOT}/protein/management/tools/gpcrdb_table.html")
            urlData = requests.get(url)
            urltext = urlData.text
            l_urltext = urltext.split("\n")

            table = 0
            over_header = 0

            for line in l_urltext:
                if "<table" in line: 
                    table_info.writelines(line+"\n")
                    table = 1
                elif "</table" in line:
                    table_info.writelines(line+"\n")
                    table = 0
                    table_info.close()
                    break
                elif "<tr class='over_header over_header_row'" in line: 
                    over_header = 1
                elif "</tr" in line and over_header == 1: 
                    over_header = 0 
                elif table == 1 and over_header == 0: 
                    table_info.writelines(line+"\n")

        # Get the dataset from gpcrdb on pandas
        print("     > Getting the dataset...")
        gpcrdb_table = pd.read_html(f"{MODULES_ROOT}/protein/management/tools/gpcrdb_table.html")
        gpcrdb_table = gpcrdb_table[0].iloc[1:,1:-1] 

        # Create State dictionary from table 
        print("     > Creating the state dictionary ([pdb] = state)... & update ProteinState model.")
        dic_state = {}
        for index, row in tqdm(gpcrdb_table.iterrows(), total=gpcrdb_table.shape[0]):
            pdb_id = str(row["PDB"])
            state = str(row["State"])
            if pdb_id not in dic_state.keys():
                dic_state[pdb_id] = state
        # Save the elements into table ProteinPDB
                state_id = ProteinState.objects.filter(name=state).values("id")
                if not ProteinPDB.objects.filter(pdb=pdb_id).exists():
                    query = ProteinPDB(pdb = pdb_id, state = int(state_id[0]["id"]))
                    query.save()
                else:
                    # print(f"     > PDB {pdb_id} already exists.")
                    continue

        # Write information into data.py file on dynadb main directory
        print("     > Writing info into modules/dynadb/data.py...")
        dic_state_file = open(mode="w", file=f"{MODULES_ROOT}/dynadb/data.py")
        dic_state_file.write(f"pdb_state={dic_state}")
        dic_state_file.close()

        