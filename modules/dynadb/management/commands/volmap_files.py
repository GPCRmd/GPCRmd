"""This  script (executed in vagrant) extracts the specified files from the GPCRmd database into a pickle file in the folder MEDIA_ROOT /Precomputed used to create the volmaps. 
The pickle file contains the list of pdb and trajectory filepaths (vagrant pahts) of which the volmaps will later be created.
To create the volmaps, one should execute the script: 'create_volmaps.py' on their LOCAL computer (not in vagrant, VMD can not be run there). 
The argument --filename is necessary to fill in. So to use the script one would do: python manage.py volmap_files --filename [name of picklefile]
Volmaps.py uses the just created pickle file to create the actual occupancy or density maps. """

import re
import os
from os import path
import gc
import pickle
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
import numpy as np

from modules.dynadb.models import *
from django.conf import settings


class Command(BaseCommand):
    help = "Creates the list of files used to create the water density maps and occupancy maps. By default, al ready for publication dynamics are considered"
    def add_arguments(self, parser):
        parser.add_argument(
           '--sub',
            dest='submission_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify submission id(s) for which the density and occupancy map will be precomputed.'
        )
        parser.add_argument(
           '--dyn',
            dest='dynamics_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify dynamics id(s) for which the density and/or occupancy map will be precomputed. '
        )
        parser.add_argument(
           '--traj',
            dest='traj_id',
            nargs='*',
            action='store',
            default=False,
            help='Specify file id(s) of trajectories for which an occupancy file will be precomputed. '
        )
        parser.add_argument(
            '--ignore_publication',
            action='store_true',
            dest='ignore_publication',
            default=False,
            help='Consider both published and unpublished dynamics.'
        )

        parser.add_argument(
           '--filename',
            dest='filename',
            nargs='*',
            type=str,
            action='store',
            #default=False,
            required = True,
            help='Specify the filename in which the list with dynamics will be saved. '
        )

        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            default=False,
            help='Overwrites already generated pickle files.'
        )


    def handle(self, *args, **options):

        #create folder where files should be accessed from and where information will be stored
        dynamics_path = settings.MEDIA_ROOT + "Dynamics"
        pickle_path = settings.MEDIA_ROOT + "Precomputed/WaterMaps"

        #give the options of the different parserarguments. 

        if not os.path.isdir(pickle_path):
            os.makedirs(pickle_path)

        if options['ignore_publication']:
            dynobj=DyndbDynamics.objects.all()
        else:
            dynobj=DyndbDynamics.objects.filter(is_published=True)
        if options['submission_id']:
            dynobj=dynobj.filter(submission_id__in=options['submission_id'])
        if options['dynamics_id']:
            dynobj=dynobj.filter(id__in=options['dynamics_id'])

        #dynobj=dynobj.annotate(traj_id=F('dyndbfilesdynamics__id_files__id'))
        if options['traj_id']:
            dynobj=dynobj.annotate(traj_id=F('dyndbfilesdynamics__id_files__id'))
            dynobj=dynobj.filter(traj_id__in=options['traj_id'])


        pdbfiles = dynobj.annotate(dyn_id=F('id'))                                      #file id from DyndbFilesDynamics table and on website id/12/
        pdbfiles = pdbfiles.filter(dyndbfilesdynamics__id_files__id_file_types_id=2)
        pdbfiles = pdbfiles.annotate(file_id=F('dyndbfilesdynamics__id_files_id'))      #last id not neccesary, gives same result without it. 
        pdbfiles = pdbfiles.annotate(pdb_path=F('dyndbfilesdynamics__id_files__filepath'))  #the order matters when to annotate 
        pdbfiles = pdbfiles.values('dyn_id', 'file_id', 'pdb_path')
        #print(pdbfiles)

        #{'pdb_path': settings.MEDIA_ROOT + 'Dynamics/10177_dyn_9.pdb', 'dyn_id': 9, 'file_id': 10177} which is a dictionary 

        #create the actual dictionary 
        dyn_dict = {}
        for i in pdbfiles:
            if i['dyn_id'] not in dyn_dict:
                dyn_dict[i['dyn_id']] = dict()                    #4: {}
                dyn_dict[i['dyn_id']]['dyn_id'] = i['dyn_id']
                dyn_dict[i['dyn_id']]['file_id'] = i['file_id']   #4: {'file_id': 10142}
                dyn_dict[i['dyn_id']]['pdb_path'] = i['pdb_path'] #4: {'file_id: 10142', 'pdb_path:/path/file.pdb'}
                dyn_dict[i['dyn_id']]['traj_files'] = dict()      #4: {'file_id: 10142', 'pdb_path:/path/file.pdb', 'traj_path': {}}
            if i['dyn_id'] is None:
                continue

        del pdbfiles
        del dynobj

        gc.collect()

        #get trajectory information and filepaths for dyn_ids present in dictionary 
        trajfiles = DyndbFiles.objects.annotate(dyn_id=F('dyndbfilesdynamics__id_dynamics'))
        trajfiles = trajfiles.filter(dyn_id__in=list(dyn_dict), id_file_types__is_trajectory=True)
        trajfiles = trajfiles.annotate(file_id=F('dyndbfilesdynamics__id_files_id'))
        trajfiles = trajfiles.values('dyn_id', 'file_id', 'filepath')

        #add trajfiles to dictionary dyn_dict. 
        for traj in trajfiles:
            dyn_dict[traj['dyn_id']]['traj_files'][traj['file_id']] = dict()
            if traj['filepath'] not in dyn_dict[traj['dyn_id']]['traj_files'][traj['file_id']]:
                dyn_dict[traj['dyn_id']]['traj_files'][traj['file_id']]['file_id'] = traj['file_id']
                dyn_dict[traj['dyn_id']]['traj_files'][traj['file_id']]['traj_path'] = traj['filepath']

        del trajfiles
        gc.collect()

        if len(dyn_dict.keys()) == 0:
            self.stdout.write(self.style.NOTICE("No dynamics found with specified conditions."))

        #transform dyn_dict into sorted list 
        dyn_list = [dyn_dict[dyn_id] for dyn_id in sorted(list(dyn_dict))]
        del dyn_dict
        gc.collect()

        for dyn in dyn_list:
            dyn['traj_files'] = [dyn['traj_files'][traj_id] for traj_id in sorted(list(dyn['traj_files']))]
        gc.collect()

        for i in dyn_list:
            print(i)
        print(len(dyn_list))

        #create pickle file 
        file_name = options['filename'][0]  #options gives a list with the saved input argument. To get the content of this list, specify [0]
        full_filename = os.path.join(pickle_path, file_name)
        exists = os.path.isfile(full_filename)
        create_file = False
        if exists:
            if options['overwrite']:   
                create_file = True
                self.stdout.write(self.style.NOTICE("Picklefile "+file_name+" already exists, but will be overwritten."))
            else: 
                self.stdout.write(self.style.NOTICE("Pickle file %s already exists and will not be overwritten."%file_name))
        else:
            create_file = True 

        if create_file == True:
            file_Object = open(full_filename, 'wb')
            pickle.dump(dyn_list, file_Object)
            file_Object.close()
