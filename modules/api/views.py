# DJANGO REST-API DATABASE TOOLS ########################################################################################################################################
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django.views.decorators.csrf import csrf_protect

from rest_framework import generics
from rest_framework.response import Response

from modules.api.serializers import *
from modules.dynadb.models import DyndbDynamics, DyndbModel, DyndbProtein, DyndbSubmissionMolecule
from modules.protein.models import ProteinFamily
from modules.interaction.models import StructureLigandInteraction

#search_dyn_class
class SearchByClass(generics.ListAPIView):
    """
    Retrieve a list with all dynamic ids in GPCRmd database using as input one or more classes (e.g. A, B1, B2, T, F,...).
    """
    serializer_class = DynsClassSerializer # Get info from DyndbDynamics using ids relationships

    def get_queryset(self, *args, **kwargs):
        classname = self.kwargs['classname']
        classname = classname.replace(" ", "").upper()
        classname = classname.split(",")
        classname = list(filter(None, classname)) # Remove empty strings in list
        class_slugs = []
        for cl in classname: 
            s_main_id = ProteinFamily.objects.filter(name__contains=f'Class {cl}').values_list("slug", flat = True)
            f_ids = ProteinFamily.objects.filter(slug__startswith=s_main_id[0]).values_list("id", flat = True)
            class_slugs.append({"classname":cl, "fam_ids":f_ids})

        return class_slugs

# search_comp    
class SearchCompound(generics.ListAPIView):
    """
    Retrieve information about the compounds elements simulated in GPCRmd grouped by type. 
    
    Use as input the next ids as a list to select the role of the ligand (e.g. 1, 3, 4): 
     0 - All
     1 - Orthosteric ligand
     2 - Allosteric ligand
     3 - Crystallographic ions
     4 - Crystallographic lipids
     5 - Crystallographic waters
     6 - Other co-crystalized item
     7 - Bulk waters
     8 - Bulk lipids
     9 - Bulk ions
    10 - Other bulk component
    """
    serializer_class = CompRoleSerializer # Get info from DyndbDynamics using ids relationships

    def get_queryset(self, *args, **kwargs):
        d_comp_type = {
            0:'Orthosteric ligand',
            1:'Allosteric ligand',
            2:'Crystallographic ions',
            3:'Crystallographic lipids',
            4:'Crystallographic waters',
            5:'Other co-crystalized item',
            6:'Bulk waters',
            7:'Bulk lipids',
            8:'Bulk ions',
            9:'Other bulk component',
        }

        ligrole = self.kwargs['ligroleids']
        ligrole = ligrole.replace(" ", "").upper()
        ligrole = ligrole.split(",")
        l_lig_ids = [] 
        if "0" in ligrole:
            ligrole = list(DyndbSubmissionMolecule.objects.order_by("type").values_list("type", flat = True).distinct())
        ligrole = list(filter(None, ligrole)) # Remove empty strings in list
        for lt in ligrole: 
            lt_m = int(lt)-1
            try:
                mol_ids = list(DyndbSubmissionMolecule.objects.filter(type=lt_m).values_list("molecule_id_id", flat = True))
                sub_ids = list(DyndbSubmissionMolecule.objects.filter(type=lt_m).values_list("submission_id_id", flat = True))
            except:
                continue
            l_lig_ids.append({"ligrole":d_comp_type[lt_m], "molecule_ids":mol_ids, "submission_ids":sub_ids})

        return l_lig_ids

# search_dyn_lig_type    
class SearchByLigType(generics.ListAPIView):
    """
    Retrieve a list with all dynamic ids in GPCRmd database if they have ligand (complex) or not (apoform).
    """
    serializer_class = DynsLigTypeSerializer # Get info from DyndbDynamics using ids relationships

    def get_queryset(self, *args, **kwargs):
        lig_type = [0, 1] 
        l_model_ids = [] 
        for lt in lig_type: 
            type_ids = DyndbModel.objects.filter(is_published=True).filter(type=lt).values_list("id", flat = True)
            if lt == 0: 
                ligtypename = "Apoform"
            else:
                ligtypename = "Complex"
            l_model_ids.append({"ligtype":ligtypename, "model_ids":type_ids})

        return l_model_ids
    
# search_all_pdbs
class SearchAllPdbs(generics.ListAPIView):
    """
    Retrieve a list with all Pdbs codes in GPCRmd database. 
    """

    queryset = DyndbModel.objects.filter(is_published=True).values("pdbid").distinct().order_by("pdbid")
    serializer_class = AllPdbsSerializer

# search_dyn_pdbs/

class SearchByPdbs(generics.ListAPIView):
    """
    Retrieve a list with all dynamic ids in GPCRmd database using as input one or more pdbid codes (e.g. 5TVN,4DKL).
    """
    serializer_class = DynsPdbsSerializer # Get info from DyndbDynamics using ids relationships

    def get_queryset(self, *args, **kwargs):
        pdbid = self.kwargs['pdbid']
        pdbid = pdbid.replace(" ", "").upper()
        pdbid = pdbid.split(",")
        pdbid = list(filter(None, pdbid)) # Remove empty strings in list
        model_ids = []
        for pdb in pdbid: 
            m_ids = DyndbModel.objects.filter(pdbid__contains=pdb).filter(is_published=True).values_list("id", flat = True)
            model_ids.append({"pdbid":pdb, "mol_ids":m_ids})
        # queryset = DyndbDynamics.objects.filter(id_model__in=model_ids)
                
        return model_ids
        
# search_all_uniprots
class SearchAllUniprots(generics.ListAPIView):
    """
    Retrieve a list with all Uniprot ids in GPCRmd database. 
    """

    queryset = DyndbProtein.objects.filter(is_published=True).values("uniprotkbac").distinct().order_by("uniprotkbac")
    serializer_class = AllUniprotsSerializer

# search_dyn_uniprots/
class SearchByUniprots(generics.ListAPIView):
    """
    Retrieve a list with all dynamic ids in GPCRmd database using as input one or more uniprotkbac codes (e.g. P28222, P42866).
    """
    serializer_class = DynsUniprotsSerializer # Get info from DyndbDynamics using ids relationships

    def get_queryset(self, *args, **kwargs):
        uniprotid = self.kwargs['uniprotid']
        uniprotid = uniprotid.replace(" ", "").upper()
        uniprotid = uniprotid.split(",")
        uniprotid = list(filter(None, uniprotid)) # Remove empty strings in list
        queryset = DyndbProtein.objects.filter(uniprotkbac__in=uniprotid).filter(is_published=True).distinct("uniprotkbac")
        
        return queryset
    
# search_dyn
class SearchByDyn(generics.ListAPIView):
    """
    Retrieve information related with the dynamic id in GPCRmd database. Same information displayed in the Search tool: https://www.gpcrmd.org/dynadb/search/. The input could be one or more dynamic ids (e.g. 11 or 17, 21)
    """
    serializer_class = DynsSearchSerializer # Get info from DyndbDynamics using ids relationships
    
    def get_queryset(self, *args, **kwargs):
        dyn_id = self.kwargs['dyn_id']
        dyn_id = dyn_id.replace(" ", "")
        dyn_id = dyn_id.split(",")
        dyn_id = list(filter(None, dyn_id)) # Remove empty strings in list
        dyn_id = [ int(x) for x in dyn_id ] # Convert to int
        queryset = DyndbDynamics.objects.filter(id__in=dyn_id)
        return queryset

# search_sub
class SearchBySub(generics.ListAPIView):
    """
    Return the dynamic/s id related with the submission/s id indicated. The input could be one or more submission ids (e.g. 200,1427).
    """
    serializer_class = SubsSearchSerializer # Get info from DyndbDynamics using ids relationships
    
    def get_queryset(self, *args, **kwargs):
        sub_id = self.kwargs['sub_id']
        sub_id = sub_id.replace(" ", "")
        sub_id = sub_id.split(",")
        sub_id = list(filter(None, sub_id)) # Remove empty strings in list
        sub_id = [ int(x) for x in sub_id ] # Convert to int
        queryset = DyndbDynamics.objects.filter(submission_id__in=sub_id)
        return queryset

# NOT API TOOLS ###############################################################################################################################################################
import os
from os.path import join
import shutil
import time
import json

from wsgiref.util import FileWrapper

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse
from django.utils import timezone

from modules.dynadb.models import DyndbFiles, DyndbFilesDynamics
from modules.api.models import AllDownloads

from celery.result import AsyncResult
from .tasks import prepare_file

class IDDownloader():
    def __init__(self, dyns, user):
        """
        __init__ function to start and define parameters used on class Downloader. 

        Params: 
            > dyns --> List of dynamic ids. 
            > user --> User id that request the file. 
            > outfile --> Name of the directory. 
            > l_dyns --> List python type of dyns parameter.
            > tmp --> Path of the main temporary folder.
            > tmpdir --> Path of the temporary folder that will contain all the files.
            > dic_files --> Dictionary that contains dyn ids as keys and list of file ids as value.
            > dyn_path --> Path of the temporary folder that will contain the files of one dynamic.
        """
        self.dyns = dyns
        self.user = user
        try:
            id = AllDownloads.objects.latest('id').id
        except:
            return JsonResponse({'error': 'Task not completed or failed.'}, status=400)
        self.outfile = f"download_all_{id}"
        self.zip = f"{self.outfile}.zip"

        #Modify list of values
        dyns = self.dyns.replace(" ","") # Clean whitespaces e.g. 36
        self.l_dyns = dyns.split(",") # Create list

        #Create directory to store 
        self.tmp = settings.DOWNLOAD_FILES
        self.tmpdir = join(self.tmp,self.outfile) # .../tmp/GPCRmd_downloads/download_all_0
        os.umask(0)
        os.makedirs(self.tmpdir, mode=0o777, exist_ok=True)
        # self.dirdyn = join(self.tmpdir,"dynamics") # .../tmp/GPCRmd_downloads/download_all_0
        # os.makedirs(self.dirdyn, mode=0o777, exist_ok=True)

@login_required
@csrf_protect
def download_id(request): 
    request.session.set_expiry(0) 
    dyn_ids = request.GET.get('dyn_ids')
    if not dyn_ids:
        return JsonResponse({'error': 'dyn_ids parameter is required.'}, status=400)
    obj = json.dumps(IDDownloader(dyn_ids, request.user.id).__dict__)
    task = prepare_file.delay(obj)
    data = dict()
    #data["url"] = join("/dynadb/tmp/GPCRmd_downloads/", obj["zip"])  # CHANGE URL 
    data["task_id"] = task.task_id
    return JsonResponse(data)

def download_link(request, task_id):
    result = AsyncResult(task_id)
    time.sleep(5)
    if result.state == 'SUCCESS':
        return JsonResponse({'zip_url': result.result, 'log_url':result.result.replace(".zip", ".log")})
    else:
        return JsonResponse({'error': 'Task not completed or failed.'}, status=400)
