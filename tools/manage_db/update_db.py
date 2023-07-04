#!/opt/gpcrmdenv/bin python

# Modules
import os
import sys


def get_dump(path_dump, name_dump, extension, *args, **kwargs):
    """Check if the dump file exists & returns the path where this dump is located.

    Args:
        path_dump (str): base path of the dump file.
        name_dump (str): name of the dump
        extension (str): extension of the dump

    Raises:
        Exception: in case the dump file is not found

    Returns:
        str: absolute path of the dump file.
    """
    
    if extension != "backup":
        raise Exception(f"Extension {extension} not permitted.")
    
    if not extension in name_dump: 
        name_dump = name_dump + '.' + extension
        
    dump = f"{path_dump}/{name_dump}"
    
    if not os.path.isfile(dump):
        raise Exception("Dump file not found.")
    
    print("     - File found!")
    return dump 

def restore_db(dump, *args, **kwargs): 
    """
    Restores a database from a dump file.
    """
    
    os.system(f"pg_restore -U gpcrmd_admin -d gpcrmd --no-owner --password -h localhost --clean  -v {dump}")
    
if __name__ == "__main__":
    
    if len(sys.argv) < 3:
        print("Usage: restore_db.py <path_dump> <name_dump> (<extension>)")
        print("- Extesion could be included in the name_dump parameter.")
        sys.exit(1)
    
    path_dump = sys.argv[1]
    name_dump = sys.argv[2]
    extension = sys.argv[3]
    
    # Get dump file
    print("- Checking if the file exists...")
    dump = get_dump(path_dump, name_dump, extension)
    
    # Restore database
    print(f"- Restoring database using dump {dump}...")
    restore_db(dump)
    print("- Database restore!")
    
    # Make migrations of models (tables)
    print("- Check tables & parameters")
    
    print("- Exiting...")