from django.core.management.base import BaseCommand, CommandError
from modules.dynadb.models import DyndbDynamics, DyndbFiles, DyndbDynamicsComponents
import random
import mdtraj as md
import os
import json
from django.conf import settings, DEV

class Command(BaseCommand):
    help="Set new random entry of the month. To choose among published dynamics."

    def handle(self, *args, **options):

        def random_entrymonth():

            # Get random published dynamics objects
            filespath = settings.MEDIA_ROOT + ""
            DD = list(DyndbDynamics.objects.filter(is_published=True))
            random_dyn = random.choice(DD)
            dynid = random_dyn.id
            if DEV == True:
                dynid = 90
            print("The selected entry of the month is %d"%dynid)

            # Get first trajectory file and model PDB file of this thing
            df = DyndbFiles.objects.filter(dyndbfilesdynamics__type=2, dyndbfilesdynamics__id_dynamics=dynid)[0]
            trajfile = settings.MEDIA_ROOT[:-1] + df.filepath
            fileid = df.id
            pdbfile = settings.MEDIA_ROOT[:-1] + DyndbFiles.objects.filter(dyndbfilesdynamics__type=0, dyndbfilesdynamics__id_dynamics=dynid)[0].filepath

            # Create filtered trajectory file if not yet exists
            # trajfile_out = "Dynamics/%d_dyn_%d_filtered.dcd"%(fileid,dynid)
            topfile_out = "Dynamics/%d_dyn_%d_filtered.pdb"%(fileid,dynid)
            # entrymonth_dict = {'trajfile' : trajfile_out, 'topfile' : topfile_out, 'dynid' : dynid }
            entrymonth_dict = {'topfile' : topfile_out, 'dynid' : dynid }
            # trajfile_path = filespath+trajfile_out
            topfile_path = filespath+topfile_out
            if not os.path.exists(topfile_path):
                # Get ligands resnames
                resname_list = [a[0] for a in DyndbDynamicsComponents.objects.filter(id_dynamics=dynid, type=1).values_list('resname')]
                lignames = ' '.join(resname_list)

                # Load files with MDtraj
                traj = md.load(trajfile, top=pdbfile)

                # Select protien and ligand. OMit rest
                mysel = traj.topology.select('protein or resname '+lignames)
                traj_filt = traj.atom_slice(mysel)

                # Save dcd file of first 500 frames. Only    
                traj_reduced = traj_filt[:60] if len(traj_filt) > 100 else traj_filt
                # traj_reduced.save_dcd(trajfile_path)
                traj_reduced.save_pdb(topfile_path)

            # Modify entry of the month dictionary 
            entrymonth = settings.MEDIA_ROOT + "entry_month.json"
            with open(entrymonth, "w") as out:
                json.dump(entrymonth_dict, out)

            try: 
                pass
            except Exception as E: 
                # If an entry-of-the-month file could not be created from this dynid, try a new one
                print("Production of entry-of-the-month files for dynid %d failed because of %s. Repeating process..."%(dynid,E))
                # random_entrymonth()

        random_entrymonth()
