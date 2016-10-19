from django.shortcuts import render
from django.http import HttpResponse
from dynadb.models import DyndbFiles, DyndbFilesDynamics
from view.assign_generic_numbers_from_DB import obtain_gen_numbering

def index(request):
    #Obtain the filepaths --> from this, differentiate the structure and the trajectory files and pass it to the viewer.
    dyn_id =1 #EXAMPLE
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dyn_id)
    paths_list=[e.id_files.filepath for e in dynfiles]

    #Obtain the proteien info
    numbers, num_scheme = obtain_gen_numbering(dyn_id) #this will return a dict of position-gen_numbering and the name of the numbering method


 

####################### Example data:
    structure = "ex_model.pdb"
    traj_list = ["ex_traj.xtc", "ex_traj2.dcd", "ex_traj3.xtc"]
    ligand = "CLZ"
    context={"structure":structure, "traj_list":traj_list , "ligandname": ligand}
    return render(request, 'view/index.html', context)
# Get from the DB a given simulation. Obtain its structure file, a list of its trajectories, its ligands, ions, etc. Pass all that to the template.
