import sys
condapath = ['', '/env/lib/python3.4', '/env/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/lib-dynload', '/usr/lib/python3.4', '/usr/lib/python3.4/plat-x86_64-linux-gnu', '/env/lib/python3.4/site-packages']
sys.path = sys.path + condapath
import time
start_time = time.time()
import re
import os
from json import dumps
from view.obtain_gpcr_numbering import generate_gpcr_pdb
from view.data import change_lig_name
from view.views import obtain_compounds, sort_by_myorderlist, obtain_prot_chains, obtain_DyndbProtein_id_list, obtain_seq_pos_info
from django.db import models
from django.forms import ModelForm, Textarea
from dynadb.models import DyndbFilesDynamics
from django.core.management.base import BaseCommand, CommandError

    

class Command(BaseCommand):

    def obtain_dyn_files_from_id(dyn_id):
        """Given a dyn id, provides the stricture file name and a list with the trajectory filenames and ids."""
        dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics = dyn_id)
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


    def parse_pdb(residue_id, pdbfile, residue_num = None):
        """ 
        Finds chain number and residue number for a given residue_id
        """
        sel_chain_id = ""
        sel_residue_num = ""

        for line in open(pdbfile, "r"):
            if "END" in line: 
                break
            line_residue_id = line[17:21].replace(" ","")
            line_chain_id = line[21]
            line_residue_num = line[22:26].replace(" ","")
            if residue_id == line_residue_id:
                if ((residue_num is not None) and (residue_num == line_residue_num)) or residue_num is None:
                    sel_chain_id = line_chain_id
                    sel_residue_num = line_residue_num
        return(sel_chain_id, sel_residue_num)


    ###########################
    ## Trajectory and PDB files
    ###########################


    sys.argv[2] = str(sys.argv[2])

    # Obtain filenames
    structure_file,structure_file_name,traj_list,traj_name_list = obtain_dyn_files_from_id(sys.argv[2])

    #Create directory for dynamic simulation id if it doesn't exists yet
    directory = "/protwis/sites/files/Precomputed/get_contacts_files/dynamic_symlinks/dyn" + sys.argv[2]
    if not os.path.exists(directory):
        os.makedirs(directory)

    #Inside this folder, create symbolic links to desired files (and delete any previous with same name)
    basepath = "/protwis/sites/files/"
    pdbpath = basepath + structure_file
    mypdbpath =  directory + "/dyn" + str(sys.argv[2]) + ".pdb"
    if os.path.exists(mypdbpath):
        os.remove(mypdbpath)       
    os.symlink(pdbpath, mypdbpath)

    #Create symbolic links also for trajectory file list
    for i in range(0,len(traj_list)):
        trajpath = basepath + traj_list[i][0]
        mytrajpath = directory + "/dyn" + sys.argv[2] + "_" + str(i) + ".dcd"
        if os.path.exists(mytrajpath):
            os.remove(mytrajpath)
        os.symlink(trajpath, mytrajpath)


    ############
    #Ligand file
    ############

    # Obtain ligand by dynID
    (comp_li,lig_li,lig_li_s) = obtain_compounds(sys.argv[2])
    # Open out file
    ligfile_name = directory + "/dyn" + sys.argv[2] + "_ligand.txt"
    ligfile = open(ligfile_name, "w")

    # Print each ligand in a ligand file, after finding out its chain and residue id in the PDB
    for ligand in lig_li_s:
        # If we have the dyn7 exception of ligand being one cholesterol among others
        if "and" in ligand: # If its like 'CHL1 and 59'
            ligpos_list = ligand.split(" and ")
            ligres = ligpos_list[0]
            lignum_prov = ligpos_list[1]
            (ligchain, lignum) = parse_pdb(ligres, mypdbpath, lignum_prov)
            ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))


        else:
            ligres = ligand
            (ligchain, lignum) = parse_pdb(ligres, mypdbpath)
            ligfile.write("%s\t%s\t%s" % (lignum,ligchain,ligres))

    ligfile.close()

    ##################
    ## Dictionary file
    ##################
    dictfile_name = directory + "/dyn" + sys.argv[2] + "_dict.txt"
    dictfile = open(dictfile_name, "w")
    mydict = generate_gpcr_pdb(sys.argv[2], mypdbpath)
    dictfile.write(dumps(mydict))
    dictfile.close()
        
    ##############################
    # Execute get_contacts scripts
    ##############################
    for i in range(0,len(traj_list)):
        mytrajpath = directory + "/dyn" + sys.argv[2] + "_" + str(i) + ".dcd"
        os.system("bash /protwis/sites/protwis/contact_plots/scripts/get_contacts_dynfreq.sh " +  
            mypdbpath + " " +
            mytrajpath + " " +
            dictfile_name + " " + 
            ligfile_name + 
            " dyn" + sys.argv[2] )
