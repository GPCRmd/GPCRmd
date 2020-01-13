#ths script downloads the files from GPCRmd database, creates the volmaps and stores them in the Precomputed folder on the local computer in shared folder. 
#urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/10346_dyn_30.pdb', mypath+"test.pdb")
# You can define in this script if you want the maps to be overwritten
#It is NOT executed in vagrant, but on local computer. VMD 1.9.3 and Python 3.4 should be used and loaded. VMD should be able to start from the commandline. Check: website. 

import urllib.request
from urllib.request import urlopen
import os
from os import path 
import subprocess
from subprocess import Popen, PIPE     
import pickle  
import argparse 
import sys
import re


def file_exist (dyn_path, filepath, fileid, dynid, dyntype):
    exist_list = []
    # print(filepath)

    full_path = os.path.join(filepath)
    exist_list.append(full_path)

    if dyntype == 'pdb':
        pdb_path = os.path.join(dyn_path,str(fileid)+'_dyn_'+str(dynid)+'.pdb' )
        # print('check '+ pdb_path)
        exist_list.append(pdb_path)

    elif dyntype == 'traj':
        traj_path_xtc = os.path.join(dyn_path,str(fileid)+'_trj_'+str(dynid)+'.xtc' )
        traj_path_dcd = os.path.join(dyn_path,str(fileid)+'_trj_',str(dynid)+'.dcd' )
        exist_list.append(traj_path_xtc)
        exist_list.append(traj_path_dcd)

    # print('exlist')
    # print(exist_list)

    for i in exist_list:
        if os.path.isfile(i):
            exist = True
            return(exist)
        else:
            exist = False 

    return exist 


"""This function downloads the pdb file. You should specify the filename (fileid) and the path where it will be stored. """
def download_dynfiles(dyn_path, path_local, fileid, dynid, filetype):
    if filetype == 'pdb':

        try:
            fileroot=re.search("([\w_]*)\.pdb$",path_local).group()
            urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ fileroot, os.path.join(dyn_path, fileroot))
            sys.stdout.write("File with fileid: %s was downloaded (location: %s)\n" % (fileid, dyn_path))

        except:

            filename=str(fileid)+'_dyn_' + str(dynid) + '.pdb'
            urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ filename, os.path.join(dyn_path, filename))
            sys.stdout.write("File with fileid: %s was downloaded (location: %s)\n" % (fileid, dyn_path))

    elif filetype == 'traj':
        try:
            fileroot=re.search("([\w_]*)\.\w*$",path_local).group()
            urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ fileroot, os.path.join(dyn_path, fileroot))
            sys.stdout.write("Trajectory with fileid: %s was downloaded (location: %s)\n" % (fileid, dyn_path))
        except:
            filename_xtc=str(fileid)+'_trj_'+str(dyn_id) + '.xtc'
            filename_dcd=str(fileid)+'_trj_'+str(dyn_id) + '.dcd'
            if urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ filename_xtc, os.path.join(dyn_path, filename_xtc)):
                return
            else:
                urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ filename_dcd, os.path.join(dyn_path, filename_dcd))






# def download_traj(dyn_path, fileid, dynid):

#     fileroot=re.search("([\w_]*)\.\w*$",path).group()
#     urllib.request.urlretrieve('https://submission.gpcrmd.org/dynadb/files/Dynamics/'+ fileroot, path)
#     sys.stdout.write("Trajectory with fileid: %s was downloaded (location: %s)\n" % (fileid, path))

"""This function creates the volmaps by communicating with VMD. It requires the maptype, the precompute path and the filename """


# use argument parser
parser = argparse.ArgumentParser(description='This script is generating volumetric occupancy maps. If you want the maps to be overwritten, you should specify that.')

parser.add_argument(
            '--occupancy',
            action='store_true',
            dest='occupancy',
            default=False,
            help='Create occupancy maps, default is False.',
        )


parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated volumetric maps.',
        )

parser.add_argument(
            '--filename',
            dest='filename',
            nargs='*',
            type=str,
            action='store',
            #default=False,
            required = True,
            help='Specify the filename of the pickle file created by the script volmap_files.py which contains the information of the IDs for which the occupancy maps will be calculated. '
        )

arguments = parser.parse_args()
dic_arg = vars(arguments)

#import picklefile created by volmap_files as list and transform to paths of local computer
dyn_path = "/protwis/sites/files/Dynamics"
precomp_path = "/protwis/sites/files/Precomputed/WaterMaps"

 # MANUALLY change this path to the folder on local computer where gpcrmd_vagrant is located
if not os.path.isdir(precomp_path):
    os.makedirs(precomp_path)


file_name = dic_arg['filename'][0]  
                                       
full_filename = os.path.join(precomp_path, file_name)

if not os.path.isfile(full_filename):

    sys.stdout.write("'Something went wrong! Pickle file with dynamics does not exist, please make sure you executed the script volmap_files.py correctly.'\n")
    quit()

file_Object = open(full_filename, 'rb')
dyn_list = pickle.load(file_Object)
for i in dyn_list:
    print(i)


if len(dyn_list) == 0:
    sys.stdout.write("'Something went wrong! The pickle file is empty, please make sure you executed the script 'volmap_files.py' correctly.'\n")
    quit()


# MANUALLY change l_path (path in local computer to gpcrmd_vagrant/shared/sites/files/Dynamics)
path_v = '/protwis/sites/files/Dynamics'                             #vagrant path, don't change this
path_l = '/protwis/sites/files/Dynamics' #MANUALLY replace this with local path of where the folder: gpcrmd_vagrant/shared/sites/files/Dynamics is located on your local computer. 


# iterate over dynamics files (pdb and its trajectories) and create volmaps 
for file in dyn_list:
    dyn_id = file['dyn_id']
    print(dyn_id)
    pdb_path_v = file['pdb_path']         # extract filepath of pdb files (vagrant path) and replace it with path of local computer 
    pdb_path_l= pdb_path_v.replace(path_v, path_l)
    pdb_file = file['file_id']          # file_id of pdb file 
    traj_list = file['traj_files']

    if len(traj_list) == 0:
        sys.stdout.write("No trajectory files found for dynid: %s.\n" %s (str(dyn_id)))

    # if necessary, download pdb file CHECK THIS
    exist_pdb= file_exist(dyn_path, pdb_path_l, pdb_file, dyn_id, 'pdb')
    print(pdb_path_l)
    if not exist_pdb:
        #download file
        download_dynfiles(dyn_path, pdb_path_l, pdb_file, dyn_id, 'pdb')

    for i in range(len(traj_list)):
        file_id = traj_list[i]['file_id']    #use file_id of trajectory as output filename 
        traj_path_v = traj_list[i]['traj_path']  # extract filepath of trajfiles (vagrant path) and replace it with path of local computer #
        traj_path_l = traj_path_v.replace(path_v, path_l)

        exist_traj = file_exist(dyn_path, traj_path_l, file_id, dyn_id, 'traj')

        if not exist_traj:
            download_dynfiles(dyn_path,traj_path_l, file_id, dyn_id, 'traj')

        #create maps using VMD 
        cmd = ['vmd', pdb_path_l, traj_path_l, '-dispdev', 'text']
        type_map = 'occupancy'
        filename = '%s_%s_%s.dx' % (file_id, type_map, dyn_id)
        create_maps = False
        exist = os.path.isfile(os.path.join(precomp_path, filename))
        if exist == True:
            if arguments.overwrite == True:
                create_maps = True
                sys.stdout.write("The occupancy map "+filename+" already exists, but will be overwritten.\n")
            else:
                sys.stdout.write("The occupancy map "+filename+"already exists and will not be overwritten.\n")
                 
        else:
            create_maps = True 

        if create_maps == True:
            vmd = Popen(cmd, stdin=PIPE, universal_newlines=True)
            vmd.stdin.write("\n".join(['set molid top', 'set as [atomselect $molid "water and noh and within 10 of protein"]',\
            'animate delete beg 0 end 0 $molid','set minmax [measure minmax $as]','volmap occupancy $as -res 1.0 -allframes -combine avg -checkpoint 0 -o %s/%s' % (precomp_path, filename),'quit']))
            vmd.stdin.close()
            vmd.wait()














