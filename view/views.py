from django.shortcuts import render
from django.http import HttpResponse
from structure.assign_generic_numbers_gpcr import GenericNumbering
from django.core.files import File
from io import StringIO

def index(request):
#
    f = open("/home/vagrant/dir/structures/test_model.pdb")
    str_file = File(f)
    generic_numbering = GenericNumbering(StringIO(str_file.read()))
#    out_struct = generic_numbering.assign_generic_numbers()

#
    structure = "ex_model2.pdb"
    traj_list = ["ex_traj.xtc", "ex_traj2.dcd", "ex_traj3.xtc"]
    ligand = "CLZ"
    context={"structure":structure, "traj_list":traj_list , "ligandname": ligand}
    return render(request, 'view/index.html', context)
# Get from the DB a given simulation. Obtain its structure file, a list of its trajectories, its ligands, ions, etc. Pass all that to the template.
