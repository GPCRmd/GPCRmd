#!/opt/gpcrmdenv/bin python

# Modules
import os
import sys
# import argparse

# Django commands
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Func, Value
from django.conf import settings

# Django models
from modules.dynadb.models import DyndbFiles, DyndbSubmissionDynamicsFiles
from modules.covid19.models import CovidFiles

class Command(BaseCommand):
    help = "Admin commands to manage the GPCRmd database."
    
    # VirtualEnv activation
    # os.system(f"source /opt/gpcrmdenv/bin/activate")
    def add_arguments(self, parser):
        # Arguments
        # argParser = argparse.ArgumentParser(description="Restore or update the GPCRmd database.")
        
        # General options
        allparser = parser.add_argument_group("General options", "Options used on more than one part of the update.")
        allparser.add_argument("-u", "--update", help="Update the data used to update the tables.", action="store_true")

        # SQL options (database dumps)
        sqlparser = parser.add_argument_group("PostgreSQL options", "Manage the GPCRmd database.")
        sqlparser.add_argument("-sr", "--restore", type=str, help="Restore the database from a dump file.", metavar="file")
        sqlparser.add_argument("-sf", "--pathfile", help="Replace the urls of path files with correct ones.", action="store_true")

        # Protein tables
        protparser = parser.add_argument_group("Protein tables options", "Options to update the protein tables using data from GPCRdb.")
        protparser.add_argument("-p", "--protein", help="Update all the protein tables in the database. Englobe all the other options list below.", action="store_true")
        protparser.add_argument("-pf", "--protfamily", help="Update the protein family table in the database.", action="store_true")
        protparser.add_argument("-ps", "--protstate", help="Update the protein state & pdb tables in the database.", action="store_true")
        protparser.add_argument("-pp", "--species", help="Update the species table in the database.", action="store_true")
        protparser.add_argument("-pg", "--gene", help="Update the gene table in the database.", action="store_true")

        # Dyndb tables
        dynparser = parser.add_argument_group("Dyndb tables options", "Options to update the dyndb tables.")
        dynparser.add_argument("-dm", "--dynmodel", help="Update the dyndb model table.", action="store_true")
    
    def handle(self, *args, **kwargs):
        # General functions
        def replace_func(field_name, find_str, replace_str):
            return Func(
                F(field_name),
                Value(find_str), Value(replace_str),
                function='replace'
            )                  

        # SQLdb functions
        def restore_db(path_dump, *args, **kwargs): 
            """
            Restores a database from a dump file.
            """
            
            print(f"    - Checking if the file {path_dump} exists...")
            
            if not os.path.isfile(path_dump):
                raise Exception("Dump file not found.")
            
            print(f"    - Restoring database using dump file {path_dump}...")

            os.system(f"pg_restore -U gpcrmd_admin -d gpcrmd --no-owner --password -h localhost --clean  -v {path_dump}")
            
            print("     - Database restored!")
            
        def path_files_db(*args, **kwargs): 
            """
            Restores the path to the files database into tables: dyndb_files, dyndb_submission_dynamics_files & covid_files. Remove "/protwis/sites/files". 
            """
            
            remove = "/protwis/sites/files"
            replace = ""

            gpcrmd_tables = [DyndbFiles, DyndbSubmissionDynamicsFiles, CovidFiles]
            
            for g_table in gpcrmd_tables:
                print(f"    - Restore file path in {g_table}.")
                entry = g_table.objects.update(
                    filepath = replace_func("filepath", remove, replace)
                    )
            
        # Protein functions
        def update_prot (*args, **kwargs):
            """
            Update protein table of GPCRmd database.
            """
            
            print(f"    - Protein table...")
                
            if args[0]["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_protein --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_protein")
            
        def update_prot_family(*args, **kwargs):
            """
            Update the protein family table of GPCRmd database.
            """
            
            print(f"    - Protein family table...")

            if args[0]["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_protein_family --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_protein_family")
            
        def update_prot_state(*args, **kwargs):
            """
            Update the protein state & pdb tables of GPCRmd database.
            """
            
            print(f"    - Protein state & pdb tables...")
            
            if args[0]["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_protein_state --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_protein_state")
        
        def update_species(*args, **kwargs):
            """
            Update the species table of GPCRmd database.
            """
            
            print(f"    - Species table...")
                
            if args[0]["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_species --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_species")
        
        def update_gene(*args, **kwargs):
            """
            Update the gene table of GPCRmd database.
            """
            
            print(f"    - Gene table...")
                
            if args[0]["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_gene --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_gene")
            
         # Dyndb functions
        def update_dyndb_model(*args, **kwargs):
            """
            Update dyndb model table of GPCRmd database.
            """

            print(f"    - Dyndb model table...")

            os.system(f"python /var/www/GPCRmd/manage.py update_dyndb_model")
        
        if len(sys.argv) < 3:
            raise Exception("No arguments given. Use the help option (-h | --help) to check the available options.") 
        
        # Update SQL database
        # Check if both arguments are available
        if kwargs["restore"]:
            print(f"- Restoring GPCRmd database...")
            restore_db(kwargs["restore"])     # Get dump file & restore database
        
        if kwargs["pathfile"]:
            print(f"- Restoring GPCRmd database path files...")
            path_files_db(kwargs)
            
        # Update protein tables
        if kwargs["protein"]:
            print(f"- Updating protein tables...")
            update_prot_family(kwargs)
            update_prot_state(kwargs)
            update_species(kwargs)
            # update_gene(kwargs)
            update_prot(kwargs)
            sys.exit("Exiting...")
            
        # Protein family table
        if kwargs["protfamily"]:
            update_prot_family(kwargs)

        # Protein state table
        if kwargs["protstate"]:
            update_prot_state(kwargs)

        # Species table
        if kwargs["species"]:
            update_species(kwargs)

        # Genes table
        if kwargs["gene"]:
            update_gene(kwargs)

        # Update dyndb tables

        # Dyndb model table 
        if kwargs["dynmodel"]:
            update_dyndb_model(kwargs)

        sys.exit("Exiting...")  
                