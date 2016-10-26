from django.shortcuts import render
from django.http import HttpResponse
from dynadb.models import DyndbFiles, DyndbFilesDynamics
from view.assign_generic_numbers_from_DB import obtain_gen_numbering
from view.assign_generic_numbers_from_DB import obtain_gen_numbering
from dynadb.pipe4_6_0 import *
import re

def index(request):
    #Obtain the filepaths --> from this, differentiate the structure and the trajectory files and pass it to the viewer.
    dyn_id =1 #EXAMPLE
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    if len(dynfiles) ==0:
        # ERROR: files not found
        pass
    else:
        paths_list=[e.id_files.filepath for e in dynfiles]
        structure_file=""
        structure_name=""
        traj_list=[]
        p=re.compile("(/protwis/sites/files/)(.*)")
        p2=re.compile("[\.\w]*$")
        for path in paths_list:
            myfile=p.search(path).group(2)
            myfile_name=p2.search(path).group()
            if myfile_name.endswith(".pdb"): #, ".ent", ".mmcif", ".cif", ".mcif", ".gro", ".sdf", ".mol2")): In which of these formats do we store the structures? Only pdb or more?
                structure_file=myfile
                structure_name=myfile_name
            elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
                traj_list.append((myfile, myfile_name))

        #Obtain the proteien info
        (numbers, num_scheme, db_seq) = obtain_gen_numbering(dyn_id)



######################## Constructing
        # Align DB sequence with pdb sequence
        pdb_name = "/protwis/sites/files/"+structure_file
        tablepdb,pdb_sequence,hexflag=checkpdb(pdb_name, segid="",start=-1,stop=99999, chain="P")
        result=matchpdbfa(db_seq,pdb_sequence, tablepdb, hexflag)
        gpcr_pdb={}
        for pos in result:
            #print(pos)#
            if pos[0] != "-":
                db_pos=pos[1][1]
                if numbers[db_pos][1]:
                    gpcr_pdb[numbers[db_pos][1]]=(db_pos, pos[0][2])
#        for e in sorted(gpcr_pdb, key=lambda pos: gpcr_pdb[pos][0]):
#            print(e, " - ", gpcr_pdb[e])
        a = request.POST.get('gpcr_num', False) ## IN PROCESS --> Maybe I should do this but with ajax, or maybe I can pass the dict as json..!




###################################
#    structure = "ex_model.pdb"
#    traj_list = ["ex_traj.xtc", "ex_traj2.dcd", "ex_traj3.xtc"]
    ligand = "CLZ" # EXAMPLE
    context={"structure_file":structure_file, "structure_name":structure_name , "traj_list":traj_list, "ligandname": ligand}
    return render(request, 'view/index.html', context)
