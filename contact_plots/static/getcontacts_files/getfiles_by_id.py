from dynadb.models import DyndbFilesDynamics
from sys import argv
import re
import os

basepath = "/protwis/sites/files/" #The base directory path to files in server/vagrant 

def obtain_dyn_files(dyn_id):
    """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    traj_list=[]
    traj_name_list=[]
    p=re.compile("(/protwis/sites/files/)(.*)")
    p2=re.compile("[\.\w]*$")
    for fileobj in dynfiles:
        path=fileobj.id_files.filepath
        myfile=p.search(path).group(2)
        myfile_name=p2.search(myfile).group()
        if myfile.endswith(".pdb"): 
            structure_file=myfile
            structure_file_name=myfile_name
        elif myfile.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append([myfile,fileobj.id_files.id])
            traj_name_list.append(myfile_name)
    return (structure_file,structure_file_name,traj_list,traj_name_list)

structure_file,structure_file_name,traj_list,traj_name_list = obtain_dyn_files(argv[1])

#Create directory for dynamic simulation id if it doesn't exists yet
directory = "dyn_id" + argv[1]
if not os.path.exists(directory):
    os.makedirs(directory)

#Inside this folder, create symbolic links to desired files
pdbpath = basepath + structure_file
os.symlink(pdbpath, directory + "/" + directory + ".pdb")

#Create symbolic links also for trajectory file list
for i in range(0,len(lis)):
    trajpath = basepath + traj_list[i][0]
    os.symlink(trajpath, directory + "/" + directory + "_" + i + ".dcd")
