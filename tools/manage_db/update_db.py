#!/opt/gpcrmdenv/bin python

# Modules
import os
import sys
import argparse

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
    
def update_prot_family(*args, **kwargs):
    """
    Update the protein family table of GPCRmd database.
    """
    
    print(f"    - Protein family table...")
        
    if gpcrargs.update:
        print(f"    - Force update of the data from GPCRdb...")
        return os.system(f"python /var/www/GPCRmd/manage.py update_protein_family --update")
        
    os.system(f"python /var/www/GPCRmd/manage.py update_protein_family")
    
def update_prot_state(*args, **kwargs):
    """
    Update the protein state table of GPCRmd database.
    """
    
    print(f"    - Protein state table...")
        
    if gpcrargs.update:
        print(f"    - Force update of the data from GPCRdb...")
        return os.system(f"python /var/www/GPCRmd/manage.py update_protein_state --update")
        
    os.system(f"python /var/www/GPCRmd/manage.py update_protein_state")

if __name__ == "__main__":
    
    # VirtualEnv activation
    # os.system(f"source /opt/gpcrmdenv/bin/activate")

    # Arguments
    argParser = argparse.ArgumentParser(description="Restore or update the GPCRmd database.")
    
    # General options
    allparser = argParser.add_argument_group("General options", "Options used on more than one part of the update.")
    allparser.add_argument("-u", "--update", help="Update the data used to update the tables.", action="store_true")

    # SQL options (database dumps)
    sqlparser = argParser.add_argument_group("PostgreSQL options", "Restore the GPCRmd database.")
    sqlparser.add_argument("-r", "--restore", type=str, help="Restore the database from a dump file.", metavar="file")

    # Protein tables
    protparser = argParser.add_argument_group("Protein tables options", "Options to update the protein tables using data from GPCRdb.")
    protparser.add_argument("-p", "--protein", help="Update all the protein tables in the database. Englobe all the other options listes below.", action="store_true")
    protparser.add_argument("-fa", "--protfamily", help="Update the protein family table in the database.", action="store_true")
    protparser.add_argument("-s", "--protstate", help="Update the protein state table in the database.", action="store_true")

    
    gpcrargs = argParser.parse_args()
    
    if len(sys.argv) < 2:
        argParser.error("No arguments given. Use the help option (-h | --help) to check the available options.") 
    
    # Check if both arguments are available
    if gpcrargs.restore:
        print(f"- Restoring GPCRmd database...")
        restore_db(gpcrargs.restore)     # Get dump file & restore database

    # Update protein tables
    if gpcrargs.protein:
        update_prot_family(gpcrargs)
        update_prot_state(gpcrargs)

    elif not gpcrargs.protein:
        print(f"- Updating protein tables...")

    # Protein family table
    if gpcrargs.protfamily:
        update_prot_family(gpcrargs)
        
    # Protein state table
    if gpcrargs.protstate:
        update_prot_state(gpcrargs)
        
        
    # Exit
    print("- Exiting...")