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
        sqlparser.add_argument("-r", "--restore", type=str, help="Restore the database from a dump file.", metavar="file")
        sqlparser.add_argument("-pf", "--pathfile", help="Replace the urls of path files with correct ones.", action="store_true")

        # Protein tables
        protparser = parser.add_argument_group("Protein tables options", "Options to update the protein tables using data from GPCRdb.")
        protparser.add_argument("-p", "--protein", help="Update all the protein tables in the database. Englobe all the other options listes below.", action="store_true")
        protparser.add_argument("-fa", "--protfamily", help="Update the protein family table in the database.", action="store_true")
        protparser.add_argument("-s", "--protstate", help="Update the protein state table in the database.", action="store_true")
    
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
            
            print(f"- Checking if the file {path_dump} exists...")
            
            if not os.path.isfile(path_dump):
                raise Exception("Dump file not found.")
            
            print(f"- Restoring database using dump file {path_dump}...")

            os.system(f"pg_restore -U gpcrmd_admin -d gpcrmd --no-owner --password -h localhost --clean  -v {path_dump}")
            
            print("- Database restored!")
            
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
        def update_prot_family(*args, **kwargs):
            """
            Update the protein family table of GPCRmd database.
            """
            
            print(f"    - Protein family table...")
                
            if kwargs["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_protein_family --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_protein_family")
            
        def update_prot_state(*args, **kwargs):
            """
            Update the protein state table of GPCRmd database.
            """
            
            print(f"    - Protein state table...")
                
            if kwargs["update"]:
                print(f"    - Force update of the data from GPCRdb...")
                return os.system(f"python /var/www/GPCRmd/manage.py update_protein_state --update")
                
            os.system(f"python /var/www/GPCRmd/manage.py update_protein_state")
        
        # gpcrargs = parser.parse_args()
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
            update_prot_family(kwargs)
            update_prot_state(kwargs)

        elif not kwargs["protein"]:
            print(f"- Updating protein tables...")
            
            # Protein family table
            if kwargs["protfamily"]:
                update_prot_family(kwargs)
                
            # Protein state table
            if kwargs["protstate"]:
                update_prot_state(kwargs)
            
            
        # Exit
        print("- Exiting...")