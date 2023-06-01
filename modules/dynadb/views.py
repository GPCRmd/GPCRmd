
# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import Count
from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseForbidden, HttpResponseServerError, Http404
from django.urls import reverse
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils import timezone
from django.template import loader
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from modules.accounts.user_functions import user_passes_test_args, is_submission_owner, is_published_or_submission_owner
from collections import OrderedDict
from sendfile import sendfile
from pathlib import Path
import xml.etree.ElementTree as ET
import re, os, pickle
import shutil
import time
import sys
import json
import mimetypes
import requests
import math
import itertools
import numpy as np
import mdtraj as md
import tarfile
from bs4 import BeautifulSoup
from operator import itemgetter
from os import listdir
from os.path import isfile, normpath
import urllib
from modules.accounts.models import User
from django.db.models.functions import Concat
from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from .customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension, DownloadGenericError, RequestBodyTooLarge, FileTooLarge, TooManyFiles, SubmissionValidationError
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from .sequence_tools import get_mutations, check_fasta
from .csv_in_memory_writer import CsvDictWriterNoFile, CsvDictWriterRowQuerySetIterator
from .uploadhandlers import TemporaryFileUploadHandlerMaxSize,TemporaryMoleculeFileUploadHandlerMaxSize
from .molecule_properties_tools import open_molecule_file, check_implicit_hydrogens, check_non_accepted_bond_orders, generate_inchi, generate_inchikey, generate_smiles, get_net_charge, write_sdf, generate_png, stdout_redirected, neutralize_inchikey, standarize_mol_by_inchi,validate_inchikey,remove_isotopes
from rdkit.Chem import MolFromInchi,MolFromSmiles, MolFromPDBFile
from rdkit.Chem import SanitizeMol, RemoveHs, SDMolSupplier
from rdkit.Chem.Draw.MolDrawing import DrawingOptions
from rdkit.Chem.Draw import MolToFile, PrepareMolForDrawing
from .molecule_download import retreive_compound_data_pubchem_post_json, retreive_compound_sdf_pubchem, retreive_compound_png_pubchem, CIDS_TYPES, pubchem_errdata_2_response, retreive_molecule_chembl_similarity_json, chembl_get_compound_id_query_result_url,get_chembl_molecule_ids, get_chembl_prefname_synonyms, retreive_molecule_chembl_id_json, retreive_compound_png_chembl, chembl_get_molregno_from_html, retreive_compound_sdf_chembl, chembl_errdata_2_response
#from .models import Question,Formup
#from .forms import PostForm
from modules.structure.models import StructureType, StructureModelLoopTemplates
from modules.protein.models import Protein
from modules.common.models import  WebResource
from .models import DyndbBinding,DyndbEfficacy,DyndbReferencesExpInteractionData,DyndbExpInteractionData,DyndbReferences, DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel,  DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbCannonicalProteins,  DyndbSubmissionMolecule, DyndbSubmissionProtein,DyndbComplexProtein,DyndbReferencesProtein,DyndbComplexMoleculeMolecule,DyndbComplexMolecule,DyndbComplexCompound,DyndbReferencesMolecule,DyndbReferencesCompound,DyndbComplexExp, DyndbNonGPCRDynamics

from modules.dynadb import psf_parser as psf
from .models import DyndbSubmissionProtein, DyndbFilesDynamics, DyndbReferencesModel, DyndbModelComponents,DyndbProteinMutations,DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbModeledResidues, DyndbDynamicsMembraneTypes, DyndbDynamicsSolventTypes, DyndbDynamicsMethods, DyndbAssayTypes, DyndbSubmissionModel, DyndbFilesModel,DyndbSubmissionDynamicsFiles,DyndbSubmission, DyndbReferences, DyndbInhibition
from .pdbchecker import split_protein_pdb, split_resnames_pdb, molecule_atoms_unique_pdb, diff_mol_pdb, residue_atoms_dict_pdb, residue_dict_diff, get_atoms_num, get_frames_num


#from django.views.generic.edit import FormView
from .forms import * 
#from .forms import NameForm, TableForm

from .view_decorators import test_if_closed
from .pipe4_6_0 import *
from time import sleep
from random import randint
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from .models import Model2DynamicsMoleculeType, smol_to_dyncomp_type, smol_to_modelcomp_type
from django.conf import settings
from django.views.defaults import server_error
from revproxy.views import ProxyView
import mdtraj as md
from modules.view.assign_generic_numbers_from_DB import obtain_gen_numbering 
from scipy import constants
from modules.dynadb.data import *
model_2_dynamics_molecule_type = Model2DynamicsMoleculeType()
color_label_forms=["blue","red","yellow","green","orange","magenta","brown","pink"]
# Custom view function wrappers
from functools import wraps
import copy
from rdkit.Chem import ForwardSDMolSupplier, AssignAtomChiralTagsFromStructure

def obtain_prot_chains(pdb_name):
    chain_name_s=set()
    if not settings.MEDIA_ROOT[:-1] in pdb_name: 
        pdb_name = settings.MEDIA_ROOT[:-1] + pdb_name
    fpdb=open(pdb_name,'r')
    for line in fpdb:
        if useline2(line):
            chain_name_s.add(line[21])
    return list(chain_name_s)

def default_500_handler(view_func):
    @wraps(view_func)
    def _wrapped_view(request,*args, **kwargs):
        try:
            return view_func(request,*args, **kwargs)
        except:
            if settings.DEBUG:
                raise
            else:
                return server_error(request)
    return _wrapped_view
    
def textonly_500_handler(view_func):
    @wraps(view_func)
    def _wrapped_view(request,*args, **kwargs):

        try:
            return view_func(request,*args, **kwargs)
        except:
            if settings.DEBUG:
                raise
            else:
                return HttpResponseServerError("Server Error (500).",content_type='text/plain; charset=UTF-8')
    return _wrapped_view
    
def textonly_404_handler(view_func):
    @wraps(view_func)
    def _wrapped_view(request,*args, **kwargs):

        try:
            return view_func(request,*args, **kwargs)
        except:
            if settings.DEBUG:
                raise
            else:
                return HttpResponseNotFound("Not Found (404).",content_type='text/plain; charset=UTF-8')
    return _wrapped_view
# Create your views here.

@login_required
#@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def REFERENCEview(request, submission_id=None):
    if request.method == 'POST' and is_submission_owner(request.user, int(request.POST['submission_id'])):
        submission_id=request.POST['submission_id']
        if submission_id is None:
            iii1="Please, fill in the 'Submission_id' field "
            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
            sub =''
        else:
            sub = submission_id
        action="/".join(["/dynadb/REFERENCEfilled",sub])
        now=timezone.now()
        author="jmr"
#        forminfo={'issue':'1','url':'http://localhost:8000/ttt/prueba','doi':'8382938','title':'prinncii','journal_press':'marca','pub_year':'1996', 'volume':'agosto', 'pages':'2-3','authors':'pepe; luis', 'pmid':'4'}
        def_user_dbengine=settings.DATABASES['default']['USER']
        def_user=request.user.id
        print("HOLA  ", def_user)
        initREFF={'dbname':None, 'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
        fdbREFF = dyndb_ReferenceForm(request.POST)
#####  Fill the empty fields in the fdbREFF instance with data from the initREFF dictionary
##### Check whether the fdbREFF instance of dyndb_ReferenceForm is valid:
        SubmitRef=True
        qRFdoi=DyndbReferences.objects.filter(doi=request.POST['doi'])
        qRFpmid=DyndbReferences.objects.filter(pmid=request.POST['pmid'])
        if qRFdoi.exists():
            iii1="Please, Note that the reference you are trying to submit has a DOI previously stored in the GPCRmd. Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCRmd administrator"
            print(iii1)
            response = HttpResponse(iii1,content_type='text/plain; charset=UTF-8')
            FRpk = qRFdoi.values_list('id',flat=True)
            SubmitRef=False
           # return response
        if qRFpmid.exists():
            iii1="Please, Note that the reference you are trying to submit has a PMID previously stored in the GPCRmd.  Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCRmd administrator"
            print(iii1)
            response = HttpResponse(iii1,content_type='text/plain; charset=UTF-8')
            SubmitRef=False
            FRpk = qRFpmid.values_list('id',flat=True)
           # return response
            
        if SubmitRef:
            if fdbREFF.is_valid(): 
                # process the data in form.cleaned_data as required
                formREFF=fdbREFF.save(commit=False)
                for (key,value) in initREFF.items():
                    setattr(formREFF, key, value)
                
                print(fdbREFF.data,"  datos objeto fdbREFF")
                formREFF.save()
                FRpk = formREFF.pk
            else:
                iii=fdbREFF.errors.as_text()
                print("Errors", iii)
                response = HttpResponse(iii,status=422,sreason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
                pass
        qSubmission=DyndbSubmission.objects.filter(id=submission_id)
        qT=list(qSubmission.filter(dyndbsubmissionprotein__submission_id=submission_id,dyndbsubmissionmolecule__submission_id=submission_id,dyndbsubmissionmodel__submission_id=submission_id,dyndbdynamics__submission_id=submission_id).values('dyndbsubmissionprotein__protein_id','dyndbsubmissionmolecule__molecule_id','dyndbsubmissionmolecule__molecule_id__id_compound','dyndbsubmissionmodel__model_id','dyndbdynamics__id'))
        dictprot={'id_protein':qT[0]['dyndbsubmissionprotein__protein_id'], 'id_references':FRpk}
        dictmod={'id_model':qT[0]['dyndbsubmissionmodel__model_id'], 'id_references':FRpk }
        dictdyn={'id_dynamics':qT[0]['dyndbdynamics__id'], 'id_references':FRpk }
        print("SubmitRef", SubmitRef)
        refprot=dyndb_References_Protein(dictprot)
        if SubmitRef:
            if not qRFdoi.filter(dyndbreferencesprotein__id_protein=qT[0]['dyndbsubmissionprotein__protein_id'],dyndbreferencesprotein__id_references=FRpk).exists():
                if refprot.is_valid():
                    refprot.save()
                else:
                    print("refprot is not valid",refprot.errors.as_text())
                
        refmod=dyndb_References_Model(dictmod)
        if  SubmitRef:
            if not qRFdoi.filter(dyndbreferencesmodel__id_model=qT[0]['dyndbsubmissionmodel__model_id'],dyndbreferencesmodel__id_references=FRpk).exists():
                if refmod.is_valid():
                    refmod.save()
                else:
                    print("refmod is not valid",refmod.errors.as_text())
        
        refdyn=dyndb_References_Dynamics(dictdyn)

        if SubmitRef:
            if not qRFdoi.filter(dyndbreferencesdynamics__id_dynamics=qT[0]['dyndbdynamics__id'],dyndbreferencesdynamics__id_references=FRpk).exists():
                if refdyn.is_valid():
                    refdyn.save()
                    print("refdyn may  be saved ",refdyn.errors.as_text())
                else:
                    print("refdyn is not valid",refdyn.errors.as_text())
        

        dictmol={}
        dictcomp={}
        i=0
        for l in qT:
            dictmol[i]={'id_molecule':qT[i]['dyndbsubmissionmolecule__molecule_id'],  'id_references':FRpk}
            refmol=dyndb_References_Molecule(dictmol[i])                                     
            if SubmitRef:
                if not qRFdoi.filter(dyndbreferencesmolecule__id_molecule=qT[i]['dyndbsubmissionmolecule__molecule_id'],dyndbreferencesmolecule__id_references=FRpk).exists():
                    if refmol.is_valid():                                                         
                        refmol.save()                                                             
                    else:                                                                         
                        print("refmol is not valid",refmol.errors.as_text())                      
          
            dictcomp[i]={'id_compound':qT[i]['dyndbsubmissionmolecule__molecule_id__id_compound'],  'id_references':FRpk}
            refcomp=dyndb_References_Compound(dictcomp[i])
            if not SubmitRef:
                if not qRFdoi.filter(dyndbreferencescompound__id_compound=qT[i]['dyndbsubmissionmolecule__molecule_id__id_compound'],dyndbreferencescompound__id_references=FRpk).exists():
                    if refcomp.is_valid():
                        refcomp.save()
                    else:
                        print("refcomp is not valid",refcomp.errors.as_text())
            i=i+1
       # return HttpResponseRedirect("/".join(["/dynadb/REFERENCEfilled",submission_id]), {'submission_id':submission_id, 'fdbREFF':fdbREFF } )

        
    # if a GET (or any other method) we'll create a blank form
        return HttpResponse("Successful reference submission!!!", content_type='application/json')
    elif request.method == 'POST' and not is_submission_owner(request.user, int(request.POST['submission_id'])):
        message="You are not allowed to add references to the chosen submission. "
        return HttpResponseForbidden(message, content_type='text/plane')
    else:
        fdbREFF = dyndb_ReferenceForm()
        return render(request,'dynadb/REFERENCES.html', {'fdbREFF':fdbREFF, 'submission_id':submission_id})

@login_required
def show_alig(request, alignment_key):
    '''Performs an aligment between two strings and returns the result to a view. '''
    if request.method=='POST':
        wtseq=request.POST.get('wtseq')
        mutseq=request.POST.get('mutant')
        if '\n' in mutseq or '>' in mutseq:
            mutlines=mutseq.split('\n')
            if '>' in mutlines[0]:
                mutlines=mutlines[1:]
            mutseq=''.join(mutlines)
        result=align_wt_mut(wtseq,mutseq)
        result='>uniprot:\n'+result[0]+'\n>system_seq:\n'+result[1]
        request.session[alignment_key]=result
        tojson={'alignment':result, 'message':'' , 'userkey':alignment_key}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')
    else:
        alignment=request.session[alignment_key]
        return render(request,'dynadb/show_alignment.html', {'alig':alignment})

def delProtByUpdateProtein(protein_id,ii,submission_id,is_mutated_val):
    

    Prot_in_other_sub=DyndbSubmissionProtein.objects.filter(protein_id=protein_id).exclude(submission_id=submission_id)
    if not Prot_in_other_sub.exists():
        qisit_Canprot=DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id,id_cannonical_proteins=protein_id)
        if qisit_Canprot.exists(): #if so protein_id is the cannonical protein!!! look for other non-canonical proteins linked to it
            qProt_CanProt_all=DyndbProteinCannonicalProtein.objects.filter(id_cannonical_proteins=protein_id)
            qProt_CanProt_others=qProt_CanProt_all.exclude(id_protein=protein_id)
            if not qProt_CanProt_others.exists():
                if qProt_CanProt_all.exists(): #there is only the protein_id linked to the canonical which is itself
                    print("Protein_id is the only protein linked to the canonical protein which is itself and it can be deleted if only is involved in the current model and complex. \n int_id y submission_id =", ii," ",submission_id )
                    DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id).delete()
                DyndbCannonicalProteins.objects.filter(id_protein=protein_id).delete()
                DyndbOtherProteinNames.objects.filter(id_protein=protein_id).delete()
                DyndbProteinSequence.objects.filter(id_protein=protein_id).delete()
                DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=ii).update(protein_id=None,int_id=None,submission_id=None)
                DyndbProtein.objects.filter(id=protein_id).delete()
        else: #protein_id is not the canonical but maybe there is no other proteins linked to its canonical
            qrelCanprot=DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id)
            qrelProtCanprot=DyndbProteinCannonicalProtein.objects.filter(id_cannonical_proteins=qrelCanprot.values('id_cannonical_proteins')).exclude(id_protein=protein_id)
            if len(qrelProtCanprot)==1: # only the entry relating the canonical protein with itself is included as the one involving the current protein was excluded
                print("Protein_id is the only protein linked to the canonical protein and both can be deleted if they only are involved in the current model and complex")
                qPdP=list(DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id).values_list('id_cannonical_proteins',flat=True))
                qSubCanProt_with_int_id=DyndbSubmissionProtein.objects.filter(submission_id=submission_id,protein_id=protein_id,int_id=ii).exclude(int_id=None)
                print("if the canonical protein has a int_id in this submission should not be removed")
                if not qSubCanProt_with_int_id.exists(): #if the canonical protein has int_id it is being used instead the original mutated protein. Then remove it does not exist
                    DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id).delete()
                    DyndbCannonicalProteins.objects.filter(id_protein__in=qPdP).delete()
                    DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=None,protein_id__in=qPdP).delete()
                    DyndbOtherProteinNames.objects.filter(id_protein__in=qPdP).delete()
                    DyndbProteinSequence.objects.filter(id_protein__in=qPdP).delete()
                    DyndbProteinSequence.objects.filter(id_protein=protein_id).delete()
                    if is_mutated_val or DyndbProtein.objects.filter(id=protein_id,is_mutated=True).exists():
                        DyndbProteinMutations.objects.filter(id_protein=protein_id).delete()
                    DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=ii,protein_id=protein_id).update(protein_id=None,int_id=None)
                    DyndbProtein.objects.filter(id__in=qPdP).delete()
                    DyndbProtein.objects.filter(id=protein_id).delete()
                else:
                    DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id).exclude(id_cannonical_proteins=qrelCanprot.values('id_cannonical_proteins')).delete()
                    DyndbProteinSequence.objects.filter(id_protein=protein_id).delete()
                    if is_mutated_val or DyndbProtein.objects.filter(id=protein_id,is_mutated=True).exists():
                        DyndbProteinMutations.objects.filter(id_protein=protein_id).delete()
                    DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=ii,protein_id=protein_id).update(protein_id=None,int_id=None)
                    DyndbProtein.objects.filter(id=protein_id).delete()
                    
            else:
                print("Protein_id is not the only protein linked to the canonical protein and only it can be deleted if it is only involved in the current model and complex")
                DyndbProteinCannonicalProtein.objects.filter(id_protein=protein_id).delete()
                DyndbProteinSequence.objects.filter(id_protein=protein_id).delete()
                if is_mutated_val or DyndbProtein.objects.filter(id=protein_id,is_mutated=True).exists():
                    DyndbProteinMutations.objects.filter(id_protein=protein_id).delete()
                DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=ii,protein_id=protein_id).update(protein_id=None,int_id=None)
                DyndbProtein.objects.filter(id=protein_id).delete()

def deleteComplexByUpdateProtein(protein_id,ii,submission_id,is_mutated_val,model_del_prot=False):
    qAllCexp_invg_prot =DyndbComplexExp.objects.filter(dyndbcomplexprotein__id_protein=protein_id)
    qOthersCexp_invg_prot = qAllCexp_invg_prot.exclude(dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel__submission_id=submission_id) 
    qCexp_invd_this_sub = qAllCexp_invg_prot.filter(dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel__submission_id=submission_id) 
    if not qOthersCexp_invg_prot.exists():
        if qCexp_invd_this_sub.exists():#only 
            models_invg_this_Complex=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp=qCexp_invd_this_sub) 
            if len(models_inv_this_Complex)==1:#the complex only exist in the model in this submission can be deleted
                other_sub_invg_ComplexExp=DyndbSubmissionModel.objects.filter(model_id__id_complex_molecule__id_complex_exp=qCexp_invd_this_sub).exclude(submission_id=submission_id)
                if not other_sub_invg_mol.exists():#the molecule and the compound have been used only in this submission and can be removed
                    DyndbMoleculeComplexMolecule.objects.filter(id_complex_molecule__id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexMolecule.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexCompound.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexProtein.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexExp.objects.filter(id=qCexp_inv_this_sub).delete()
                    print(qCexp_inv_this_sub, "Complex deleted")
                    if model_del_molec:
                        delProtByUpdateProtein(protein_id,ii,submission_id,is_mutated_val)   
    else:
        if qCexp_invd_this_sub.exists():#only 
            models_invg_this_Complex=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp=qCexp_invd_this_sub) 
            if len(models_invg_this_Complex)==1:#the complex only exist in the model in this submission can be deleted
                other_sub_invg_ComplexExp=DyndbSubmissionModel.objects.filter(model_id__id_complex_molecule__id_complex_exp=qCexp_invd_this_sub).exclude(submission_id=submission_id)
                if not other_sub_invg_mol.exists():#the molecule and the compound have been used only in this submission and can be removed
                    DyndbMoleculeComplexMolecule.objects.filter(id_complex_molecule__id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexMolecule.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexCompound.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexProtein.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                    DyndbComplexExp.objects.filter(id=qCexp_inv_this_sub).delete()
                    print(qCexp_inv_this_sub, "Complex deleted")
                    #protein must not be deleted

def deleteModelbyUpdateProtein(protein_id,ii,submission_id,is_mutated_val):
    #The protein_id will be removed not updated!!!!!
    qMod_apo_all=DyndbModel.objects.filter(id_protein=protein_id)
    qMod_apo_others=qMod_apo_all.exclude(dyndbsubmissionmodel__submission_id=submission_id)
    qMod_comp_all=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein=protein_id)#models involving complexes in which protein_id is involved
    qMod_comp_others=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein=protein_id).exclude(dyndbsubmissionmodel__submission_id=submission_id) #models involving complexes in which the protein is involved but the model in this submission is excluded. Maybe the complex in the model in the submission is used in models in other submission.
    if not qMod_apo_others.exists() and not qMod_comp_others.exists(): #if no other models exist check if the model in this submission exist. 
       #  if qMod_apo_all.exist or qMod_comp_all.exists: check the model is not being using in other submission
        if qMod_apo_all.exists(): 
            other_sub_using_model=DyndbSubmissionModel.objects.filter(model_id=qMod_apo_all).exclude(submission_id=submission_id)
            if not other_sub_using_model.exists():          
                DyndbSubmissionModel.objects.filter(submission_id=submission_id)
                DyndbModeledResidues.objects.filter(id_protein=protein_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                DyndbModel.objects.filter(id__in=qMod_apo_all).update(id_complex_molecule=None,id_protein=None,model_creation_submission_id=None)
                delProtByUpdateProtein(protein_id,ii,submission_id,is_mutated_val) #Borrar Complex si es posible
        elif qMod_comp_all.exists():#the Model has to be updated by updating Complex_Protein and Modeled REsidues
            other_sub_using_model=DyndbSubmissionModel.objects.filter(model_id=qMod_comp_all).exclude(submission_id=submission_id)
            if not other_sub_using_model.exists():          
                DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id,bonded_to_id_modeled_residues_id__in=DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id).values('id')).exclude(id_protein=protein_id).update(bonded_to_id_modeled_residues=None)
                DyndbModeledResidues.objects.filter(id_protein=protein_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                DyndbModel.objects.filter(id__in=qMod_comp_all).update(id_complex_molecule=None,id_protein=None,model_creation_submission_id=None)
                deleteComplexByUpdateProtein(protein_id,ii,submission_id,is_mutated_val,model_del_prot=True)        
        else:#no model involving the protein exists yet,so remove the protein
            delProtByUpdateProtein(protein_id,ii,submission_id,is_mutated_val) #Borrar Complex si es posible
    else:
        if qMod_comp_all.exists():#the Model has to be updated by updating Complex_Protein and Modeled REsidues
            Mod_invg_comp_and_sub=qMod_comp_all.filter(dyndbsubmissionmodel__submission_id=submission_id)
            other_sub_using_model=DyndbSubmissionModel.objects.filter(model_id=Mod_invg_comp_and_sub).exclude(submission_id=submission_id)
            if not other_sub_using_model.exists():          
                DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id,bonded_to_id_modeled_residues_id__in=DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id).values('id')).exclude(id_protein=protein_id).update(bonded_to_id_modeled_residues=None)
                DyndbModeledResidues.objects.filter(id_protein=protein_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                DyndbModel.objects.filter(id__in=qMod_comp_all).update(id_complex_molecule=None,id_protein=None,model_creation_submission_id=None)
                deleteComplexByUpdateProtein(protein_id,ii,submission_id,is_mutated_val,model_del_prot=False)        

def delMolByUpdateMolecule(molecule_id,ii,submission_id):
    print("\ndeleteComplexByUpdateMolecule ")
    qisit_Std_mol =DyndbMolecule.objects.filter(id=molecule_id,id_compound__std_id_molecule=molecule_id)
    if qisit_Std_mol.exists(): #if so protein_id is the cannonical protein!!! look for other non-canonical proteins linked to it
        qcompo_mol =DyndbCompound.objects.filter(dyndbmolecule__id_compound=F('id'),std_id_molecule=molecule_id)#includes the molecule to be updated
        if len(qcompo_mol) == 1:#only the molecule to be updated is linked to the compound
            other_sub_invg_mol=DyndbSubmissionMolecule.objects.filter(molecule_id=molecule_id).exclude(submission_id=submission_id)
            if not other_sub_invg_mol.exists():#the molecule and the compound have been used only in this submission and can be removed
                 DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id,id_dynamics__submission_id=submission_id).delete()
                 DyndbModelComponents.objects.filter(id_molecule=molecule_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                 DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None,int_id=None)
                 compid=qcompo_mol.values_list('id',flat=True)[0]
                 DyndbFiles.objects.filter(dyndbfilesmolecule__id_molecule=molecule_id).delete()
                 DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).delete()
                 qcompo_mol.update(std_id_molecule=None)
                 DyndbMolecule.objects.filter(id_compound=compid).delete()
                 DyndbOtherCompoundNames.objects.filter(id_compound=compid).delete()
                 DyndbCompound.objects.filter(id=compid).delete()
                 qcompo_mol.delete()
            else:
                 DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id,id_dynamics__submission_id=submission_id).delete()
                 DyndbModelComponents.objects.filter(id_molecule=molecule_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                 DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None,int_id=None)
        else:
             DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None,int_id=None)
    else:#the molecule_id object is not the std molecule 
        std_mol=DyndbMolecule.objects.filter(id=molecule_id).values('id_compound__std_id_molecule')  
        qcompo_mol =DyndbCompound.objects.filter(dyndbmolecule__id_compound=F('id'),std_id_molecule=std_mol)#includes the molecule to be updated
        if len(qcompo_mol) == 2: #only the std molecule and the current are registered
            sub_invg_mol=DyndbSubmissionMolecule.objects.filter(molecule_id=molecule_id)
            sub_invg_stdmol=DyndbSubmissionMolecule.objects.filter(molecule_id=std_mol)
            if len(sub_invg_mol)==1:
                if len(sub_invg_stdmol)==1:#the std molecule, compound and not standard molecule have to be removed and submission_id updated
                    if not sub_invg_stdmol.filter(int_id=None,type=None).exists():
                        DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id,id_dynamics__submission_id=submission_id).delete()
                        DyndbModelComponents.objects.filter(id_molecule=molecule_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                        sub_invg_stdmol.update(molecule_id=None,not_in_model=None)
                        sub_invg_mol.update(molecule_id=None,not_in_model=None)
                        DyndbFiles.objects.filter(dyndbfilesmolecule__id_molecule=molecule_id).delete()
                        DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).delete()
                        DyndbFiles.objects.filter(dyndbfilesmolecule__id_molecule=std_mol).delete()
                        DyndbFilesMolecule.objects.filter(id_molecule=std_mol).delete()
                        compid=qcompo_mol.values_list('id',flat=True)[0]
                        qcompo_mol.update(std_id_molecule=None)
                        DyndbMolecule.objects.filter(id_compound=compid).delete()
                        DyndbCompound.objects.filter(id=compid).delete()
                    else:# not standart molecule has to be removed
                        DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id,id_dynamics__submission_id=submission_id).delete()
                        DyndbModelComponents.objects.filter(id_molecule=molecule_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                        sub_invg_mol.update(molecule_id=None,not_in_model=None)#only contains one record which has to be updated for reuse
                        DyndbMolecule.objects.filter(id=molecule_id).delete()
                else:
                    DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id,id_dynamics__submission_id=submission_id).delete()
                    DyndbModelComponents.objects.filter(id_molecule=molecule_id,id_model__dyndbsubmissionmodel__submission_id=submission_id).delete()
                    DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None,int_id=None)
    print("\nLLLdeleteComplexByUpdateMolecule ")
                       
def deleteComplexByUpdateMolecule(molecule_id,ii,submission_id,model_del_molec=False):
    print("ideleteComplexByUpdateMolecule ")
    qAllCexp_invg_mol =DyndbComplexExp.objects.filter(dyndbcomplexmolecule__dyndbcomplexmoleculemolecule__id_molecule=molecule_id)
    qOthersCexp_invg_mol = qAllCexp_invg_mol.exclude(dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel__submission_id=submission_id) 
    qCexp_invd_this_sub = qAllCexp_invg_mol.filter(dyndbcomplexmolecule__dyndbmodel__dyndbsubmissionmodel__submission_id=submission_id) 
    if not qOthersCexp_invg_mol.exists():
        if qCexp_invd_this_sub.exists():#only 
           models_invg_this_Complex=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp=qCexp_invd_this_sub) 
           if not models_invg_this_Complex.exists(): #This occurs when the complex only existed in the model in this submission but the dependecy was removed in deleteModelbyUpdateMolecule
               DyndbMoleculeComplexMolecule.objects.filter(id_complex_molecule__id_complex_exp=qCexp_inv_this_sub).delete()
               DyndbComplexMolecule.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
               DyndbComplexCompound.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
               DyndbComplexProtein.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
               DyndbComplexExp.objects.filter(id=qCexp_inv_this_sub).delete()
               if model_del_molec:
                   delMolByUpdateMolecule(molecule_id,ii,submission_id)   
    else:
        if qCexp_invd_this_sub.exists():#only 
            models_invg_this_Complex=DyndbModel.objects.filter(id_complex_molecule__id_complex_exp=qCexp_invd_this_sub) 
            if not models_invg_this_Complex.exists(): #This occurs when the complex only existed in the model in this submission but the dependecy was removed in deleteModelbyUpdateMolecule
                DyndbMoleculeComplexMolecule.objects.filter(id_complex_molecule__id_complex_exp=qCexp_inv_this_sub).delete()
                DyndbComplexMolecule.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                DyndbComplexCompound.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                DyndbComplexProtein.objects.filter(id_complex_exp=qCexp_inv_this_sub).delete()
                DyndbComplexExp.objects.filter(id=qCexp_inv_this_sub).delete()
                #do not delete molecule by updating molecule!!!! it is needed in other complexes
                DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None)
    print("LLLideleteComplexByUpdateMolecule ")

def deleteModelbyUpdateMolecule(molecule_id,ii,submission_id):
    print("deleteModelbyUpdateMolecule ")
    #dynamics components are updated to be reused here!!!
    Dyn_comp_link_mol =DyndbDynamicsComponents.objects.filter(id_molecule=molecule_id)
    Dyn_comp_link_mol_sub= Dyn_comp_link_mol.filter(id_dynamics__submission_id=submission_id)
    if Dyn_comp_link_mol_sub.exists():
        Dyn_comp_link_mol_sub.update(numberofmol=None,resname=F('id'),type=None)

    #The molecule_id will be removed not updated if model complex and requirements!!!!!
    AllMod_invg_molec =DyndbModel.objects.filter(id_complex_molecule__dyndbcomplexmoleculemolecule__id_molecule=molecule_id)
    OtherMod_invg_molec =DyndbModel.objects.filter(id_complex_molecule__dyndbcomplexmoleculemolecule__id_molecule=molecule_id).exclude(dyndbsubmissionmodel__submission_id=submission_id)

    if not OtherMod_invg_molec.exists(): #if no other models exist check if the model in this submission exist. 
        if AllMod_invg_molec.exists():#the Model has to be updated by updating Complex_Protein and Modeled REsidues
            other_sub_using_model=DyndbSubmissionModel.objects.filter(model_id__in=AllMod_invg_molec).exclude(submission_id=submission_id)
            if not other_sub_using_model.exists():#borrar modelo o update modelo          
                #Delete       
                DyndbModelComponents.objects.filter(id_model__in=AllMod_invg_molec,id_molecule=molecule_id).update(numberofmol=None,resname=F('id'),type=None)
                DyndbModel.objects.filter(id__in=AllMod_invg_molec).update(id_complex_molecule=None,id_protein=None,model_creation_submission_id=None)
                #DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id) #Maybe an update can be made!!!!
                deleteComplexByUpdateMolecule(molecule_id,ii,submission_id,model_del_molec=True) #Borrar Complex si es posible
        else:#No model involving the molecule exists yet
            delMolByUpdateMolecule(molecule_id,ii,submission_id)   

    else:
        if AllMod_invg_molec.exists():#the Model has to be updated by updating Complex_Protein and Modeled REsidues
            Mod_invg_molec_and_sub =AllMod_invg_molec.filter(dyndbsubmissionmodel__submission_id=submission_id)   
            other_sub_using_model=DyndbSubmissionModel.objects.filter(model_id__in=Mod_invg_molec_and_sub).exclude(submission_id=submission_id)
            if not other_sub_using_model.exists():#borrar modelo          
                            #removing dependencies between fragments in the protein and remove fragments
                DyndbModelComponents.objects.filter(id_model__in=Mod_invg_molec_and_sub,id_molecule=molecule_id).update(numberofmol=None,resname=F('id'),type=None)
                #DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id) #Maybe an update can be made!!!!
                DyndbModel.objects.filter(id__in=Mod_invg_molec_and_sub).update(id_complex_molecule=None,id_protein=None,model_creation_submission_id=None)
                deleteComplexByUpdateMolecule(molecule_id,ii,submission_id,model_del_molec=False)#Borrar Complex si es posible
            else:
                DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None)
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed                
def PROTEINview(request, submission_id):
    
    p= submission_id
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    
    if request.method == 'POST':
        lrp=[]
        l_checkinpost=[]

        for o in request.POST.keys():
            if o.split("-")[0] == 'form':
                lrp.append(("-").join(o.split("-")[:2]))
        lrp=list(set(lrp))
        for ll in ['name','sequence']:
            for o in lrp:
                l_checkinpost.append(("-").join([o,ll]))
        for l in  l_checkinpost:     
            if request.POST[l] == '':
                error=("").join(["\nPlease, before submission fill every field manually (unlocked fields) or by retrieving data from UniProtKB (locked fields) in the different sections of the Step 1.\n\nPay attention to the SMOL #",str(int(l.split('-')[1])+1)," object"])
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        def_user_dbengine=settings.DATABASES['default']['USER']
        def_user=request.user.id
        print("HOLA  ", def_user)
        initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
        author="jmr"   #to be modified with author information. To initPF dict
        action="/".join(["/dynadb/PROTEINfilled",submission_id," "])
        now=timezone.now()
        print("REQUEST.POST\n",request.POST,"\n")
#####  inintPF dictionary containing fields of the form dynadb_ProteinForm not
#####  available in the request.POST
#####
#####  initOPN dictionary dyndb_Other_Protein_NamesForm. To be updated in the
#####  view. Not depending on is_mutated field in dynadb_ProteinForm 
        initOPN={'id_protein':'1','other_names':'Lulu' } #other_names should be updated from UniProtKB Script Isma

        form=re.compile('form-')
        dictpost=request.POST
        dictprot={}
        dictprotinit={}
        dictOPN={}
        indexl=[]
        nummutl={} # Dictionary of index lists designating the mutation line for every mutated protein
        nummut_indb={}
        for key,val in dictpost.items():
            if form.search(key):   #if the form- prefix is found several proteins are submitted in the HTML
                index=int(key.split("-")[1]) #index stand for the number of protein
                if index not in indexl:
                    indexl.append(index)
                    dictprot[index]={} #a dictprot dictionary is created per each protein in the form
                    dictprotinit[index]={} #a dictprot dictionary is created per each protein in the form
                nkey="-".join(key.split("-")[2:])   # HTML labels (keys in dictpost) modified by JavaScript are reset to match the key in the models 
            else: 
                if len(indexl)==0:
                    index=0
                    indexl.append(0)
                    dictprot[0]={}
                    dictprotinit[0]={} #a dictprot dictionary is created per each protein in the form
                nkey=key # the keys does not have to be modifyied as a single protein has been submitted in the html form and labels match the models 
            dictprot[index][nkey]=val 
            dictprotinit[index][key]=val 
        print("DICTPROT\n",dictprot,"\n")
    #    return HttpResponse("HOLA PIPOL")
####   List of dictionaries used for filling tables
        fdbPF={}
        fdbSP={}
        fdbPS={}
        fdbPM={}
        fdbCaP={}
        fdbPCaP={}
        dictSP={}
        dictPM={}
        listON={}
        fdbOPN={}
        formPF={}
        formSP={}
        formPS={}
        formOPN={}
        formCaP={} 
        initPS={}
        initPM={}
        dictCP={}
        fdbCP={} #dyndb_Complex_Protein
        auxdictprot={}
        fdbPFaux={}
        formPFaux={}   
        dictSPaux={}  
        fdbSPaux={}
        fdbPSaux={}
        fdbCaPaux={}
        fdbPCaPaux={}
        initPSaux={}
        qCanProt={}
        qCaP={}
        
        indexl.sort()
        qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
        qSubreuse=DyndbSubmissionProtein.objects.filter(int_id=None,protein_id=None) #entry list to be reused
        lqSubreuse_used=[] 
        if qSub.exists(): ### MIRAR HTML
            print("QSUB exists")
            qSub_protl=list(qSub.values_list('submission_id','protein_id','int_id','protein_id__dyndbproteinsequence__sequence','protein_id__is_mutated'))
            qSub_p_sid_int_id=[]
            for ll in qSub_protl:
                qSub_p_sid_int_id.append((ll[0],ll[2]))
        for ii in indexl:
            if dictprot[ii]['name'] == '' and dictprot[ii]['sequence'] == '':
                print("Protein #",ii+1," Item is empty!!!")
                if qSub.filter(int_id=ii).exists():
                    for ll in qSub_protl:
                        print("list ",ll)
                        if ll[2]==ii:
                            protein_id=ll[1]
                            if ll[4]:
                                is_mutated_val=True
                            else:
                                is_mutated_val=False
                            deleteModelbyUpdateProtein(protein_id,ii,submission_id,is_mutated_val)#starts the deletions of objects involving the protein to be updated!!!
                            continue_indexl=True
                            break
                    if continue_indexl:
                        continue

            if 'is_mutated' in dictprot[ii].keys():
                is_mutated_val=True
            #### Check if the Protein in the HTML is already in the database 
                browse_protein_response=check_protein_entry_exist(dictprot[ii]['uniprotkbac'],is_mutated_val,dictprot[ii]['msequence'],dictprot[ii]['isoform'])#### POR AQUI!!!!!!!!!!!!!! 
                if "ERROR" in browse_protein_response.keys():
                    response= HttpResponse(browse_protein_response['Message'],status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                if len(browse_protein_response['id_protein'])==0 and not "ERROR" in browse_protein_response.keys():
                    prev_sub_prot_match_formProtidySeqyIntid=False #protein submitted in this submission
                    prev_sub_prot_match_formProtidySeq=False #protein submitted in this submission
                    print("                    prev_sub_prot_match_formprotidyseq=False")
                else:
                    print("Valor funcion ", len(browse_protein_response), browse_protein_response)
                    prev_sub_prot_match_formProtidySeqyIntid=qSub.filter(protein_id=int((browse_protein_response['id_protein'])[0]),int_id=ii,protein_id__dyndbproteinsequence__sequence=dictprot[ii]['msequence']).exists() #protein submitted in this submission
                    prev_sub_prot_match_formProtidySeq=DyndbSubmissionProtein.objects.filter(protein_id=int((browse_protein_response['id_protein'])[0]),protein_id__dyndbproteinsequence__sequence=dictprot[ii]['msequence']).exists() #protein submitted in this submission
            else:
                is_mutated_val=False
                #### Check if the Protein in the HTML is already in the database 
                browse_protein_response=check_protein_entry_exist(dictprot[ii]['uniprotkbac'],is_mutated_val,dictprot[ii]['sequence'],dictprot[ii]['isoform'])#### POR AQUI!!!!!!!!!!!!!! 
                if "ERROR" in browse_protein_response.keys():
                    response= HttpResponse(browse_protein_response['Message'],status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                if len(browse_protein_response['id_protein'])==0 and not "ERROR" in browse_protein_response.keys():
                    prev_sub_prot_match_formProtidySeqyIntid=False #protein submitted in this submission
                    prev_sub_prot_match_formProtidySeq=False #protein submitted in this submission
                    print("                    prev_sub_prot_match_formprotidyseq=False")
                else: 
                    print("Valor funcion ", len(browse_protein_response), browse_protein_response)
                    prev_sub_prot_match_formProtidySeqyIntid=qSub.filter(protein_id=int((browse_protein_response['id_protein'])[0]),int_id=ii,protein_id__dyndbproteinsequence__sequence=dictprot[ii]['sequence']).exists() #protein submitted in this submission
                    prev_sub_prot_match_formProtidySeq=DyndbSubmissionProtein.objects.filter(protein_id=int((browse_protein_response['id_protein'])[0]),protein_id__dyndbproteinsequence__sequence=dictprot[ii]['sequence']).exists() 
                    print ("prev_sub_prot_match_formProtidySeq   ",prev_sub_prot_match_formProtidySeq)
            if len(browse_protein_response['id_protein'])==1:
                print(browse_protein_response['Message'])
                dictSP[ii]={'submission_id':int(submission_id), 'protein_id':int(browse_protein_response['id_protein'][0]), 'int_id':ii} #int_id is 0 for the protein #1, 1 for the protein #2, ...
                fdbSP[ii]=dyndb_Submission_Protein(dictSP[ii])
                if qSub.filter(int_id=ii).exists():
                    if not prev_sub_prot_match_formProtidySeqyIntid: #the protein_id and sequence in the submission table is different than the one in the current form. An update is needed!! first remove saved protein from the table
                        protein_id=qSub.filter(int_id=ii).values_list('protein_id',flat=True)[0]
                        qSub.filter(int_id=ii).update(int_id=1000) 
                        if prev_sub_prot_match_formProtidySeq: #the protein_id and sequence in the submission table is different than the one in the current form. An update is needed!! first remove saved protein from the table
                            print("ACTUALIZACION DE INT ID")
                            DyndbSubmissionProtein.objects.filter(submission_id=submission_id,protein_id=int(dictSP[ii]['protein_id'])).update(int_id=int(ii))
                            Update_canProt_to_formProt=True #info from canonical protein wont be erased if it is eventually used in this submission
                        else:
                            DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=int(ii)).update(protein_id=int(browse_protein_response['id_protein'][0]))
                        
                        Check_protein_id_tbremoved_is_in_othersubmission=DyndbSubmissionProtein.objects.filter(protein_id=protein_id).exclude(int_id=1000)
                        if not Check_protein_id_tbremoved_is_in_othersubmission.exists():
                            
                            deleteModelbyUpdateProtein(protein_id,1000,submission_id,is_mutated_val)#starts the deletions of objects involving the protein to be updated!!!
                        DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=1000).update(protein_id=None,int_id=None)
                        continue
                    else:                    
                        browseres=(int(submission_id),int(browse_protein_response['id_protein'][0]))
                        print("\n ESTA en la DB COMPARA ",browseres,"  ",ii," con ", qSub_protl[0])
                        print("PPPPPPPPPP",browse_protein_response['Message'])
                        continue
                else:
                    if qSubreuse.exists():
                        for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                            qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=int(dictSP[ii]['int_id']),protein_id=int(dictSP[ii]['protein_id'])) 
                            lqSubreuse_used.append(rows.id) 
                            break
                    else:
                        if fdbSP[ii].is_valid():
                            fdbSP[ii].save()
                        else:
                            iii1=fdbSP[ii].errors.as_text()
                            print("fdbSP[",ii,"] no es valido")
                            print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n")
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
                    if ii==indexl[-1]:#if ii is the last element of the list indexl
                        print("\nThis is the last protein in the form",browse_protein_response['Message'])
                        break
                    else:
                        print("\nStill there are more proteins to be submitted",browse_protein_response['Message'])
                        continue
            else:
                if len(browse_protein_response['id_protein'])>1:
                    print(browse_protein_response['Message'])
                    response = HttpResponse(browse_protein_response['Message'],status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
#### If the protein ii is not found in our database create a new entry
            if qSub.exists():
                if qSub.filter(int_id=ii).exclude(protein_id=None).exists(): #there is a protein_id in the submission table but the protein in the form is not in the database so the stored one is different than the one in the current form. An update is needed!! first remove saved protein from the table
                    print("\n\nThe protein in the form is not in the database but a protein with this submission_id exists in the database. This one must be removed if possible\n")
                    protein_id=qSub.filter(int_id=ii).values_list('protein_id',flat=True)[0]
                    deleteModelbyUpdateProtein(protein_id,ii,submission_id,is_mutated_val)#starts the deletions of objects involving the protein to be updated!!!
            print("valor ii=", ii, "dictprot[ii]=\n", dictprot[ii])
            dictprot[ii]['protein_creation_submission_id']=int(submission_id)
            print("\nAAAA",dictprot[ii]['protein_creation_submission_id'])
            dictprot[ii]['id_species']=1
            initPF['id_uniprot_species']=dictprot[ii]['id_species']
            p=Protein.objects.filter(accession=dictprot[ii]['uniprotkbac'])
            if len(p.values())==1:
                initPF['receptor_id_protein']=p.values_list('id')[0][0]
                print(initPF)
            elif len(p.values())==0:
                initPF['receptor_id_protein']=None
            fdbPF[ii]=dyndb_ProteinForm(dictprot[ii])
            
#####  Fill the empty fields in the fdbPF instance with data from the initPF dictionary
            for key,value in initPF.items():
                fdbPF[ii].data[key]=value
            print("\nDICT dbPF[ii].data", fdbPF[ii].data  )
##### Check whether the fdbPF instance of dyndb_ProteinForm is valid and save formPF entry in the database:
            if fdbPF[ii].is_valid(): 
                formPF[ii]=fdbPF[ii].save()
                print("\n primary  key: ", formPF[ii].pk )
            else:
                iii1=fdbPF[ii].errors.as_text()
                print("fdbPF",ii," no es valido")
                print("!!!!!!Errores despues del fdbPF[",ii,"]\n",iii1,"\n")
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
##### Fill the submission protein table  (Submission PROTEIN dictionary dictSP) 
            New_Sub_Object=False
            if qSub.exists() :
                try:
                    print (qSub_p_sid_int_id)
                except NameError:
                    print ("qSub_p_sid_int_id Not defined")
                    qSub_p_sid_int_id=[]
                if (int(submission_id),int(ii)) in qSub_p_sid_int_id:
                    DyndbSubmissionProtein.objects.filter(submission_id=submission_id,int_id=int(ii)).update(protein_id=int(formPF[ii].pk))
                else:
                    New_Sub_Object=True
            if not qSub.exists() or New_Sub_Object:  
                dictSP[ii]={'submission_id':int(submission_id), 'protein_id':formPF[ii].pk, 'int_id':ii} #int_id is 0 for the protein #1, 1 for the protein #2, ...
                print("dictSP[ii]=\n",dictSP[ii])
                fdbSP[ii]=dyndb_Submission_Protein(dictSP[ii])
                if qSubreuse.exists():
                    for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                        qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=int(dictSP[ii]['int_id']),protein_id=int(dictSP[ii]['protein_id'])) 
                        break
                else:
                    if fdbSP[ii].is_valid():
                        fdbSP[ii].save()
                    else:
                        iii1=fdbSP[ii].errors.as_text()
                        print("fdbSP[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n")
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        return response
#####  Fill dyndb_Protein_SequenceForm fields depending on whether the protein is mutated   
#####  'msequence' does not appear in models but it does in the html so the information in 
#####  this html field should be tranfered into the 'sequence' field in the form instance      
            if 'sequence' not in dictprot[ii].keys():
                dictprot[ii]['sequence']="TOTO"
                if seq is None:
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response
            if 'is_mutated' in fdbPF[ii].data: 
                dictPM[ii]={}
                nummutl[ii]=[]
                fdbPM[ii]={}
                ##### Let's search for form fields ending in a number which stand for fields belonging to the dyndbProteinMutations models
                ##### the fields corresponding to a mutation [nummunt] in a protein [ii] will be stored in the dictionary dictPM[ii][nummut]
                for k,v in dictprot[ii].items():
                    try:
                        nummut=int(k.split("-")[-1])
                        key=("").join(k.split("-")[:-1])
                        print("lll",k,key)
                    except:
                        continue
                    if nummut not in nummutl[ii]:
                        nummutl[ii].append(nummut)
                        dictPM[ii][nummut]={}
                    dictPM[ii][nummut][key]=v
                if len(nummutl[ii])==0:
                    response = HttpResponse('Protein mutations have not been obtained. Please follow these steps: 1) After having obtained the retrieved data about the current protein from the UniprotKB DB ("Wild-type" sequence can be manually entered if no data about the protein exist in UniprotKB) and having provided the "Mutant sequence" in the corresponding field in the form, remember to align the "Mutant sequence" to the Wild type one by clicking the "Align to the wild type" button. Then, click the "Get mutations" button and the check if the mutations in the "Protein Mutations" table are correct. If no results are obtained, please make the database administrator know.' ,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
##### Let's create the field 'id_protein' in dyndb_Protein_MutationsForm so that an entry could be registered in the version not supporting Mutations scripts
                mseq=dictprot[ii]['msequence']
                seq=dictprot[ii]['sequence']
                lmseq=len(mseq)
                initPS[ii]={'id_protein':formPF[ii].pk,'sequence':mseq,'length':lmseq} 
                if mseq == seq:
                    response = HttpResponse('Provided mutated sequence matches the wild type one!!! Please include mutations in the "Mutant sequence" field' ,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response
                if mseq is None:
                    response = HttpResponse('Mutated sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response
                if seq is None:
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response
                #####  For each nummut (i.e. number of mutation in an specific protein ii) a dyndb_Protein_MutationsForm instace should be created to save data in the database.
                qlmut=DyndbProteinMutations.objects.filter(id_protein__dyndbsubmissionprotein__submission_id=submission_id,id_protein__dyndbsubmissionprotein__int_id=ii) 
                qlmut_list=list(qlmut.values_list('resid','resletter_from','resletter_to','id_protein','id'))
                mut_used=()
                nummut_indb[ii]=[]
                for nm in nummutl[ii]:
                    dictPM[ii][nm]['id_protein']=formPF[ii].pk
                    if len(dictPM[ii][nm]) == 1:    # solo hay la id_protein en dictPM[ii][nm]
                        print ("len(dictPM[ii][nm]) ", len(dictPM[ii][nm])) 
                    else:
                        el=(int(dictPM[ii][nm]['resid']),dictPM[ii][nm]['resletter_from'],dictPM[ii][nm]['resletter_to'])
                        if len(qlmut_list)>0:
                            for x in qlmut_list:
                                if x[:3] == el:  #rows in the form are exactly matching values in db so both elements are not used in further updates
                                    mut_used.append(x)
                                    nummut_indb[ii].append(nm)
                                    break
                qlmut_to_update=list(set(qlmut_list)-set(mut_used))
                for nm in nummutl[ii]:
                    if len(mut_used) == len(qlmut_list):#no more available rows to update in the database
                        break
                    if nm not in nummut_indb[ii]:
                        for el_to_up in qlmut_to_update:
                            if el_to_up not in mut_used:
                                el=(int(dictPM[ii][nm]['resid']),dictPM[ii][nm]['resletter_from'],dictPM[ii][nm]['resletter_to'],int(dictPM[ii][nm]['id_protein']))
                                DyndbProteinMutations.objects.filter(id=el_to_up[4]).update(resid=el[0],resletter_from=el[1],resletter_to=el[2],protein_id=el[3])  
                                nummut_indb.append(nm)
                                mut_used.append(el_to_up)
                                break
                if len(nummutl[ii])<len(qlmut_list):
                     del_l=[]
                     for el_to_up in qlmut_to_update:
                         if el_to_up not in mut_used:
                             del_l.append(el_to_up[4])
                     DyndbProteinMutations.objects.filter(id__in=del_l).delete()
                else:  
                    for nm in nummutl[ii]:
                        if nm not in nummut_indb[ii]:
                            fdbPM[ii][nm] = dyndb_Protein_MutationsForm(dictPM[ii][nm])
                 
                            if fdbPM[ii][nm].is_valid():
                                fdbPM[ii][nm].save()
                            else:
                                iii1=fdbPM[ii][nm].errors.as_text()
                                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                                DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                                DyndbProteinMutations.objects.filter(id_protein=formPF[ii].pk).delete()#Some other names may have been recorded before the wrong dyndb_Protein_MutationsForm
                                DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                                return response
            else: #PROTEIN is not mutated!!!!!!!!!
                seq=dictprot[ii]['sequence']
                lseq=len(seq)
                initPS[ii]={'id_protein':formPF[ii].pk,'sequence':seq,'length':lseq} 
                if seq is None:
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response
#########   Intance of the forms depending on the is_mutated value in dyndb_ProteinForm
            fdbPS[ii] = dyndb_Protein_SequenceForm(initPS[ii])
            if fdbPS[ii].is_valid():
                fdbPS[ii].save()
            else:
                iii1=fdbPS[ii].errors.as_text()
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                if is_mutated_val:
                    DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()
                return response
            #### Check if canonical Protein has been already submitted to the database. 
            #### First we browse the non mutated proteins matching UniProtKbac. We have to decide if we want CANONICAL or WILDTYPE (WILDTYPE involves one entry per isoform in DyndbCannonicalProteins and add a constrain in the query:filter(isoform=isoform).
#            qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=dictprot[ii]['uniprotkbac']).filter(isoform=isoform).exclude(is_mutated=True)#NO BUSCA CANONICAL SINO EL ISOMORF ESPECIFICADO!!
            qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=dictprot[ii]['uniprotkbac']).exclude(is_mutated=True).exclude(id=formPF[ii].pk) # BUSCA CANONICAL PROTEIN !!!
#            qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=formPF[ii].uniprotkbac).exclude(id=formPF[ii].pk).exclude(is_mutated=True)
            lqid=[] #list of id in the query (not mutated proteins with the same UniProtKB AC than the new one without including it)
            for el in qCanProt[ii].values():
                lqid.append(el['id'])
            qCaP[ii]=DyndbCannonicalProteins.objects.filter(pk__in=lqid)
            if len(qCaP[ii].values())==0: #no Cannonical Protein exists for this UniProtKBAC in our database
                auxdictprot[ii]={}
                dunikb=PROTEINv_get_data_upkb(request, uniprotkbac=dictprot[ii]['uniprotkbac']) #Request the data of the canonical protein in the UniProtKB DB
                if isinstance(dunikb,HttpResponse):
                    return dunikb 
                if "Aliases" in  dunikb.keys():
                    translate={'Entry':'uniprotkbac','Isoform':'isoform','Name':'name','Aliases':'other_names','Sequence':'sequence','Organism':'id_species_autocomplete','speciesid':'id_species'} #dictionary for the translation between the data in uniprot and the data in our tables
                else:
                    translate={'Entry':'uniprotkbac','Isoform':'isoform','Name':'name','Sequence':'sequence','Organism':'id_species_autocomplete','speciesid':'id_species'} #dictionary for the translation between the data in uniprot and the data in our tables
                for key,val in translate.items():
                    auxdictprot[ii][val]=dunikb[key]
  #####         We have to check if the current Protein entry matches the cannonical sequence. If not a new entry for the canonical sequence must be tracked. 
                if auxdictprot[ii]['sequence']!=initPS[ii]['sequence']:
                      # auxdictprot[ii]['sequence'] stands for the canonical sequence from UniProtKB DB
                      # initPS[ii]['sequence'] stands for the sequence of the protein to be tracked (either wild type or mutant depending on the field is_mutated)
                   #Let's create entries in DyndbProtein, DyndbProteinSequence, DyndbSubmissionProtein, 
                    auxdictprot[ii]['is_mutated']=False
                    initPF['id_uniprot_species']=auxdictprot[ii]['id_species']
                    for key,value in initPF.items():
                        auxdictprot[ii][key]=value
                    fdbPFaux[ii]=dyndb_ProteinForm(auxdictprot[ii])
                    DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=auxdictprot[ii]['id_species'])
                    if fdbPFaux[ii].is_valid(): 
                        formPFaux[ii]=fdbPFaux[ii].save()
                    else:
                        iii1=fdbPFaux[ii].errors.as_text()
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                        if is_mutated_val:
                            DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()
                        return response
                    dictSPaux[ii]={'int_id':None, 'submission_id':int(submission_id), 'protein_id':formPFaux[ii].pk}
                                  #int_id is Null because the entry has been generated automatically to find a cannonical sequence corresponding 
                                  #to the user uploaded mutant protein,                                                             
                    fdbSPaux[ii]=dyndb_Submission_Protein(dictSPaux[ii])
                    if qSubreuse.exists():
                        for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                            qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=None,protein_id=int(dictSPaux[ii]['protein_id'])) 
                            break
                    else:
                        if fdbSPaux[ii].is_valid():
                            fdbSPaux[ii].save()
                        else:
                            iii1=fdbSPaux[ii].errors.as_text()
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                            DyndbProtein.objects.filter(id=formPFaux[ii].pk).delete()
                            DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                            DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                            if is_mutated_val:
                                DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()
                            return response
##### Createe a  a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
#####           
                    if 'other_names' in auxdictprot[ii].keys():
                        listON[ii]=auxdictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
                        listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
                        dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
                        fdbOPN[ii]={}
                        numON=0
                        for on in listON[ii]:
                            numON=numON+1
                            dictOPN[ii][numON]={}
                            fdbOPN[ii][numON]={}
                            dictOPN[ii][numON]['other_names']=on
                            dictOPN[ii][numON]['id_protein']=formPFaux[ii].pk
                            fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
                            if fdbOPN[ii][numON].is_valid():
                                fdbOPN[ii][numON].save()
                            else:
                                iii1=fdbOPN[ii][numON].errors.as_text()
                                print("fdbOPN[",ii,"] no es valido")
                                print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
                                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                                DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                                DyndbOtherProteinNames.objects.filter(id_protein=formPFaux[ii].pk).delete()#Some other names may have been recorded before the wrong d_Other_Protein_NamesForm
                                DyndbProtein.objects.filter(id=formPFaux[ii].pk).delete()
                                DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                                DyndbSubmissionProtein.objects.filter(protein_id=formPFaux[ii].pk).delete()
                                DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                                if is_mutated_val:
                                    DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()
                                return response
                    else:
                        print("NO OTHER NAMES have been found\n")
                    seq=auxdictprot[ii]['sequence']
                    lseq=len(seq)
                    initPSaux[ii]={'id_protein':formPFaux[ii].pk,'sequence':auxdictprot[ii]['sequence'],'length':lseq}
                    fdbPSaux[ii] = dyndb_Protein_SequenceForm(initPSaux[ii])
                    if fdbPSaux[ii].is_valid():
                        fdbPSaux[ii].save()
                        print ("hasta aqui")
                    else:
                        iii1=fdbPSaux[ii].errors.as_text()
                        print("fdbPSaux[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbPSaux[",ii,"] \n",iii1,"\n")
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        DyndbProtein.objects.filter(id=formPFaux[ii].pk).delete()
                        DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPFaux[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                        if is_mutated_val:
                            DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                        return response                                                                                
                        #Filling the dyndb_Cannonical_Protein entry for the cannonical protein corresponding to the mutant in the form!!!! 
                    fdbCaPaux[ii]=dyndb_Cannonical_ProteinsForm({'id_protein':formPFaux[ii].pk})
                    if fdbCaPaux[ii].is_valid():
                        fdbCaPaux[ii].save()
                    else:
                        iii1=fdbCaPaux[ii].errors.as_text()
                        print("fdbCaPaux[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbCaPaux[",ii,"]\n",iii1,"\n") 
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        DyndbProtein.objects.filter(id=formPFaux[ii].pk).delete()
                        DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPFaux[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPFaux[ii].pk).delete()
                        if is_mutated_val:
                            DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                        return response                                                                                
                    ### NOTe this fdbPCaPaux corresponds to the Cannonical protein created automatically in the view!!!
                    fdbPCaPaux[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':formPFaux[ii].pk,'id_protein':formPFaux[ii].pk})
                        #id_protein is the fk pointing to dyndb_Protein. formPFaux[ii].pk is the dyndb_Protein.pk in the Created cannonical entry!!!   
                        #id_cannonical_protein is the fk to dyndb_Cannonical_Protein. formPFaux[ii].pk is also the dyndb_Cannonical_Protein.pk    
                    if fdbPCaPaux[ii].is_valid(): 
                        fdbPCaPaux[ii].save()
                    else:
                        iii1=fdbPCaPaux[ii].errors.as_text()
                        print("fdbPCaPaux[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbPCaPaux[",ii,"]\n",iii1,"\n") 
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        DyndbProtein.objects.filter(id=formPFaux[ii].pk).delete()
                        DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPFaux[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPFaux[ii].pk).delete()
                        DyndbCannonicalProteins.filter(id_protein=formPFaux[ii].pk).delete()
                        if is_mutated_val:
                            DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                        return response                                                                                
                    vformPFPCaP=formPFaux[ii].pk## For completing the dyndbProteinCanonicalProtein table!!!! If the Canonical sequence has been retrieved from Uniprot and not from the HTML form definition 
                else: ###### If the protein in the form is the canonical protein as its sequence matches the one from the UniProtKB DB
                #Filling the dyndb_Cannonical_Protein in the case of having a cannonical protein in the form!!!! 
                    vformPFPCaP=formPF[ii].pk##  For completing the dyndbProteinCanonicalProtein table!!!! If sequence in the form is the Canonical Sequence!!!! Otherwise the value is taken from the UniProtKB entry
                    DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=auxdictprot[ii]['id_species'])
                    print("HHHHHHHHHHHH",auxdictprot[ii]['id_species'])
                    fdbCaP[ii]=dyndb_Cannonical_ProteinsForm({'id_protein':formPF[ii].pk})
                    if fdbCaP[ii].is_valid():
                        fdbCaP[ii].save()
                    else:
                        iii1=fdbCaP[ii].errors.as_text()
                        print("fdbCaPaux[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbCaPaux[",ii,"]\n",iii1,"\n") 
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                        DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete()
                        DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                        DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                        if is_mutated_val:
                            DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                        return response                                                                                
#####           #if the protein in the form is the canonical protein as its sequence matches the one from the UniProtKB DB It is needed to keep track of the
                # other names in the form. REMEMBER OTHER NAMES are only filled for the Canonical Protein!!!!
##### Create a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
                    if len(dictprot[ii]['other_names'])> 0:
                        listON[ii]=dictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
                        listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
                        dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
                        fdbOPN[ii]={}
                        numON=0
                        for on in listON[ii]:
                            numON=numON+1
                            dictOPN[ii][numON]={}
                            fdbOPN[ii][numON]={}
                            dictOPN[ii][numON]['other_names']=on
                            dictOPN[ii][numON]['id_protein']=formPF[ii].pk
                            fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
                            if fdbOPN[ii][numON].is_valid():
                                fdbOPN[ii][numON].save()
                            else:
                                iii1=fdbOPN[ii][numON].errors.as_text()
                                print("fdbOPN[",ii,"] no es valido")
                                print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
                                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                                DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                                DyndbCannonicalProteins.objects.filter(id_protein=formPF[ii].pk).delete()
                                DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete() #Some other names may have been recorded before the wrong dyndb_Other_Protein_NamesForm
                                DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                                DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                                if is_mutated_val:
                                    DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                                return response
                    else:
                        print("NO OTHER NAMES have been found\n")
          ### NOTe this fdbPCaP corresponds to the protein created from the POST info!!!
                fdbPCaP[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':vformPFPCaP,'id_protein':formPF[ii].pk})
                    #id_protein is the fk pointing to dyndb_Protein. formPF[ii].pk is the dyndb_Protein.pk in the mutant protein Entry!!!!   
                    #id_cannonical_protein is the fk to dyndb_Cannonical_Protein. formPFaux[ii].pk is the dyndb_Cannonical_Protein.pk!!!!    
                if fdbPCaP[ii].is_valid(): 
                    fdbPCaP[ii].save()
                else:
                    iii1=fdbPCaP[ii].errors.as_text()
                    print("fdbPCaP[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbPCaP[",ii,"]\n",iii1,"\n") 
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbOtherProteinNames.objects.filter(id_protein=formPF[ii].pk).delete()
                    DyndbCannonicalProteins.objects.filter(id_protein=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                    if is_mutated_val:
                        DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                    return response
            else: # One or More Canonical Protein entries have been retrieved from the query qCanProt. (Just one entry should be retrived!!!!)
                if len(qCaP[ii].values()) > 1:
                    print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                    print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                    print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                    print("Several Canonical Protein entries with UNIPROTKBAC=",qCanProt[ii].filter(pk__in=qCaP[ii].values()),"exist in the DB")
                    iii1=(" ").join[("Several Canonical Protein entries with UniprotKB AC=",str(qCanProt[ii].filter(pk__in=qCaP[ii].values())),"exist in the DB. Please, make the DB administrator know")]
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
           # the dyndb_Cannonical_Protein already exists so it is not created again!!!!! let's create dyndb_Protein_Cannonical_Protein entry
           # from info contained in the query qCanProt (qCanProt.values()[0]['id']) this is the id of the first and only element in the query
                if len(qCaP[ii].values()) == 1:
                    id_species=DyndbProtein.objects.filter(id__in=lqid).values_list('id_uniprot_species',flat=True)[0]
                    DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=id_species)
                    fdbPCaP[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':qCaP[ii].values()[0]['id_protein_id'],'id_protein':formPF[ii].pk})
                if fdbPCaP[ii].is_valid():
                    fdbPCaP[ii].save()
                else:
                    iii1=fdbPCaP[ii].errors.as_text()
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    print("fdbPCaP[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbCaP[",ii,"]\n",iii1,"\n") 
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    DyndbProteinSequence.objects.filter(id_protein=formPF[ii].pk).delete()
                    if is_mutated_val:
                        DyndbProteinMutations.object.filter(id_protein=formPF[ii].pk).delete()                     
                    return response
            # redirect to a new URL:
        response = HttpResponse("Step 1 \"Protein Information\" form has been successfully submitted.",content_type='text/plain; charset=UTF-8')
        return response
    # if a GET (or any other method) we'll create a blank form
    else:
        qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id')
        print(len(qSub),"len")
        print("SEGUROi")
        if len(qSub)==0:
            int_id=[1]
            int_id0=[0]
            alias=[]
            mseq=[]
            wseq=[]
            MUTations=[]
            sci_na_codel=[]
            qPROT=[1]
            sci_namel=[]
            sci_namel.append('')
            fdbPF = dyndb_ProteinForm()
            fdbPS = dyndb_Protein_SequenceForm()
            fdbPM = dyndb_Protein_MutationsForm()
            fdbOPN= dyndb_Other_Protein_NamesForm()
            return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id,'saved':False, 'colorlist':color_label_forms})
        else:
            print(len(qSub),"len")
            print("SEGUROi")
            saved=True
            int_id=[]
            int_id0=[]
            alias=[]
            mseq=[]
            wseq=[]
            MUTations=[]
            sci_na_codel=[]
            qPROT=[]
            for l in qSub:
                sci_name=list(DyndbUniprotSpecies.objects.filter(id= l.protein_id.id_uniprot_species_id).values_list('scientific_name','code')[0])
                if sci_name[0] is None:
                    sci_name[0]=""
                if sci_name[1] is None:
                    sci_name[1]=""
                sci_na_code=("").join([sci_name[0]," (",sci_name[1],")"])
                print(sci_na_code,"sci_na_code")
                sci_na_codel.append(sci_na_code)
                qprot=DyndbProtein.objects.filter(id=l.protein_id_id)[0]
                qPROT.append(qprot)
                int_id.append(l.int_id +1) 
                int_id0.append(l.int_id) 
###              MUT=qPROT.values('id','is_mutated')
                qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
                if l.protein_id.is_mutated: 
                    print("SEGURO ES MUTADA")
###                  MUT.values('is_mutated').filter(id=tt)[0]['is_mutated']:
                    llsm=qSEQ
                    mseq.append(llsm)
                    qpCp=DyndbProteinCannonicalProtein.objects.filter(id_protein=l.protein_id).values_list('id_cannonical_proteins',flat=True)[0]
                    llsw=DyndbProteinSequence.objects.filter(id_protein=qpCp).values_list('sequence',flat=True)[0]
                    qPMut=DyndbProteinMutations.objects.filter(id_protein=l.protein_id).order_by('resid')
                    MUTations.append(qPMut)
                    print(MUTations)
                else:
                    llsw=qSEQ
                    mseq.append('')
                    MUTations.append('')
                wseq.append(llsw) 
                qALIAS=DyndbOtherProteinNames.objects.filter(id_protein=l.protein_id)
                llo=("; ").join(qALIAS.values_list('other_names',flat=True))
                alias.append(llo) 
                print(alias)
                print("mutant",mseq)
                print(wseq)
                print("mutations",MUTations)
  

        return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id, 'saved':saved, 'colorlist':color_label_forms})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
@textonly_500_handler
def delete_protein(request,submission_id):
    if request.method == "POST":
        protein_num = request.POST["protein_num"]
        response = HttpResponse('Success.',content_type='text/plain; charset=UTF-8')
    else:
        response = HttpResponseForbidden()
    return response
    
@textonly_500_handler
def autocomplete(request):
    '''Uses haystack functionality to return on the fly suggestions to the user input according to the names it has indexed.'''
    other_names= SearchQuerySet().autocomplete(other_names=request.GET.get('q', ''))[:5]
    main_names= SearchQuerySet().autocomplete(mainnames=request.GET.get('q', ''))[:5]
    suggestions = [result.other_names for result in other_names]
    suggestions2= [result.name for result in main_names]
    suggestions+=suggestions2
    suggestions = list(set(suggestions))
    data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(data, content_type='application/json')

def count_dynamics(result_id,result_type):
    '''Counts how many times a given result_id appears in a simulation and saves its id. Returns the names list and the number of times it appeas. Loads the whole database in memory, probably not a good idea.'''
    dynset=set()
    if result_type=='compound': #we need to count complexcompound too!!!!
        for molecule in DyndbMolecule.objects.filter(id_compound=result_id):
            somenumber,dynsets=count_dynamics(molecule.id,'molecule')
            dynset=dynset.union(dynsets)
    simus = DyndbDynamics.objects.select_related('id_model__id_complex_molecule__id_complex_exp')
    if settings.QUERY_CHECK_PUBLISHED:
        simus = simus.filter(is_published=True)
    for simu in simus:
        if result_type=='protein':
            modelobj=DyndbModel.objects.select_related('id_protein').get(pk=simu.id_model.id).id_protein
            if modelobj is not None:
                if modelobj.id==result_id:
                    dynset.add(simu.id)
                    continue
            else:
                # workarround for id_complex_molecule
                id_complex_molecule = simu.id_model.id_complex_molecule
                if id_complex_molecule is None:
                    print('Simulation with broken model. DYN=%d MODEL=%d.' % (simu.id,simu.id_model.id))
                    continue
                for prot in DyndbComplexProtein.objects.select_related('id_protein').filter(id_complex_exp=simu.id_model.id_complex_molecule.id_complex_exp.id):
                    if prot.id_protein.id==result_id:
                        dynset.add(simu.id)
        elif result_type=='molecule':
            molflag=0
            for comp in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=simu.id):
                if comp.id_molecule.id==result_id:
                    molflag=1
                    dynset.add(simu.id)
                    break
            if molflag==0: #molecule was not found in dynamics components, maybe it is in model components
                for comp in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=simu.id_model.id):
                    if comp.id_molecule.id==result_id:
                        molflag=1
                        dynset.add(simu.id)
                        break
            if molflag==0: #molecule not found in dynamics nor model components, maybe it is in the complex molecule
                try:
                    for mol in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=simu.id_model.id_complex_molecule.id):
                        if mol.id_molecule.id==result_id:
                            dynset.add(simu.id)
                            break
                except AttributeError:
                    pass #the dynamics has an apoform model
        elif result_type=='compound':
            try:
                cexp_id=simu.id_model.id_complex_molecule.id_complex_exp
                for ccomp in DyndbComplexCompound.objects.filter(id_complex_exp=cexp_id):
                    if ccomp.id_compound.id==result_id:
                        dynset.add(simu.id)
            except:
                continue           
    return len(dynset),dynset

def get_imagepath(id, type):
    '''Returns the path to the image of the molecule or compound with the given id. If type is molecule, it returns the image of the molecule, if it is a compound, it returns the image of the standard molecule for that compound.'''
    if type=='compound':
        try:
            pk2filesmolecule=DyndbCompound.objects.select_related('std_id_molecule').get(pk=id).std_id_molecule.id
            imagepath=DyndbFilesMolecule.objects.select_related('id_files').filter(id_molecule=pk2filesmolecule).filter(type=2)[0].id_files.filepath
            if settings.MEDIA_ROOT[:-1] in imagepath:
                imagepath=imagepath.replace(settings.MEDIA_ROOT[:-1],"") #No absolute path
        except:
            imagepath=''
    else:
        try:
            imagepath=DyndbFilesMolecule.objects.select_related('id_files').filter(id_molecule=id).filter(type=2)[0].id_files.filepath
            if settings.MEDIA_ROOT[:-1] in imagepath:
                imagepath=imagepath.replace(settings.MEDIA_ROOT[:-1],"") #No absolute path
        except:
            imagepath=''
    return imagepath

@textonly_500_handler
def ajaxsearcher(request):
    '''Searches user input among indexed data. If "search by id" option is allowed, a simple database query is used using that ID.'''
    if request.method == 'POST':
        comoldic=dict()
        moleculelist=list()
        proteinlist=list()
        gpcrlist=list()
        compoundlist=list()
        reslist=list()
        names=list()
        return_type=request.POST["return_type"]
        sqs=SearchQuerySet().all() #get all indexed data.
        user_input = request.POST.get('cmolecule')
        if len(user_input)==0: #prevent the user from doing an empty search that returns the whole database.
            tojson={'compound':[], 'protein':[],'gpcr':[],'molecule':[],'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        if request.POST.get("id_search",False)=='true': #uses user_input as an ID to search the database. get("id_search",False) the false is used as a default value in case it cant get any other
            if return_type=='gpcr' or return_type=='All':
                try:
                    protein=DyndbProtein.objects.filter(is_published=True).get(pk=user_input)
                    isrec=protein.receptor_id_protein
                    spname=protein.id_uniprot_species.scientific_name
                    mut=str(protein.is_mutated).replace('True',', mutant')
                    mut=mut.replace('False',', wild type')
                    if isrec is not None:
                        gpcrlist.append([str(protein.id),str(protein.name).capitalize(),mut,spname])
                except:
                    gpcrlist=[]
            if return_type=='protein' or return_type=='All':
                try:
                    protein=DyndbProtein.objects.filter(is_published=True).get(pk=user_input)
                    isrec=protein.receptor_id_protein
                    spname=protein.id_uniprot_species.scientific_name
                    mut=str(protein.is_mutated).replace('True',', mutant')
                    mut=mut.replace('False',', wild type')
                    if isrec is None:
                        proteinlist.append([str(protein.id),str(protein.name).capitalize(),mut,spname])
                except:
                    proteinlist=[]
            if return_type=='molecule' or return_type=='All':
                try:
                    molecule=DyndbMolecule.objects.select_related('id_compound').filter(is_published=True).get(pk=user_input)
                    netcharge=molecule.net_charge
                    if netcharge>0:
                        netcharge='+'+str(netcharge)
                    comp=molecule.id_compound.id
                    compname=molecule.id_compound.name
                    imagepath=get_imagepath(user_input, 'molecule')
                    moleculelist.append([str(molecule.id),str(molecule.inchikey),imagepath,compname.capitalize(),netcharge])
                except:
                    moleculelist=[]
            if return_type=='compound' or return_type=='All': #call the corresponding view??????
                try:
                    compound=DyndbCompound.objects.select_related('std_id_molecule').filter(is_published=True).get(pk=user_input)
                    imagepath=get_imagepath(user_input, 'compound')
                    try:
                        netcharge=compound.std_id_molecule.net_charge
                        if netcharge>0:
                            netcharge='+'+str(netcharge)
                    except:
                        netcharge='?'
                    compoundlist.append([ str(compound.id),str(compound.name).capitalize(),compound.pubchem_cid,imagepath,netcharge ])
                except:
                    compoundlist=[]
            if return_type=='complex' or return_type=='All':
                liglist=[]
                receptorlist=[]
                if len(DyndbComplexExp.objects.filter(id=user_input,is_published=True))>0:
                    for match in DyndbComplexCompound.objects.select_related('id_compound').filter(id_complex_exp=user_input):
                        if match.type==0 or match.type==1:
                            liglist.append(match.id_compound.name)

                    for rmatch in DyndbComplexProtein.objects.select_related('id_protein__receptor_id_protein').filter(id_complex_exp=user_input):
                        isrec=rmatch.id_protein.receptor_id_protein
                        if isrec is not None:
                            receptorlist.append(isrec.name)
                    if len(receptorlist)!=0:
                        names.append([[user_input, receptorlist, liglist],'complex'])
            if return_type=='model' or return_type=='All':
                if len(DyndbModel.objects.filter(id=user_input,is_published=True))>0:
                    try:
                        modelname=getligrec([user_input],'model')
                        names.append(modelname+['model'])
                    except:
                        pass
            if return_type=='dynamics' or return_type=='All':
                if len(DyndbDynamics.objects.filter(id=user_input,is_published=True))>0:
                    try:
                        dyname=getligrec([user_input],'dynamics')
                        names.append(dyname+['dynamics'])
                    except:
                        pass
        else: #standard search with plain text
            if len(user_input)>2:
                results=sqs.auto_query(user_input) #haystack function to search among indexed data
                for res in results:
                    published=len(DyndbCompound.objects.filter(id=res.id_compound,is_published=True))>0
                    if ('compound' in str(res.id)) and (str(res.id_compound) not in [i[0] for i in compoundlist]) and published:
                        for mol in DyndbMolecule.objects.select_related('id_compound').filter(id_compound=res.id_compound, is_published=True):
                            print(res.id_compound,mol,mol.id,'there you have it')
                            if str(mol.id) not in [i[0] for i in moleculelist]: #molecule
                                mol_id=mol.id
                                netcharge=mol.net_charge
                                if netcharge>0:
                                    netcharge='+'+str(netcharge)
                                comp=res.id_compound 
                                compname=mol.id_compound.name.capitalize()
                                imagepath=get_imagepath(mol.id, 'molecule')
                                moleculelist.append([str(mol_id),str(res.inchikey),imagepath,compname,netcharge]) 
                                try:
                                    comoldic[str(res.id_compound)].add(str(mol_id))
                                except:
                                    comoldic[str(res.id_compound)]={str(mol_id)}
                            imagepath=get_imagepath(res.id_compound, 'compound')
                        try:
                            compound=DyndbCompound.objects.get(id=res.id_compound)
                            netcharge=compound.std_id_molecule.net_charge
                            pubchem=compound.pubchem_cid   
                            if netcharge>0:
                                netcharge='+'+str(netcharge)
                        except:
                            netcharge='?'
                            pubchem='?'
                        compoundlist.append([ str(res.id_compound),str(res.name).capitalize(),pubchem,imagepath,netcharge ])
                    elif 'protein' in str(res.id):
                        published=len(DyndbProtein.objects.filter(id=res.id_protein,is_published=True))>0
                        if (str(res.id_protein) not in [i[0] for i in gpcrlist]) and (str(res.id_protein) not in [i[0] for i in proteinlist]) and published:
                            protein=DyndbProtein.objects.get(pk=res.id_protein)
                            isrec=protein.receptor_id_protein
                            spname=protein.id_uniprot_species.scientific_name
                            mut=str(protein.is_mutated).replace('True',', mutant').replace('False',', wild type')
                            if isrec is None:
                                proteinlist.append([str(protein.id),str(protein.name).capitalize(),mut,spname])
                            else:
                                gpcrlist.append([str(protein.id),str(protein.name).capitalize(),mut,spname])
                            #include all mutants of the found protein:    
                            for mutants in DyndbProtein.objects.filter(uniprotkbac=protein.uniprotkbac):
                                isrecm=mutants.receptor_id_protein
                                spname=mutants.id_uniprot_species.scientific_name
                                mut=str(mutants.is_mutated).replace('True',', mutant').replace('False',', wild type')
                                if isrecm is None and (str(mutants.id) not in [i[0] for i in proteinlist]):
                                    proteinlist.append([str(mutants.id),str(mutants.name),mut,spname])
                                if isrecm is not None and (str(mutants.id) not in [i[0] for i in gpcrlist]):
                                    gpcrlist.append([str(mutants.id),str(mutants.name),mut,spname])
                    elif 'molecule' in str(res.id):
                        mol_id=res.id.split('.')[2]
                        published=len(DyndbMolecule.objects.filter(id=mol_id,is_published=True))>0
                        if str(mol_id) not in [i[0] for i in moleculelist] and published: #molecule
                            molobj=DyndbMolecule.objects.select_related('id_compound').get(pk=mol_id)
                            netcharge=molobj.net_charge
                            if netcharge>0:
                                netcharge='+'+str(netcharge)
                            comp=molobj.id_compound.id
                            compname=molobj.id_compound.name.capitalize()
                            imagepath=get_imagepath(mol_id,'molecule')
                            moleculelist.append([str(mol_id),str(res.inchikey),imagepath,compname,netcharge]) #define inchikey in searchindex
                            try:                              
                                comoldic[str(comp)].add(str(mol_id))
                            except:
                                comoldic[str(comp)]={str(mol_id)}
        proteinlist=list(set(tuple([tuple(prot) for prot in proteinlist])))
        proteinlist=[list(prot) for prot in proteinlist]
        gpcrlist=list(set(tuple([tuple(gpcr) for gpcr in gpcrlist])))
        gpcrlist=[list(gpcr) for gpcr in gpcrlist]
        for keys in comoldic:
            comoldic[keys]=list(comoldic[keys])
        #add number of simulations in which every result appears.
        for mol in moleculelist:
            mol.append(len(count_dynamics(int(mol[0]),'molecule')[1]))
        for pro in proteinlist:
            pro.append(len(count_dynamics(int(pro[0]),'protein')[1]))
        for gpcr in gpcrlist:
            gpcr.append(len(count_dynamics(int(gpcr[0]),'protein')[1]))
        for comp in compoundlist:
            comp.append(len(count_dynamics(int(comp[0]),'compound')[1]))
        if return_type=='protein':
            tojson={'compound':[], 'protein':proteinlist,'gpcr':[],'molecule':[], 'comoldic':{},'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        if return_type=='gpcr':
            tojson={'compound':[], 'protein':[],'gpcr':gpcrlist,'molecule':[],'comoldic':{},'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        elif return_type=='molecule':
            tojson={'compound':[], 'protein':[],'gpcr':[],'molecule':moleculelist,'names':[], 'comoldic':comoldic, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        elif return_type=='compound':
            tojson={'compound':compoundlist, 'protein':[],'gpcr':[],'molecule':[],'names':[],'comoldic':comoldic, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        elif return_type=='complex' or return_type=='model' or return_type=='dynamics':
            tojson={'compound':[], 'protein':[],'gpcr':[],'molecule':[], 'names':names,'comoldic':{}, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        elif return_type=='All': #no filter
            tojson={'compound':compoundlist, 'protein':proteinlist,'gpcr':gpcrlist,'molecule':moleculelist,'comoldic':comoldic,'names':names, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
###################################################################################################################################

@textonly_500_handler
def emptysearcher(request):
    '''Returns every result matching the filters the user has activated, but ignores the composition of the simulation. Only its properties are searched, like apoform or not, software used, etc.'''
    if request.method == 'POST':
        dynresult=[]
        modelresult=[]
        if request.POST.get('restype')=='model': #model
            modelids=[]
            modelresult=[]
            if request.POST.get('is_apo')=='apo' or request.POST.get('is_apo')=='both':
                for model in DyndbModel.objects.select_related('id_protein').filter(is_published=True):
                    modprot=model.id_protein
                    if modprot != None:
                        modelresult.append([model.id , DyndbProtein.objects.get(pk=modprot.id).name.rstrip() ]) #modelresult.append(mod.id)
            if request.POST.get('is_apo')=='com' or request.POST.get('is_apo')=='both':
                for model in DyndbModel.objects.select_related('id_protein').filter(is_published=True):
                    modprot=model.id_protein
                    if modprot is None:
                        modelids.append(model.id)
                modelresult=modelresult+getligrec(modelids,'model')
        else: #dynamics
            dynlist=set()
            if request.POST.get('is_apo')=='apo' or request.POST.get('is_apo')=='both':
                for model in DyndbModel.objects.select_related('id_protein').filter(is_published=True):
                    if model.id_protein != None:
                        for dyn in DyndbDynamics.objects.filter(id_model=model.id):
                            dynlist.add(dyn.id)
            if request.POST.get('is_apo')=='com' or request.POST.get('is_apo')=='both':
                for model in DyndbModel.objects.filter(is_published=True):
                    if model.id_protein == None:
                        for dyn in DyndbDynamics.objects.filter(id_model=model.id):
                            dynlist.add(dyn.id)
            ffset=set()
            tstepset=set()
            solset=set()
            memset=set()
            methodset=set()
            sofset=set()
            if request.POST.get('ff')!='':
                for dyn in DyndbDynamics.objects.filter(ff=request.POST.get('ff')):
                    ffset.add(dyn.id)
                dynlist=dynlist.intersection(ffset)
            if request.POST.get('tstep')!='':
                if request.POST.get('gle')=='smaller':
                    for dyn in DyndbDynamics.objects.filter(timestep__lte=request.POST.get('tstep') ):
                        tstepset.add(dyn.id)
                if request.POST.get('gle')=='greater':
                    for dyn in DyndbDynamics.objects.filter(timestep__gte=request.POST.get('tstep') ):
                        tstepset.add(dyn.id)
                if request.POST.get('gle')=='equal':
                    for dyn in DyndbDynamics.objects.filter(timestep=request.POST.get('tstep') ):
                        tstepset.add(dyn.id)
                dynlist=dynlist.intersection(tstepset)
            if request.POST.get('sol')!='':
                for dyn in DyndbDynamics.objects.filter(id_dynamics_solvent_types=request.POST.get('sol') ):
                    memset.add(dyn.id)
                dynlist=dynlist.intersection(memset)
            if request.POST.get('mem')!='':
                for dyn in DyndbDynamics.objects.filter(id_dynamics_membrane_types=request.POST.get('mem') ):
                    memset.add(dyn.id)
                dynlist=dynlist.intersection(memset)
            if request.POST.get('method')!='':
                for dyn in DyndbDynamics.objects.filter(id_dynamics_methods=request.POST.get('method') ):
                    methodset.add(dyn.id)
                dynlist=dynlist.intersection(methodset)
            if request.POST.get('sof')!='':
                for dyn in DyndbDynamics.objects.filter(software=request.POST.get('sof')):
                    sofset.add(dyn.id)
                dynlist=dynlist.intersection(sofset)
            dynresult=[]
            dynresult=getligrec(dynlist,'dynamics')
    tojson={'dynlist':dynresult,'model':modelresult,'result':[],'message':''}
    data = json.dumps(tojson)
    return HttpResponse(data, content_type='application/json')

###################################################################################################################################
def getligrec(idlist,return_type):
    '''For every id in idlist, the ligands and receptors of the dynamics/model/complex of that given id are returned. '''
    if return_type=='complex':
        complex_list_names=[]
        cmolq = DyndbComplexMolecule.objects.filter(id__in=idlist).select_related('id_complex_exp')
        #TODO optimize: change code bellow to use annoate and .values() instead
        cmolq = cmolq.prefetch_related(Prefetch("id_complex_exp__compounds",queryset=DyndbCompound.objects.annotate(type=F('dyndbcomplexcompound__type'))))
        cmolq = cmolq.prefetch_related("id_complex_exp__proteins")  
        for cmolobj in cmolq:
            cmolid = cmolobj.id
            exp_id=cmolobj.id_complex_exp.id
            liglist=[]
            receptorlist=[]
            for match in cmolobj.id_complex_exp.compounds.all():
                if match.type==0 or match.type==1:
                    liglist.append(match.name.rstrip())
            for rmatch in cmolobj.id_complex_exp.proteins.all():
                if rmatch.receptor_id_protein is not None:
                    receptorlist.append(rmatch.name.rstrip())
                else:
                    liglist.append(rmatch.name.rstrip())
            complex_list_names.append([exp_id, receptorlist, liglist])
        return complex_list_names
    elif return_type=='model':
        modelshowresult=[]
        modq = DyndbModel.objects.filter(pk__in=idlist).select_related('id_protein')
        for modobj in modq:
            modid = modobj.pk
            cmol_id = None
            prot_id = None
            if modobj.id_complex_molecule is not None:            
                cmol_id= modobj.id_complex_molecule.id
                modelshowresult.append( [modid] + getligrec([cmol_id],'complex')[0][1:] )
            if modobj.id_protein is not None:
                prot_id = modobj.id_protein.id
                prot_name = modobj.id_protein.name.rstrip() 
                modelshowresult.append([modid,prot_name] )
            if (cmol_id is None) == (prot_id is None):
                if settings.DEBUG:
                    print('WARNING: Model %d has id_complex_molecule = "%s" and id_protein = "%s".' % (modid, str(cmol_id),str(prot_id)))
                else:
                    raise ValueError('Model %d has id_complex_molecule = "%s" and id_protein = "%s".' % (modid, str(cmol_id),str(prot_id)))
        return modelshowresult
    else:
        dynresult=[]
        dynq = DyndbDynamics.objects.filter(id__in=idlist).values('id','id_model')
        for dyn in dynq:
            dyn_id = dyn['id']
            cmol_id = dyn['id_model']
            dynresult.append([dyn_id] + getligrec([cmol_id],'model')[0][1:] )
        return dynresult
###################################################################################################################################
def complexmatch(result_id,querylist):
    ''' Extracts every element from each complex in result_id and checks if there are elements in the complex which are not in the querylist '''
    moltypetrans={0:'orto',1:'alo'}
    cmolecule=DyndbComplexMolecule.objects.select_related('id_complex_exp').get(pk=result_id)
    for mol in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=result_id):
        print('this molecule',mol.id_molecule.id,' is in the cmol', result_id)
        strid=str(mol.id_molecule.id)
        if (['molecule',strid, moltypetrans[mol.type]] not in querylist) and (['molecule',strid, 'all'] not in querylist):
            return 'fail'
    for cprotein in DyndbComplexProtein.objects.select_related('id_protein__receptor_id_protein').filter(id_complex_exp=cmolecule.id_complex_exp.id):
        is_receptor=cprotein.id_protein.receptor_id_protein is not None
        if is_receptor is True:
            is_receptor='true'
        cprotstr=str(cprotein.id_protein.id)
        print(['protein',cprotstr,is_receptor], 'this protein is in this cmol')
        if ['protein',cprotstr,is_receptor] not in querylist:
            print('missing protein:',['protein',str(cprotein.id_protein.id),is_receptor])
            return 'fail'
    for ccompound in DyndbComplexCompound.objects.select_related('id_compound').filter(id_complex_exp=cmolecule.id_complex_exp.id):
        comstr=str(ccompound.id_compound.id)
        print('this compound is in this cmol',['compound',comstr,moltypetrans[ccompound.type]])
        if (['compound',comstr,moltypetrans[ccompound.type]] not in querylist) and (['compound',comstr,'all'] not in querylist):
            print('mising compound:',['compound',str(ccompound.id_compound.id),moltypetrans[ccompound.type]])
            return 'fail' 
    return 'pass'

def exactmatchtest(arrays,return_type,result_id):
    ''' Extracts every element from each complex, model or dynamic in result_id and checks if there are elements in it which are not in the querylist '''
    rowdict=dealwithquery(arrays)
    querylist=list()
    for keys,values in rowdict.items():
        if keys[1]!='NOT':
            if type(values[1])==list:
                for item in values:
                    if len(item)==3:
                        querylist.append(item)
                    elif len(item)>3 and item[0]!='NOT':
                        querylist.append(item[1:])
            else:
                querylist.append(values)
    #hack the list to add the corresponding molecules and compounds to the ones the user has queried.
    tmpquerylist=[]
    for item in querylist:
        if item[0]=='compound':
            for molid in DyndbMolecule.objects.filter(id_compound=item[1]):
                tmpquerylist.append(['molecule',str(molid.id),item[2]])
        elif item[0]=='molecule':
            tmpquerylist.append(['compound',str(DyndbMolecule.objects.get(pk=item[1]).id_compound.id),item[2]])
    querylist+=tmpquerylist
    if return_type=='complex':
        return complexmatch(result_id,querylist)
    elif return_type=='model':
        for comp in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=result_id):
            if comp.type!=1:
                compstr=str(comp.id_molecule.id)
                if (['molecule',compstr,'other'] not in querylist) and (['molecule',compstr,'all'] not in querylist):
                    print(['molecule',str(comp.id_molecule.id),'other'],'MISSING!')
                    return 'fail'
        apotest=DyndbModel.objects.select_related('id_complex_molecule').get(pk=result_id).id_complex_molecule
        if apotest is not None:
            return complexmatch(apotest.id,querylist)
        else:
            return 'pass'
    else:
        modelobj=DyndbDynamics.objects.select_related('id_model').get(pk=result_id).id_model
        for comp in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=result_id):
            compstr=str(comp.id_molecule.id)
            if (['molecule',compstr,'other'] not in querylist) and (['molecule',compstr,'all'] not in querylist):
                print(['molecule',str(comp.id_molecule.id),'other'],'MISSING!')
                return 'fail'
        for comp in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=modelobj.id):
            compstr=str(comp.id_molecule.id)
            if comp.type!=1:
                if (['molecule',compstr,'other'] not in querylist) and (['molecule',compstr,'all'] not in querylist):
                    print(['molecule',str(comp.id_molecule.id),'other'],'MISSSING!')
                    return 'fail'
        if DyndbDynamics.objects.get(pk=result_id).id_model.id_complex_molecule is not None:
            return complexmatch(modelobj.id_complex_molecule.id,querylist)
    return 'pass'

##########################################################################################################################################
def prepare_to_boolean(resultdic):
    '''Transforms a dic with keys [counter, boolean] to a list where the index is the counter and the first element of every list is the boolean'''
    #resultdic is like: dic[rownumber,boolean]=[1,2,3,4]
    list_of_lists=[[] for i in range(len(resultdic))] #initialize the list of lists
    for keys in sorted(resultdic):
        list_of_lists[keys[0]]=([ keys[1],resultdic[keys] ]) #now we have a list instead of a dic. The index of the list is the row number and the first value of the list is the boolean. 
    return list_of_lists

##########################################################################################################################################
def do_boolean(list_of_lists): #[ ['NONE',[1,2,3] ], ['OR',[3,4,5] ], ['AND',[1,2,3,4] ]     ]
    ''' Performs interesection, union and difference operations to find an id which matches all demands. AND operations take priority '''
    notset=set()
    orset=set()
    result_set=set()
    for i in range(len(list_of_lists)-1,-1,-1): #go from the bottom to the top
        if list_of_lists[i][0]=='AND':
            list_of_lists[i-1][1]=list( set(list_of_lists[i][1]).intersection(set(list_of_lists[i-1][1])) ) #it cant give index error because first item is NONE,not AND.
        elif list_of_lists[i][0]=='NOT':
            notset.update(list_of_lists[i][1])
        elif list_of_lists[i][0]=='OR':
            orset.update(list_of_lists[i][1])
        else:
            noneboo=set(list_of_lists[i][1])
    noneboo.update(orset)
    noneboo=noneboo.difference(notset)
    return noneboo

##########################################################################################################################################
def do_query(table_row,return_type): #table row will be a list as [id,type]
    '''Returns a list of id's of the selected type (complex, model or dynamics) where the element in table_row appears. If the elemnt in table_row is a compound the ids brom both the compound and all the correspondent molecules are retrieved'''
    rowlist=[]
    if return_type=='complex':
        if table_row[0]=='protein':
            is_receptor=DyndbProtein.objects.get(pk=table_row[1]).receptor_id_protein
            if (table_row[2]=='true' and is_receptor is not None) or (table_row[2]==False and is_receptor is None):
                q=DyndbProtein.objects.filter(pk=table_row[1])
                q=q.annotate(cmol_id=F('dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule__id'))
                q=q.values('cmol_id')
                for row in q:
                    rowlist.append(row['cmol_id'])
        elif table_row[0]=='molecule':
            user_molecule = table_row[1]
            if table_row[2]=='orto' or table_row[2]=='all': #orthosteric ligand
                for comp in DyndbComplexMoleculeMolecule.objects.select_related('id_complex_molecule').filter(id_molecule=user_molecule).filter(type=0): 
                    rowlist.append(comp.id_complex_molecule.id)
            elif table_row[2]=='alo' or table_row[2]=='all': #alosteric ligand
                for comp in DyndbComplexMoleculeMolecule.objects.select_related('id_complex_molecule').filter(id_molecule=user_molecule).filter(type=1): 
                    rowlist.append(comp.id_complex_molecule.id)
        else:
            user_compound = table_row[1]
            for mol in DyndbMolecule.objects.filter(id_compound=user_compound):
                rowlist+=do_query([ 'molecule' , mol.id , table_row[2] ], 'complex')
            q = DyndbComplexCompound.objects.filter(id_compound=user_compound)
            q = q.annotate(cmol_id=F('id_complex_exp__dyndbcomplexmolecule__id'))
            q = q.values('type','cmol_id')
            for row in q:
                if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0: #ortoligand
                    rowlist.append(row['cmol_id'])
                if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1: #alosteric ligand
                    rowlist.append(row['cmol_id'])
        ############################
    elif return_type=='model':
        if table_row[0]=='protein':
            is_receptor=DyndbProtein.objects.get(pk=table_row[1]).receptor_id_protein
            if (table_row[2]=='true' and is_receptor is not None) or (table_row[2]==False and is_receptor is None):
                q = DyndbComplexProtein.objects.filter(id_protein=table_row[1])
                q = q.annotate(model_id=F('id_complex_exp__dyndbcomplexmolecule__dyndbmodel__id'))
                q = q.values('id_protein','model_id')
                for row in q:
                    if row['model_id'] is not None:
                        rowlist.append(row['model_id'])
            for model in DyndbModel.objects.filter(id_protein=table_row[1]): #apoforms
                rowlist.append(model.id)
        elif table_row[0]=='molecule':
            user_molecule = table_row[1]
            q=DyndbComplexMoleculeMolecule.objects.filter(id_molecule=user_molecule)
            q=q.annotate(model_id=F('id_complex_molecule__dyndbmodel__id'))
            q=q.values('model_id','type')
            for row in q:
                if row['model_id'] is not None:
                    if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0: #orthosteric ligand
                        rowlist.append(row['model_id'])
                    if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1: #alosteric ligand
                        rowlist.append(row['model_id'])
            if table_row[2]=='other' or table_row[2]=='all':
                for modcomp in DyndbModelComponents.objects.filter(id_molecule=user_molecule):
                    if int(modcomp.type) in [0,2,3,4]:
                        rowlist.append(modcomp.id_model.id)
        else: #it is a compound
            user_compound=table_row[1]
            for mol in DyndbMolecule.objects.filter(id_compound=user_compound):
                rowlist+=do_query([ 'molecule' , mol.id , table_row[2] ], 'model')
            q=DyndbComplexCompound.objects.filter(id_compound=user_compound)
            q=q.annotate(id_model=F('id_complex_exp__dyndbcomplexmolecule__dyndbmodel__id'))
            q=q.values('id_model','type')
            for row in q:
                if row['id_model'] is not None:
                    if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0:
                        rowlist.append(row['id_model'])
                    if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1:
                        rowlist.append(row['id_model'])
            if table_row[2]=='other' or table_row[2]=='all':
                for molecule in DyndbMolecule.objects.filter(id_compound=user_compound):
                    for modcomp in DyndbModelComponents.objects.select_related('id_model').filter(id_molecule=molecule.id):
                        if int(modcomp.type) in [0,2,3,4]:
                            rowlist.append(modcomp.id_model.id)
        #######################
    else: #return Dynamics
        if table_row[0]=='protein':
            is_receptor=DyndbProtein.objects.get(pk=table_row[1]).receptor_id_protein 
            if (table_row[2]=='true' and is_receptor is not None) or (table_row[2]==False and is_receptor is None):
                q=DyndbComplexProtein.objects.filter(id_protein=table_row[1])
                q=q.annotate(id_dynamics=F('id_complex_exp__dyndbcomplexmolecule__dyndbmodel__dyndbdynamics__id'))
                q=q.values('id_dynamics')
                for row in q:
                    if row['id_dynamics'] is not None:
                        rowlist.append(row['id_dynamics'])
            q=DyndbModel.objects.filter(id_protein=table_row[1]) #apoforms
            q=q.annotate(id_dynamics=F('dyndbdynamics__id'))
            q=q.values('id_dynamics')
            for row in q:
                if row['id_dynamics'] is not None:
                    rowlist.append(row['id_dynamics'])
        elif table_row[0]=='molecule':
            user_molecule = table_row[1]
            q=DyndbComplexMoleculeMolecule.objects.filter(id_molecule=user_molecule)
            q=q.annotate(dynamics_id=F('id_complex_molecule__dyndbmodel__dyndbdynamics__id'))
            q=q.values('dynamics_id','type')
            for row in q:
                if row['dynamics_id'] is not None:
                    if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0:
                        rowlist.append(row['dynamics_id'])
                    if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1:
                        rowlist.append(row['dynamics_id'])
            if table_row[2]=='other' or table_row[2]=='all':
                for dyncomp in DyndbDynamicsComponents.objects.select_related('id_dynamics').filter(id_molecule=user_molecule):
                    rowlist.append(dyncomp.id_dynamics.id)
                for modcomp in DyndbModelComponents.objects.select_related('id_model').filter(id_molecule=user_molecule):
                    if int(modcomp.type) in [0,2,3,4]:
                        for dyid in DyndbDynamics.objects.filter(id_model=modcomp.id_model.id): #dynamics whose model has the mol of user's interest.
                            rowlist.append(dyid.id)
        else:
            user_compound=table_row[1]
            for mol in DyndbMolecule.objects.filter(id_compound=user_compound):
                rowlist+=do_query([ 'molecule' , mol.id , table_row[2] ], 'dynamics')
            q=DyndbComplexCompound.objects.filter(id_compound=user_compound)
            q=q.annotate(id_dynamics=F('id_complex_exp__dyndbcomplexmolecule__dyndbmodel__dyndbdynamics__id'))
            q=q.values('id_dynamics','type')
            for row in q:
                if row['id_dynamics'] is not None:
                    if (table_row[2]=='orto' or table_row[2]=='all') and row['type']==0:
                        rowlist.append(row['id_dynamics'])
                    if (table_row[2]=='alo' or table_row[2]=='all') and row['type']==1:
                        rowlist.append(row['id_dynamics'])
            if table_row[2]=='other' or table_row[2]=='all':
                q=DyndbMolecule.objects.filter(id_compound=user_compound)
                q=q.annotate(id_dynamics=F('dyndbdynamicscomponents__id_dynamics__id'), id_model=F('dyndbmodelcomponents__id_model__id'), typemodel=F('dyndbmodelcomponents__type'))
                q=q.values('id_dynamics','id_model','typemodel')
                for row in q:
                    if (row['id_dynamics'] is not None) and row['id_dynamics'] not in rowlist:
                        rowlist.append(row['id_dynamics'])
                    if (row['typemodel'] is not None) and row['typemodel'] in [0,2,3,4]:
                        for dyn in DyndbDynamics.objects.filter(id_model=row['typemodel']):
                            if dyn.id not in rowlist:
                                rowlist.append(dyn.id)
    rowlist=[res_id for res_id in rowlist if res_id is not None]
    return rowlist

##########################################################################################################################################
def dealwithquery(arrays):
    ''' Transforms the table in the searcher to a dictionary with keys (row number, boolean) and the row or the rows inside the parenthesis as values.'''
    listofdic=[]
    counter=0
    rowdict=dict()
    paren_list=list()
    while counter<len(arrays):
        if arrays[counter][1]=='(':
            flag=0
            paren_list=[]
            #rowdict[ (len(rowdict), arrays[counter][0]) ]=[]
            paren_list.append([arrays[counter][2],arrays[counter][3],arrays[counter][4]]) # [id,type,isligrec] a 'NONE' boolean will be added.
            counter2=counter+1 #start at the next line
            while flag==0 and counter2<len(arrays): #until you find the closing parenthesis:
                if arrays[counter2][5]==')':
                    flag=1 #flag 1 will stop the appending to this parenthesis
                    paren_list.append([ arrays[counter2][0],arrays[counter2][2],arrays[counter2][3],arrays[counter2][4] ])
                else:
                    paren_list.append([ arrays[counter2][0],arrays[counter2][2],arrays[counter2][3],arrays[counter2][4] ])
                    counter2+=1
            rowdict[ (len(rowdict), arrays[counter][0]) ]=paren_list #once ")" found, save the paren_list with the boolean behind it as part of the key
            counter=counter2+1 #jump all rows that have already been parsed.
        else:
            rowdict[ (len(rowdict), arrays[counter][0]) ]= [ arrays[counter][2],arrays[counter][3],arrays[counter][4] ] #id,type,isligand/isreceptor
            counter+=1
    return rowdict

##########################################################################################################################################
def mainsearcher(arrays,return_type):
    #TODO optimize: use single query
    rowdict=dealwithquery(arrays)
    results=dict()
    for keys,values in rowdict.items():
        #we need to differentiate between list of lists, and simples lists
        #parenthesis lines are like: dict[key]=[ [ID, TYPE]  [AND, ID, TYPE], [OR, ID, TYPE], [AND, ID, TYPE]  ]
        #other lines are like: dickt[key]=[AND, ID, TYPE]
        inner_results=list()
        if type(values[0])==list: #inside of parenthesis
            for item in values: #values is a list, so it keeps the order of the rows, so does inner_results.
                if item[0]=='AND' or item[0]=='OR' or item[0]=='NOT':
                    inner_results.append([ item[0] , do_query(item[1:4],return_type) ]) #inner_results=[ ['AND', [1,2,3] ]  ],  ['OR', [2,3,5] ]  ]

                else: #first line inside parenthesis, the boolean of this row aplies to the whole parenthesis and it is stored in the rowdict.                
                    inner_results.append([ 'NONE' , do_query(item[0:3], return_type)])
            results[keys]=list(do_boolean(inner_results)) #results[counter,boolean]=[1,2,3,4] #counter is the row number where the '(' appears
        else: #simple row
            results[keys]=do_query(values,return_type) #do query for each value, save it under same key
    aaa=do_boolean( prepare_to_boolean(results) )
    return aaa

##########################################################################################################################################
@textonly_500_handler
def NiceSearcher(request):
    '''Searchs for complexes, models or dynamics with the combination of elements and features (apoform or not, software, etc) designed by the user'''
    arrays_def=[]
    if request.method == 'POST':
        arrays=request.POST.getlist('bigarray[]')
        counter=0
        rememberlist=list()
        setlist=list()
        model_list=list()
        dynlist=list()
        return_type=request.POST.get('restype')
        model_protein=list() #save here the PROTEINS the user has used to search and its boolean. 
        for array in arrays[1:]: #each array is a row in the dynamic "search table". Avoid table header with [1:]
            array=array.split(',') # example [OR, protein, 1,true] [boolean operator, type, id, is receptor/is ligand]
            array[2]=array[2].replace('StandardF','compound').replace('SpecificS','molecule');
            if array[4]=='false':
                array[4]=False
            arrays_def.append(array)
        resultlist=mainsearcher(arrays_def,return_type)
        if len(resultlist)==0:
            tojson={'result':[],'model':[],'dynlist':[],'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        rememberlist=[]
        for array in arrays_def:
            rememberlist.append([array[2],array[3],array[4]]) #we should avoid other/all molecules!
        a=[ [ i[1], i[2] ] for i in rememberlist if i[0]=='molecule'] #[[id, type],...] of every molecule in table search
        b=[ [ i[1], i[2] ] for i in rememberlist if i[0]=='protein']
        c=[ [ i[1], i[2] ] for i in rememberlist if i[0]=='compound']
        resultlist=list(resultlist) #it was a set until now
        if return_type=='complex':
            if request.POST.get('exactmatch')=='true':
                tmplist=[]
                for i in resultlist:
                    if exactmatchtest(arrays_def,'complex',i)=='pass':
                        tmplist.append(i)
                resultlist=tmplist
            resultlist=list(filter(lambda x: len(DyndbComplexExp.objects.filter(id=x,is_published=True))>0,resultlist))
            complex_list_names=list()
            corresponding_cexp=[]
            complex_list_names=getligrec(resultlist,'complex')
            tojson={'result': complex_list_names,'model':model_list,'dynlist':dynlist,'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        #############MODEL SEARCH
        elif return_type=='model':
            modelresult=[]
            corresponding_cexp=[]       
            tmplist=[]
            if request.POST.get('is_apo')=='apo' or request.POST.get('is_apo')=='both':
                for model_id in resultlist:
                    if DyndbModel.objects.select_related('id_protein').get(pk=model_id).id_protein is not None:
                        tmplist.append(model_id)
            if request.POST.get('is_apo')=='com' or request.POST.get('is_apo')=='both':
                for model_id in resultlist:
                    if DyndbModel.objects.select_related('id_protein').get(pk=model_id).id_protein is None:
                        tmplist.append(model_id)
            resultlist=tmplist
            if request.POST.get('exactmatch')=='true':
                tmplist=[]
                for i in resultlist:
                    if exactmatchtest(arrays_def,'model',i)=='pass':
                        tmplist.append(i)
                resultlist=tmplist  
            resultlist=list(filter(lambda x: len(DyndbModel.objects.filter(id=x,is_published=True))>0,resultlist))
            modelresult=getligrec(resultlist,'model')
            tojson={'result': resultlist,'model':modelresult,'dynlist':dynlist,'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')
        #########DYNAMICS SEARCH
        dynlist=set()
        ffset=set()
        tstepset=set()
        solset=set()
        memset=set()
        methodset=set()
        sofset=set()
        tmplist=[]
        if request.POST.get('is_apo')=='apo' or request.POST.get('is_apo')=='both':
            for dyn_id in resultlist:
                if DyndbDynamics.objects.select_related('id_model__id_protein').get(pk=dyn_id).id_model.id_protein is not None:
                    tmplist.append(dyn_id)
        if request.POST.get('is_apo')=='com' or request.POST.get('is_apo')=='both':
            for dyn_id in resultlist:
                if DyndbDynamics.objects.select_related('id_model__id_protein').get(pk=dyn_id).id_model.id_protein is None:
                    tmplist.append(dyn_id)
        resultlist=set(tmplist)
        if request.POST.get('exactmatch')=='true':
            tmplist=[]
            for i in resultlist:
                if exactmatchtest(arrays_def,'dynamics',i)=='pass':
                    tmplist.append(i)
            resultlist=tmplist 
        dynlist=set(resultlist)
        if request.POST.get('ff')!='':
            for dyn in DyndbDynamics.objects.filter(ff=request.POST.get('ff')):
                ffset.add(dyn.id)
            dynlist=dynlist.intersection(ffset)
        if request.POST.get('tstep')!='':
            if request.POST.get('gle')=='smaller':
                for dyn in DyndbDynamics.objects.filter(timestep__lte=request.POST.get('tstep') ):
                    tstepset.add(dyn.id)
            if request.POST.get('gle')=='greater':
                for dyn in DyndbDynamics.objects.filter(timestep__gte=request.POST.get('tstep') ):
                    tstepset.add(dyn.id)
            if request.POST.get('gle')=='equal':
                for dyn in DyndbDynamics.objects.filter(timestep=request.POST.get('tstep') ):
                    tstepset.add(dyn.id)
            dynlist=dynlist.intersection(tstepset)
        if request.POST.get('sol')!='':
            for dyn in DyndbDynamics.objects.filter(id_dynamics_solvent_types=request.POST.get('sol') ):
                memset.add(dyn.id)
            dynlist=dynlist.intersection(memset)
        if request.POST.get('mem')!='':
            for dyn in DyndbDynamics.objects.filter(id_dynamics_membrane_types=request.POST.get('mem') ):
                memset.add(dyn.id)
            dynlist=dynlist.intersection(memset)
        if request.POST.get('method')!='':
            for dyn in DyndbDynamics.objects.filter(id_dynamics_methods=request.POST.get('method') ):
                methodset.add(dyn.id)
            dynlist=dynlist.intersection(methodset)
        if request.POST.get('sof')!='':
            for dyn in DyndbDynamics.objects.filter(software=request.POST.get('sof')):
                sofset.add(dyn.id)
            dynlist=dynlist.intersection(sofset)
        resultlist=list(DyndbDynamics.objects.filter(id__in=resultlist,is_published=True).values_list('id',flat=True))
        dynlist=list(DyndbDynamics.objects.filter(id__in=dynlist,is_published=True).values_list('id',flat=True))
        dynresult=getligrec(dynlist,'dynamics')
        tojson={'result':resultlist ,'model':model_list,'dynlist':dynresult,'message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

###################################################################################
def get_uniprot_species_id_and_screen_name(mnemonic):
  speciesqs = DyndbUniprotSpecies.objects.filter(code=mnemonic)
  speciesqs = speciesqs.annotate(screen_name=Concat('scientific_name',V(' ('),'code',V(')'),output_field=TextField()))
  try:
    record = speciesqs.order_by('id')[0]
  except IndexError:
    return None
  except:
    raise
  return (record.pk,record.screen_name)
###################################################################################
def generate_molecule_properties_BindingDB(SDFpath):
    pngsize = 300
    RecMet = False
    formre = re.compile('^form-(\d+)-')
    data={}
    data['sinchi']={}
    data['inchi']={}
    SDFhandler=open(SDFpath,'rb')
    mol = open_molecule_file(SDFhandler) # EL objeto mol es necesario para trabajar en RD KIT use this function with ARGUMENT! -> filetype='sdf' #MODIFIED BY ALEJANDRO, DO NOT KEEP THIS VERSION ON MERGE
    try:
        sinchi,code,msg = generate_inchi(mol,FixedH=False,RecMet=False)
        print("\nSINCHI",code)
        if code > 1:
             data['msg'] ='Error while computing Standard InChI:\n'+msg
             return(data)
        data['sinchi']['sinchi'] = sinchi
        data['sinchi']['code'] = code
        data['inchi'] = dict()
        inchi,code,msg = generate_inchi(mol,FixedH=True,RecMet=RecMet)
        if code > 1:
             data['msg'] ='Error while computing InChI:\n'+msg
             return(data)
        data['inchi']['inchi'] = inchi
        data['inchi']['code'] = code
    except:
        data['msg'] ='Error while computing InChI.'
    data['smiles'] = generate_smiles(mol)
    data['charge'] = get_net_charge(mol)
    try:    
        data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])
        data['inchikey'] = generate_inchikey(data['inchi']['inchi'])
        data['inchicol'] = 1
        data['inchicol'] = 1
    except:
        data['msg'] ='Error while computing InChIKey.'
    SDFhandler.close()
    return data

@textonly_500_handler
def do_analysis(request): #warning, delete this view!
    if request.method == 'POST':
        full_results=dict()
        arrays=request.POST.getlist('frames[]')
        percentage_cutoff=int(arrays[3])
        trajectory = md.load('dynadb/b2ar_isoprot/b2ar.dcd',top='dynadb/b2ar_isoprot/build.pdb')
        trajectory=trajectory[int(arrays[0]):int(arrays[1])]
        atom_indices = [a.index for a in trajectory.topology.atoms if a.name == str(arrays[2])]
        t=trajectory
        trajectory=trajectory.atom_slice(atom_indices, inplace=False)
        atoms=psf.parser('dynadb/b2ar_isoprot/b2ar.psf')
        frametime=(t.time).reshape(len(t.time),1)
        sasa=md.shrake_rupley(trajectory)
        label = lambda hbond : '%s--%s' % (t.topology.atom(hbond[0]), t.topology.atom(hbond[2]))
        hbonds_ks=md.wernet_nilsson(t, exclude_water=True, periodic=True, sidechain_only=False)
        histhbond=dict()
        hbonds_residue=dict()
        hbonds_residue_notprotein=dict()
        for frameres in hbonds_ks:
            for hbond in frameres:
                try:
                    histhbond[tuple(hbond)]+=1
                except KeyError:
                    histhbond[tuple(hbond)]=1
        for keys in histhbond:
            histhbond[keys]= round(histhbond[keys]/len(t),3)*100
            if abs(keys[0]-keys[2])>60 and histhbond[keys]>10: #the hbond is not between neighbourd atoms and the frecuency across the traj is more than 10%
                labelbond=label([keys[0],histhbond[keys],keys[2]])
                labelbond=labelbond.replace(' ','')
                labelbond=labelbond.split('--')
                donor=labelbond[0]
                acceptor=labelbond[1]
                acceptor_res=acceptor[:acceptor.rfind('-')]
                donor_res=donor[:donor.rfind('-')]
                if donor_res!=acceptor_res: #do not consider hbond inside the same residue.
                    histhbond[keys]=str(histhbond[keys])[:4]
                    if (not t.topology.atom(keys[0]).residue.is_protein) or (not t.topology.atom(keys[2]).residue.is_protein): #other hbonds
                        try:
                            if acceptor_res not in [i[0] for i in hbonds_residue_notprotein[donor_res]]:
                                hbonds_residue_notprotein[donor_res].append([acceptor_res,histhbond[keys],str(keys[0]),str(keys[2])]) # HBONDS[donor]=[acceptor,freq,atom1index,atom2index]
                        except KeyError:
                            hbonds_residue_notprotein[donor_res]=[[acceptor_res,histhbond[keys],str(keys[0]),str(keys[2])]]
                    else: #intraprotein hbonds
                        try:
                            if acceptor_res not in [i[0] for i in hbonds_residue[donor_res]]:
                                hbonds_residue[donor_res].append([acceptor_res,histhbond[keys],str(keys[0]),str(keys[2])])
                        except KeyError:
                            hbonds_residue[donor_res]=[[acceptor_res,histhbond[keys],str(keys[0]),str(keys[2])]]
        sasa4allatoms=sasa.sum(axis=0)
        time=trajectory.time
        total_sasa = sasa.sum(axis=1)
        time=time.tolist()
        total_sasa = total_sasa.tolist()
        result=list(zip(time,total_sasa))
        result=[list(i) for i in result]
        full_results['sasa']=result
        full_results['hbonds'] = hbonds_residue
        full_results['hbonds_notprotein'] = hbonds_residue_notprotein
        full_results['salt_bridges'] = psf.true_saline_bridges(t,atoms,distance_threshold=0.4, percentage_threshold=percentage_cutoff)
        full_results['salt_bridges'] = [(label([int(saltb[0])-1,'-',int(saltb[1])-1]),str(round(saltb[2],3)*100)[:4], saltb[0]-1,saltb[1]-1 ) for saltb in full_results['salt_bridges']] # -1 to return to zero indexing.
        seqbadr1='MGDGWLPPDCGPHNRSGGGGATAAPTGSRQVSAELLSQQWEAGMSLLMALVVLLIVAGNVLVIAAIGRTQRLQTLTNLFITSLACADLVMGLLVVPFGATLVVRGTWLWGSFLCECWTSLDVLCVTASIETLCVIAIDRYLAITSPFRYQSLMTRARAKVIICTVWAISALVSFLPIMMHWWRDEDPQALKCYQDPGCCDFVTNRAYAIASSIISFYIPLLIMIFVYLRVYREAKEQIRKIDRCEGRFYGSQEQPQPPPLPQHQPILGNGRASKRKTSRVMAMREHKALKTLGIIMGVFTLCWLPFFLVNIVNVFNRDLVPDWLFVFFNWLGYANSAFNPIIYCRSPDFRKAFKRLLCFPRKADRRLHAGGQPAPLPGGFISTLGSPEHSPGGTWSDCNGGTRGGSESSLEERHSKTSRSESKMEREKNILATTRFYCTFLGNGDKAVFCTVLRIVKLFEDATCTCPHTHKLKMKWRFKQHQA'
        ourseq=''
        for res in trajectory.topology.residues:
            if res.is_protein:
                ourseq+=d[res.name]
        alig=align_wt_mut(ourseq,seqbadr1)
        bridge_dic=dict()
        for bond in full_results['salt_bridges']:
            labelbond=bond[0]
            labelbond=labelbond.replace(' ','')
            labelbond=labelbond.split('--')
            donor=labelbond[0]
            acceptor=labelbond[1]
            acceptor_res=acceptor[:acceptor.rfind('-')]
            donor_res=donor[:donor.rfind('-')]
            if donor_res in bridge_dic:
                bridge_dic[donor_res].append([acceptor_res,bond[1],str(bond[2]),str(bond[3])])
            elif acceptor_res in bridge_dic:
                bridge_dic[acceptor_res].append([donor_res,bond[1],str(bond[2]),str(bond[3])])
            else:
               bridge_dic[donor_res]=[[acceptor_res,bond[1],str(bond[2]),str(bond[3])]]
        full_results['salt_bridges']=bridge_dic
        trajectory = md.load('dynadb/b2ar_isoprot/b2ar.dcd',top='dynadb/b2ar_isoprot/build.pdb')
        atomindexes_prot=[atom.index for atom in trajectory.topology.atoms if atom.residue.is_protein]
        trajprot=trajectory.superpose(trajectory,0,atom_indices=atomindexes_prot) #works!
        trajprot.save('./superposed.dcd')
        data = json.dumps(full_results)
        return HttpResponse(data, content_type='application/json')
    else:
        answer={'mdsrv_url':obtain_domain_url(request),'traj_file':'Dynamics/15_trj_1_2.xtc','structure_file':'Dynamics/12_dyn_1.pdb'}
        return render(request, 'dynadb/analysis_results.html',{'answer':answer})

def search_protein(protein_id):
    fiva=dict()
    actlist=list()
    fiva['mutations']=list()
    fiva['models']=list()
    fiva['other_names']=list()
    fiva['activity']=list()
    fiva['references']=list()
    try:
        protein_record = DyndbProtein.objects.select_related(None).get(pk=protein_id)
    except ObjectDoesNotExist:
        return 'This protein does not exist'
    except:
        return 'Something went wrong'
    fiva['Uniprot_id']=protein_record.uniprotkbac    
    fiva['Protein_name']=protein_record.name
    fiva['is_mutated']=protein_record.is_mutated
    fiva['cannonical']=DyndbProteinCannonicalProtein.objects.select_related("id_cannonical_proteins").get(id_protein=protein_id).id_cannonical_proteins.id_protein.id #2 hits
    fiva['scientific_name'] = DyndbProtein.objects.select_related("id_uniprot_species").get(pk=protein_id).id_uniprot_species.scientific_name #1hit
    for match in DyndbProteinMutations.objects.filter(id_protein=protein_id):
        fiva['mutations'].append( (match.resid,match.resletter_from, match.resletter_to) )
    for match in DyndbOtherProteinNames.objects.filter(id_protein=protein_id): #checked
        fiva['other_names'].append(match.other_names)
    for match in DyndbModel.objects.values('id').filter(id_protein=protein_id):
        if match['id'] is not None:
            fiva['models'].append(match['id'])
    q = DyndbComplexProtein.objects.filter(id_protein=protein_id)
    q = q.annotate(model_id=F('id_complex_exp__dyndbcomplexmolecule__dyndbmodel__id'))
    q = q.values('id_protein','model_id')
    for row in q:
        if row['model_id'] is not None:
            fiva['models'].append(row['model_id'])
    fiva['Protein_sequence']=DyndbProteinSequence.objects.get(pk=protein_id).sequence #Let's make the sequence fancier:
    numberoflines= math.ceil( ( len(fiva['Protein_sequence']) + (4 * ( len(fiva['Protein_sequence']) /50 ))) /54)
    beautyseq=''
    for line in range(1,numberoflines+1):
        count=0
        signal_number=[i for i in range(line*50-40,line*50+10,10)]
        string=' '*(10-len(str(signal_number[0])))+str(signal_number[0])+' '+' '*(10-len(str(signal_number[1])))+str(signal_number[1])+' '+' '*(10-len(str(signal_number[2])))+str(signal_number[2])+' '+' '*(10-len(str(signal_number[3])))+str(signal_number[3])+' '+' '*(10-len(str(signal_number[4])))+str(signal_number[4])+'\n'
        cutoff=line*50
        cuton=cutoff-50
        fiva['Protein_sequence'][cuton:cutoff]
        seqline=''
        for char in fiva['Protein_sequence'][cuton:cutoff]:
            if count==9:
                seqline=seqline+char+' '
                count=0
            else:
                seqline=seqline+char
                count+=1
        seqline+='\n'
        cutnumbering=seqline.rfind('') #if the sequences finishes, stop the counting.
        string=string[0:cutnumbering]
        if '\n' not in string:
           string=string+'\n'
        beautyseq=beautyseq+string+seqline
    fiva['Protein_sequence']=beautyseq
    for match in DyndbReferencesProtein.objects.filter(id_protein=protein_id):
        ref={'doi':match.id_references.doi,'title':match.id_references.title,'authors':match.id_references.authors,'url':match.id_references.url,'journal':match.id_references.journal_press,'issue':match.id_references.issue,'pub_year':match.id_references.pub_year,'volume':match.id_references.volume}
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        fiva['references'].append(ref)  
    for match in DyndbExpProteinData.objects.filter(id_protein=protein_id):
        for match2 in DyndbProteinActivity.objects.filter(pk=match.id):
            fiva['activity'].append((match2.rvalue,match2.units,match2.description))
    return fiva

@user_passes_test_args(is_published_or_submission_owner)
def query_protein(request, protein_id):
    '''Returns database information about the given protein_id. If incall is True, it will return a dictionary, otherwise, it will retun an Http response.'''
    fiva=search_protein(protein_id)
    if type(fiva)=='str':
        raise Http404(fiva)
    return render(request, 'dynadb/protein_query_result.html',{'answer':fiva})

@textonly_500_handler
@user_passes_test_args(is_published_or_submission_owner)
def query_protein_fasta(request,protein_id):
    '''Gets the sequence of the given protein and returns its sequence in fasta format.'''
    yourseq=DyndbProteinSequence.objects.get(pk=protein_id)
    seq=getattr(yourseq,'sequence')
    uniprot_id=DyndbProtein.objects.get(pk=protein_id).uniprotkbac
    count=0
    fseq=''
    for char in seq:
        if count==79:
            fseq=fseq+'\n'+char
            count=0
        else:
            fseq=fseq+char
        count=count+1
    response = HttpResponse('', content_type='text/plain; charset=UTF-8')
    response['Content-Disposition'] = 'attachment; filename="protein_'+'protein_id'+'.fa"'
    response.write('> GPCRmd:'+protein_id+'|Uniprot ID:'+uniprot_id.replace(" ","")+':\n')
    response.write(fseq)
    return response

def search_molecule(molecule_id):
    molec_dic=dict()
    molec_dic['myid']=molecule_id
    molec_dic['inmodels']=list()
    molec_dic['references']=list()
    try:
        molobj=DyndbMolecule.objects.select_related('id_compound').get(pk=molecule_id)
    except ObjectDoesNotExist:
        return 'That molecule does not exist.'
    except:
        return 'Something went wrong.'
    molec_dic['link_2_compound']=molobj.id_compound.id
    molec_dic['name']=molobj.id_compound.name
    molec_dic['sdf']=''
    molec_dic['smiles']=molobj.smiles
    molec_dic['description']=molobj.description
    molec_dic['netcharge']=molobj.net_charge
    molec_dic['inchi']=molobj.inchi
    molec_dic['inchikey']=molobj.inchikey
    molec_dic['inchicol']=molobj.inchicol
    molec_dic['imagelink']=get_imagepath(molecule_id, 'molecule')
    filesmol_li=DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).filter(type=0)
    if filesmol_li:
        molec_dic['sdfile']=filesmol_li[0].id_files.filename
    else:
        molec_dic['sdfile']=[]
    for match in DyndbModelComponents.objects.filter(id_molecule=molecule_id):
        molec_dic['inmodels'].append(match.id_model.id)
    for molfile in DyndbFilesMolecule.objects.select_related('id_files').filter(id_molecule=molecule_id).filter(type=0):
        if os.path.isfile(settings.MEDIA_ROOT[:-1] + molfile.id_files.filepath): #Sometimes molecule files is not created
            intext=open(settings.MEDIA_ROOT[:-1] + molfile.id_files.filepath,'r')
            string=intext.read()
            molec_dic['sdf']=string
        else: # To avoid error of file not found
            molec_dic['sdf']=""
    for match in DyndbReferencesMolecule.objects.select_related('id_references').filter(id_molecule=molecule_id):
        ref={'doi':match.id_references.doi,'title':match.id_references.title,'authors':match.id_references.authors,'url':match.id_references.url,'journal':match.id_references.journal_press,'issue':match.id_references.issue,'pub_year':match.id_references.pub_year,'volume':match.id_references.volume}
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        molec_dic['references'].append(ref)  
    return molec_dic

@user_passes_test_args(is_published_or_submission_owner)
def query_molecule(request, molecule_id,incall=False):
    '''Returns information about the given molecule_id. If incall is True, it returns a simple dictionary, otherwise, an http response is returned. '''
    molec_dic=search_molecule(molecule_id)
    if type(molec_dic)=='str':
        raise Http404(molec_dic)
    return render(request, 'dynadb/molecule_query_result.html',{'answer':molec_dic})
    
@user_passes_test_args(is_published_or_submission_owner)
def query_molecule_sdf(request, molecule_id):
    '''Gets the sdf file of the given molecule_id '''
    molfilesurl = DyndbFilesMolecule.objects.filter(id_molecule=molecule_id,type=0).values_list('id_files__url',flat=True) #MAKE SURE ONLY ONE FILE IS POSSIBLE
    if len(molfilesurl) == 1:
        molfileurl = molfilesurl[0]
        return HttpResponseRedirect(molfileurl) 
    elif len(molfilesurl) > 1:
        raise RuntimeError("Molecule ID:%d has more than one SDF file." % (molecule_id))
    else:
        return HttpResponseNotFound()
    return response

def search_compound(compound_id):
    comp_dic=dict()
    comp_dic['link_2_molecule']=list()
    comp_dic['references']=list()
    comp_dic['othernames']=list()
    for oname in DyndbOtherCompoundNames.objects.filter(id_compound=compound_id):
        comp_dic['othernames'].append(oname.other_names)
    try:
        comp_obj=DyndbCompound.objects.select_related('std_id_molecule').get(pk=compound_id)
    except ObjectDoesNotExist:
        return 'That compound does not exist.'
    except:
        return 'Something went wrong.'

    comp_dic['name']=comp_obj.name
    comp_dic['iupac_name']=comp_obj.iupac_name
    comp_dic['pubchem_cid']=comp_obj.pubchem_cid
    comp_dic['chemblid']=comp_obj.chemblid
    comp_dic['sinchi']=comp_obj.sinchi
    comp_dic['sinchikey']=comp_obj.sinchikey
    comp_dic['imagelink']=get_imagepath(compound_id,'compound')
    comp_dic['related_mol_images']=[]
    comp_dic['myid']=comp_obj.std_id_molecule.id
    for molecule in DyndbMolecule.objects.filter(id_compound=compound_id):
        comp_dic['link_2_molecule'].append(molecule.id)
        comp_dic['related_mol_images'].append([molecule.id,get_imagepath(molecule.id,'molecule')])
    for match in DyndbReferencesCompound.objects.select_related('id_references').filter(id_compound=compound_id):
        if match.id_references.url is not None:
            url_pubchem=match.id_references.url
            url_pubchem=url_pubchem.replace('[compound id]',str(comp_dic['pubchem_cid']))
        else:
            url_pubchem=''
        if match.id_references.title is not None:
            title=match.id_references.title 
            title=title.replace('Compound data comes from Pubchem','Data for this compound was obtained from the PubChem database')
        else:
            title=''
        full_ref=''
        if match.id_references.authors is not None and len(match.id_references.authors)>0:
            full_ref+=match.id_references.authors+'. '
        if len(title)>0:
            full_ref+='<i>'+title+'</i>. '
        if match.id_references.doi is not None and len(match.id_references.doi)>0:
            full_ref+='DOI: '+match.id_references.doi+'. '
        if len(url_pubchem)>0:
            full_ref+='Available in: <a href='+url_pubchem+'>'+url_pubchem+'</a>. '
        comp_dic['references'].append(full_ref)  
    return comp_dic

@user_passes_test_args(is_published_or_submission_owner)
def query_compound(request,compound_id):
    '''Returns information about the given compound_id. If incall is True, it will return a dictionary, otherwise, it returns an Http REsponse '''
    comp_dic=search_compound(compound_id)
    if type(comp_dic)=='str':
        raise Http404(comp_dic)
    return render(request, 'dynadb/compound_query_result.html',{'answer':comp_dic})

def search_complex(complex_id):
    plist=list()
    clistorto=list()
    clistalo=list()
    model_list=list()
    comdic=dict()
    try:
        for cprotein in DyndbComplexProtein.objects.select_related('id_protein').filter(id_complex_exp=complex_id).values('id_protein__id','id_protein__name','id_protein__id_uniprot_species__scientific_name'): 
            plist.append([cprotein['id_protein__id'], cprotein['id_protein__name'],cprotein['id_protein__id_uniprot_species__scientific_name']])
    except ObjectDoesNotExist:
        return 'That complex experiment does not exist.'
    except:
        return 'Something went wrong.'
    q = DyndbComplexExp.objects.filter(pk=complex_id)
    q = q.annotate(model_id=F('dyndbcomplexmolecule__dyndbmodel__id'))
    q = q.values('id','model_id')
    for row in q:
        if row['model_id'] is not None:
            tmpmolecule=[]
            qq=DyndbModel.objects.filter(pk=row['model_id'])
            qq=qq.annotate(molecule_something= F('id_complex_molecule__dyndbcomplexmoleculemolecule__id_molecule__id') )
            qq=qq.values('molecule_something')
            for row2 in qq:
                if row2['molecule_something'] is not None:
                    tmpmolecule.append(row2['molecule_something'])
            #print([row['model_id'],tmpmolecule])
            model_list.append([row['model_id'],tmpmolecule])   
    for ccompound in DyndbComplexCompound.objects.filter(id_complex_exp=complex_id):
        imagelink=get_imagepath(ccompound.id_compound.id,'compound')
        if ccompound.type==0:
            clistorto.append([ccompound.id_compound.id,imagelink])
        else:
            clistalo.append([ccompound.id_compound.id,imagelink])
    q = DyndbComplexExp.objects.filter(pk=complex_id)
    q = q.annotate(ec_fifty_val=F('dyndbexpinteractiondata__dyndbefficacy__id'))
    q = q.annotate(binding_val=F('dyndbexpinteractiondata__dyndbbinding__id'))
    q = q.annotate(references=F('dyndbexpinteractiondata__dyndbreferencesexpinteractiondata__id_references__id'))
    q = q.annotate(inhi_val=F('dyndbexpinteractiondata__dyndbinhibition__id'))
    q = q.values('ec_fifty_val','binding_val','inhi_val','references')
    efflist=[]
    bindlist=[]
    inhilist=[]
    inhibition=dict()
    efficacy=dict()
    binding=dict()
    reference_list=[]
    references=dict()
    for row in q: #warning: one cexp can have more than one binding affinity value (one from bindingdb and other from iuphar)
        if row['ec_fifty_val'] is not None:
            efficacyrow=DyndbEfficacy.objects.get(pk=row['ec_fifty_val'])
            assay_type=str(efficacyrow.type==3).replace('True','IC50').replace('False','EC50')
            if 'iuphar' in efficacyrow.description:
                description=str(efficacyrow.description.split('_')[1])
                description='http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId='+description
                efflist.append([efficacyrow.rvalue,efficacyrow.units,description,'IUPHAR',assay_type])
            else:
                description='https://www.bindingdb.org/jsp/dbsearch/Summary_ki.jsp?reactant_set_id='+efficacyrow.description+'&energyterm=kJ%2Fmole&kiunit=nM&icunit=nM'
                efflist.append([efficacyrow.rvalue,efficacyrow.units,description,'BindingDB',assay_type])
        if row['binding_val'] is not None:
            bindrow=DyndbBinding.objects.get(pk=row['binding_val'])
            if 'iuphar' in bindrow.description: 
                description=str(bindrow.description.split('_')[1])
                description='http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId='+description
                bindlist.append([bindrow.rvalue,bindrow.units,description,'IUPHAR'])
            else:
                description='https://www.bindingdb.org/jsp/dbsearch/Summary_ki.jsp?reactant_set_id='+bindrow.description+'&energyterm=kJ%2Fmole&kiunit=nM&icunit=nM'
                bindlist.append([bindrow.rvalue,bindrow.units,description,'BindingDB'])
        if row['inhi_val'] is not None:
            inhirow=DyndbInhibition.objects.get(pk=row['inhi_val'])
            if 'iuphar' in inhirow.description: 
                description=str(inhirow.description.split('_')[1])
                description='http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId='+description
                inhilist.append([inhirow.rvalue,inhirow.units,description,'IUPHAR'])
            else:
                description='https://www.bindingdb.org/jsp/dbsearch/Summary_ki.jsp?reactant_set_id='+inhirow.description+'&energyterm=kJ%2Fmole&kiunit=nM&icunit=nM'
                inhilist.append([inhirow.rvalue,inhirow.units,description,'BindingDB'])
        if row['references'] is not None:
            references=dict()
            refrow=DyndbReferences.objects.get(pk=row['references'])
            references['url']=refrow.url
            references['journal']=refrow.journal_press          
            references['volume']=refrow.volume
            references['issue']=refrow.issue
            references['doi']=refrow.doi           
            references['pmid']=refrow.pmid
            references['authors']=refrow.authors
            references['title']=refrow.title
            references['pub_year']=refrow.pub_year
            for keys in references:
                if references[keys] is None:
                    references[keys]=''
            reference_list.append(references)
    comdic={'proteins':plist,'compoundsorto': clistorto,'compoundsalo': clistalo, 'models':model_list, 'reference':reference_list,'efflist':efflist,'bindlist':bindlist,'inhilist':inhilist}
    return comdic

@user_passes_test_args(is_published_or_submission_owner)
def query_complex(request, complex_id):
    '''Returns information about the given complex_id. If incall is True, it will return a dictionary, otherwise, it returns an Http REsponse '''
    comdic=search_complex(complex_id)
    if type(comdic)=='str':
        raise Http404(comdic)
    return render(request, 'dynadb/complex_query_result.html',{'answer':comdic})

def search_model(model_id):
    model_dic=dict()
    numbertostring={0:'Apomorfic (no ligands)',1:'Complex Structure (proteins and ligands)'}
    #model_dic['description']=DyndbModel.objects.get(pk=model_id).description #NOT WORKING BECAUSE OF MISSING INFOMRATION
    try:
        modelobj=DyndbModel.objects.select_related('id_protein','id_complex_molecule').get(pk=model_id)
    except ObjectDoesNotExist:
        return 'That model does not exist.'
    except:
        return 'Something went wrong.'
    model_dic['pdbid']=modelobj.pdbid
    model_dic['type']=numbertostring[modelobj.type]
    model_dic['link2protein']=list()
    model_dic['ortoligands']=list()
    model_dic['aloligands']=list()
    model_dic['references']=list()
    model_dic['components']=list()
    model_dic['dynamics']=list()
    model_dic['my_id']=model_id
    try:
        model_dic['complex']=DyndbModel.objects.select_related('id_complex_molecule__id_complex_exp').get(pk=model_id).id_complex_molecule.id_complex_exp.id
    except:
        model_dic['complex']=None
    try: #if it is apomorfic
        model_dic['link2protein'].append([modelobj.id_protein.id, search_protein(modelobj.id_protein.id)['Protein_name'] ])
    except:
        q = DyndbModel.objects.filter(pk=model_id)
        q = q.annotate(protein_id=F('id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__id'))
        q = q.values('id', 'protein_id')
        for row in q:
            if row['protein_id'] not in model_dic['link2protein']:
                model_dic['link2protein'].append([row['protein_id'],search_protein(row['protein_id'])['Protein_name'] ])
    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=model_id):
        model_dic['components'].append([match.id_molecule.id, search_molecule(match.id_molecule.id)['imagelink'],match.id_molecule.id_compound.name, match.type ])
    for match in DyndbDynamics.objects.filter(id_model=model_id):
        model_dic['dynamics'].append(match.id)
    if modelobj.id_complex_molecule is not None:
        cmol_id=modelobj.id_complex_molecule.id
        for match in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=cmol_id):
            if match.type==0:
                model_dic['ortoligands'].append([match.id_molecule.id,search_molecule(match.id_molecule.id)['imagelink']])
            else:
                model_dic['aloligands'].append([match.id_molecule.id,search_molecule(match.id_molecule.id)['imagelink']])
    for match in DyndbReferencesModel.objects.select_related('id_references').filter(id_model=model_id):
        ref={'doi':match.id_references.doi,'title':match.id_references.title,'authors':match.id_references.authors,'url':match.id_references.url,'journal':match.id_references.journal_press,'issue':match.id_references.issue,'pub_year':match.id_references.pub_year,'volume':match.id_references.volume}
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        model_dic['references'].append(ref)  
    model_dic['molecules_string']='%$!'.join([str(int(i[0])) for i in model_dic['components'] if i[3]!=0])
    model_dic['molecules_names']='%$!'.join([str(i[2]) for i in model_dic['components'] if i[3]!=0])
    return model_dic

@user_passes_test_args(is_published_or_submission_owner)
def query_model(request,model_id):
    '''Returns information about the given model_id. If incall is True, it will return a dictionary, otherwise, it returns an Http Response '''
    model_dic=search_model(model_id)
    if type(model_dic)=='str':
        raise Http404('Oops.This model does not exist')
    return render(request, 'dynadb/model_query_result.html',{'answer':model_dic})

def obtain_domain_url(request):
    current_host = request.get_host()
    domain=current_host.rsplit(':',1)[0]
    if request.is_secure():
        protocol = 'https'
    else:
        protocol = 'http'
    if hasattr(settings, 'MDSRV_PORT'):
        port = settings.MDSRV_PORT
    else:
        port = 80
    if hasattr(settings, 'MDSRV_URL'):
        mdsrv_url = settings.MDSRV_URL.strip()
        if mdsrv_url.find('/') == len(mdsrv_url) - 1:
           mdsrv_url = mdsrv_url[:-1]
    else:
        mdsrv_url = protocol+'://'+domain+':'+str(port)
    return(mdsrv_url)

def obtain_dyn_files(paths_dict):
    """Given a list of files related to a dynamic, separates them in structure files and trajectory files."""
    structure_file=""
    structure_name=""
    traj_list=[]
    compString='('+ settings.MEDIA_ROOT[:-1] +')(.*)'
    p=re.compile(compString)
    p2=re.compile("[\.\w]*$")
    for f_id , path in paths_dict.items():
        myfile=p.search(settings.MEDIA_ROOT[:-1] + path).group(2)
        myfile_name=p2.search(path).group()
        if myfile_name.endswith(".pdb"): #, ".ent", ".mmcif", ".cif", ".mcif", ".gro", ".sdf", ".mol2"))
            structure_file=myfile
            structure_file_id=f_id
            structure_name=myfile_name
        elif myfile_name.endswith((".xtc", ".trr", ".netcdf", ".dcd")):
            traj_list.append((myfile, myfile_name, f_id))
    print(traj_list)
    return (structure_file,structure_file_id,structure_name, traj_list)

def assign_seq_pdb(pdb_name,dynamics_id,dynprot_obj,seq_pdb,pdb_chain_li):
    chains_taken = set()
    prot_obj=dynprot_obj.receptor_id_protein
    dynprot_id=dynprot_obj.id
    seq=DyndbProteinSequence.objects.get(id_protein=dynprot_id).sequence
    gpcr_num_found=False
    if prot_obj is not None:
        gen_num_res=obtain_gen_numbering(dynamics_id, dynprot_obj,prot_obj)
        if len(gen_num_res) > 2:
            (numbers, num_scheme, db_seq, current_class) = gen_num_res
            pos_gnum = numbers[current_class]
            gpcr_num_found=True
    for chain_name in pdb_chain_li:
        checkpdb_res=checkpdb_ngl(pdb_name, segid="",start=-1,stop=9999999999999999999, chain=chain_name)
        if isinstance(checkpdb_res, tuple):
            tablepdb,pdb_sequence,hexflag=checkpdb_res
            result=matchpdbfa_ngl(seq,pdb_sequence, tablepdb, hexflag)
            if isinstance(result, list):
                if chain_name not in chains_taken:
                    chains_taken.add(chain_name)
                    for pos in result:
                        if pos[0] != "-": #Consider only num in the pdb
                            db_pos=pos[1][1]
                            if db_pos:
                                this_gnum=""
                                if gpcr_num_found:
                                    this_gnum = pos_gnum[db_pos][1]
                                    if this_gnum:
                                        (chain_num,bw,gpcrdb)=re.split('\.|x', this_gnum)
                                        this_gnum=chain_num+"x"+gpcrdb
                                seq_pdb[db_pos]=[pos[0][1],chain_name,this_gnum]
    return (seq_pdb,chains_taken)

def get_act_state(pdbid):
    pdbid=pdbid.upper()
    if "." in pdbid:
        pdbid=pdbid.split(".")[0]
    state=""
    if pdbid in pdb_state:
        state=pdb_state[pdbid]
    return state

def get_nonlig_comp_info(match,moltype):
    mol_id=match.id_molecule.id
    mol_name=match.id_molecule.id_compound.name
    if not mol_name.isupper():
        mol_name=mol_name.capitalize()
    show_img=True
    mol_chem_name=""
    img_path=search_molecule(match.id_molecule.id)['imagelink']
    if moltype==0: #ions
        show_img=False
        mol_chem_smiles=match.id_molecule.smiles
        mol_chem_name=re.sub("\[|\]","",mol_chem_smiles)
        mol_chem_name=mol_chem_name.replace("+","<sup>+</sup>").replace("-","<sup>-</sup>")
    elif moltype==3:#water
        show_img=False
        mol_chem_name="H<sub>2</sub>O"
    numbmol=match.numberofmol
    candidatecomp=[mol_id,img_path,mol_name,moltype,show_img,mol_chem_name,numbmol]
    return candidatecomp

def extract_all_nonlig_info(dynamics_id):
    membcomp={}
    ioncomp={}
    totallipidmol=0
    totalwatermol=0
    link_2_molecules_dict={}
    ligmolid_to_nummol={}
    for match in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=dynamics_id):
        moltype=match.type
        candidatecomp=get_nonlig_comp_info(match,moltype)
        #dyna_dic['link_2_molecules'].append(candidatecomp)
        molid=candidatecomp[0]
        link_2_molecules_dict[molid]=candidatecomp
        num_mol=candidatecomp[6]
        if moltype==1: 
            molid=match.id_molecule.id
            ligmolid_to_nummol[molid]=match.numberofmol
        if not num_mol:
            num_mol=0
        if moltype==3:
            totalwatermol+=num_mol
        if moltype==2:
            membcomp[match.resname]=num_mol
            totallipidmol+=num_mol
        if moltype==0:
            ioncomp[candidatecomp[2]]=num_mol
    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id):
        moltype=match.type
        candidatecomp=get_nonlig_comp_info(match,moltype)
        molid=candidatecomp[0]
        num_mol=candidatecomp[6]
        if molid not in link_2_molecules_dict:
            link_2_molecules_dict[molid]=candidatecomp
        if moltype==1: #we don't take ligands, only save the num of mol
            molid=match.id_molecule.id
            if molid not in ligmolid_to_nummol:
                ligmolid_to_nummol[molid]=match.numberofmol
        if moltype==2:
            numlipmol=num_mol
            if not numlipmol:
                numlipmol=0
            membcompresname=match.resname
            if membcompresname not in membcomp:
                membcomp[membcompresname]=numlipmol
                totallipidmol+=numlipmol
        if moltype==0:
            ionname=candidatecomp[2]
            if ionname not in ioncomp:
                ioncomp[ionname]=num_mol
            link_2_molecules_dict.values()
    allmolinfo=[]       
    for molinfo in link_2_molecules_dict.values():
        nummols=molinfo[6]
        if not nummols:
            molinfo[6]=""
            allmolinfo.append(molinfo)
            continue
        if nummols==1:
            nummols_s="%i molecule" % nummols
        else:
            nummols_s="%i molecules" % nummols
        molinfo[6]=nummols_s
        allmolinfo.append(molinfo)
    if int(dynamics_id)==7:
        membcomp["CHL1"]=112
        totallipidmol+=112
    if len(membcomp)>1:
        finmemcompli=[]
        for lipres,lipnum in membcomp.items():
            percentlipidmol=(lipnum/totallipidmol)*100
            lipiddata="%s (%.1f%%)" % (lipres,percentlipidmol)
            finmemcompli.append(lipiddata)
        finmemcomp=(", ").join(finmemcompli)
    elif len(membcomp)==1:
        finmemcomp=list(membcomp.keys())[0]
    else:
        finmemcomp=""
    totalwatervol=totalwatermol/constants.N_A*18/1000 #1 mol H2O=num_avogadro molecules H2O; 18g H2O=1 mol H2O; 1L H2O=1000g H2O
    ion_fin_l=[]
    if totalwatervol:
        for ion_name,ion_num in ioncomp.items():
            ion_conc=((ion_num/constants.N_A)/totalwatervol)*1000
            ion_fin_l.append("%s (%i mM)" % (ion_name,round(ion_conc)))
    else:
        ion_fin_l=ioncomp.keys()
    finioncomp=", ".join(ion_fin_l)
    return (finmemcomp,finioncomp,allmolinfo,ligmolid_to_nummol)

def extract_mutations(mutation_li,seq_pdb):
    prot_mut_li_pre=[]
    insertion_num=0
    for (pos,fromaa,toaa) in sorted(mutation_li,key=lambda x:x[0]):
        if toaa=="-":
            insertion_num+=1
        correctedpos=pos - insertion_num
        if correctedpos <=0:
            continue
        if correctedpos not in seq_pdb:
            continue
        if seq_pdb[correctedpos][2]:
            pos_gpcrnum=seq_pdb[correctedpos][2]
        else:
            pos_gpcrnum="-"
        pos_resid=seq_pdb[correctedpos][0]
        toappend=(correctedpos,fromaa,toaa,pos_gpcrnum,pos_resid)
        prot_mut_li_pre.append(toappend)
    #filter out long deletions without GPCR num - likely due to loop segments not simulated rather than genetic mutations 
    continuous_del=set()
    to_remove=set()
    previous_el=(None,None,None,None)
    for i,(pos,fromaa,toaa,gpcrnum,pos_resid) in enumerate(prot_mut_li_pre):
        if gpcrnum == "-" and toaa=="-":
            if pos == previous_el[0]:
                continuous_del.add(i-1)
                continuous_del.add(i)
                continue
        if len(continuous_del)>4:
            to_remove=to_remove.union(continuous_del)
        continuous_del=set()
        previous_el=(pos,fromaa,toaa,gpcrnum)
    to_remove=to_remove.union(continuous_del)
    prot_mut_li=[]
    for i,element in enumerate(prot_mut_li_pre):
        if i not in to_remove:
            prot_mut_li.append(element)
    return prot_mut_li
    
@user_passes_test_args(is_published_or_submission_owner)
def query_dynamics(request,dynamics_id):
    '''Returns information about the given dynamics_id.Returns an Http Response '''
    mdsrv_url=obtain_domain_url(request)
    dynfiles=DyndbFilesDynamics.objects.prefetch_related("id_files").filter(id_dynamics=dynamics_id)
    paths_dict={}
    for e in dynfiles:
        paths_dict[e.id_files.id]=e.id_files.filepath
    (structure_file,structure_file_id,structure_name, traj_list)=obtain_dyn_files(paths_dict)
    traj_displayed=""
    if len(traj_list)>0:
        traj_displayed=traj_list[0][0]
    dyna_dic=dict()
    try:
        dynaobj=DyndbDynamics.objects.select_related('id_dynamics_solvent_types','id_dynamics_membrane_types').get(pk=dynamics_id)
    except ObjectDoesNotExist:
        raise Http404('Oops. That dynamics does not exist')
    except:
        raise
    user=User.objects.get(dyndbsubmission__dyndbdynamics=dynamics_id)
    if int(dynamics_id) in range(4,11):
        author="GPCR drug discovery group (Pompeu Fabra University)"
    elif user.id in {1, 3, 5, 12, 14}:
        author="GPCRmd community"
    else:
        if DyndbDynamics.objects.get(id=dynamics_id).is_published:
            author=user.first_name + " "+ user.last_name+", "+user.institution
        else:
            author=False
    dyna_dic["author"]=author
    dyna_dic['nglviewer_id']=dynamics_id
    dyna_dic['atom_num']=dynaobj.atom_num
    dyna_dic['link_2_molecules']=list()
    dyna_dic['files']={"struc_files":list(), "param_files":list()}
    dyna_dic['references']=list()
    dyna_dic['related']=list()
    dyna_dic['soft']=dynaobj.software
    dyna_dic['softv']=dynaobj.sversion
    dyna_dic['forcefield']=dynaobj.ff
    dyna_dic['forcefieldv']=dynaobj.ffversion
    dyna_dic['link_2_model']=dynaobj.id_model.id
    dyna_dic['model_name']=dynaobj.id_model.name.capitalize()
    dyna_dic['description']=dynaobj.description
    dyna_dic['timestep']=dynaobj.timestep
    dyna_dic['delta']=dynaobj.delta
    dyna_dic['solventtype']=dynaobj.id_dynamics_solvent_types.type_name
    dyna_dic['membranetype']=dynaobj.id_dynamics_membrane_types.type_name
    dyna_dic['ortoligands']=list()
    dyna_dic['aloligands']=list()
    dyna_dic['link2protein']=list()
    dyna_dic['expdatabind']=''
    dyna_dic['expdataeff']=''
    dyna_dic['expdatainhi']=''
    pdbid=dynaobj.id_model.pdbid
    dyna_dic["pdbid"]=pdbid
    dyna_dic["mutation_dict"]={}
    dyna_dic["act_state"]=get_act_state(pdbid)
    try:
        dyna_dic['link_2_complex']=dynaobj.id_model.id_complex_molecule.id_complex_exp.id
        expdata=search_complex(dyna_dic['link_2_complex'])
        dyna_dic['expdatabind']=expdata['bindlist']
        dyna_dic['expdataeff']=expdata['efflist']
        dyna_dic['expdatainhi']=expdata['inhilist']
    except:
        dyna_dic['link_2_complex']=''
    dyna_dic['mdsrv_url'] = mdsrv_url
    dyna_dic['structure_file'] = structure_file
    dyna_dic['traj_file'] = traj_displayed

    (finmemcomp,finioncomp,allmolinfo,ligmolid_to_nummol)=extract_all_nonlig_info(dynamics_id)
    number_of_mols=[[e[2], e[6].split(" ")[0] ] for e in allmolinfo]
    dyna_dic['link_2_molecules']=allmolinfo 
    dyna_dic['membcomp']=finmemcomp
    dyna_dic['ioncomp']=finioncomp
    cmolid=dynaobj.id_model.id_complex_molecule
    if cmolid is not None:
        cmol_id=cmolid.id
        for match in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=cmol_id):
            molname=match.id_molecule.id_compound.name.capitalize()
            mol_id=match.id_molecule.id
            num_of_mol=ligmolid_to_nummol[match.id_molecule_id]
            if num_of_mol==1:
                num_of_mol_s="%s molecule" % num_of_mol
            else:
                num_of_mol_s="%s molecules" % num_of_mol
            if {m.type for m in  DyndbModelComponents.objects.filter(id_molecule=mol_id)} == {0}:
                continue # Do not include ions
            resname=list(set([r.resname for r in DyndbDynamicsComponents.objects.filter(id_molecule=mol_id)]))[0]
            if match.type==0:
                dyna_dic['ortoligands'].append([mol_id,search_molecule(match.id_molecule.id)['imagelink'],resname,molname,num_of_mol_s])
                i=0
                while i < len(dyna_dic['link_2_molecules']):
                    if dyna_dic['link_2_molecules'][i][0]==mol_id:
                        dyna_dic['link_2_molecules'][i][2]+= " (orthosteric lig.)"
                    i+=1
            else:
                dyna_dic['aloligands'].append([mol_id,search_molecule(match.id_molecule.id)['imagelink'],resname,molname,num_of_mol_s])
                i=0
                while i < len(dyna_dic['link_2_molecules']):
                    if dyna_dic['link_2_molecules'][i][0]==mol_id:
                        dyna_dic['link_2_molecules'][i][2]+= " (allosteric lig.)"
                    i+=1

    for match in DyndbRelatedDynamicsDynamics.objects.select_related('id_related_dynamics__id_dynamics').filter(id_dynamics=dynamics_id):
        dyna_dic['related'].append(match.id_related_dynamics.id_dynamics.id)

    prot_muts={}
    prot_li=[]
    dynprot_id_list = []

    dynmodel_obj=dynaobj.id_model
    
    pdb_name=os.path.join(settings.MEDIA_ROOT[:-1],structure_file)
    pdb_chain_li=obtain_prot_chains(pdb_name)
    seq_pdb={}
    # check if it is apomorfic
    dynprot_obj=dynmodel_obj.id_protein
    if dynprot_obj is not None:
        dynprot_li_all=[dynprot_obj]
    else:
        #if it is a complex
        dynprot_li_all=DyndbProtein.objects.filter(dyndbcomplexprotein__id_complex_exp__dyndbcomplexmolecule=dynmodel_obj.id_complex_molecule.id)
    number_of_prots={}
    for dynprot_obj in dynprot_li_all:
        dynprot_id=dynprot_obj.id
        search_prot_res=search_protein(dynprot_id)
        prot_name=search_prot_res['Protein_name']
        if prot_name not in number_of_prots:
            number_of_prots[prot_name]=0
        number_of_prots[prot_name]+=1
        if dynprot_id not in dynprot_id_list:
            prot_li.append([dynprot_obj,dynprot_obj.receptor_id_protein])
            is_prot_lig=not dynprot_obj.receptor_id_protein
            prot_sel_s= {":%s" % res.chain.upper() for res in DyndbModeledResidues.objects.filter(id_protein=dynprot_obj.id)}
            prot_sel=" or ".join(prot_sel_s)
            dynprot_id_list.append(dynprot_id)
            dyna_dic['link2protein'].append([dynprot_id,prot_name,is_prot_lig , prot_sel ])
            seq_pdb,chains_taken=assign_seq_pdb(pdb_name,dynamics_id,dynprot_obj,seq_pdb,pdb_chain_li)
            is_mutated=search_prot_res["is_mutated"]
            if is_mutated:
                #prot_mut_li=[(pos,fromaa,toaa,seq_pdb[pos][2]) if seq_pdb[pos][2] else (pos,fromaa,toaa,"-") for (pos,fromaa,toaa) in search_prot_res["mutations"]]
                mutation_li=search_prot_res["mutations"]
                prot_mut_li=extract_mutations(mutation_li,seq_pdb)
                prot_muts[dynprot_id]=prot_mut_li
        else:
            raise RuntimeError("Protein %d in molecular complex %d is duplicated." % (dynprot_id,dynmodel_obj.id_complex_molecule.id))

    number_of_mols += [[k,v] for k,v in number_of_prots.items()]
    try:
        number_of_mols=sorted( number_of_mols, key=lambda x: int(x[1]) , reverse=True)
    except:
           number_of_mols=number_of_mols 
    dyna_dic["number_of_mols"]=number_of_mols
    link2ligandprotein=[ [e[0],e[1],e[3],number_of_prots[e[1]]] for e in dyna_dic['link2protein'] if e[2]]
    for e in link2ligandprotein:
        nummols=e[3]
        if nummols==1:
            nummols_s="%i molecule" % nummols
        else:
            nummols_s="%i molecules" % nummols
        e[3]=nummols_s
    dyna_dic['link2ligandprotein']=link2ligandprotein
    if not (dyna_dic['link2ligandprotein'] or dyna_dic['ortoligands'] or dyna_dic['aloligands']):
        dyna_dic['model_name']+=" (apoform)"
    dyna_dic["mutation_dict"]=prot_muts
    mut_sel_li=[]
    for prot_id,mut_li in prot_muts.items():
        for (res,fromaa,toaa,gnum,mut_resid) in mut_li:
            # Find chain of this mutation
            chain = DyndbModeledResidues.objects.filter(id_protein=prot_id)[0].chain
            mut_sel_li.append("(:%s and %s)" % (chain,mut_resid))
    mut_sel=" or ".join(mut_sel_li)
    dyna_dic["mut_sel"]=mut_sel

    for match in DyndbReferencesDynamics.objects.select_related('id_references').filter(id_dynamics=dynamics_id):
        ref={'doi':match.id_references.doi,'title':match.id_references.title,'authors':match.id_references.authors,'url':match.id_references.url,'journal':match.id_references.journal_press,'issue':match.id_references.issue,'pub_year':match.id_references.pub_year,'volume':match.id_references.volume}
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        dyna_dic['references'].append(ref)
    filestraj=dict()
    num_replicates=0
    accum_framenum=0
    for match in DyndbFilesDynamics.objects.select_related('id_files').filter(id_dynamics=dynamics_id):
        typeobj=match.id_files.id_file_types
        if typeobj.is_parameter or typeobj.is_anytype:
            myfilename=match.id_files.filename
            print(myfilename)
            btn_text=""
            if "prm" in myfilename:
                btn_txt="Parameters file (ID: %s)" % match.id_files.id
            elif "prt" in myfilename:
                btn_txt="Protocol file (ID: %s)" % match.id_files.id
            else:
                btn_txt="Others file (ID: %s)" % match.id_files.id
            dyna_dic['files']["param_files"].append( ( match.id_files.filepath.replace("/var/www/","/dynadb/") , match.id_files.filename , btn_txt) ) 
        else:
            btn_txt=""
            typeobj=match.id_files.id_file_types
            if (typeobj.is_model):
                btn_txt="Model file (ID: %s)" % match.id_files.id
            elif typeobj.is_topology:
                btn_txt="Topology file (ID: %s)" % match.id_files.id
            elif typeobj.is_trajectory:
                btn_txt="Trajectory file (ID: %s)" % match.id_files.id
                num_replicates+=1
                if match.framenum:
                    accum_framenum+=match.framenum
            else:
                btn_txt="File (ID: %s)" % match.id_files.id

            strucfile_info=(match.id_files.filepath.replace("/var/www/","/dynadb/") , match.id_files.filename ,btn_txt)
            dyna_dic['files']["struc_files"].append( strucfile_info ) 
    accum_sim_time=(accum_framenum*dyna_dic['delta'])/1000
    dyna_dic['accum_sim_time']=accum_sim_time
    dyna_dic['replicates']=num_replicates
    dyna_dic['molecules_string']='%$!'.join([str(int(i[0])) for i in dyna_dic['link_2_molecules'] if i[3]!=0]) #no ions
    dyna_dic['molecules_names']='%$!'.join([str(i[2]) for i in dyna_dic['link_2_molecules'] if i[3]!=0]) #no ions
    dyna_dic['molecules_number']='%$!'.join(["(%s)"%str(i[6]) for i in dyna_dic['link_2_molecules'] if i[3]!=0]) #no ions
    return render(request, 'dynadb/dynamics_query_result.html',{'answer':dyna_dic})
    
@user_passes_test_args(is_published_or_submission_owner)    
def carousel_model_components(request,model_id):
    model_dic=dict()
    model_dic['components']=[]
    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=model_id):
        model_dic['components'].append([match.id_molecule.id, search_molecule(match.id_molecule.id)['imagelink'],match.id_molecule.id_compound.name])    
    return render(request, 'dynadb/model_carousel.html',{'answer':model_dic})
    
@user_passes_test_args(is_published_or_submission_owner)    
def carousel_dynamics_components(request,dynamics_id):
    dyna_dic=dict()
    dyna_dic['link_2_molecules']=[]
    image_name=[]
    link_2_molecules_dict={}
    for match in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=dynamics_id):
        moltype=match.type
        if moltype!=1:#we don't take ligands
            candidatecomp=get_nonlig_comp_info(match,moltype)
            molid=candidatecomp[0]
            link_2_molecules_dict[molid]=candidatecomp
            #dyna_dic['link_2_molecules'].append(candidatecomp)
            image_name.append([match.id_molecule.id_compound.name , search_molecule(match.id_molecule.id)['imagelink']])
    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id):
        moltype=match.type
        if moltype!=1:#we don't take ligands
            candidatecomp=get_nonlig_comp_info(match,moltype)
            molid=candidatecomp[0]
            if molid in link_2_molecules_dict:
                link_2_molecules_dict[molid][6]+=candidatecomp[6]
            else : 
                link_2_molecules_dict[molid]=candidatecomp
                image_name.append([match.id_molecule.id_compound.name,search_molecule(match.id_molecule.id)['imagelink']])
    allmolinfo=[]       
    for molinfo in link_2_molecules_dict.values():
        nummols=molinfo[6]
        if not nummols:
            molinfo[6]=""
            allmolinfo.append(molinfo)
            continue
        if nummols==1:
            nummols_s="%i molecule" % nummols
        else:
            nummols_s="%i molecules" % nummols
        molinfo[6]=nummols_s
        allmolinfo.append(molinfo)
    dyna_dic['link_2_molecules']=allmolinfo 
    dyna_dic['imagetonames']= image_name

    ortholig=[]
    alolig=[]
    cmolid=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id_complex_molecule
    if cmolid is not None:
        cmol_id=cmolid.id
        for match in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=cmol_id):
            if match.type==0:
                ort_mol_id=match.id_molecule.id
                i=0
                while i < len(dyna_dic['link_2_molecules']):
                    if dyna_dic['link_2_molecules'][i][0]==ort_mol_id:
                        dyna_dic['link_2_molecules'][i][2]+= " (orthosteric lig.)"
                    i+=1
            else:
                al_mol_id=match.id_molecule.id
                i=0
                while i < len(dyna_dic['link_2_molecules']):
                    if dyna_dic['link_2_molecules'][i][0]==al_mol_id:
                        dyna_dic['link_2_molecules'][i][2]+= " (allosteric lig.)"
                    i+=1
    return render(request, 'dynadb/dynamics_carousel.html',{'answer':dyna_dic})
    
@textonly_500_handler
@login_required
def protein_get_data_upkb(request, uniprotkbac=None):
    
    KEYS = set(('entry','entry name','organism','length','name','aliases','sequence','isoform','speciesid'))
    if request.method == 'POST' and 'uniprotkbac' in request.POST.keys():
      uniprotkbac = request.POST['uniprotkbac']
      
    if uniprotkbac is not None:
      if valid_uniprotkbac(uniprotkbac):
        if uniprotkbac.find('-') < 0:
          uniprotkbac_noiso = uniprotkbac
          isoform = None
          qPROT=DyndbProtein.objects.filter(uniprotkbac=uniprotkbac,is_mutated=False,id=F('dyndbproteincannonicalprotein__id_cannonical_proteins'))
        else:
          uniprotkbac_noiso,isoform = uniprotkbac.split('-')
          qPROT=DyndbProtein.objects.filter(uniprotkbac=uniprotkbac,isoform=isoform,is_mutated=False)
        if qPROT.exists():
          lqPROT=list(qPROT.values_list('uniprotkbac','isoform','name','dyndbproteinsequence__sequence','id_uniprot_species__scientific_name','id_uniprot_species','id_uniprot_species__code'))[0]
          data={}
          data['GPCRmd']=True
          #Django uses LEFT JOIN, so it always exists. We alo have to check is result is not NULL.
          if qPROT.values('dyndbotherproteinnames__other_names').exists():
            aliases = list(qPROT.values_list('dyndbotherproteinnames__other_names',flat=True))
            if len(aliases) > 0:
              if aliases[0] is not None:
                data['Aliases']=(";").join(aliases)
          if 'Aliases' not in data:
            data['Aliases']=""
          data['Entry'],data['Isoform'],data['Name'],data['Sequence'],data['Org'],data['speciesid'],data['code']=lqPROT  
          data['Organism']=('').join([data['Org'],data['code']])
          response = JsonResponse(data) 
          return response
        data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,accession,organism_name,length,')
        if errdata == dict():
          if data == dict():
            response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain; charset=UTF-8')
            return response
          if data['Entry'] != uniprotkbac_noiso and isoform is not None:
            response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain; charset=UTF-8')
            return response
          data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])
          time.sleep(10)
          namedata,errdata = retreive_protein_names_uniprot(uniprotkbac_noiso)
          
          if errdata == dict():
            name, other_names = get_other_names(namedata)
            data['Name'] = name
            data['Aliases'] = ';'.join(other_names)
            time.sleep(10)
            seqdata,errdata = retreive_fasta_seq_uniprot(uniprotkbac)
            if errdata == dict():
              if seqdata['sequence'] == '':
                seqdata['sequence'] = 'Sequence not available for ' + uniprotkbac+'.'
              data['Sequence'] = seqdata['sequence']
              if uniprotkbac_noiso == uniprotkbac:
                time.sleep(10)
                dataiso,errdata = retreive_isoform_data_uniprot(data['Entry'])
                if errdata == dict():
                  if dataiso == dict():
                    data['Isoform'] = '1'
                  else:
                    data['Isoform'] = dataiso['Displayed'].split('-')[1]
              else:
                data['Isoform'] = isoform
        if 'Error' in errdata.keys():
          if errdata['ErrorType'] == 'HTTPError':
            if errdata['status_code'] == 404 or errdata['status_code'] == 410:
              response = HttpResponseNotFound('No data found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain; charset=UTF-8')
            else:
              response = HttpResponse('Problem downloading from UniProtKB:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason'],status=502,content_type='text/plain; charset=UTF-8')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from UniProtKB:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain; charset=UTF-8')
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain; charset=UTF-8')
          else:
            response = HttpResponse('Cannot connect to UniProt server:\n'+errdata['reason'],status=504,content_type='text/plain; charset=UTF-8')
            
        else:
          datakeys = set([i.lower() for i in data.keys()])
          if datakeys == KEYS:
            data['GPCRmd']=False
            response = JsonResponse(data) 
          else:
            response = HttpResponse('Invalid response from UniProtKB.',status=502,content_type='text/plain; charset=UTF-8')
      else:
        response = HttpResponse('Invalid UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    else:
      response = HttpResponse('Missing UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    return response

def get_uniprot_species_id_and_screen_name(mnemonic):
  speciesqs = DyndbUniprotSpecies.objects.filter(code=mnemonic)
  speciesqs = speciesqs.annotate(screen_name=Concat('scientific_name',V(' ('),'code',V(')'),output_field=TextField()))
  try:
    record = speciesqs.order_by('id')[0]
  except IndexError:
    return None
  except:
    raise
  return (record.pk,record.screen_name)

@textonly_500_handler
def download_specieslist(request):
    """A view that streams a TSV file."""
    COMMENT_BLOCK = '# id = species GPCRmd internal identifier\r\n\
# kingdom = \'A\' archaea;\'B\' bacteria;\'E\' eukaryota;\'V\' viruses and phages;\'O\' Others;\r\n\
# taxon_node = taxonomic node id number in the NCBI taxonomy\r\n\
# scientific_name = official organism name\r\n'
    fieldnames = []
    for field in DyndbUniprotSpecies._meta.get_fields():
      if not field.is_relation:
        if field.name != 'code':
          fieldnames.append(field.name)
    speciesqso = DyndbUniprotSpecies.objects.filter(code=None)
    writer = CsvDictWriterNoFile(fieldnames, dialect='excel-tab',extrasaction='ignore')
    iterator = speciesqso.iterator()
    csvwiterator = CsvDictWriterRowQuerySetIterator(writer,iterator,comment_block=COMMENT_BLOCK)
    response = StreamingHttpResponse(csvwiterator,
                                     content_type="text/tab-separated-values")
    response['Content-Disposition'] = 'attachment; filename="alt_speclist.tsv"'
    return response
    
@textonly_500_handler
def get_specieslist(request):
  """A view that shows an 'screen_name' = scientific_name +' (' + (uniprot_)code + ')' 
  that matches a searched 'term'."""
  LIMIT=50
  code_max_length = DyndbUniprotSpecies._meta.get_field('code').max_length
  sbracketsre1 = re.compile(r'^(.*?) ?\(([A-Za-z0-9]{1,'+str(code_max_length)+r'})$')
  sbracketsre2 = re.compile(r'^(.*?) ?\(([A-Za-z0-9]{'+str(code_max_length)+r'})\)$')
  sbracketsre3 = re.compile(r'^([A-Za-z0-9]{1,'+str(code_max_length)+r'})\)$')
  sbracketsre4 = re.compile(r'^(.*?) \(?$')
  # Remove ' (' and ')' from term and filter scientific_name and code by term.
  term4 = ''
  if request.method == 'GET':
    term = request.GET['term']
  elif request.method == 'POST':
    term = request.POST['term']
  m1 = sbracketsre1.search(term)
  if m1:
    term2 = m1.group(2)
    term3 = m1.group(1)
    speciesqscode = DyndbUniprotSpecies.objects.filter(code__istartswith=term2)
  else:
    m2 = sbracketsre2.search(term)
    if m2:
      term2 = m2.group(2)
      term3 = m2.group(1)
      speciesqscode = DyndbUniprotSpecies.objects.filter(code__iexact=term2)
    else:
      term3 = ''
      m3 = sbracketsre3.search(term)
      if m3:
        term2 = m3.group(1)
        speciesqscode = DyndbUniprotSpecies.objects.filter(code__iendswith=term2)
      else:
        speciesqscode = DyndbUniprotSpecies.objects.filter(code__icontains=term)
        m4 = sbracketsre4.search(term)
        if m4:
          term4 = m4.group(1)
          
  if term3 != '':
    speciesqscode = speciesqscode.filter(scientific_name__iendswith=term3)
  speciesqsname = DyndbUniprotSpecies.objects.filter(scientific_name__icontains=term)
  if term4 != '':
    speciesqsname = speciesqsname | DyndbUniprotSpecies.objects.filter(scientific_name__iendswith=term4)

  # select if 
  speciesqs = speciesqsname | speciesqscode
  
  ## create new field 'screen_name'
  # SELECT CASE 
  # WHEN code IS NULL THEN scientific_name
  #
  # ELSE
  # concatenate(scientific_name,' (',code,')')
  # AS screen_name;
  speciesqs = speciesqs.annotate(screen_name=Case(
    When(code__isnull=True,
         then='scientific_name'),
    default=Concat('scientific_name',V(' ('),'code',V(')'),output_field=TextField()),
    output_field=TextField()))
  speciesqs = speciesqs.order_by('screen_name')[:LIMIT]
  speciesqs = speciesqs.values('id','screen_name')

  datajson = json.dumps(list(speciesqs))

  response = HttpResponse(datajson, content_type="application/json")
  return response

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def submitpost_view(request,submission_id,model_id=1):
    if request.method == 'POST':

        indexl=[]
        for x in list(request.POST.keys()):
            try:
                index=int(x.split('-')[1])
                print(x," ", index)
                if index not in indexl:
                    indexl.append(index)
            except:
                print("NO NO")
                index=0
                if index not in indexl:
                    indexl.append(index)
                pass
        indexl.sort()
       
        response=SMALL_MOLECULEview(request.POST, submission_id)
        return response
    else:
        submission_id=submission_id
        fdbMF = dyndb_Molecule()
        fdbSub = dyndb_Submission_Molecule()
        fdbCF=dyndb_CompoundForm()
        fdbON=dyndb_Other_Compound_Names()
        fdbF = dyndb_Files()
        fdbFM = dyndb_Files_Molecule()
        fdbMM = dyndb_Complex_Molecule_Molecule()
        if model_id==0:
            return render(request,'dynadb/SMALL_MOLECULE.html', {'submission_id' : submission_id})
        else:
            return render(request,'dynadb/SMALL_MOLECULEreuse.html', {'submission_id' : submission_id, 'model_id':model_id})

@textonly_500_handler  
def get_mutations_view(request):
    if request.method == 'POST':
        try:
            fasta = request.POST['alignment']
            refseq = request.POST['sequence']
            if check_fasta(fasta,allow_stop=False):
                return JsonResponse(get_mutations(fasta,refseq),safe=False)
            elif check_fasta(fasta,allow_stop=True):
                raise ParsingError('Translation stop character (*) is not allowed. Please truncate sequence until first stop.')
            else:
                raise ParsingError('Invalid fasta format.')
        except ParsingError as e:
            print(e)
            response = HttpResponse('Parsing error: '+str(e),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
        except:
            raise
        

def obtain_res_coords(pdb_path,res1,res2,pair, pair2): 
    '''res1 is last residue of previous segment, res2 is start of current segment. PAIR is [A,B], pair2 is [PROA,PROB]'''
    res1_coords=[]
    res2_coords=[]
    readpdb=open(settings.MEDIA_ROOT + pdb_path,'r')
    for line in readpdb:
        if line.startswith('ATOM') or line.startswith('HETATM'):
            if ( (pair==None) or (line[21:22].strip()==pair[0]) ) and ((pair2==None) or (line[72:76].strip()==pair2[0]) ):
                if line[22:27].strip() == str(res1):
                    #print('FIRST \n',line)
                    res1_coords.append([line[30:38],line[38:46],line[46:54]])
            if (pair==None or line[21:22].strip()==pair[1] ) and (pair2==None or line[72:76].strip()==pair2[1] ):
                if line[22:27].strip() == str(res2):
                    #print('LAST\n',line)
                    res2_coords.append([line[30:38],line[38:46],line[46:54]])

    return(res1_coords,res2_coords)

def bonds_between_segments2(pdb_path,res1,res2,chain_pair=None,seg_pair=None):
    if seg_pair and chain_pair:
        #print('both again')
        (res1_coords,res2_coords)=obtain_res_coords(pdb_path,res1,res2,chain_pair,seg_pair)

    elif seg_pair:
        #print('only seg again')
        (res1_coords,res2_coords)=obtain_res_coords(pdb_path,res1,res2,None,seg_pair)

    elif chain_pair:
        #print('only chain again')
        (res1_coords,res2_coords)=obtain_res_coords(pdb_path,res1,res2,chain_pair,None)

    coord_pairs=list(itertools.product(np.array(res1_coords),np.array(res2_coords)))
    bond=False
    dist_coo=[]
    for cpair in coord_pairs:
        x1=float(cpair[0][0])
        y1=float(cpair[0][1])
        z1=float(cpair[0][2])
        x2=float(cpair[1][0])
        y2=float(cpair[1][1])
        z2=float(cpair[1][2])
        dist=math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
        dist_coo.append(dist)
        if dist < 2:
            dist_coo.append(dist)
            bond=True
            break
    return(bond)

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def search_top(request,submission_id):
    '''Given a PDB interval, a sequence alignment is performed between the PDB interval sequence and the full sequence of that protein. The position of the two ends of the aligned PDB interval sequence are returned. '''
    if request.method=='POST':
        pstop='undef'
        submission_path = get_file_paths("model",url=False,submission_id=submission_id)
        submission_url = get_file_paths("model",url=True,submission_id=submission_id)
        pdbname = get_file_name_submission("model",submission_id,0,ext="pdb",forceext=False,subtype="pdb")
        pdbname =  os.path.join(submission_path,pdbname)
        bond_list=dict()
        if os.path.isfile(pdbname) is False: 
            return HttpResponse('File not uploaded. Please upload a PDB file',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')

        arrays=request.POST.getlist('bigarray[]')
        #print(arrays)
        counter=0
        resultsdict=dict()
        resultsdict['message']=''
        resultsdict['warningmess']=''
        for array in arrays:
            array=array.split(',') #array is a string with commas.
            prot_id= int(array[0])-1 #int(request.POST.get('id_protein')) #current submission ID. #WARNING! ##CHANGED to array[0]-1 ISMA!!!!
            start=array[3].strip()
            stop=array[4].strip()
            
            try:
                if start == '' or not (start.isdigit()):
                    start = int(array[3],16)
                else:
                    start=int(array[3])
                if stop =='' or not (stop.isdigit()):
                    stop = int(array[4],16)           
                else:
                    stop=int(array[4])
            except ValueError:
                results={'type':'string_error','title':'Missing information or wrong information', 'message':'Missing or incorrect information in the "Res from" or "Res to" fields. Maybe some whitespace?'}
                data = json.dumps(results)
                return HttpResponse('Missing or incorrect information in the "Res from" or "Res to" fields.\nMaybe some whitespace?',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                
                
            
            if start>stop:
                results={'type':'string_error','title':'Missing information or wrong information', 'message':'"Res from" greater than "Res to"'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json') 
            chain=array[1].strip().upper() #avoid whitespace problems
            segid=array[2].strip().upper() #avoid whitespace problems

            try:
                protid=DyndbSubmissionProtein.objects.filter(int_id=prot_id).filter(submission_id=submission_id)[0].protein_id.id
                sequence=DyndbProteinSequence.objects.filter(id_protein=protid)[0].sequence
            except:
                results={'type':'string_error','title':'Range error', 'message':'The protein you have selected does not exist.'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json')  

            res=searchtop(pdbname,sequence, start,stop,chain,segid)
            if isinstance(res,tuple):
                seq_res_from,seq_res_to,warningmess=res
                resultsdict[counter]=[seq_res_from,seq_res_to]
                if len(warningmess)>0:
                    resultsdict['warningmess']=resultsdict['warningmess']+'\n\n -'+warningmess
            elif isinstance(res,str):
                resultsdict['message']=resultsdict['message']+'\n\n -'+res
            if pstop!='undef':
                bonded=False
                if len(chain)>0 and len(segid)>0:
                    bonded=bonds_between_segments2(pdbname,pstop,start,chain_pair=[pchain,chain],seg_pair=[psegid,segid])
                elif len(chain)>0:
                    bonded=bonds_between_segments2(pdbname,pstop,start,chain_pair=[pchain,chain],seg_pair=None)
                elif len(segid)>0:
                    bonded=bonds_between_segments2(pdbname,pstop,start,chain_pair=None,seg_pair=[psegid,segid])

                bond_list[counter]=bonded
            pstop=stop
            pchain=chain
            psegid=segid
            counter+=1
    resultsdict['bonds']=bond_list
    data = json.dumps(resultsdict)
    
    return HttpResponse(data, content_type='application/json')

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def pdbcheck(request,submission_id):
    '''Performs an alignment between the sequence in a PDB interval and an interval in the full protein sequence. Returns a table where the original resids of the PDB are displayed with the resids it should use according to the position of that aminoacid in the alignment. Also creates a new PDB file with the correct resids.'''
    if request.method=='POST': #See pdbcheck.js
        combination_id='submission_id'+submission_id
        sub_id=submission_id
        results=dict()
        submission_path = get_file_paths("model",url=False,submission_id=submission_id)
        submission_url = get_file_paths("model",url=True,submission_id=submission_id)
        pdbname = get_file_name_submission("model",submission_id,0,ext="pdb",forceext=False,subtype="pdb")
        pdbname =  os.path.join(submission_path,pdbname)
        if os.path.isfile(pdbname) is False: 
            return HttpResponse('File not uploaded. Please upload a PDB file',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')

        arrays=request.POST.getlist('bigarray[]')
        
        counter=0
        tuple_error_dict=dict()
        full_run_dict=dict()
        errorflag=2 #initialize with no-error status. 0: error, 1:warning, 2: full run
        for array in arrays:
            array=array.split(',')
            segment_def='Protein: '+str(array[0])+' Start:'+str(array[3])+' Stop: '+str(array[4])+ ' SEGID: '+str(array[2])
            prot_id=array[0]
            chain=array[1].strip().upper()
            segid=array[2].strip().upper()

            for r in range(3,7):
                current_value = array[r].strip()
                if current_value == '' or not current_value.isdigit():
                    try:
                        if r == 3:
                            start = int(current_value,16)
                        elif r == 4 :
                            stop = int(current_value,16)
                        else:
                            raise ValueError
                    except:
                        return HttpResponse('Residue definition "'+str(current_value)+'" is invalid or empty.\n',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                else:
                    if r == 3:
                        start = int(current_value)
                    if r == 4:
                        stop = int(current_value)
            prot_id= int(array[0])-1 #int(array[0]) #OLD: int(request.POST.get('id_protein')) #current submission ID.
            start=int(array[3])
            stop=int(array[4])
            seqstart=int(array[5])
            seqstop=int(array[6])

            if seqstart>seqstop:
                results={'type':'string_error','title':'Range error', 'message':'"Seq Res from" greater than "Seq Res to"'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json')                 
            try:
                protid=DyndbSubmissionProtein.objects.filter(int_id=prot_id).filter(submission_id=sub_id)[0].protein_id.id
                sequence=DyndbProteinSequence.objects.filter(id_protein=protid)[0].sequence
                sequence=sequence[seqstart-1:seqstop]
            except:
                results={'type':'string_error','title':'Range error', 'message':'The protein you have selected does not exist.'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json')  

            if start>stop:
                results={'type':'string_error','title':'Range error', 'message':'"Res from" value is bigger to the "Res to" value'}
                data = json.dumps(results)
                request.session[combination_id] = results
                return HttpResponse(data, content_type='application/json')
            results['segments']=get_number_segments(pdbname)        
            uniquetest=unique(pdbname, chain!='',segid!='')
            if uniquetest is True:
                checkresult=checkpdb(pdbname,segid,start,stop,chain)
                if isinstance(checkresult,tuple):
                    tablepdb,simplified_sequence,hexflag=checkresult
                    guide=matchpdbfa(sequence,simplified_sequence,tablepdb,hexflag,seqstart)
                    if isinstance(guide, list):
                        path_to_repaired=repairpdb(pdbname,guide,segid,start,stop,chain,counter)
                        path_to_repaired=path_to_repaired[path_to_repaired.rfind('/files/'):]
                        path_to_repaired='/dynadb'+path_to_repaired
                        full_run_dict[(segment_def,path_to_repaired)]=guide
                    elif isinstance(guide, tuple):
                        tuple_error_dict[segment_def]=guide
                        if guide[0].startswith('Error'):
                            errorflag=1
                        elif guide[0].startswith('Warning'):
                            errorflag=0
                    else: #PDB has insertions error
                        guide='Error in segment definition: Start:'+ str(start) +' Stop:'+ str(stop) +' Chain:'+ chain +' Segid:'+ segid+'\n'+guide
                        results={'type':'string_error', 'title':'Alignment error in segment definition' ,'errmess':guide,'message':''}
                        request.session[combination_id] = results
                        request.session.modified = True
                        tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                        data = json.dumps(tojson)
                        return HttpResponse(data, content_type='application/json')
                else: #checkpdb has an error
                    results={'type':'string_error','title':'Corrupted resid numbering or missing field in PDB', 'errmess':checkresult} #prints the error resid.
                    request.session[combination_id] = results
                    request.session.modified = True
                    tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                    data = json.dumps(tojson)
                    return HttpResponse(data, content_type='application/json')
            else: #unique test failed
                results={'type':'string_error','title':'Lack of uniqueness','errmess':uniquetest} #says which combination causes the problem
                request.session[combination_id] = results
                request.session.modified = True
                tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                data = json.dumps(tojson)
                return HttpResponse(data, content_type='application/json')

            counter+=1

        if len(full_run_dict)>0 or len(tuple_error_dict)>0:
            results['type']='fullrun'
            results['table']=full_run_dict #finalguide
            results['tuple_errors']=tuple_error_dict #tuple_error_list
            errorcode_to_message={0:'One or more warnings found',1:'One or more errors found', 2: 'All right! PDB segment matches the submited sequence'}
            results['result_header']=errorcode_to_message[errorflag]
        request.session[combination_id] = results
        request.session.modified = True
        tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

    else: #NOT POST, simply display of results in the POP UP window. See pdbcheck.js
        combination_id='submission_id'+submission_id
        fav_color = request.session[combination_id]
        print('\n\nFavColor:,',fav_color)
        if fav_color['type']=='string_error':
            return render(request,'dynadb/string_error.html', {'answer':fav_color})

        elif fav_color['type']=='fullrun':
            return render(request,'dynadb/fullrun.html', {'answer':fav_color})

        else:
            fav_color={'errmess':'Most common causes are: \n -Missing one file\n -Too short interval\n -Very poor alignment\n ','title':'Unknown error'}
            return render(request,'dynadb/string_error.html', {'answer':fav_color})

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def get_submission_molecule_info(request,form_type,submission_id):
    if request.method == 'POST':
        mol_int = request.POST['molecule'].strip()
        if mol_int.isdigit():
            mol_int=int(mol_int)
        else:
            return HttpResponse('Molecule form number '+str(mol_int)+' is invalid or empty.',status=422,reason='Unprocessable Entity')
        if form_type == "model":
            molecule_type_dict = dict(DyndbModelComponents.MOLECULE_TYPE)
            smol_to_comp_type = smol_to_dyncomp_type
        elif form_type == "dynamics":
            molecule_type_dict = dict(DyndbDynamicsComponents.MOLECULE_TYPE)
            smol_to_comp_type = smol_to_dyncomp_type
        q = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=(mol_int-1))
        field_ref = 'molecule_id__id_compound__name'
        if form_type == "model":
            q = q.annotate(namemc=F(field_ref))
            field_name = "namemc"
        elif form_type == "dynamics":
            q = q.annotate(name=F(field_ref))
            field_name = "name"
        
        q = q.values('molecule_id','not_in_model',field_name,'type')
        qresults = list(q)
        if len(qresults) > 0:
            qresults[0]['type'] = smol_to_comp_type[qresults[0]['type']]
            qresults[0]['type_text'] = molecule_type_dict[qresults[0]['type']]
            
            if qresults[0]['not_in_model'] and form_type == "model":
                return HttpResponse('Molecule form number "'+str(mol_int)+'" is defined as no crystal-like.\n'+ \
                'You can change this definition by going back to the Small Molecule form.',status=422,reason='Unprocessable Entity')
            else:
                return JsonResponse(qresults[0])
        else:
            return HttpResponseNotFound('Molecule form number "'+str(mol_int)+'" not found in submission ID:'+str(submission_id))
    
@csrf_exempt
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def upload_model_pdb(request,submission_id):

    #request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,50*1024**2) #Increase size limit
    request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,100*50*1024**2)

    try:
        return _upload_model_pdb(request,submission_id)
    except (RequestBodyTooLarge, FileTooLarge, TooManyFiles) as e:
        return HttpResponse(e.args[0],status=413,reason='Payload Too Large',content_type='text/plain; charset=UTF-8')
    except:
        raise
@csrf_protect
def _upload_model_pdb(request,submission_id):
    pdbfilekey = 'file_source'
    if request.method == 'POST':
        if  pdbfilekey in request.FILES.keys():
            data = dict()
            uploadedfile = request.FILES[pdbfilekey]
            submission_path = get_file_paths("model",url=False,submission_id=submission_id)
            os.makedirs(submission_path,exist_ok=True)
            submission_url = get_file_paths("model",url=True,submission_id=submission_id)
            pdbname = get_file_name_submission("model",submission_id,0,ext="pdb",forceext=False,subtype="pdb")
            pdbfilepath =  os.path.join(submission_path,pdbname)
            data['download_url_pdb'] =  os.path.join(submission_url,pdbname)
            try:
                save_uploadedfile(pdbfilepath,uploadedfile)
                data['msg'] = 'File successfully uploaded.'
                response = JsonResponse(data)
            except:
                os.remove(pdbfilepath)
                response = HttpResponseServerError('Cannot save uploaded file.',content_type='text/plain; charset=UTF-8')
            finally:
                uploadedfile.close()
                return response
            
        else:
            for upload_handler in request.upload_handlers:
                if hasattr(upload_handler,'exception'):
                    if upload_handler.exception is not None:
                        raise upload_handler.exception
            msg = 'No file was selected or cannot find molecule file reference.'
            return HttpResponse(msg,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')

def get_sdf_from_db_by_submission(submission_id,int_ids):
    sdf_mol_file_type = type_inverse_search(DyndbFilesMolecule.filemolec_types,searchkey='Molecule',case_sensitive=False)
    submol = DyndbSubmissionMolecule._meta.db_table
    submol_pk_db_column = DyndbSubmissionMolecule._meta.pk.get_attname_column()[1]
    int_id_db_column = DyndbSubmissionMolecule._meta.get_field("int_id").get_attname_column()[1]
    molecule_id_db_column = DyndbSubmissionMolecule._meta.get_field("molecule_id").get_attname_column()[1]
    submission_id_db_column = DyndbSubmissionMolecule._meta.get_field("submission_id").get_attname_column()[1]
    
    filesmol = DyndbFilesMolecule._meta.db_table
    id_molecule_db_column = DyndbFilesMolecule._meta.get_field("id_molecule").get_attname_column()[1]
    id_files_db_column = DyndbFilesMolecule._meta.get_field("id_files").get_attname_column()[1]
    type_db_column = DyndbFilesMolecule._meta.get_field("type").get_attname_column()[1]
    
    files = DyndbFiles._meta.db_table
    files_pk_db_column = DyndbFiles._meta.pk.get_attname_column()[1]
    filepath_db_column = DyndbFiles._meta.get_field("filepath").get_attname_column()[1]
    
    int_id_string = ",".join([str(key) for key in int_ids])
    with connection.cursor() as cursor:
        q = cursor.execute(''.join(('''SELECT   submol."''',int_id_db_column,'''" AS int_id,
                                                submol."''',molecule_id_db_column,'''"AS molecule_id,
                                                files."''',filepath_db_column,'''" AS "filepath"
                                                FROM "''',submol,'''" AS submol
                                                INNER JOIN "dyndb_files_molecule" AS filesmol ON 
                                                (molecule_id = filesmol."''',id_molecule_db_column,'''")
                                                LEFT OUTER JOIN "''',files,'''" AS files ON (filesmol."''',id_files_db_column,'''" = files."''',files_pk_db_column,'''")
                                                WHERE (
                                                    submol."''',submission_id_db_column,'''" = %s
                                                        AND int_id IN (''',int_id_string,''')
                                                        AND filesmol."''',type_db_column,'''" = %s
                                                )''')),[str(submission_id),str(sdf_mol_file_type)])
        return dictfetchall(cursor)

def get_model_pdb_from_db_by_submission(submission_id):
    submodel = DyndbSubmissionModel._meta.db_table
    submodel_pk_db_column = DyndbSubmissionModel._meta.pk.get_attname_column()[1]
    model_id_db_column = DyndbSubmissionModel._meta.get_field("model_id").get_attname_column()[1]
    submission_id_db_column = DyndbSubmissionModel._meta.get_field("submission_id").get_attname_column()[1]
    filesmodel = DyndbFilesModel._meta.db_table
    id_model_db_column = DyndbFilesModel._meta.get_field("id_model").get_attname_column()[1]
    id_files_db_column = DyndbFilesModel._meta.get_field("id_files").get_attname_column()[1]
    files = DyndbFiles._meta.db_table
    files_pk_db_column = DyndbFiles._meta.pk.get_attname_column()[1]
    filepath_db_column = DyndbFiles._meta.get_field("filepath").get_attname_column()[1]
    
    with connection.cursor() as cursor:
        q = cursor.execute(''.join(('''SELECT   submodel."''',model_id_db_column,'''"AS model_id,
                                                files."''',filepath_db_column,'''" AS "filepath"
                                                FROM "''',submodel,'''" AS submodel
                                                INNER JOIN "dyndb_files_model" AS filesmodel ON 
                                                (model_id = filesmodel."''',id_model_db_column,'''")
                                                LEFT OUTER JOIN "''',files,'''" AS files ON (filesmodel."''',id_files_db_column,'''" = files."''',files_pk_db_column,'''")
                                                WHERE (
                                                    submodel."''',submission_id_db_column,'''" = %s
                                                )''')),[str(submission_id)])
        rows = dictfetchall(cursor)
    if len(rows) == 1:
        return rows[0]["filepath"]
    else:
        return None
    
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def pdbcheck_molecule(request,submission_id,form_type):
    if form_type=="dynamicsreuse":
        form_type="dynamics"
    post_mc_dict = {'resname':'residue name','molecule':'molecule form number','id_molecule':'molecule ID'}
    postkeys_mc = post_mc_dict.keys()
    response = None
    if form_type == "model":
        prefix_mc='formmc'
    elif form_type == "dynamics":
        prefix_mc='formc'
        post_mc_dict['type_int'] = 'molecule type'
        water_type = type_inverse_search(DyndbDynamicsComponents.MOLECULE_TYPE,searchkey='water',case_sensitive=False,first_match=False)
        water_types = [i[1] for i in water_type.items()]
        water_int_id_list = []
    postkeys_ps = {'chain','segid','resid_from','resid_to'}
    prefix_ps='formps'
    if request.method == 'POST':
            submission_path = get_file_paths(form_type,url=False,submission_id=submission_id)
            submission_url = get_file_paths(form_type,url=True,submission_id=submission_id)
            pdbname = get_file_name_submission(form_type,submission_id,0,ext="pdb",forceext=False,subtype="pdb")
            pdbfilepath =  os.path.join(submission_path,pdbname)
            if not os.path.isfile(pdbfilepath):
                return JsonResponse({'msg':'Cannot find uploaded PDB coordinate file. Try to upload the file again.'},status=422,reason='Unprocessable Entity')
            data = dict()
            data['download_url_log'] = None
            fieldset_mc = dict()
            fieldset_ps = dict()
            for key in request.POST:
                print("keyi ", key)
                if key.find(prefix_mc) == 0:
                    print(" key.find(prefix_mc) == 0")
                    fieldsplit = key.split('-')
                    fieldname = fieldsplit[2]
                    if fieldname in postkeys_mc:
                        num = int(fieldsplit[1])
                        if num not in fieldset_mc.keys():
                            fieldset_mc[num] = dict()    
                        fieldset_mc[num][fieldname] = request.POST[key].strip()
                        if fieldname in {'molecule','id_molecule','numberofmol','type_int'}:
                            if fieldset_mc[num][fieldname].isdigit():
                                fieldset_mc[num][fieldname] = int(fieldset_mc[num][fieldname])
                            else:
                                msgtype = post_mc_dict[fieldname].split(maxsplit=1)
                                return JsonResponse({'msg':msgtype[0].title()+' '+msgtype[1]+' "'+str(fieldset_mc[num][fieldname])+'" is invalid or empty.'},status=422,reason='Unprocessable Entity')
                elif key.find(prefix_ps) == 0 and form_type == "model":
                    fieldsplit = key.split('-')
                    fieldname = fieldsplit[2]
                    if fieldname in postkeys_ps:
                        num = int(fieldsplit[1])
                        if num not in fieldset_ps.keys():
                            fieldset_ps[num] = dict()
                        fieldset_ps[num][fieldname] = request.POST[key].strip()
                        if fieldname in {'resid_from','resid_to'}:
                            if fieldset_ps[num][fieldname].isdigit():
                                fieldset_ps[num][fieldname] = int(fieldset_ps[num][fieldname])
                            else:
                                try:
                                    fieldset_ps[num][fieldname] = int(fieldset_ps[num][fieldname],16)
                                except ValueError:
                                    return JsonResponse({'msg':'Residue definition "'+str(fieldset_ps[num][fieldname])+'" is invalid or empty.'},status=422,reason='Unprocessable Entity')
                elif key in postkeys_mc:
                    if 0 not in fieldset_mc.keys():
                        print ("if 0 not in fieldset_mc.keys():")
                        fieldset_mc[0] = dict()
                    fieldset_mc[0][key] = request.POST[key].strip()
                    if key in {'molecule','id_molecule','numberofmol'}:
                        if fieldset_mc[0][key].isdigit():
                            fieldset_mc[0][key] = int(fieldset_mc[0][key])
                        else:
                            msgtype = post_mc_dict[key].split(maxsplit=1)
                            return JsonResponse({'msg':msgtype[0].title()+' '+msgtype[1]+' "'+str(fieldset_mc[0][key])+'" is invalid or empty.'},status=422,reason='Unprocessable Entity')
                elif key in postkeys_ps and form_type == "model":
                    if 0 not in fieldset_ps.keys():
                        fieldset_ps[0] = dict()
                    fieldset_ps[0][key] = request.POST[key].strip()
                    if key in {'resid_from','resid_to'}:
                        if fieldset_ps[0][key].isdigit():
                            fieldset_ps[0][key] = int(fieldset_ps[0][key])
                        else:
                            try:
                                fieldset_ps[0][key] = int(fieldset_ps[0][key],16)
                            except ValueError:
                                return JsonResponse({'msg':'Residue definition "'+str(fieldset_ps[0][key])+'" is invalid or empty.'},status=422,reason='Unprocessable Entity')
            if fieldset_mc == dict() or (fieldset_ps == dict() and form_type == "model"):
                return JsonResponse({'msg':'Missing POST keys.'},status=422,reason='Unprocessable Entity')
            for num in fieldset_mc.keys():
                if fieldset_mc[num].keys() != postkeys_mc:
                    return JsonResponse({'msg':'Missing POST keys.'},status=422,reason='Unprocessable Entity')
            if form_type == "model":       
                for num in fieldset_ps.keys():
                    if fieldset_ps[num].keys() != postkeys_ps:
                        return JsonResponse({'msg':'Missing POST keys.'},status=422,reason='Unprocessable Entity')
            if form_type == "model":
                fieldset_ps = [fieldset_ps[key] for key in sorted(fieldset_ps,key=int)]
            elif form_type == "dynamics":
                q = DyndbSubmissionModel.objects.filter(submission_id=submission_id)
                fields_list = list(postkeys_ps)
                path = 'model_id__dyndbmodeledresidues__'
                fields = dict()
                for field in fields_list:
                    fields[field] = F(path+field)
                q = q.annotate(**fields)
                q = q.values(*fields_list)
                fieldset_ps = list(q)
            molintdict = dict()
            form_resnames = set()
            for key in fieldset_mc:
                int_id = fieldset_mc[key]['molecule'] - 1
                if int_id not in molintdict:
                    molintdict[int_id] = dict()
                    molintdict[int_id]['resname'] = set()
                    if form_type == "dynamics" and fieldset_mc[key]['type_int'] in water_types:
                        water_int_id_list.append(int_id)
                    #molintdict[int_id]['resname_list'] = []
                    #molintdict[int_id]['numberofmol'] = []
                resname = fieldset_mc[key]['resname']
                if resname in molintdict[int_id]['resname']:
                    return JsonResponse({'msg':'Resname "'+resname+'" definition is duplicated'},status=422,reason='Unprocessable Entity')
                #molintdict[int_id]['resname_list'].append(resname)
                molintdict[int_id]['resname'].add(resname)
                form_resnames.add(resname)
                molintdict[int_id]['id_molecule'] = fieldset_mc[key]['id_molecule']
                #molintdict[int_id]['numberofmol'].append(fieldset_mc[key]['numberofmol'])
            del fieldset_mc    
            int_ids = molintdict.keys()
            int_ids_db = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(int_id=None)
            if form_type == "model":
                int_ids_db = int_ids_db.filter(not_in_model=False)
            int_ids_db = int_ids_db.values('int_id')
            diff_int_id_form_db = set(list([row['int_id'] for row in int_ids_db])).difference(set(molintdict.keys()))
            if diff_int_id_form_db != set():
                return JsonResponse({'msg':'You have the following unused molecules in step 2: '+','.join(['#'+str(i+1) for i in diff_int_id_form_db])+'.\nPlease, delete them if they are not part of your submission.'},status=422,reason='Unprocessable Entity')
            results = get_sdf_from_db_by_submission(submission_id,int_ids)
            if len(results) == 0:
                return JsonResponse({'msg':'Cannot find the selected  molecules or their respective files in the current submission.'},status=422,reason='Unprocessable Entity')
            for row in results:
                int_id = row['int_id']
                if molintdict[int_id]['id_molecule'] != row['molecule_id']:
                    return JsonResponse({'msg':'Molecule form number "'+str(int_id+1)+'" does not match mol ID.'},status=422,reason='Unprocessable Entity')
                molintdict[int_id]['molfile'] = row['filepath']
            for int_id in molintdict:
                if 'molfile' not in molintdict[int_id]:
                    missing_sdf = True
                else:
                    if not molintdict[int_id]['molfile']:
                        missing_sdf = True
                    else:
                        missing_sdf = False
                if missing_sdf:
                    return JsonResponse({'msg':'Cannot find the molecule with form number "'+str(int_id+1)+\
                    '" or its respective file in the current submission.'},status=422,reason='Unprocessable Entity')
            os.makedirs(submission_path,exist_ok=True)
            logname = get_file_name_submission(form_type,submission_id,0,ext="log",forceext=False,subtype="log")
            logfile = open(os.path.join(submission_path,logname),'w')
            data['download_url_log'] = join_path(submission_url,logname,url=True)
            pdbcheckerpath = os.path.join(submission_path,'pdbchecker')
            try:
                shutil.rmtree(pdbcheckerpath)
            except:
                pass
            try:
                os.remove(os.path.join(pdbcheckerpath,'pdbchecker.tar.gz'))
            except:
                pass
            os.makedirs(pdbcheckerpath,exist_ok=True)
            print("Splitting into protein and non-protein residues...",file=logfile)
            try:
                try:
                    proteinpdbfilename,nonproteinpdbfilename = split_protein_pdb(pdbfilepath,fieldset_ps,outputfolder=pdbcheckerpath)
                    print("Splitting non-protein residues by residue names...",file=logfile)
                    datares = split_resnames_pdb(nonproteinpdbfilename,outputfolder=pdbcheckerpath)
                    resnames = datares.keys()
                    data['atom_num'] = get_atoms_num(pdbfilepath,'coor')
                    print(str(len(resnames))+" resname(s) found: "+", ".join(resnames),file=logfile)
                    print("Checking non-protein residues naming consistency...",file=logfile)
                    errorflaglist = []
                    pdbdict = dict()
                    for resname in resnames:
                        pdbdict[resname],datares[resname]['num_of_mol'],errorflag = molecule_atoms_unique_pdb(datares[resname]['filename'], outputfolder=pdbcheckerpath,logfile=logfile)
                        print("Found "+str(datares[resname]['num_of_mol'])+" "+resname+" molecule(s).",file=logfile)
                        errorflaglist.append(errorflag)
                    if sum(errorflaglist) > 0:
                        data['msg'] = 'Errors found while parsing PDB file. Please check log file.'
                        response = JsonResponse(data,status=422,reason='Unprocessable Entity')
                        return response
                except ParsingError as e:
                    response = JsonResponse({'msg':e.args[0]},status=422,reason='Unprocessable Entity')
                    return response
                except:
                    if settings.DEBUG:
                        raise
                    else:
                        response = HttpResponseServerError('Unknown error while processing PDB file.',content_type='text/plain; charset=UTF-8')
                        return response
                pdb_resnames = set(resnames)
                diff_pdb_form = pdb_resnames.difference(form_resnames)
                diff_form_pdb = form_resnames.difference(pdb_resnames)####!!
                if diff_pdb_form != set():
                    data['msg'] = 'Found non-declared residue name(s): "'+", ".join(sorted(diff_pdb_form))+'" . Please, add the missing resnames.'
                    response = JsonResponse(data,status=422,reason='Unprocessable Entity')
                    return response
                if diff_form_pdb != set():
                    data['msg'] = 'Residue name(s) "'+",".join(sorted(diff_form_pdb))+'" not found.'
                    response = JsonResponse(data,status=422,reason='Unprocessable Entity')
                    return response
                print("\nChecking non-protein residues topology...\n",file=logfile)
                fail = 0
                for int_id in sorted(molintdict.keys(),key=int):
                    print("Loading mol #"+str(int_id+1)+", mol ID "+str(molintdict[int_id]['id_molecule'])+'.',file=logfile)
                    print(molintdict[int_id])
                    try:
                        with open(molintdict[int_id]['molfile'],'rb') as molfile:
                            mol = open_molecule_file(molfile,logfile=logfile,filetype='sdf')
                    except (ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension) as e:
                        print(e.args[0],file=logfile)
                        data['msg'] = 'Cannot open molecule file of molecule form number #'+str(int_id+1)+'.'
                        response = JsonResponse(data,status=500,reason='Internal Server Error')
                        return response
                    for resname in sorted(list(molintdict[int_id]['resname'])):
                        print("\n------------------------------\n",file=logfile)
                        try:
                            print("Checking mol #"+str(int_id+1)+" resname "+resname+", mol ID "+str(molintdict[int_id]['id_molecule'])+'.',file=logfile)
                            failc, pdbmol, nhpdbmol = diff_mol_pdb(mol,pdbdict[resname],logfile=logfile)
                            fail += failc
                            try:
                                #generate_png(pdbmol,pdbdict[resname]+'.png',logfile=os.devnull,size=300)
                                write_sdf(pdbmol,pdbdict[resname]+'.sdf')
                                write_sdf(nhpdbmol,pdbdict[resname]+'nh.sdf')
                            except:
                                pass
                            finally:
                                del pdbmol
                                del nhpdbmol
                        except ParsingError as e:
                            print(e.args[0],file=logfile)
                            data['msg'] = "Cannot read from PDB mol #"+str(int_id+1)+" resname "+resname+", mol ID "+str(molintdict[int_id]['id_molecule'])+'.'
                            response = JsonResponse(data,status=500,reason='Internal Server Error')
                            return response
                    del mol
                    print("\n##############################\n",file=logfile)
                if form_type == "dynamics":
                    model_pdbfilepath = get_model_pdb_from_db_by_submission(submission_id)
                    if model_pdbfilepath is None:
                        data['msg'] = "Cannot find model PDB file. Did you fill step 3 form?"
                        response = JsonResponse(data,status=500,reason='Internal Server Error')
                        return response
                    print("\nSplitting model PDB file into protein and non-protein residues...\n",file=logfile)
                    try:
                        model_proteinpdbfilename,model_nonproteinpdbfilename = split_protein_pdb(model_pdbfilepath,fieldset_ps,outputfolder=pdbcheckerpath)
                    except:
                        data['msg'] = "Cannot process model PDB file. Did you fill and validate step 3 form?"
                        response = JsonResponse(data,status=500,reason='Internal Server Error')
                        return response
                    print("\nChecking PDB protein model vs simulation assembly coherence...",file=logfile)
                    model_protein_residue_dict,errorflag1 = residue_atoms_dict_pdb(model_proteinpdbfilename,logfile=logfile)
                    dyn_protein_residue_dict,errorflag2 = residue_atoms_dict_pdb(proteinpdbfilename,logfile=logfile)
                    diff_protein = residue_dict_diff(model_protein_residue_dict,dyn_protein_residue_dict,logfile=logfile,ignore_extra_residues=False)
                    print("\nChecking PDB non-protein model vs simulation assembly coherence...",file=logfile)
                    model_nonprotein_residue_dict,errorflag3 = residue_atoms_dict_pdb(model_nonproteinpdbfilename,logfile=logfile)
                    dyn_nonprotein_residue_dict,errorflag4 = residue_atoms_dict_pdb(nonproteinpdbfilename,logfile=logfile)
                    diff_nonprotein = residue_dict_diff(model_nonprotein_residue_dict,dyn_nonprotein_residue_dict,logfile=logfile,ignore_extra_residues=True)
                    fail += sum((errorflag1,errorflag2,errorflag3,errorflag4))
                    data['num_of_solvent'] = 0
                    for int_id in water_int_id_list:
                        for resname in molintdict[int_id]['resname']:
                            data['num_of_solvent'] += datares[resname]['num_of_mol']
                else:
                    # protein is not checked
                    diff_protein = False
                    diff_nonprotein = False
                print("\nEND\n",file=logfile)
                if fail == 0 and not diff_protein and not diff_nonprotein:
                    data['msg'] = 'Validation complete. Everything seems fine.'
                else:
                    data['msg'] = 'Validation finished with warnings. Please, see log file and double check your PDB file.'
                data['resnames'] = datares
                data['download_url_pdbchecker'] = join_path(submission_url,'pdbchecker.tar.gz',url=True)
                response = JsonResponse(data)
                return response
            except:
                raise
            finally:
                try:
                    logfile.close()
                except:
                    pass
                tgzfile = tarfile.open(name=os.path.join(submission_path,'pdbchecker.tar.gz'),mode='w:gz')
                tgzfile.add(pdbcheckerpath,arcname='pdbchecker')
                tgzfile.add(os.path.join(submission_path,logname),arcname=os.path.join('pdbchecker/',logname))
                tgzfile.close()
                if response is None:
                    raise
                else:
                    return response

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def check_trajectories(request,submission_id):
    if request.method == 'POST':
        submission_path = get_file_paths("dynamics",url=False,submission_id=submission_id)
        submission_url = get_file_paths("dynamics",url=True,submission_id=submission_id)
        pdbname = get_file_name_submission("dynamics",submission_id,0,ext="pdb",forceext=False,subtype="pdb")
        pdbfilepath =  os.path.join(submission_path,pdbname)
        if not os.path.isfile(pdbfilepath):
            return JsonResponse({'msg':'Cannot find uploaded PDB file. Try to upload the file again.'},status=422,reason='Unprocessable Entity')
        return HttpResponse("Success!",content_type='text/plain; charset=UTF-8')
        
@login_required
def MODELreuseREQUESTview(request,model_id,submission_id=None):
    if request.method == 'GET':
        return render(request,'dynadb/MODELreuseREQUEST.html', {'action':'#'})
    # Dealing with POST data
    elif request.method == 'POST':
        dictsubid={}#dictionary for instatiating dyndbSubmission and obtaining a new submission_id for our new submission
        dictsubid['user_id']=str(request.user.pk)
        dictsubid['is_reuse_model']=str(1)
        fdbsub=dyndb_Submission(dictsubid)
        fdbsubobj=fdbsub.save()
        chosen_model_id_state = None
        chosen_submission_id_state = None
        submission_id = fdbsubobj.pk
        print("submission_id",fdbsubobj.pk)
        #Parsing POST keys        
        if 'Choose_reused_model' in request.POST:
            chosen_model_id = request.POST['Choose_reused_model'].strip()
            if chosen_model_id.isdigit():
                chosen_model_id = int(chosen_model_id)
                chosen_model_id_state = 'valid'
            elif chosen_model_id == "":
                chosen_model_id_state = 'empty'
            else:
                chosen_model_id_state = 'invalid'
        else:
            chosen_model_id = None
            chosen_model_id_state = None
        if 'Choose_submission_id' in request.POST:
            chosen_submission_id = request.POST['Choose_submission_id'].strip()
            if chosen_submission_id.isdigit():
                chosen_submission_id = int(chosen_submission_id)
                chosen_submission_id_state = 'valid'
            elif chosen_submission_id == "":
                chosen_submission_id_state = 'empty'
            else:
                chosen_submission_id_state = 'invalid'
        else:
            chosen_submission_id = None
            chosen_submission_id_state = None
        if chosen_model_id_state in {'valid','invalid'} and chosen_submission_id_state in {'valid','invalid'}:
            return render(request,'dynadb/MODELreuseREQUEST.html', \
            {'message':'Please, provide either complex structure ID or submission ID, but not both.', 'error':'both','action':'#'})
        elif chosen_model_id_state in {'empty',None} and chosen_submission_id_state in {'empty',None} :
            return render(request,'dynadb/MODELreuseREQUEST.html', \
            {'message':'Please, provide either complex structure ID or submission ID.', 'error':'both','action':'#'})
        elif chosen_model_id_state == 'invalid':
            return render(request,'dynadb/MODELreuseREQUEST.html', {'message':'Invalid complex structure ID.', 'error':'model','action':'#'})
        elif chosen_submission_id_state == 'invalid':    
            return render(request,'dynadb/MODELreuseREQUEST.html', {'message':'Invalid submission ID.','error':'submission','action':"#"})
        # By model
        elif chosen_model_id_state == 'valid':
            is_owner_or_pub = is_published_or_submission_owner(request.user,object_type='model',model_id=chosen_model_id)
            # check if the submission for this model is closed
            # do if chosen_model_id corresponds to a model
            if is_owner_or_pub is not None:
                is_published = DyndbModel.objects.filter(pk=chosen_model_id,is_published=True).exists()
                if not is_published:
                    # do if the submission for this model is not closed 
                    if not DyndbSubmissionModel.objects.filter(model_id=chosen_model_id,submission_id__is_closed=True).exists():
                        return render(request,'dynadb/MODELreuseREQUEST.html', \
                        {'message':"Complex structure with ID: %d not found or available." % (chosen_model_id), 'error':'model','action':'#'})
            if is_owner_or_pub:
                model_id = chosen_model_id
            else:
                return render(request,'dynadb/MODELreuseREQUEST.html', \
                {'message':"Complex structure with ID: %d not found or available." % (chosen_model_id),'error':'model','action':'#'})
        # By submission
        elif chosen_submission_id_state == 'valid':
            is_owner = is_submission_owner(request.user,submission_id=chosen_submission_id)
            # do if chosen_submission_id corresponds to a submission
            is_published = False
            if is_owner is not None:
                subq = DyndbSubmission.objects.filter(pk=chosen_submission_id).values('is_published','is_closed')
                sub_data = subq[0]
                is_published = sub_data['is_published']
                if not is_published and not sub_data['is_closed']:
                    return render(request,'dynadb/MODELreuseREQUEST.html', \
                    {'message':"Submission with ID: %d not found or available." % (chosen_submission_id), 'error':'submission','action':'#'})
            if is_owner or is_published:
                model_id = DyndbSubmissionModel.objects.filter(submission_id=chosen_submission_id).values_list('model_id',flat=True)[0]
            else:
                return render(request,'dynadb/MODELreuseREQUEST.html', \
                {'message':"Submission with ID: %d not found or available." % (chosen_submission_id), 'error':'submission','action':'#'})
        submission_model=dyndb_Submission_Model({'model_id':model_id, 'submission_id':fdbsubobj.pk})
        if submission_model.is_valid():
            submission_model.save()
            return HttpResponseRedirect(reverse('dynadb:modelreuse',kwargs={'submission_id':submission_id}))
        else:
            print("ERROR",submission_model.errors.as_text())
            return render(request,'dynadb/MODELreuseREQUEST.html', \
                {'message':"Error while creating the new submission:\n%s" % (submission_model.errors.as_text()), 'error':'both','action':'#'}) 

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def MODELreuseview(request, submission_id ):    
    enabled=False
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    model_id=int(qSubModNew.values_list('model_id',flat=True)[0])
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]).order_by('int_id')
    print(qSub,"  ", model_id, submission_id)
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    if qSubPNew.exists() and qSubMolNew.exists(): #el submit Model is submitted when clicking the " Continue to step 4: Dynamics Information " button 
        enabled=True
    qModel=DyndbModel.objects.filter(id=model_id)
    INITsubmission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]
    p=qModel
    Typeval=p.values()[0]['type']
    Type=p.model.MODEL_TYPE[Typeval][1]
    STypeval=p.values()[0]['source_type']
    SType=p.model.SOURCE_TYPE[STypeval][1]
    qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id,id_protein__dyndbsubmissionprotein__submission_id=INITsubmission_id).annotate(int_id=F('id_protein__dyndbsubmissionprotein__int_id')).order_by('resid_from')
    lformps=list(range(0,len(qMODRES)))
    rowsMR=qMODRES
    lmrstype=[]
    for l in qMODRES:
        mrstype=l.SOURCE_TYPE[l.source_type]
        lmrstype.append(mrstype)
    qMODCOMP=DyndbModelComponents.objects.filter(id_model=model_id).exclude(type=None).exclude(numberofmol=None)
    qMODCOMP=qMODCOMP.order_by('id')
    lmtype=[]
    lformmc=list(range(0,len(qMODCOMP)))
    lcompname=[]
    l_ord_mol=[]
    d=0
    for l in qMODCOMP:
        d=d+1
        mtype=l.MOLECULE_TYPE[l.type]
        lmtype.append(mtype)
        qName=DyndbCompound.objects.filter(id=DyndbMolecule.objects.filter(id=l.id_molecule_id).values_list('id_compound',flat=True)).values_list('name',flat=True)[0]
        lcompname.append(qName)
        l_ord_mol.append(d)
    rowsMC=qMODCOMP.values('resname','id_molecule_id','numberofmol','type')
    action="/".join(["/dynadb/modelreuse",submission_id,""])
    reuse_model=model_id
    if request.method == 'POST':
        if not qSubModNew.exists():
            dictsubmod={'submission_id':submission_id, 'model_id':request.POST['model_id']}
            fdbSM=dyndb_Submission_Model(dictsubmod)
            if fdbSM.is_valid():
                fdbSM.save()
                response = HttpResponse("Step 3 \"Crystal Assembly Information\" has been successfully submitted for this submission.",content_type='text/plain; charset=UTF-8')
            else:
                response = HttpResponse( ("").join([fdbSM.errors.as_text(), ". The submission model form has not been saved."]),content_type='text/plain; charset=UTF-8')
        else:
            response = HttpResponse("Step 3 \"Crystal Assembly Information\" has been previously submitted for this submission.",content_type='text/plain; charset=UTF-8')
        return response
       # return HttpResponseRedirect("/".join(["/dynadb/MODELreuse",submission_id,""]), {'submission_id':submission_id} )
    else:
        fdbMF = dyndb_Model()
        fdbPS = dyndb_Modeled_Residues()
        fdbMC = dyndb_Model_Components()
        return render(request,'dynadb/MODEL.html', {'rowsMR':rowsMR,'lcompname':lcompname,'lformps':lformps,'lformmc':lformmc,'SType':SType,'Type':Type,'lmtype':lmtype,'lmrstype':lmrstype,'rowsMC':rowsMC, 'p':p ,'l_ord_mol':l_ord_mol,'fdbPS':fdbPS,'fdbMC':fdbMC,'submission_id':submission_id,'model_id':model_id, 'enabled':enabled, 'modelr_form':True})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def PROTEINreuseview(request, submission_id ):
    enabled=False
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    model_id=qSubModNew.values_list('model_id',flat=True)[0]
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id')
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]).exclude(int_id=None).order_by('int_id')
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
        enabled=True
    int_id=[]
    int_id0=[]
    alias=[]
    mseq=[]
    wseq=[]
    MUTations=[]
    sci_na_codel=[]
    qPROT=[]
    for l in qSub:
        sci_name=list(DyndbUniprotSpecies.objects.filter(id=l.protein_id.id_uniprot_species_id).values_list('scientific_name','code')[0])
        if sci_name[0] is None:
            sci_name[0]=""
        if sci_name[1] is None:
            sci_name[1]=""
        sci_na_code=("").join([sci_name[0]," (",sci_name[1],")"])
        sci_na_codel.append(sci_na_code)
        qprot=DyndbProtein.objects.filter(id=l.protein_id_id)[0]
        qPROT.append(qprot)
        int_id.append(l.int_id +1) 
        int_id0.append(l.int_id) 
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
            llsm=qSEQ
            mseq.append(llsm)
            qpCp=DyndbProteinCannonicalProtein.objects.filter(id_protein=l.protein_id).values_list('id_cannonical_proteins',flat=True)[0]
            llsw=DyndbProteinSequence.objects.filter(id_protein=qpCp).values_list('sequence',flat=True)[0]
            qPMut=DyndbProteinMutations.objects.filter(id_protein=l.protein_id)
            MUTations.append(qPMut)
        else:
            llsw=qSEQ
            mseq.append('')
            MUTations.append('')
        wseq.append(llsw) 
        qALIAS=DyndbOtherProteinNames.objects.filter(id_protein=l.protein_id)
        llo=("; ").join(qALIAS.values_list('other_names',flat=True))
        alias.append(llo) 
    return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id,'model_id':model_id, 'enabled':enabled })

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def SMALL_MOLECULEreuseview(request, submission_id, model_id ):
    enabled=False
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(int_id=None)
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    model_id=qSubModNew.values_list('model_id',flat=True)[0]
    if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
        enabled=True
    qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=True).filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0],molecule_id__dyndbfilesmolecule__id_files__id_file_types=19,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url')).order_by('int_id')
    labtypel=[]
    int_id=[]
    int_id0=[]
    alias=[]
    qCOMP=[]
    qMOL=[]
    imp=[]
    Type=[]
    url=[]
    urlstd=[]
    for l in qSub:
        urlstd.append(str(l.urlstd).strip())
        url.append(str(l.url).strip())
        labtype=l.COMPOUND_TYPE[l.type]
        labtypel.append(labtype) 
        if  not l.not_in_model:
            imp.append(True)
        else:
            imp.append(False)

        int_id.append(l.int_id+1)
        int_id0.append(l.int_id)
        typt=l.type
        Type.append(typt)
        qmol=DyndbMolecule.objects.filter(id=l.molecule_id.id)[0]
        qMOL.append(qmol)
        qCOMPtt=DyndbCompound.objects.filter(id=qmol.id_compound.id)[0] # VERIFICAR!!!!!!!!!!!!!!!!!!!
        qALIAS=DyndbOtherCompoundNames.objects.filter(id_compound=qmol.id_compound.id)
        llo=("; ").join(qALIAS.values_list('other_names',flat=True))
        alias.append(llo) 
        qCOMP.append(qCOMPtt) 
    listExtraMolColapse=list(range(max(int_id),40))
    fdbSub = dyndb_Submission_Molecule()
    last=int_id0[-1]
    qSubNotMod=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=False).filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).order_by('int_id').annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url'))
    print("VALUES XXXXX",qSubNotMod.values(),"   qSubNotMod.exists ",qSubNotMod.exists())
    print("ENABLED???? ",enabled," ")
    if enabled and qSubNotMod.exists():
        labtypelNotMod=[]
        print(qSubNotMod)  ######POR AQUI!!!! ORDENAR POR INT_ID LA QUERY qMOL!!! 
        int_idNotMod=[]
        int_id0NotMod=[]
        aliasNotMod=[]
        qCOMPNotMod=[]
        qMOLNotMod=[]
        impNotMod=[]
        TypeNotMod=[]
        urlNotMod=[]
        urlstdNotMod=[]
        for l in qSubNotMod:
            urlNotMod.append(str(l.url).strip())
            urlstdNotMod.append(str(l.urlstd).strip())
            print("\nstd url ",l.urlstd)
            print(urlNotMod)
            labtype=l.COMPOUND_TYPE[l.type]
            labtypelNotMod.append(labtype) 
            if  not l.not_in_model:
                impNotMod.append(True)
            else:
                impNotMod.append(False)
            int_idNotMod.append(l.int_id+1)
            int_id0NotMod.append(l.int_id)
            typtNotMod=l.type
            TypeNotMod.append(typtNotMod)
            qmolNotMod=DyndbMolecule.objects.filter(id=l.molecule_id.id)[0]
            qMOLNotMod.append(qmolNotMod)
            qCOMPttNotMod=DyndbCompound.objects.filter(id=qmolNotMod.id_compound.id)[0] # VERIFICAR!!!!!!!!!!!!!!!!!!!
            qALIASNotMod=DyndbOtherCompoundNames.objects.filter(id_compound=qmolNotMod.id_compound.id)
            lloNotMod=("; ").join(qALIASNotMod.values_list('other_names',flat=True))
            aliasNotMod.append(lloNotMod) 
            qCOMPNotMod.append(qCOMPttNotMod) 
        listExtraMolColapseNotMod=list(range(max(int_idNotMod+int_id),40))
        fdbSub = dyndb_Submission_Molecule()
        last=max(int_id0NotMod+int_id0)
        lastNotMod=max(int_id0NotMod)
    else:
        labtypelNotMod=[]
        int_idNotMod=[]
        int_id0NotMod=[]
        aliasNotMod=[]
        qCOMPNotMod=[]
        qMOLNotMod=[]
        impNotMod=[]
        TypeNotMod=[]
        urlNotMod=[]
        urlstdNotMod=[]
        urlNotMod.append(str(l.url).strip())
        urlstdNotMod.append(str(l.urlstd).strip())
        int_idNotMod.append(1)
        int_id0NotMod.append(0)
        typtNotMod=""
        TypeNotMod.append(typtNotMod)
        qmol=""
        qMOLNotMod.append(qmol)
        qCOMPttNotMod="" # VERIFICAR!!!!!!!!!!!!!!!!!!!
        qALIASNotMod=""
        aliasNotMod.append("") 
        qCOMPNotMod.append("") 
        listExtraMolColapseNotMod=list(range(max(int_idNotMod),40))
        fdbSub = dyndb_Submission_Molecule()
        lastNotMod=int_id0[-1]
        last=int_id0[-1]
    return render(request,'dynadb/SMALL_MOLECULE.html', {'url':url,'urlstd':urlstd,'fdbSub':fdbSub,'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'last':last,'alias':alias,'submission_id':submission_id,'model_id':model_id,'list':listExtraMolColapse, 'enabled':enabled, 'urlNotMod':urlNotMod,'urlstdNotMod':urlstdNotMod,'qMOLNotMod':qMOLNotMod,'labtypelNotMod':labtypelNotMod,'TypeNotMod':TypeNotMod,'impNotMod':impNotMod,'qCOMPNotMod':qCOMPNotMod,'int_idNotMod':int_idNotMod,'int_id0NotMod':int_id0NotMod,'lastNotMod':lastNotMod,'aliasNotMod':aliasNotMod,'listNotMod':listExtraMolColapseNotMod, 'qSubNotModsaved':qSubNotMod.exists() })
 
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def DYNAMICSreuseview(request, submission_id, model_id ):
    if request.method == 'POST':
        #Defining variables and dictionaries with information not available in the html form. This is needed for form instances.
        author="jmr"   #to be modified with author information. To initPF dict
        action="/dynadb/DYNAMICSfilled/"
        now=timezone.now()
        initDyn={'id_model':model_id,'id_compound':'1','update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
        initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
        ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
        # Defining a dictionary "d_fdyn_t" containing choices in the table dyndb_files_dynamics (field 'type')
        d_fdyn_t={'coor':'0','top':'1','traj':'2','parm':'3','other':'3'}
        dicpost=request.POST
        dicfiles=request.FILES
        print("CLASS traj",type(request.FILES['traj'])," ",request.FILES['traj'] )
        print("CLASS traj",type(request.FILES['traj'])," ",request.FILES.getlist('traj') )
        print(len(request.FILES.getlist('traj')))
        lkeydyncomp=["id_molecule","molecule","name","numberofmol","resname","type"]
        indexl=[]
        indexfl=[]
        POSTimod={} #Dictionary of dyctionarys containing POST for each SIMULATION REPLICATE keys have been modified to match table fields
        FILEmod={} #Dictionary of dyctionarys containing FILES for each SIMULATION REPLICATE keys have been modified to match table fields
        ## Crear diccionario para instanciar dyndb_dynamicsform
        # compilation of regex patterns for searching and modifying keys and make them match the table fields  
        form=re.compile('form-')
        formc=re.compile('formc-')
        for key,val in dicpost.items():
            if form.search(key):
                index=int(key.split("-")[1])
                if index not in indexl:
                    indexl.append(index)
                    POSTimod[index]={}
                POSTimod[index]["-".join(key.split("-")[2:])]=val
            else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
                if len(indexl)==0:
                    indexl.append(0)
                    POSTimod[0]={}
                POSTimod[0][key]=val 
        Pscompmod={} #Dictionary of dyctionarys containing Simulation Components for each SIMULATION REPLICATE  keys have been modified to match table fields
        dyn_ins={}
        dyn_obj={}
        dyn_objf={}
        Scom_inst={}
        Scom_obj={}
        print("lista indexl", indexl," pipol")
        indexl.sort()
        print("lista indexl", indexl," ordenada")
        for key,val in dicfiles.items():
            if form.search(key):
                indexf=int(key.split("-")[1])
                if indexf not in indexfl:
                    indexfl.append(indexf)
                    FILEmod[indexf]={}
                    print("indexf ", indexf, " Key, Val ", key, val)
                nkey="-".join(key.split("-")[2:])
                if nkey == 'traj':
                    FILEmod[indexf][nkey]={} 
                    continue
                FILEmod[indexf][nkey]=val
            else:
                if len(indexfl)==0:
                    indexfl.append(0)
                    print("indexf=0")
                    FILEmod[0]={}
                print("key en dicfiles ", key, val)
                if key == 'traj':
                    FILEmod[0][key]={} #needed !!!! 
                    continue
                FILEmod[0][key]=val  ###################### ME QUEDE AQUI
        file_ins={}
        filedyn_ins={}
        file_obj={}
        filedyn_obj={}
        print("\n\nINDEXL: ", indexl)
        for ii in indexl:
            file_ins[ii]={}
            filedyn_ins[ii]={}
            file_obj[ii]={}
            filedyn_obj[ii]={}
            indexcl=[]
            print("\nelemento ", ii, "en indexl")
            Scom_inst[ii]={}
            Scom_obj[ii]={}
            Pscompmod[ii]={}
            dyn_ins[ii]=dyndb_Dynamics(POSTimod[ii])
            for key,value in initDyn.items():
                dyn_ins[ii].data[key]=value
            if dyn_ins[ii].is_valid():
                dyn_objf[ii]=dyn_ins[ii].save(commit=False)   
                dyn_obj[ii]=dyn_ins[ii].save()
            else:
                print("errors in the form Dynamics", ii," ", dyn_ins[ii].errors)
            print("\nPOSTimod",ii,POSTimod[ii])
            for key,val in POSTimod[ii].items(): # hay que modificar esto!!!!
                if formc.search(key):
                    indexc=int(key.split("-")[1]) 
                    if indexc not in indexcl:
                        indexcl.append(indexc)
                        Pscompmod[ii][indexc]={}
                        Scom_inst[ii][indexc]={}
                        Scom_obj[ii][indexc]={}
                    Pscompmod[ii][indexc][key.split("-")[2]]=val
                      # print("\nPOSTimod keys",ii,POSTimod[ii].keys())
                    print("\nkey value compmod", key , val, key.split("-")[2],"indexc ", indexc," Index ii: ", ii)
                else:
                    if key in lkeydyncomp:
                        if len(indexcl)==0:
                            print("\nno hay formc\n")
                            indexcl.append(0)
                            Scom_inst[ii][0]={}
                            Scom_obj[ii][0]={}
                            Pscompmod[ii][0]={}
                        Pscompmod[ii][0][key]=val
            print("\nlista numero 0 \n",Pscompmod[ii][0].items() )
            print("\nlongitud de indexcl \n",len(indexcl),"dinamica",ii) 
            for iii in indexcl:
                print("ii y iii", ii," ", iii)
                Pscompmod[ii][iii]['id_dynamics']=dyn_obj[ii].pk
                Pscompmod[ii][iii]['id_molecule']=iii+1#modificar
                print("ii y iii", ii," ", iii, " Dictionary compound ", Pscompmod[ii][iii] )
                Scom_inst[ii][iii]=dyndb_Dynamics_Components(Pscompmod[ii][iii])
                if Scom_inst[ii][iii].is_valid():
                    Scom_obj[ii][iii]=Scom_inst[ii][iii].save(commit=False)
                    Scom_obj[ii][iii]=Scom_inst[ii][iii].save()
                else:
                    print("Errores en el form Simulation Components ", ii, " ", Scom_inst[ii][iii].errors.as_data()) 
            #Create storage directory: Every Simulation # has its own directory labeled as "dyn"+dyn_obj[ii].pk
            #Maybe we have to label the directory with submissionID?????
            direct=settings.MEDIA_ROOT+'Dynamics/dyn'+str(submission_id) 
            print("\nDirectorio a crear ", direct)
            if not os.path.exists(direct):
                os.makedirs(direct)
            print("Dynamica ",ii," print FILEmod[ii] ",FILEmod[ii].items())
            for key,val in FILEmod[ii].items():
                if key == 'traj':
                    i=0
                    file_ins[ii]['traj']={}
                    file_obj[ii]['traj']={}
                    filedyn_ins[ii][key]={}
                    filedyn_obj[ii][key]={}
                    for files in request.FILES.getlist('traj'):
                        print("TRAJ ",  files)
                        fext="".join(files.name.split(".")[1:])
                        initFiles['id_file_types']=dict_ext_id[fext]
                        initFiles['filename']=files.name
                        initFiles['filepath']=direct
                        file_ins[ii][key][i]=dyndb_Files(initFiles)
                        if file_ins[ii][key][i].is_valid(): 
                            file_obj[ii][key][i]=file_ins[ii][key][i].save()
                            newname=str(file_obj[ii][key][i].pk)+"_dyn_"+str(submission_id)+"_rep_"+str(i)+"."+fext
                            handle_uploaded_file(files,direct,newname)
                            completepath=direct+"/"+newname
                            file_obj[ii][key][i].filename=newname   #rename filename in the database after saving the initial name
                            file_obj[ii][key][i].filepath=completepath   #rename filename in the database after saving the initial name
                            file_obj[ii][key][i].save() 
                            dicfyndyn={}
                            dicfyndyn['type']=d_fdyn_t[key]
                            dicfyndyn['id_dynamics']=dyn_obj[ii].pk
                            dicfyndyn['id_files']=file_obj[ii][key][i].pk
                            print("numero de fichero ",i, "id_files", file_obj[ii][key][i].pk)
                            filedyn_ins[ii][key][i]=dyndb_Files_Dynamics(dicfyndyn)
                            if filedyn_ins[ii][key][i].is_valid():
                                filedyn_obj[ii][key][i]=filedyn_ins[ii][key][i].save()
                            else:
                                print("Errores en el form dyndb_Files_Dynamics ", ii, " ",key, " ", i," ",  filedyn_ins[ii][key].errors.as_data())
                        else:
                            iii1=file_ins[ii][key][i].errors.as_data()
                            print("file_ins[",ii,"]['traj'][",i,"] no es valido")
                            print("!!!!!!Errores despues del file_ins[",ii,"]['traj'][",i,"]\n",iii1,"\n")
                        i=i+1
                else:
                    fext="".join(val.name.split(".")[1:])
                    print("val ",val, " ;val split",fext," Tambien id",dict_ext_id[fext])
                    if fext in dict_ext_id.keys():
                        initFiles['id_file_types']=dict_ext_id[fext]
                        initFiles['filename']=val.name
                        initFiles['filepath']=direct
                    else:
                        print("This extension is not valid for submission")
                    file_ins[ii][key]=dyndb_Files(initFiles)
                    if file_ins[ii][key].is_valid(): 
                        dicfyndyn={}
                        file_obj[ii][key]=file_ins[ii][key].save()
                        newname=str(file_obj[ii][key].pk)+"_dyn_"+str(submission_id)+"."+fext
                        handle_uploaded_file(FILEmod[ii][key],direct,newname)
                        completepath=direct+"/"+newname
                        file_obj[ii][key].filename=newname   #rename filename in the database after saving the initial name
                        file_obj[ii][key].filepath=completepath #rename filepath to the one including the new filename in the database after saving the initial name
                        file_obj[ii][key].save() 
                        dicfyndyn['type']=d_fdyn_t[key]
                        dicfyndyn['id_dynamics']=dyn_obj[ii].pk
                        dicfyndyn['id_files']=file_obj[ii][key].pk
                        filedyn_ins[ii][key]=dyndb_Files_Dynamics(dicfyndyn)
                        if filedyn_ins[ii][key].is_valid():
                            filedyn_obj[ii][key]=filedyn_ins[ii][key].save(commit=False)
                            filedyn_obj[ii][key]=filedyn_ins[ii][key].save()
                        else:
                            print("Errores en el form dyndb_Files_Dynamics ", ii, " ",key, " ",  filedyn_ins[ii][key].errors.as_data())
                    else:
                        print("Errores en el form dyndb_Files ", ii, " ",key, " ",  file_ins[ii][key].errors.as_data())  
        return HttpResponseRedirect("/".join(["/dynadb/DYNAMICSfilled",submission_id,""]))
    else:
        qDS=DyndbDynamics.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).values_list('submission_id',flat=True)[0])
        ddown={}
        ddown['id_dynamics_methods']= DyndbDynamicsMethods.objects.filter(id=qDS.values_list('id_dynamics_methods',flat=True)[0]).values_list('type_name',flat=True)[0]
        ddown['id_assay_types']= DyndbAssayTypes.objects.filter(id=qDS.values_list('id_assay_types',flat=True)[0]).values_list('type_name',flat=True)[0]
        ddown['id_dynamics_membrane_types']=DyndbDynamicsMembraneTypes.objects.filter(id=qDS.values_list('id_dynamics_membrane_types',flat=True)[0]).values_list('type_name',flat=True)[0]
        ddown['id_dynamics_solvent_types']=DyndbDynamicsSolventTypes.objects.filter(id=qDS.values_list('id_dynamics_solvent_types',flat=True)[0]).values_list('type_name',flat=True)[0]
        print(qDS.values()[0])
        compl=[]
        dctypel=[]
        for tt in qDS.values_list('id',flat=True):
            qDC=DyndbDynamicsComponents.objects.filter(id_dynamics=tt).exclude(numberofmol=None,type=None).order_by('id')
            compl.append(qDC)
            d=0
            l_ord_mol=[]
            lcompname=[]
            for l in qDC:
                dctype=qDC.model.MOLECULE_TYPE[l.type][1]
                dctypel.append(dctype)
                d=d+1
                qName=DyndbCompound.objects.filter(id=DyndbMolecule.objects.filter(id=l.id_molecule_id).values_list('id_compound',flat=True)).values_list('name',flat=True)[0]
                lcompname.append(qName)
                l_ord_mol.append(d)
        dd=dyndb_Dynamics()
        ddC =dyndb_Dynamics_Components()
        qDMT =DyndbDynamicsMembraneTypes.objects.all().order_by('id')
        qDST =DyndbDynamicsSolventTypes.objects.all().order_by('id')
        qDMeth =DyndbDynamicsMethods.objects.all().order_by('id')
        qAT =DyndbAssayTypes.objects.all().order_by('id')
        return render(request,'dynadb/DYNAMICS.html', {'dd':dd,'ddC':ddC, 'qDMT':qDMT, 'qDST':qDST, 'qDMeth':qDMeth, 'qAT':qAT, 'qDS':qDS,'dctypel':dctypel,'lcompname':lcompname,'compl':compl,'l_ord_mol':l_ord_mol,'ddown':ddown,'submission_id':submission_id,'model_id':model_id})

def get_components_info_from_components_by_submission(submission_id,component_type='model'):
    if component_type not in {'model','dynamics'}:
        raise ValueError('"component_type" keyword must be defined as "model" or "dynamics"')
    if component_type == 'model':
        q = DyndbSubmissionModel.objects.filter(submission_id=submission_id,model_id__dyndbmodelcomponents__id_molecule__dyndbsubmissionmolecule__submission_id=submission_id)
        q = q.exclude(model_id__dyndbmodelcomponents__id_molecule=None).exclude(model_id__dyndbmodelcomponents__type=None)
        fields_list = DyndbModelComponents._meta.get_fields()
        path = 'model_id__dyndbmodelcomponents__'
    elif component_type == 'dynamics':
        q = DyndbDynamics.objects.filter(submission_id=submission_id,dyndbdynamicscomponents__id_molecule__dyndbsubmissionmolecule__submission_id=submission_id)
        q = q.exclude(dyndbdynamicscomponents__id_molecule=None).exclude(dyndbdynamicscomponents__type=None)
        fields_list = DyndbDynamicsComponents._meta.get_fields()
        path = 'dyndbdynamicscomponents__' 
    fields = dict()
    for field in fields_list:
        fields[field.name] = F(path+field.name)
    del fields['id']
    fields['name'] = F(path+'id_molecule__id_compound__name')
    fields['int_id'] = F(path+'id_molecule__dyndbsubmissionmolecule__int_id')
    fields['not_in_model'] = F(path+'id_molecule__dyndbsubmissionmolecule__not_in_model')
    q = q.annotate(**fields).order_by('int_id')
    q = q.values(*list(fields.keys()))
    print("valor q\n",q.query)
    return list(q)
        
def get_components_info_from_submission(submission_id,component_type=None):
    if component_type not in {'model','dynamics'}:
        raise ValueError('"component_type" keyword must be defined as "model" or "dynamics"')
    q = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(int_id=None)
    q = q.annotate(id_molecule=F('molecule_id'))
    field_ref = 'molecule_id__id_compound__name'
    if component_type == 'model':
        q = q.filter(not_in_model=False)
        q = q.annotate(namemc=F(field_ref))
        field_name = 'namemc'
    elif component_type == 'dynamics':
        q = q.filter(not_in_model=True)
        q = q.annotate(name=F(field_ref))
        field_name = 'name'
    q = q.values('int_id','id_molecule',field_name,'type')
    q = q.order_by('int_id')
    result = list(q)
    i = 0
    for row in result:
        result[i]['type'] = smol_to_dyncomp_type[result[i]['type']]
        i +=1
    return result

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed    
def MODELview(request, submission_id):
    def model_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        fdbF={}
        fdbFobj={}
       #####  
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
       ##############
        for key,val  in dname.items():
            fext="".join(val['path'].split(".")[1:])
            initFiles['id_file_types']=dict_ext_id[fext]
            initFiles['url']=val['url']
            initFiles['filename']="".join(val['path'].split("/")[-1])
            initFiles['filepath']=val['path']
            initFiles['description']="pdb crystal-derived assembly coordinates"
            fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
            dicfmod={}
            fdbFM={}
            if fdbF[key].is_valid():
                fdbFobj[key]=fdbF[key].save()
                dicfmod['id_model']=MFpk
                dicfmod['id_files']=fdbFobj[key].pk
            else:
                prev_entryFile=DyndbFiles.objects.filter(dyndbfilesmodel__id_model__dyndbsubmissionmodel__submission_id=submission_id)
                dicfmod['id_files']=prev_entryFile.values_list('id',flat=True)[0]
                dicfmod['id_model']=MFpk
                prev_entryFile.update(update_timestamp=timezone.now(),last_update_by_dbengine=user,filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])            
            fdbFM[key]=dyndb_Files_Model(dicfmod)
            if fdbFM[key].is_valid():
                fdbFM[key].save()
            else:
                prev_entryFileM=DyndbFilesModel.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id)
                prev_entryFileM.update(id_model=dicfmod['id_model'],id_files=dicfmod['id_files'])
    # Function for saving files
    request.session['info']="PASAR a SESSION"
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None,'id_structure_model':None, 'template_id_model':None,'model_creation_submission_id':submission_id,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user    }
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  }
    # Dealing with POST data
    if request.method == 'POST':
        lrps=[]
        l_checkinpostps=[]
        for o in request.POST.keys():
            if o.split("-")[0] == 'formps':
                lrps.append(("-").join(o.split("-")[:2]))
        lrps=list(set(lrps))
        for ll in ['name', 'pdbid','prot', 'resid_to', 'seq_resid_from', 'resid_from', 'seq_resid_to', 'chain']:
            if ll in ["name","pdbid"]:
                if request.POST[ll] == "":
                    error="\n\nPlease, fill any missing fields in the section A after submitting the form."
                    response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                else:
                    continue
            for o in lrps:
                l_checkinpostps.append(("-").join([o,ll]))
        for l in  l_checkinpostps:     
            if request.POST[l] == '':
                error="\n\nPlease, fill any missing fields in the section B cells and click validate after submitting the form."
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        lrmc=[]
        l_checkinpostmc=[]
        for o in request.POST.keys():
            if o.split("-")[0] == 'formmc':
                lrmc.append(("-").join(o.split("-")[:2]))
        lrmc=list(set(lrmc))
        for ll in ['namemc', 'resname', 'numberofmol']:
            for o in lrmc:
                l_checkinpostmc.append(("-").join([o,ll]))
        for l in  l_checkinpostmc:     
            if request.POST[l] == '':
                error="\n\nPlease, fill in the missing 'Resname' cells and click validate after submitting the form."
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        #Defining variables and dictionaries with information not available in the html form. This is needed for form instances.
        action="/".join(["/dynadb/MODELfilled",submission_id,""])
        now=timezone.now()
        author="jmr"
        user="jmr"
        author_id=1
        initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None,'id_structure_model':None, 'template_id_model':None,'model_creation_submission_id':submission_id,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user    }
        initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  }
        lkeyprotsour=["id_protein","id_model","chain","resid_from","resid_to","seq_resid_from","seq_resid_to","pdbidps","source_typeps","template_id_model","bonded_to_id_modeled_residues","prot"]  
        ckeyprotsour={'source_typeps':"source_type",'pdbidps':"pdbid"}
        lkeymodcomp=["id_molecule","id_model","molecule","namemc","numberofmol","resname","typemc"]
        ckeymodcomp={'namemc':"name",'typemc':"type"}
        dictpost=request.POST
        dictfiles=request.FILES
        formps=re.compile('formps-')
        formmc=re.compile('formmc-')
        dictmodel={}
        dictprotsour={}
        dictprotsourmod={}
        dictmodcomp={}
        dictmodcompmod={}
        indexpsl=[]
        indexmcl=[]
        for key,val in dictpost.items():
            if key in lkeyprotsour or formps.search(key):
                if key in lkeyprotsour:
                    print("\nkey en prot sour", key)
                    indexps=0
                    n=0# if n=0 the HTML name label is not modified by js and there is only one protein source!!
                else:
                    indexps=int(key.split("-")[1]) 
                    n=1# if n=1 the label has been modified by javascript    
                    print("\nkey en prot sour con formps", key)
                if indexps not in indexpsl:
                    indexpsl.append(indexps)
                try: 
                    dictprotsour[indexps]
                except KeyError:
                    dictprotsour[indexps]={}  
                    dictprotsourmod[indexps]={}  
                dictprotsour[indexps][key]=val
                if n == 1:
                   dictprotsourmod[indexps]["-".join(key.split("-")[2:])]=val
                elif n == 0:
                   dictprotsourmod[indexps][key]=val
            elif key in lkeymodcomp or formmc.search(key): 
                if key in lkeymodcomp:
                    indexmc=0
                    print("\nkey en mod comp", key)
                    m=0
                else:
                    indexmc=int(key.split("-")[1])
                    print("\nkey en mod comp formmc", key)
                    m=1 
                if indexmc not in indexmcl:
                    indexmcl.append(indexmc)
                try: 
                    dictmodcomp[indexmc]
                except KeyError:
                    dictmodcomp[indexmc]={}  
                    dictmodcompmod[indexmc]={}  
                dictmodcomp[indexmc][key]=val
                if m==1:
                    dictmodcompmod[indexmc]["-".join(key.split("-")[2:])]=val
                elif m==0:
                    dictmodcompmod[indexmc][key]=val
            else:
                dictmodel[key]=val
        print ("\ndictmodel:\n", dictmodel)
        print ("\nOOOOOOOOOOOOOOOOOOO dictmodcompmod:\n", dictmodcompmod)
        indexpsl.sort()
        indexmcl.sort()
        print("MIRAR INDICES",indexpsl,"\n",indexmcl)

        def check_overlap_interval(intervalA,intervalB):
            ### Check if two intervals overlap 
            ### the input arguments are two tuples. the first one
            if not (type(intervalA)==tuple  and type(intervalB)==tuple):
                response= "both input items must be tuples"
                return response
            if not (type(intervalA[0])==int  and type(intervalA[1])==int and type(intervalB[0])==int  and type(intervalB[1])==int):   
                response= "the elements in the tuples must be integers"
                return response
            if intervalA[0] > intervalA[1] or intervalB[0] > intervalB[1]:
                response= "the first element of the tuple must be the smallest value"
                return response
            print (intervalA," ",intervalB)
            if intervalA[0] < intervalB[0]:
                small_init=intervalA
                big_init=intervalB
            elif intervalA[0] > intervalB[0]: 
                small_init=intervalB
                big_init=intervalA
            else:
                print("IGUALES!!!")
                overlap=True
                return overlap
            print(big_init, small_init)
            if big_init[0] <= small_init[1]:
                print("PIPOL",big_init[0], small_init[1])
                overlap=True
            else:
                overlap=False
            print(overlap)
            return overlap

        def overlappproteins(protseg):
            used_prot_seg_list=[]
            print("\nPROTSEG",protseg)
            for key,val in protseg.items():
                intervalA=(int(val['seq_resid_from']),int(val['seq_resid_to']))
                used_prot_seg_list.append(key)
                overlap_answer_list=[]
                for k,v in protseg.items():
                    if k not in used_prot_seg_list:
                        intervalB=(int(v['seq_resid_from']),int(v['seq_resid_to']))
                        ooo=check_overlap_interval(intervalA,intervalB)
                        print("En overlappproteins",ooo)
                        overlap_answer_list.append(ooo)  
                        if type(ooo)==str:
                           return ooo
                        if ooo:
                           return True             
            return False  
        
        apoform_NOT_ok=overlappproteins(dictprotsourmod)
        if type(apoform_NOT_ok)==str:
            resp="Please check the numbering in the \"Curated protein data\" section. \"From seq res\" < \"To seq res\". These values depends on \"From res\" and \"To res\", respectively."
            response = HttpResponse(resp,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
        if dictmodel['type']==0:
            if apoform_NOT_ok:
                resp="Please change the type to complex or check the numbering in the \"Curated protein data\" section"
                response = HttpResponse(resp,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        for i in indexpsl:
            print ("\ndictprotsour",i,":\n", dictprotsour[i])
            print ("\ndictprotsourmod",i,":\n", dictprotsourmod[i])
            
        for i in indexmcl:
            print ("\ndictmodcomp",i,":\n", dictmodcomp[i])
            print ("\ndictmodcompmod",i,":\n", dictmodcompmod[i])

######## 150
        ########   Query for obtaining molecules submitted in the current submission!!!!
        qSMolecules=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).filter(not_in_model=False).exclude(int_id=None)
        qSMol=qSMolecules.filter(type__lt=2)
        molid_typel=dict(qSMol.values_list('molecule_id','type'))
        #molid_typel=dict(set(qSMol.values_list('molecule_id','type')))
        lmol_in_modelbs =qSMol.values_list('molecule_id',flat=True)
        lmol_in_model=list(set(lmol_in_modelbs)) ###Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only cares about the type of element involved in the model, not about the number of elements
 
        ########   Query for obtaining Proteins submitted in the current submission!!!!
        qSProt=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
        lprot_in_model=qSProt.values_list('protein_id',flat=True)
        lprot_in_model=list(set(lprot_in_model))  ###Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only care about the type of element involved in the model, not about the number of elements. Actually repeated elements should not be submitted. This is just for assuring it

        ########   Query for obtaining Proteins submitted in the current submission!!!!
        qM=DyndbMolecule.objects.filter(id__in=lmol_in_model)
        comptomol=dict(list(set(qM.values_list('id_compound','id')))) #needed to get the list of compounds involved in the submission
        lcomp_in_modelbs=qM.values_list('id_compound',flat=True)  
        lcomp_in_model=list(set(lcomp_in_modelbs)) ####Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only care about the type of element involved in the model, not about the number of elements

########   Check if the Complex_Exp and the Complex_Molecule are already in the GPCRmd DB. IT IS NEEDED A VERY COMPLEX QUERY IN RAW SQL
            # Complex stand for the sets of proteins (and compounds/molecules) disregarding the number of items involved in the model
            #lists for creating the query targeting the COMPLEX_EXP and COMPLEX_MOLECULE (if it proceeds... note a complex molecule does not make sense in a complex exp involving only proteins) matching the current one being submitted if it exist previously in the database!!!!!
            # COMPLEX_EXP involves proteins and may involve (if they exist) Compounds in the Model. COMPLEX_MOLECULE involves proteins and the specific form of the compounds (molecules) in the model (Complex_Molecule only makes sense if there are molecules in the model)
        scol=[] #SELECT clause of the QUERY
        From=[] #FROM clause of the QUERY
        where=[]   #WHERE clause of the QUERY
        p=0
        Find_Complex=False
        if len(lprot_in_model)==1 and len(lmol_in_model)==0:   
            resp = 'There is a single Protein entry involved in the Model!!! No molecules are included in it!!! This model may involve either a single Protein Aporform or a HOMOOLIGOMER!!'
            print(resp)
            if apoform_NOT_ok:
                if dictmodel['type']==1: #it is not possible apoform_NOT_ok and dictmodel['type']==0:
                    Find_Complex=True
            else:
                message = '\nNo complex Protein is used in this Model!!! This model involves a just a Protein Aporform!!'
        else:
            Find_Complex=True

        if Find_Complex:
            for pid in lprot_in_model:
                p=p+1
                tp=("").join(["t",str(p)])
                if pid==lprot_in_model[0]:
                    tinit=tp
                    scol.append(("").join(["SELECT ",tp,".id_complex_exp "]))
                    #scolmol.append(("").join(["SELECT ",tp,".id_complex_exp, ",tp,".id_protein"]))
                    From.append(("").join(["FROM dyndb_complex_protein AS ",tp]))
                    where.append(("").join(["WHERE ",tp,".id_protein = ", str(pid)]))
                else:
                    #scolmol.append(("").join([", ",tp,".id_protein "]))
                    From.append(("").join([" INNER JOIN dyndb_complex_protein AS ",tp," ON ",tinit,".id_complex_exp = ", tp,".id_complex_exp "]))
                    where.append(("").join([" AND ",tp,".id_protein = ", str(pid)]))
            print( "JJJJJOOOOOLLLL"  )
            if len(lmol_in_model)==0: #If there is not any molecule in the model the query is focused on the proteins (QUERYp)
               # where.append(("AND tcm.id_complex_exp IS NULL;"))
 
                SELp=(" ").join(scol)
                FROMp=(" ").join(From)
                WHEREp=(" ").join(where)
                QUERYp=(" ").join([SELp,FROMp,WHEREp]) #QUERY when no molecule is involved in the model
 
                with connection.cursor() as cursor:
                    cursor.execute(QUERYp)
                    row=cursor.fetchall()
                    if len(list(row))==0:
                        rowl=[]
                    else:
                        ROWLp=[]
                        for line in row:# row may contain one or several hits!! let's obtain their corresponding id_complex_exp(line[0])
                            ROWLp.append(line[0]) 
                        # Let's get the id_complex_exp of complexes involving just the same proteins in our submission and NO ONE ELSE!!!!! There should be only one result. To do so we have to exclude complex_exp containing compounds!!!!
                        p=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLp).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model)).exclude(id_complex_exp__in=DyndbComplexCompound.objects.filter(id_complex_exp__gt=0).values_list('id_complex_exp',flat=True))
                        if(len(p)>1):# Complexes involving exactly the same proteins in our submission is higher than one
                            response = HttpResponse('Several complex_exp entries involving exactly the same set of proteins exist in the GPCRmd DB... Please Report that error to the GPCRmd administrator',status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
                        elif(len(p)==1):
                            ce=p[0]['id_complex_exp']
                            rowl=[ce] #Complex exp
                            CE_exists=True 
            else: # otherwise molecules should be included in the query. Two queries are needed... Complex_Compound (QUERYComp) and Complex_Molecule (QUERY)
                scolComp=scol[:]
                FromComp=From[:]
                whereComp=where[:]
                s=p
                for cid in lcomp_in_model: #Query complex_compound IT IS NEEDED WHEN NO COMPLEX_MOLECULE involving the exact type of molecules in the submission exist but COMPLEX_EXP involving COMPOUNDS in the submission does 
                    s=s+1
                    sp=("").join(["t",str(s)])
                    #scolComp.append(("").join([", ",sp,".id_compound"]))
                    FromComp.append(("").join([" LEFT OUTER JOIN dyndb_complex_compound AS ", sp, " ON ",tinit,".id_complex_exp = ", sp,".id_complex_exp"]))
                    whereComp.append(("").join([" AND ",sp,".id_compound = ", str(cid)]))
                    if cid==lcomp_in_model[-1]:
                        whereComp.append(";")
                SELComp=(" ").join(scolComp)
                FROMComp=(" ").join(FromComp)
                WHEREComp=(" ").join(whereComp)
                QUERYComp=(" ").join([SELComp,FROMComp,WHEREComp])
 
    #  ##### MAKING THE COMPOUND-WISE QUERY 
                ROWLCompe=[]
                #the QUERYComp is needed in order to check if the Complex_Exp exists regardless the specific Complex_molecule does
                with connection.cursor() as cursor:
                    cursor.execute(QUERYComp)
                    rowComp=cursor.fetchall()
                    if len(list(rowComp))==0:
                        rowCompl=[]
                    else:
                        for line in rowComp:# rowComp may contain one or several hits!! let's obtain their corresponding id_complex_exp(line[0] 
                            ROWLCompe.append(line[0]) 
                        # id_complex_exp of complexes with exactly the same compounds in our submission
                        cec=DyndbComplexCompound.objects.filter(id_complex_exp__in=ROWLCompe).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lcomp_in_model))
                        a=set(cec.values_list('id_complex_exp',flat=True))
                        # id_complex_exp of complexes with the same number of protein than our submission
                        cep=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLCompe).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model))  
                        b=set(cep.values_list('id_complex_exp',flat=True))
                        rowCompl=list(a&b) # if the id_complex is in both lists cep and cec this is the complex we are looking for
                        print( "JJJJJOOOOOLLLL    2"  )
                        if len(rowCompl) > 1:
                            response = HttpResponse('Several complex_exp entries involving exactly the same set of proteins and compounds exist in the GPCRmd DB... Please Report that error to the GPCRmd administrator',status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
            CE_exists=False
            CM_exists=False
            if len(lmol_in_model)==0: #Protein_Protein Complex
                if len(row) > 0: #A Complex_Exp exists for the current model. The query in rowl only consider proteins!!!!
                    print("COMPLEX_EXP: ", ce,"\nCOMPLEX_MOLECULE (MOLECULES+PROTEINS) None No molecule " ) 
                    print("This Model has a Complex EXP but neither a Complex MOLECULE nor A complex Compound and stored in the database")
                    CE_exists=True #The entries in Complex_Exp and Complex_Molecule do not have to be registered
                    CM_exists=True #if there is a complex_exp and the complex does not involve any compound the CM must exist 
                    CEpk=rowl[0] #defined in the block making the QUERYp and its processing:
                    id_complex_molecule=DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).values_list('id',flat=True)[0]
            if len(lmol_in_model)>0: #There are molecules in the complex!!!!
                if len(rowCompl) > 0: #Actually should be one or 0. If > 0 the corresponding complex_exp is in the GPCRmd database and the complex_compound entry
                    Upd_Comp_Type_l=[] #list of tupples containing info about wether the compound type has been updated
                    print( "JJJJJOOOOOLLLL    3"  )
                    print("COMPLEX_EXP: ", rowCompl[0],"\n")
                    CE_exists=True # If Complex_Exp exists Complex_Compound exist for sure
                    CEpk=rowCompl[0]
                    #### CHECK if the COMPOUND_TYPE PRIORITY OF THE COMPLEX_COMPOUND TYPE HAS TO BE UPDATED 
                    qCompType=DyndbComplexCompound.objects.filter(id_complex_exp=CEpk)
                    for l in qCompType.values_list('id_compound','id_complex_exp','type').order_by('id_compound'):
                        sub_molec_type=qSMol.filter(molecule_id__in=DyndbMolecule.objects.filter(id_compound=l[0]).values_list('id',flat=True)).values_list('type',flat=True)
                        min_molec_type =min(sub_molec_type)
                        print("MIN MOLEC ",min_molec_type,"complex_compound", l[0])
                        lid_type=l[0]
                        print("NO updated value" )
                        if min_molec_type < l[2]:
                            DyndbComplexCompound.objects.filter(id_compound=l[0]).filter(id_complex_exp=CEpk).update(type=min_molec_type)
                            comp_type_t=(True,l[0],l[1],l[2],min_molec_type)#l[0] = id_compound;l[1]=id_complex_exp l[2]= type before updating; min_molec_type= updated value if True
                                                                             # min_molec_type= type value in the current model. Field updated because if True. If error in submission
                                                                             #should be updated back to the l[2] value
                            print("updated value" )
                        else:
                            comp_type_t=(False,l[0],l[1],l[2],min_molec_type)#l[0] = id_compound;l[1]=id_complex_exp l[2]= type before updating;
                                                                             # min_molec_type= type value in the current model. Field not  updated because if False
                        Upd_Comp_Type_l.append(comp_type_t)
 
                    ##### MAKING THE MOLECULE-WISE QUERY 
                    scolmol=[] #SELECT clause of the QUERY
                    FromMOL=[] #FROM clause of the QUERY
                    where=[]   #WHERE clause of the QUERY
                    p=1
                    ### The next QUERY is based on the fact that id_complex_exp is already known at the CEpk. As one Complex_exp involving a Compound can be associated with complex molecules involving several forms (molecules) of this compound, we have to check that the selected complex molecule involve the correct number of molecules.
                    tp=("").join(["t",str(p)])
                    tcm=tp
                    scolmol.append(("").join(["SELECT ",tp,".id_complex_exp "]))
                    FromMOL.append(("").join(["FROM dyndb_complex_molecule AS ",tp]))
                    where.append(("").join(["WHERE ",tp,".id_complex_exp = ",str(CEpk)]))
                    for mid in lmol_in_model:  #Part of the Query involving molecules present in the Complex
                        p=p+1
                        tp=("").join(["t",str(p)])
                        #scolmol.append(("").join([", ",tp,".id_molecule"]))
                        FromMOL.append(("").join([" LEFT OUTER JOIN dyndb_complex_molecule_molecule AS ", tp, " ON ",tcm,".id = ", tp,".id_complex_molecule"]))
                        where.append(("").join([" AND ",tp,".id_molecule = ", str(mid)]))
                        if mid==lmol_in_model[-1]:
                            scolmol.append(("").join([", ",tp,".id_complex_molecule"])) 
                            where.append(";")
                    SEL=(" ").join(scolmol)
                    FROM=(" ").join(FromMOL)
                    WHERE=(" ").join(where)
                    QUERY=(" ").join([SEL,FROM,WHERE])
                    print(QUERY)
                    ROWLm=[]#list of complex_molecules matching the  set of Molecules from the QUERY
                    with connection.cursor() as cursor:
                        cursor.execute(QUERY)
                        row=cursor.fetchall()
                        if len(list(row))==0:
                            rowl=[]
                        else:
                            for line in row:# row may contain one or several hits!! Several id_complex_molecule (line[-1]) can exist!!!
                                ROWLm.append(line[-1]) 
                            # id_complex_molecule of complexes with the same number of molecules than our submission
                            a=DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule__in=ROWLm).values('id_complex_molecule').annotate(num=Count('id_complex_molecule')).filter(num=len(lmol_in_model))
                            lmcm=a.values_list('id_complex_molecule',flat=True)[0]
                            rowl=[CEpk,lmcm]
                    print("SEVILLA!!!")
                    if len(rowl) >0: # The Complex_molecule is also in the GPCRmd database
                        print("COMPLEX_MOLECULE: ", rowl[-1],"\n The current Complex molecule already exists in the database")
                        CM_exists=True
                        print(type(rowl[-1]))
                        print(rowl)
                        id_complex_molecule=rowl[-1]
                        print("CM_exists= True ",id_complex_molecule)
            if CE_exists==False:
                fdbCE=dyndb_Complex_Exp(initMOD) 
                if fdbCE.is_valid():
                    fdbCEobj=fdbCE.save()
                    CEpk=fdbCEobj.pk
                else:
                    iii1=fdbCE.errors.as_text()
                    print("Errores en el form dyndb_Complex_Exp\n ", iii1)                
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                for prot in lprot_in_model:
                    fdbComP=dyndb_Complex_Protein({'id_protein':prot,'id_complex_exp':CEpk})
                    if fdbComP.is_valid():
                        fdbComPobj=fdbComP.save()
                    else:
                        iii1=fdbComP.errors.as_text()
                        print("Errores en el form dyndb_Complex_Protein\n ", fdbComP.errors.as_data())    
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbComplexExp.objects.filter(id=CEpk).delete()
                        return response
                if len(lmol_in_model)>0: 
                    for comp in  lcomp_in_model: #no Complex containing these set of compounds and proteins exists in the database. Record a new entry
                        fdbComComp=dyndb_Complex_Compound({'id_complex_exp':CEpk,'id_compound':comp ,'type':molid_typel[comptomol[comp]],'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() })
                        if fdbComComp.is_valid():
                            fdbComComp.save()
                        else:
                            iii1=fdbComP.errors.as_text() 
                            print("Errores en el form dyndb_Complex_Compound\n ", fdbComP.errors.as_text())
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            DyndbComplexProtein.objects.filter(id_protein__in=lprot_in_model).filter(id_complex_exp=CEpk).delete()
                            DyndbComplexExp.objects.filter(id=CEpk).delete()
                            return response
            if CM_exists==False:   #No Complex containing the set of compounds has been recorded. !!!COMPLEX_EXP with no molecules need COMPLEX_MOLECULE to link with the MODEL OBJECT!!!!
                print ("POR AQUI")
                fdbComMol=dyndb_Complex_Molecule({'id_complex_exp':CEpk,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now(),'created_by_dbengine':author, 'last_update_by_dbengine':author, 'created_by':author_id,'last_update_by':author_id})
                if fdbComMol.is_valid():
                    fdbComMolobj=fdbComMol.save()
                    ComMolpk=fdbComMolobj.pk
                    id_complex_molecule=ComMolpk
                    print("CM_exist= False ",id_complex_molecule)
                else:
                    iii1=fdbComMol.errors.as_text() 
                    print("Errores en el form dyndb_Complex_Molecule\n ", iii1)
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    if CE_exists==False:# There was not any entry for the current complex after submitting the current data. We have to delete the registered info if the view raises an error 
                        DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
                        DyndbComplexProtein.objects.filter(id_protein__in=lprot_in_model).filter(id_complex_exp=CEpk).delete()
                        DyndbComplexExp.objects.filter(id=CEpk).delete()
                    else:
                        for comp_type_t in Upd_Comp_Type_l:
                            #comp_type_t=(True,l[0],l[1],l[2],min_molec_type)---> l[0] = id_compound;l[1]=id_complex_exp l[2]= type before updating; min_molec_type= updated value if True
                            if comp_type_t[0]:
                                DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
                    return response
                if len(lmol_in_model)>0:
                    for obj in qSMol.values():
                        fdbComMolMol=dyndb_Complex_Molecule_Molecule({'id_complex_molecule':id_complex_molecule,'id_molecule':obj['molecule_id_id'],'type':obj['type']})
                        if fdbComMolMol.is_valid():
                            fdbComMolMol.save()
                        else:
                            iii1=fdbComMolMol.errors.as_text() 
                            print("Errores en el form dyndb_Complex_Molecule_Molecule\n ", fdbComMolMol.errors.as_text())
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            if CE_exists==False:#There wasn't any entry for the current complex after submitting the current data. We have to delete the registered info if the view raises an error 
                                DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
                                DyndbComplexProtein.objects.filter(id_protein__in=lprot_in_model).filter(id_complex_exp=CEpk).delete()
                                DyndbComplexExp.objects.filter(id=CEpk).delete()
                            else:
                                for comp_type_t in Upd_Comp_Type_l:
                                   #comp_type_t=(True,l[0],l[1],l[2],min_molec_type)---> l[0] = id_compound;l[1]=id_complex_exp l[2]= type before updating; min_molec_type= updated value if True
                                    if comp_type_t[0]:
                                        DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
                            DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
                            return response
            if int(dictmodel['type'])==1:
                dictmodel['id_protein']=None
                if len(lmol_in_model)==0:
                    dictmodel['id_complex_molecule']=None
                else:
                    dictmodel['id_complex_molecule']=id_complex_molecule
            else:
                dictmodel['id_protein']=lprot_in_model[-1]
                dictmodel['id_complex_molecule']=None
        print("HHHHHHHHHHHHH")
        print (dictmodel)
        fdbMF = dyndb_Model(dictmodel)
        for key,value in initMOD.items():
            fdbMF.data[key]=value
        if not Find_Complex:
            apoform_id_prot=qSProt.values_list('protein_id',flat=True)[0]
            fdbMF.data['id_protein']=apoform_id_prot
#            fdbMF.data['id_complex_molecule']=None 
        Update_MODEL=False
        qMe=DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id)
        qMecsid=DyndbModel.objects.filter(model_creation_submission_id=submission_id)
        if not qMe.exists():
            if not qMecsid.exists():
                PREVIOUS_COMP=False
                PREVIOUS_PROT_FRAG=False
                if fdbMF.is_valid():
                    fdbMFobj=fdbMF.save()
                    MFpk=fdbMFobj.pk
                else:
                    iii1=fdbMF.errors.as_text() 
                    print("Errores en el form dyndb_Models\n", iii1)
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
            else:
                Update_MODEL=True
        else:
            Update_MODEL=True
        print ("\n",Update_MODEL,"UPDATE MODEL")
        if Update_MODEL:
            PREVIOUS_COMP=True
            PREVIOUS_PROT_FRAG=True
            print(qMe.exists())
            if qMe.exists():
                MFpk=qMe.values_list('id',flat=True)[0]
            else:
                MFpk=qMecsid.values_list('id',flat=True)[0]
            if fdbMF.data['type'] == '1':
                qMe.update(update_timestamp=timezone.now(), description=fdbMF.data['description'].strip() ,name=fdbMF.data['name'] ,type =fdbMF.data['type'] ,id_protein =None ,id_complex_molecule=id_complex_molecule , source_type=fdbMF.data['source_type'] ,pdbid=fdbMF.data['pdbid'] ,template_id_model=fdbMF.data['template_id_model'] ,id_structure_model=fdbMF.data['id_structure_model']  )
            else:
                qMe.update(update_timestamp=timezone.now(), description=fdbMF.data['description'].strip() ,name=fdbMF.data['name'] ,type =fdbMF.data['type'] ,id_protein =fdbMF.data['id_protein'] , id_complex_molecule=None , source_type=fdbMF.data['source_type'] ,pdbid=fdbMF.data['pdbid'] ,template_id_model=fdbMF.data['template_id_model'] ,id_structure_model=fdbMF.data['id_structure_model']  )
       #Fill the dyndb_Submission_Model form. Remember there is just a single Model for each submission !!!!
        if not qMe.exists():
            dictSMd={'model_id':MFpk,'submission_id':submission_id}
            fdbSMd=dyndb_Submission_Model(dictSMd)
            if fdbSMd.is_valid():
                fdbSMd.save()
            else:
                iii1=fdbSMd.errors.as_text()
                print("fdbSMd no es valido")
                print("!!!!!!Errores despues del fdbSMd\n",iii1,"\n")
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        #Create storage directory: Every MODEL has its own directory in which the corresponding pdb file is saved. This directory is labeled as "PDBmodel"+ MFpk (primary key of the model)
        #Maybe we have to label the directory with submissionID?????
        pathpdb=get_file_paths("model",url=False,submission_id=submission_id)
        namepdb=get_file_name_submission("model",submission_id,formid=0,ext="pdb",subtype="pdb")
        urlpdb=get_file_paths("model",url=True,submission_id=submission_id)
        path_namefpdb=("").join([pathpdb,namepdb]) 
        url_namefpdb=("").join([urlpdb,namepdb]) 
        dname={'dnamepdb':{'path':path_namefpdb,'url':url_namefpdb}}
        ooo= model_file_table(dname,MFpk)
        if type(ooo)==HttpResponse:
            print("http!!!!!!!!")
            return ooo
        fdbPS={} 
        fdbPSobj={} 
        qMR=DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id,source_type__gte=0,id_protein__dyndbsubmissionprotein__submission_id=submission_id).order_by('resid_from')
        qMRl=list(qMR.values_list('id_model','id_protein','resid_from','resid_to','seq_resid_from','seq_resid_to','id_protein__dyndbsubmissionprotein__int_id','chain','segid','pdbid','bonded_to_id_modeled_residues','id').order_by('resid_from'))#the 11th element of the tuple is the id in model components
        for ii in indexpsl:
            if "segid" not in dictprotsourmod[ii].keys():
                dictprotsourmod[ii]['segid']=''
            if "chain" not in dictprotsourmod[ii].keys():
                dictprotsourmod[ii]['chain']=''
            dictprotsourmod[ii]['id_model']=MFpk
            dictprotsourmod[ii]['template_id_model']=None
            dictprotsourmod[ii]['id_protein']=qSProt.values().filter(int_id=int(dictprotsourmod[ii]['prot'])-1)[0]['protein_id_id']
            dictprotsourmod[ii]['source_type']=dictprotsourmod[ii].pop('source_typeps')
            dictprotsourmod[ii]['pdbid']=dictprotsourmod[ii].pop('pdbidps')
            if dictprotsourmod[ii]['pdbid'] == "None":
                dictprotsourmod[ii]['pdbid']=None
            if (ii == indexpsl[0]) or ('bonded_to_id_modeled_residues' not in dictprotsourmod):
                dictprotsourmod[ii]['bonded_to_id_modeled_residues']=None
                print("indexpsl", dictprotsourmod[ii]['bonded_to_id_modeled_residues'], indexpsl)
        qlinecounter=-1
        if len(qMRl)>0:    
            for key,val in dictprotsourmod.items():
                print("TTT")
                qlinecounter=qlinecounter+1
                if key != indexpsl[0]: 
                    print ("\n  keys dictprot form ",dictprotsourmod[key].keys())
                    if "bonded_to_id_modeled_residues" in dictprotsourmod[key].keys():
                        if qlinecounter <= len(qMRl):
                            dictprotsourmod[key]['bonded_to_id_modeled_residues']=qMRl[qlinecounter-1][11]
                        else:
                            print("\n sourmod",dictprotsourmod[key])
                            print( int(dictprotsourmod[key]['seq_resid_from'])-1, int(dictprotsourmod[key]['id_protein']))
                            try:  
                                dictprotsourmod[key]['bonded_to_id_modeled_residues']=DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id,source_type__gte=0,id_protein__dyndbsubmissionprotein__submission_id=submission_id,seq_resid_to=(int(dictprotsourmod[key]['seq_resid_from'])-1),id_protein=int(dictprotsourmod[key]['id_protein'])).values_list('id',flat=True)[0] 
                            except:
                                keyi1=(" ").join(["Please, be careful with the 'bond' checkbox in the row ",str(key+1)," from the table 'Curated protein data'"])
                                response = HttpResponse(keyi1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                                return response
                    else:
                        print ("\n  keys dictprot NOT form ",dictprotsourmod[key].items())
                        dictprotsourmod[key]['bonded_to_id_modeled_residues']=None
                else:
                    dictprotsourmod[key]['bonded_to_id_modeled_residues']=None
                    print ("\n In the first line of the protein should be bonded_to_id_modeled_residues=None",dictprotsourmod[key].items())
                l_qrows_used=[]
                formline=(int(dictprotsourmod[key]['id_model']),int(dictprotsourmod[key]['id_protein']),int(dictprotsourmod[key]['resid_from']),int(dictprotsourmod[key]['resid_to']),int(dictprotsourmod[key]['seq_resid_from']),int(dictprotsourmod[key]['seq_resid_to']),int(dictprotsourmod[key]['prot'])-1,dictprotsourmod[key]['chain'],dictprotsourmod[key]['segid'],dictprotsourmod[key]['pdbid'],dictprotsourmod[key]['bonded_to_id_modeled_residues'])
                try:
                    len(qMRl[qlinecounter])>0 #if number of qMRl rows is less than qlinecounter len((qMRl[qlinecounter])==0. No more DB lines to update except:
                    print("len qMRl[qlinecounter]",qMRl[qlinecounter])
                    print(formline)
                    print(qMRl[qlinecounter][:11])  
                    if formline == qMRl[qlinecounter][:11]: #the 11th element of the tuple is the id in model components
                        print ("protein source line ", key, "queryline", qlinecounter, "is the same in the query")
                        continue
                    else:
                        print("Do not match")
                        qMR.filter(id=qMRl[key][11]).update(id_model=int(dictprotsourmod[key]['id_model']),id_protein=int(dictprotsourmod[key]['id_protein']),resid_from=int(dictprotsourmod[key]['resid_from']),resid_to=int(dictprotsourmod[key]['resid_to']),seq_resid_from=int(dictprotsourmod[key]['seq_resid_from']),seq_resid_to=int(dictprotsourmod[key]['seq_resid_to']),chain=dictprotsourmod[key]['chain'],segid=dictprotsourmod[key]['segid'],pdbid=dictprotsourmod[key]['pdbid'],bonded_to_id_modeled_residues=dictprotsourmod[key]['bonded_to_id_modeled_residues'])
                        print("protein segment updated")
                except:
                    print(dictprotsourmod[key])       
                    fdbPS[key] = dyndb_Modeled_Residues(dictprotsourmod[key])
                    if fdbPS[key].is_valid():                                                                                                                                                                                            
                        fdbPSobj[key]=fdbPS[key].save(commit=False)
                        fdbPSobj[key]=fdbPS[key].save()
                        print("\n__________________Se ha grabado la linea del form: ", key+1, "  ", dictprotsourmod[key])
                        fdbPSobj[key].pk
                    else:
                        keyi1=fdbPS[key].errors.as_text()
                        print("Errores en el form dyndb_Modeled_Residues\n ", fdbPS[key].errors.as_text())
                        response = HttpResponse(keyi1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
            if len(indexpsl)<len(qMRl):
                id_list=[]
                for i in range(len(indexpsl),len(qMRl)):
                    id_list.append(qMRl[i][11])
                qMR.filter(id__in=id_list).delete()
            #update the 'bonded_to_id_modeled_residues' field in rows beyond the length of the data stored in the DB                                                                                                                                                                                     
        else:
            for ii in dictprotsourmod.keys():
                if dictprotsourmod[ii]['bonded_to_id_modeled_residues'] == 'on':
                    dictprotsourmod[ii]['bonded_to_id_modeled_residues']= fdbPSobj[ii-1].pk  
                fdbPS[ii] = dyndb_Modeled_Residues(dictprotsourmod[ii])
                if fdbPS[ii].is_valid():                                                                                                                                                                                            
                    fdbPSobj[ii]=fdbPS[ii].save(commit=False)
                    fdbPSobj[ii]=fdbPS[ii].save()
                    print("\n__________________Se ha grabado la linea del form: ", ii+1, "  ", dictprotsourmod[ii])
                    fdbPSobj[ii].pk
                else:
                    iii1=fdbPS[ii].errors.as_text()
                    print("Errores en el form dyndb_Modeled_Residues\n ", fdbPS[ii].errors.as_text())
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response 
        fdbMC={} 
        fdbMCobj={} 
#       _    NEW MODEL COMPONENTS BLOCK ADAPTED FROM DYNAMICS COMPONENTS   _________________________________________________________ 

        invMOL_TYPE=dict((v,k) for k, v in dict(DyndbModelComponents.MOLECULE_TYPE).items()) # use if dropdown box in the html is converted to input
        for ii in indexmcl:
            print("\nTYPEMC",dictmodcompmod[ii]['typemc'])
            dictmodcompmod[ii]['id_model']=MFpk
            dictmodcompmod[ii]['name']=dictmodcompmod[ii].pop('namemc')
            dictmodcompmod[ii]['id_molecule']= qSMolecules.filter(int_id=int(dictmodcompmod[ii]['molecule'])-1).values_list('molecule_id',flat=True)[0]
            dictmodcompmod[ii]['type']=dictmodcompmod[ii].pop('typemc')
            print ("\ndictmodcompmod type  name y id_model",i,":\n", dictmodcompmod[ii]['type'], dictmodcompmod[ii]['name'],  dictmodcompmod[ii]['id_model'])
        if PREVIOUS_COMP==False:
            for ii in indexmcl:
                fdbMC[ii] = dyndb_Model_Components(dictmodcompmod[ii])

                if fdbMC[ii].is_valid():
                    fdbMCobj[ii]=fdbMC[ii].save()
                else:
                    iii1=fdbMC[ii].errors.as_text()
                    print("Errores en el form dyndb_Model_Components\n ", iii1 )
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        else: 
            print("\n __________________________else")
            qDC_match_form=DyndbModelComponents.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id).exclude(numberofmol=None,type=None)
            lDC_match_form=list(qDC_match_form.values('id','id_model','resname','id_molecule','numberofmol'))
            qDC_empty_rows=DyndbModelComponents.objects.filter(numberofmol=None,type=None,id_model=None)
            lempty_rows=list(qDC_empty_rows.values_list('id',flat=True))
            lenCompDB=len(lDC_match_form)
            lenform=len( dictmodcompmod)
            used_el=[]#table lines matching lines in the form. numberof mol would be updated
            del_el=[]#db lines which no longer takes part in the updated model. Will be reusable in whatever new entry
            used_val=[]# form value matching a db entrie. The number of mol in the db will be updated if needed
            new_val=[]#new form compound to be registered. We ll use a reusable entry if available. 
            counterf=0 # it counts the compounds in the form during the loop
            BREAK1=False
            BREAK2=False
            for key,val in dictmodcompmod.items(): #comparison between form info and dB. If different update.
                if len(used_el)==len(lDC_match_form):
                    print("\nBREAK1 used_el == dB el; counterf==   ", counterf)
                    qel_let_fval=True #num query elements less than form lines!!!!
                    break
                counterf=counterf+1
                for el in lDC_match_form:
                    if len(used_val)==len(dictmodcompmod):
                        qel_bit_fvl=True #num query elements > than form lines!!!!
                        break
                    print("AUN      NNNNNNNNNNNNN")
                    if el in used_el:
                        continue
                    if int(el['id_molecule'])==int(val['id_molecule']) and el['resname'].strip()==val['resname'].strip() and int(el['id_model'])==int(val['id_model']):
                        print("\n __________________________igual")
                        if not el['numberofmol'] == val['numberofmol']:
                            qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol']) #updating entries with the same compound
                        used_el.append(el)
                        used_val.append(val)
                        break
                    if el == lDC_match_form[-1]: #that means no query element matches the form compound val, so val is a new entry
                        new_val.append(val)
            for el in lDC_match_form: # creating a list of entries to be reused with a different compound
                if el not in used_el:
                    del_el.append(el)      
                    print(el, " must be removed")
            for key,val in dictmodcompmod.items():  #new compound to register in the list of entries del_el
                if val not in used_val:
                    new_val.append(val)
            used_new_val=[]                
            used_del_el=[]
            print ("\ndel elements dB",del_el) 
            if lenCompDB > lenform: #if so the number of elements in del_el is higher than in new_val. the el entries will be used for store the val form lines. Then 
                for el in del_el:
                    if BREAK1:
                        break
                    if len(new_val)>0:
                        for val in new_val:
                            if val in used_new_val:
                                continue
                            qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_model=val['id_model'],resname=val['resname'],type=val['type'])
                            used_new_val.append(val)
                            used_del_el.append(el)
                            if val == used_new_val[-1]:
                                for el in del_el:
                                    if el not in used_del_el:
                                         qDC_match_form.filter(id=el['id']).update(numberofmol=None,resname=el['id'],type=None,id_model=None) 
                                BREAK1=True
                                break
                            else:
                                break
                    else:
                        qDC_match_form.filter(id=el['id']).update(numberofmol=None,resname=el['id'],type=None,id_model=None) 
            else:
                print("\n HIGHER number of form rows")
                for val in new_val:
                    if BREAK2:
                        break
                    if len(del_el)>0:
                        for el in del_el: 
                            if el in used_del_el:
                               continue
                            qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_model=val['id_model'],resname=val['resname'],type=val['type'])
                            used_new_val.append(val)
                            used_del_el.append(el)
                            if val == new_val[-1]: #this implies that lenCompDB= lenform and len(new_val)==len(del_el) so after updating the loop is finished 
                                BREAK2=True
                                break
                            if el == del_el[-1]:
                                used_empty_rows=[]
                                if len(lempty_rows) > 0 and len(lempty_rows) > len(used_empty_rows):
                                    for i in lempty_rows:
                                        if BREAK2:
                                            break
                                        for val in new_val:
                                            if val not in used_new_val:
                                                if i not in used_empty_rows:
                                                    qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_model=val['id_model'],resname=val['resname'],type=val['type'])
                                                    used_new_val.append(val)
                                                    used_empty_rows.append(i)
                                                    if val == new_val[-1]:
                                                        BREAK2=True # all rows in the form (val) are registered... the "Break" cascade starts
                                                        break
                                                    if not i == lempty_rows[-1]:
                                                        break 
                                                    else:
                                                        continue
                                                else:
                                                    Scom_inst=dyndb_Model_Components(val)
                                                    used_new_val.append(val)
                                                    if Scom_inst.is_valid():
                                                        Scom_obj=Scom_inst.save()
                                                        if val == used_new_val[-1]:
                                                            BREAK2=True # all lines in the form (val) are registered... the "Break" cascade starts
                                                            break
                                                        continue #if there is still some row in new val list 
                                                    else:
                                                        iii1=Scom_inst.errors.as_text()
                                                        print("errors in the form Model Components", Scom_inst.errors.as_text())                                   
                                                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                                        return response                                                                                             
                                else:
                                    Scom_inst=dyndb_Model_Components(val)
                                    if Scom_inst.is_valid():
                                        Scom_obj=Scom_inst.save()
                                        continue
                                    else:
                                        iii1=Scom_inst.errors.as_text()
                                        print("errors in the form Model Components", Scom_inst.errors.as_text())                                   
                                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                        return response                                                                                                         
                    elif len(lempty_rows) > 0:
                        used_empty_rows=[]
                        for i in lempty_rows:
                            if BREAK2:
                                break
                            for val in new_val:
                                if val not in used_new_val:
                                    if i not in used_empty_rows:
                                        qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_model=val['id_model'],resname=val['resname'],type=val['type'])
                                        used_new_val.append(val)
                                        used_empty_rows.append(i)
                                        if val == new_val[-1]:
                                            BREAK2=True # all rows in the form (val) are registered... the "Break" cascade starts
                                            break
                                        if not i == lempty_rows[-1]:
                                            break 
                                        else:
                                            continue
                                    else:
                                        Scom_inst=dyndb_Model_Components(val)
                                        used_new_val.append(val)
                                        if Scom_inst.is_valid():
                                            Scom_obj=Scom_inst.save()
                                            if val == used_new_val[-1]:
                                                BREAK2=True # all lines in the form (val) are registered... the "Break" cascade starts
                                                break
                                            continue #if there is still some row in new val list 
                                        else:
                                            iii1=Scom_inst.errors.as_text()
                                            print("errors in the form Model Components", Scom_inst.errors.as_text())                                   
                                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                            return response                                                                                             
                    else:
                        Scom_inst=dyndb_Model_Components(val)
                        if Scom_inst.is_valid():
                            Scom_obj=Scom_inst.save()
                            continue
                        else:
                            iii1=Scom_inst.errors.as_text()
                            print("errors in the form Model Components", Scom_inst.errors.as_text())                                   
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                            return response                                                                                                         
        response = HttpResponse("The model has been successfully submitted" ,content_type='text/plain; charset=UTF-8')
        return response
    # if a GET (or any other method) we'll create a blank form
    else:
        qSM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        protlist=list(DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id').select_related('protein_id').values_list('int_id','protein_id__uniprotkbac','protein_id__name')) 
        if len(qSM)>0: #The form should be completely filled
            model_id=qSM.values_list('model_id',flat=True)[0]
            qModel=DyndbModel.objects.filter(id=model_id)
            INITsubmission_id=submission_id
            p=qModel
            for q in p:
                print(q.__dict__)
            Typeval=p.values()[0]['type']
            Type=p.model.MODEL_TYPE[Typeval][1]
            STypeval=p.values()[0]['source_type']
            SType=p.model.SOURCE_TYPE[STypeval][1]
            print("QMODEL ",p)
            qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id,id_protein__dyndbsubmissionprotein__submission_id=INITsubmission_id).annotate(int_id=F('id_protein__dyndbsubmissionprotein__int_id')).order_by('resid_from')
            lformps=list(range(0,len(qMODRES)))
            rowsMR=qMODRES
            lmrstype=[]
            for l in qMODRES:
                mrstype=l.SOURCE_TYPE[l.source_type]
                lmrstype.append(mrstype)
            print ("residues!!",lmrstype)
            molinmodel_in_modelcomp=DyndbSubmissionMolecule.objects.filter(type__lt=6,submission_id=submission_id,submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_model=model_id,submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_molecule=F('molecule_id')).annotate(name=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_molecule__id_compound__name'),resname=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__resname'),numberofmol=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__numberofmol'),typemc=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__type'),id_model=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_model')).exclude(not_in_model=None,int_id=None,molecule_id_id=None)
            molinmodel_not_in_modelcomp=DyndbSubmissionMolecule.objects.filter(type__lt=6,submission_id=submission_id).exclude(id__in=molinmodel_in_modelcomp).exclude(not_in_model=None,int_id=None,molecule_id_id=None)
            molinmodel_in_modelcompl=list(molinmodel_in_modelcomp.values())
            molinmodel_not_in_modelcompl=list(molinmodel_not_in_modelcomp.values())
            all_molinmodel=[]
            for entry in molinmodel_in_modelcompl:
                entry['typemc']=DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[entry['type']]]
                print(entry['type'])
                all_molinmodel.append(entry)
            for entry in molinmodel_not_in_modelcompl:
                print("PPPP\n",type(entry))
                print(entry.items())
                qName=DyndbCompound.objects.filter(id=DyndbMolecule.objects.filter(id=entry['molecule_id_id']).values_list('id_compound',flat=True)).values_list('name',flat=True)[0]
                entry['name']=qName
                entry['resname']=str()
                entry['numberofmol']=int()
                entry['typemc']=DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[entry['type']]]
                all_molinmodel.append(entry)
            qMODCOMP = sorted(all_molinmodel, key=itemgetter('int_id'))                    
            print("MIRA",qMODCOMP)
            lmtype=[]
            lformmc=list(range(0,len(qMODCOMP)))
            lcompname=[]
            l_ord_mol=[]
            d=0
            rowsMC=qMODCOMP
            reuse_model=model_id
            print(rowsMR.values)
            print("aqui",lformps)
            fdbMF = dyndb_Model()
            fdbPS = dyndb_Modeled_Residues()
            fdbMC = dyndb_Model_Components()
            return render(request,'dynadb/MODEL.html', {'rowsMR':rowsMR,'lcompname':lcompname,'lformps':lformps,'lformmc':lformmc,'SType':SType,'Type':Type,'lmrstype':lmrstype,'rowsMC':rowsMC, 'p':p ,'fdbPS':fdbPS,'fdbMC':fdbMC,'submission_id':submission_id, 'saved':True,'protlist':protlist})
        else:
            lmol_MOD_type_num=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(molecule_id=None).exclude(int_id=None).exclude(type__gt=5).order_by('int_id').values_list('type',flat=True)
            Complex=lmol_MOD_type_num.exclude(type__gt=1).order_by('int_id').exists()
            lprot_MOD=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
            if len(lprot_MOD) >1:
                Complex=True
            Smol_to_Modcomp_type=smol_to_dyncomp_type
            lmol_MOD_type_tup=[]
            molecule_type_dict=dict(DyndbModelComponents.MOLECULE_TYPE)
            for l in lmol_MOD_type_num:
                #lmol_MOD_type_tup.append(DyndbModelComponents.MOLECULE_TYPE[Smol_to_Modcomp_type[l]])
                lmol_MOD_type_tup.append((Smol_to_Modcomp_type[l],molecule_type_dict[Smol_to_Modcomp_type[l]]))
                
            fdbMF = dyndb_Model()
            fdbPS = dyndb_Modeled_Residues()
            fdbMC = dyndb_Model_Components()
            mcdata = get_components_info_from_submission(submission_id,'model')
            
            print("list",lmol_MOD_type_tup)
            i = 0
            for row in mcdata:
                mcdata[i]['resname'] = ''
                mcdata[i]['numberofmol'] = ''
                mcdata[i]['int_id'] = 1 + mcdata[i]['int_id']
                i += 1
            return render(request,'dynadb/MODEL.html', {'fdbMF':fdbMF,'Complex':Complex,'fdbPS':fdbPS,'fdbMC':fdbMC,'submission_id':submission_id,'mcdata':mcdata,'lmol_MOD_type_tup':lmol_MOD_type_tup, 'protlist':protlist})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def SMALL_MOLECULEview2(request,submission_id):
    print("REQUEST SESSIONS",request.session.items())
    print("REQUEST SESSIONS",request.path)
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        action="/".join(["/dynadb/MOLECULEfilled2",submission_id,""])
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted
        initMF={'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initCF={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initON={'other_names': onames,'id_compound':None} 
        return HttpResponse(request.session.items())

    else:
        fdbMF=dyndb_CompoundForm() 
        return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF })

@csrf_exempt
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def generate_molecule_properties(request,submission_id):
    request.upload_handlers[1] = TemporaryMoleculeFileUploadHandlerMaxSize(request,100*50*1024**2)#Increase size limit
    try:
        return _generate_molecule_properties(request,submission_id)
    except (RequestBodyTooLarge, FileTooLarge, TooManyFiles) as e:
        return HttpResponse(e.args[0],status=413,reason='Payload Too Large',content_type='text/plain; charset=UTF-8')
    except:
        raise

def testpng(request):
    context={}
    suppl = SDMolSupplier(settings.MEDIA_ROOT+'water.sdf')
    mol = next(suppl)
    print(mol.GetNumAtoms())
    filename = settings.MEDIA_ROOT+'uploadedmol.png'
    MolToFile(mol, filename, size=(300,300))
    return render(request, 'dynadb/testpng.html', context)
    
def testsub(request):
    print("\n\n\n")
    print(":)")
    pngsize = 300
    RecMet = False
    if request.method == 'POST':
        data = dict()
        print("POST!")
        uploadfile = request.FILES["sdf_file"]
        sdfname="uploaded.sdf"
        pngname="uploaded.png"
        submission_path=settings.MEDIA_ROOT+"submission_test/"
        os.makedirs(submission_path,exist_ok=True)
        try:
            os.remove(os.path.join(submission_path,sdfname))
        except:
            pass
        try:
            os.remove(os.path.join(submission_path,pngname))
        except:
            pass
        uploadedfile=uploadfile
        uploadedfile.seek(0)    
        suppl = ForwardSDMolSupplier(uploadedfile,removeHs=False)
        mol = next(suppl)
        try:
            next(suppl)
        except StopIteration:
            pass
        except:
            raise
        else:
            raise MultipleMoleculesinSDF()
        finally:
            del suppl
        print('Assigning chirality from struture...')
        AssignAtomChiralTagsFromStructure(mol,replaceExistingTags=False)
        print('Finished loading molecule.')
        uploadfile.close()
        pngpath=os.path.join(submission_path,pngname)
        size=pngsize
        print("1")
        molprep=PrepareMolForDrawing(mol)
        print(2)
        MolToFile(molprep, pngpath)
        print(3)
        del mol
        data['msg']="All good :)"
        return JsonResponse(data,safe=False)
    print("\n\n\n")
    context={}
    return render(request, 'dynadb/testsub.html', context)

@csrf_protect
def _generate_molecule_properties(request,submission_id):
    pngsize = 300
    RecMet = False
    formre = re.compile('^form-(\d+)-')

    if request.method == 'POST':
        submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
        submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
        data = dict()
        data['download_url_log'] = None
        if 'molpostkey' in request.POST.keys():
            if 'recmet' in request.POST.keys():
                RecMet = True
            if 'pngsize' in request.POST.keys():
                pngsize = int(request.POST["pngsize"])
            molpostkey = request.POST["molpostkey"]
            if molpostkey in request.FILES.keys():
                m = formre.search(molpostkey)
                if m:
                    molid = m.group(1)
                else:
                    molid = 0
                uploadfile = request.FILES[molpostkey]
                os.makedirs(submission_path,exist_ok=True)
                logname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="log",forceext=False,subtype="log")
                sdfname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")
                pngname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="png",forceext=False,subtype="image",imgsize=pngsize)
                sdfnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
                pngnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image",imgsize=pngsize)
                print("PIPOL")
                try:
                    os.remove(os.path.join(submission_path,sdfname))
                except:
                    pass
                try:
                    os.remove(os.path.join(submission_path,pngname))
                except:
                    pass
                try:
                    os.remove(os.path.join(submission_path,pngnameref))
                except:
                    pass
                try:
                    os.remove(os.path.join(submission_path,sdfnameref))
                except:
                    pass
                logfile = open(os.path.join(submission_path,logname),'w')
                data['download_url_log'] = join_path(submission_url,logname,url=True)
                try:
                    mol = open_molecule_file(uploadfile,logfile=logfile)
                except (ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension) as e:
                    print("------------------_!!!!!!!!---------------")
                    print(e.args[0],file=logfile)
                    logfile.close()
                    data['msg'] = e.args[0]
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                except:
                    msg = 'Cannot load molecule from uploaded file.'
                    print(msg,file=logfile)
                    data['msg'] = msg + ' Please, see log file.'
                    logfile.close()
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                finally:
                    uploadfile.close()
                if check_implicit_hydrogens(mol):
                    data['msg'] = 'Molecule contains implicit hydrogens. Please, provide a molecule with explicit hydrogens.'
                    print(data['msg'],file=logfile)
                    logfile.close()
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                if check_non_accepted_bond_orders(mol):
                    data['msg'] = 'Molecule contains non-accepted bond orders. Please, provide a molecule with single, aromatic, double or triple bonds only.'
                    print(data['msg'],file=logfile)
                    logfile.close()
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                data['sinchi'] = dict()
                try:
                    print('Generating Standard InChI...',file=logfile)
                    sinchi,code,msg = generate_inchi(mol,FixedH=False,RecMet=False)
                    data['sinchi']['sinchi'] = sinchi
                    data['sinchi']['code'] = code
                    print(msg,file=logfile)
                    data['inchi'] = dict()
                    print('Generating Fixed Hydrogens InChI...',file=logfile)
                    inchi,code,msg = generate_inchi(mol,FixedH=True,RecMet=RecMet)
                    data['inchi']['inchi'] = inchi
                    data['inchi']['code'] = code
                    print(msg,file=logfile)
                    data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])
                    data['inchikey'] = generate_inchikey(data['inchi']['inchi'])
                except:
                    data['msg'] ='Error while computing InChI.'
                    print(data['msg'],file=logfile)
                    logfile.close()
                    data['msg'] = msg+' Please, see log file.'
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                try:
                    print('Generating Smiles...',file=logfile)
                    data['smiles'] = generate_smiles(mol,logfile)
                except:
                    msg = 'Error while computing Smiles.'
                    print(msg,file=logfile)
                    logfile.close()
                    data['msg'] = msg+' Please, see log file.'
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                data['charge'] = get_net_charge(mol)
                try:
                    mol.SetProp("_Name",sdfname)
                    write_sdf(mol,os.path.join(submission_path,sdfname))
                    data['download_url_sdf'] = join_path(submission_url,sdfname,url=True)
                except:
                    try:
                        os.remove(os.path.join(submission_path,sdfname))
                    except:
                        pass
                    msg = 'Error while storing SDF file.'
                    print(msg,file=logfile)
                    logfile.close()
                    data['msg'] = msg+' Please, see log file.'
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                print('Drawing molecule...',file=logfile)
                data['download_url_png'] = join_path(submission_url,pngname,url=True)
                print('Finished with molecule.',file=logfile)
                logfile.close()
                del mol
            #####################
                qMOL=DyndbMolecule.objects.filter(inchi=data['inchi']['inchi'].split('=')[1],net_charge=data['charge'])
                if qMOL.exists(): # [!] BUG HERE: often mol is stored at DyndbMolecule but no id_compound__std_id_molecule
                    qMOLfilt=qMOL.filter(id_compound__std_id_molecule__dyndbfilesmolecule__type=2)
                    if not qMOLfilt: #[!] To fix the bug in the easy cases where there is only one molecule corresponding to the compound, this is assigned to the standard
                        if len(qMOLfilt) ==1:
                            mol=qMOLfilt[0]
                            mols_shared_comp=DyndbMolecule.objects.filter(id_compound= mol.id_compound)
                            if len(mols_shared_comp)==1:
                                 c=mol.id_compound
                                 c.std_id_molecule=mol
                                 c.save()
                    data['urlstdmol']=qMOLfilt.values_list('id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url',flat=True)[0]
                    data['name'],data['iupac_name'],data['pubchem_cid'],data['chemblid'] =qMOL.values_list('id_compound__name','id_compound__iupac_name','id_compound__pubchem_cid','id_compound__chemblid')[0]
                    data['other_names']=("; ").join(list(qMOL.values_list('id_compound__dyndbothercompoundnames__other_names',flat=True)))
                return JsonResponse(data,safe=False)
            else:
                data['msg'] = 'Unknown molecule file reference.'
                return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')                       
        else:
            data['msg'] = 'No file was selected or cannot find molecule file reference.'
            for upload_handler in request.upload_handlers:
                if hasattr(upload_handler,'exception'):
                    if upload_handler.exception is not None:
                        try:
                            raise upload_handler.exception
                        except(InvalidMoleculeFileExtension,MultipleMoleculesinSDF) as e :
                            data['msg'] = e.args[0]
                        except:
                            raise
            return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
        
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def get_compound_info_pubchem(request,submission_id):
    pngsize=300
    search_by='inchi'
    retrieve_type='parent'
    if request.method == 'POST':
        submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
        submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
        data = dict()
        errdata = dict()
        if 'molid' in request.POST.keys():
            molid = request.POST['molid']
        else:
            return HttpResponse('Missing POST keys.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        os.makedirs(submission_path,exist_ok=True)
        pngname = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image",imgsize=pngsize)
        sdfname = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
        try:
            os.remove(os.path.join(submission_path,sdfname))
        except:
            pass
        try:
            os.remove(os.path.join(submission_path,pngname))
        except:
            pass
        if 'update_from_id' in request.POST.keys():
            update_from_id = True
            cids = [int(request.POST['update_from_id'])]
        else:
            update_from_id = False
            if 'search_by' in request.POST.keys():
                search_by = request.POST['search_by']
            if 'retrieve_type' in request.POST.keys():
                retrieve_type = request.POST['retrieve_type']
                if retrieve_type not in CIDS_TYPES:
                    return HttpResponse("Invalid search criteria '"+retrieve_type+"'.",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            neutralize = False
            if 'neutralize' in request.POST.keys():
                neutralize = True
            if 'inchi' in request.POST.keys() and (search_by == 'sinchi' or search_by == 'sinchikeynoiso'):
                inchi = request.POST['inchi']
                mol = MolFromInchi(inchi,removeHs=False)
                if mol is None:
                    return HttpResponse('Invalid InChI.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                remove_isotopes(mol)
                mol = standarize_mol_by_inchi(mol,neutralize=neutralize)
                sinchi,code,msg = generate_inchi(mol, FixedH=False, RecMet=False)
                del mol
                if search_by == 'sinchi':
                    search_value = sinchi
                    search_property = 'inchi'
                elif search_by == 'sinchikeynoiso':
                    search_value = generate_inchikey(sinchi)
                    search_property = 'inchikey'
            elif 'sinchikey' in request.POST.keys() and search_by == 'sinchikey':
                sinchikey = request.POST['sinchikey']
                if not validate_inchikey(sinchikey):
                    return HttpResponse('Invalid InChIKey.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                
                if neutralize:
                    nsinchikey = neutralize_inchikey(sinchikey)
                else:
                    nsinchikey = sinchikey
                search_value = nsinchikey
                search_property = 'inchikey'
            elif 'smiles' in request.POST.keys() and search_by == 'smiles': 
                smiles = request.POST['smiles']
                mol = MolFromSmiles(smiles,sanitize=True)
                if mol is None or smiles == '':
                    return HttpResponse('Invalid Smiles.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                remove_isotopes(mol)
                if neutralize:
                    mol = standarize_mol_by_inchi(mol,neutralize=neutralize)
                smiles =  generate_smiles(mol)
                del mol
                search_value = smiles
                search_property = 'smiles'        
            else:
                return HttpResponse('Missing POST keys.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        data['pubchem_cid'] = None
        data['chembl_id'] = None
        data['name'] = None
        data['iupac_name'] = None
        data['synonyms'] = None
        data['download_url_sdf'] = None
        data['download_url_png'] = None
        try:
            if not update_from_id:
                datapubchem,errdata = retreive_compound_data_pubchem_post_json(search_property,search_value,operation='cids',extras={'cids_type':retrieve_type})
                #datapubchem["IdentifierList"]["CID"] = [0]
                if 'Error' in errdata.keys():    
                    raise DownloadGenericError(errdata['reason'])
                elif datapubchem["IdentifierList"]["CID"] == [0]:
                    datapubchem = None
                    errdata['Error'] = True
                    errdata['ErrorType'] = 'HTTPError'
                    errdata['status_code'] = 404
                    errdata['reason'] = 'Not found.'
                    raise DownloadGenericError(errdata['reason'])
                cids = datapubchem["IdentifierList"]["CID"]   
            data['pubchem_cid'] = cids
            if len(cids) == 1:
                time.sleep(5)
                datapubchem,errdata = retreive_compound_data_pubchem_post_json('cid',cids[0],operation='property',outputproperty='IUPACName')
                if 'Error' in errdata.keys():
                    raise DownloadGenericError(errdata['reason'])
                if "IUPACName" in datapubchem["PropertyTable"]["Properties"][0]:
                    data['iupac_name'] = datapubchem["PropertyTable"]["Properties"][0]["IUPACName"]
                time.sleep(5)
                datapubchem,errdata = retreive_compound_data_pubchem_post_json('cid',cids[0],operation='synonyms')
                if 'Error' in errdata.keys():
                    raise DownloadGenericError(errdata['reason'])
                if "Synonym" in datapubchem["InformationList"]["Information"][0]: 
                    lastidx = len(datapubchem["InformationList"]["Information"][0]["Synonym"])
                    if (lastidx > 51):
                        lastidx = 51
                    data['synonyms'] = ';'.join(datapubchem["InformationList"]["Information"][0]["Synonym"][1:lastidx])
                    data['name'] = datapubchem["InformationList"]["Information"][0]["Synonym"][0]
                del datapubchem
                time.sleep(5)
                datapubchem,errdata = retreive_compound_sdf_pubchem('cid',cids[0],outputfile=os.path.join(submission_path,sdfname),in3D=True)
                print(errdata)
                if 'Error' in errdata.keys():
                    if errdata['ErrorType'] == 'HTTPError' and (errdata['status_code'] == 404 or errdata['status_code'] == 410):
                        time.sleep(5)
                        datapubchem,errdata = retreive_compound_sdf_pubchem('cid',cids[0],outputfile=os.path.join(submission_path,sdfname),in3D=False)
                        if 'Error' in errdata.keys():
                            raise DownloadGenericError(errdata['reason'])
                    else:
                        raise DownloadGenericError(errdata['reason'])
                data['download_url_sdf'] = join_path(submission_url,sdfname,url=True)
                time.sleep(5)
                datapubchem,errdata = retreive_compound_png_pubchem('cid',cids[0],outputfile=os.path.join(submission_path,pngname),width=pngsize,height=pngsize)
                if 'Error' in errdata.keys():
                    raise DownloadGenericError(errdata['reason'])
                data['download_url_png'] = join_path(submission_url,pngname,url=True)
                return JsonResponse(data,safe=False)
            elif len(cids) > 1:
                    return JsonResponse(data,safe=False)
        except DownloadGenericError:
            try:
                os.remove(os.path.join(submission_path,sdfname))
            except:
                pass
            try:
                os.remove(os.path.join(submission_path,pngname))
            except:
                pass
            return pubchem_errdata_2_response(errdata,data=datapubchem)
        except:
            raise

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed        
def get_compound_info_chembl(request,submission_id):
    pngsize=300
    search_by='inchi'
    retrieve_type='parent'
    id_only=False
    similarity = 100
    min_similarity = 70
    max_similarity = 100
    if request.method == 'POST':
        submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
        submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
        data = dict()
        errdata = dict()
        if 'molid' in request.POST.keys():
            molid = request.POST['molid']
        else:
            return HttpResponse('Missing POST keys.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        if 'id_only' in request.POST.keys():
                id_only = True
        os.makedirs(submission_path,exist_ok=True)
        pngname = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image",imgsize=pngsize)
        sdfname = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
        if not id_only:
            try:
                os.remove(os.path.join(submission_path,sdfname))
            except:
                pass
            try:
                os.remove(os.path.join(submission_path,pngname))
            except:
                pass
        if 'update_from_id' in request.POST.keys():
            update_from_id = True
            cids = [int(request.POST['update_from_id'])]
        else:
            update_from_id = False
            if 'search_by' in request.POST.keys():
                search_by = request.POST['search_by']
            if 'similarity' in request.POST.keys():
                try:
                    similarity = int(request.POST['similarity'])
                except ValueError:
                    return HttpResponse("'similarity' filed with invalid value.",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                except:
                    raise
                if similarity > max_similarity:
                    return HttpResponse("Maximum similarity is "+str(max_similarity)+"% .",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')

                elif similarity < min_similarity:
                    return HttpResponse("Minimal allowed similarity is "+str(min_similarity)+"% ."+retrieve_type+"'.",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            if 'retrieve_type' in request.POST.keys():
                retrieve_type = request.POST['retrieve_type']
                if retrieve_type not in CIDS_TYPES:
                    return HttpResponse("Invalid search criteria '"+retrieve_type+"'.",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            neutralize = False
            if 'neutralize' in request.POST.keys():
                neutralize = True
            if 'inchi' in request.POST.keys() and (search_by == 'sinchi' or search_by == 'sinchikeynoiso'):
                inchi = request.POST['inchi']
                mol = MolFromInchi(inchi,removeHs=False)
                if mol is None:
                    return HttpResponse('Invalid InChI.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                remove_isotopes(mol)
                mol = standarize_mol_by_inchi(mol,neutralize=neutralize)
                sinchi,code,msg = generate_inchi(mol, FixedH=False, RecMet=False)
                del mol
                search_value = generate_inchikey(sinchi)
                search_property = 'inchikey'
            elif 'sinchikey' in request.POST.keys() and search_by == 'sinchikey':
                sinchikey = request.POST['sinchikey']
                if not validate_inchikey(sinchikey):
                    return HttpResponse('Invalid InChIKey.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                if neutralize:
                    nsinchikey = neutralize_inchikey(sinchikey)
                else:
                    nsinchikey = sinchikey
                search_value = nsinchikey
                search_property = 'inchikey'
            elif 'smiles' in request.POST.keys() and search_by == 'smiles': 
                smiles = request.POST['smiles']
                mol = MolFromSmiles(smiles,sanitize=True)
                if mol is None or smiles == '':
                    return HttpResponse('Invalid Smiles.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                remove_isotopes(mol)
                if neutralize:
                    mol = standarize_mol_by_inchi(mol,neutralize=neutralize)
                    smiles =  generate_smiles(mol)
                del mol
                search_value = smiles
                search_property = 'smiles'        
            else:
                return HttpResponse('Missing POST keys.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        data['chembl_id'] = None
        data['name'] = None
        data['synonyms'] = None
        data['download_url_sdf'] = None
        data['download_url_png'] = None
        try:
            if not update_from_id:
                datachembl,errdata = retreive_molecule_chembl_similarity_json(search_value,similarity=similarity)
                if 'Error' in errdata.keys():    
                    raise DownloadGenericError(errdata['reason'])
                try:
                    cids = get_chembl_molecule_ids(datachembl,parents=bool(retrieve_type == 'parent'))
                except ParsingError as e:
                    return HttpResponse('Problem downloading from ChEMBL:'\
                    +'\n'+e.args[0],status=502,content_type='text/plain; charset=UTF-8')
            data['chembl_id'] = cids
            if len(cids) == 0:
                return HttpResponseNotFound("Cannot find entry for this molecule in ChEMBL.")
            if len(cids) < 2 and not id_only:
                time.sleep(5)
                datachembl,errdata = retreive_molecule_chembl_id_json('CHEMBL'+str(cids[0]))
                if 'Error' in errdata.keys():    
                        raise DownloadGenericError(errdata['reason'])
                try:
                    prefname,aliases = get_chembl_prefname_synonyms(datachembl)
                except ParsingError as e:
                    return HttpResponse('Problem downloading from ChEMBL:'\
                    +'\n'+e.args[0],status=502,content_type='text/plain; charset=UTF-8')
                lastidx = len(aliases)
                if lastidx > 50:
                    lastidx = 50
                data['synonyms'] = ';'.join(aliases[0:lastidx])
                data['name'] = prefname
                del datachembl
                time.sleep(5)
                molregno,errdata = chembl_get_molregno_from_html('CHEMBL'+str(cids[0]))
                if 'Error' in errdata.keys():
                    raise DownloadGenericError(errdata['reason'])
                time.sleep(5)
                datachembl,errdata = retreive_compound_sdf_chembl(molregno,getmol_url='/chembl/download_helper/getmol/',outputfile=os.path.join(submission_path,sdfname))
                print(errdata)
                if 'Error' in errdata.keys():
                    raise DownloadGenericError(errdata['reason'])
                data['download_url_sdf'] = join_path(submission_url,sdfname,url=True)
                time.sleep(5)
                datachembl,errdata = retreive_compound_png_chembl('CHEMBL'+str(cids[0]),outputfile=os.path.join(submission_path,pngname),dimensions=pngsize)
                data['download_url_png'] = join_path(submission_url,pngname,url=True)
                return JsonResponse(data,safe=False)
            else:
                return JsonResponse(data,safe=False)
        except DownloadGenericError:
            try:
                os.remove(os.path.join(submission_path,sdfname))
            except:
                pass
            try:
                os.remove(os.path.join(submission_path,pngname))
            except:
                pass
            return chembl_errdata_2_response(errdata,data=datachembl)
        except:
            raise  

@login_required       
def open_pubchem(request):           
    if request.method == 'POST':
        if 'cids' in request.POST.keys():
            cids = request.POST['cids'].split(',')
            query = ''
            for cid in cids:
                query += str(cid)+'[CompoundID] OR '
            query = query[:query.rfind(' OR ')]
            return render(request,'dynadb/open_pubchem.html',{'query':query,'action':'https://www.ncbi.nlm.nih.gov/pccompound/'})

@login_required           
def open_chembl(request):           
    chembl_root_url = 'https://www.ebi.ac.uk/chembl'
    chembl_index_php = chembl_root_url+'/index.php'
    chembl_submission_url = chembl_root_url + '/compound/ids'
    field_name = 'compound_list'
    if request.method == 'POST':
        if 'cids' in request.POST.keys():
            data = dict()
            cids = request.POST['cids'].split(',')
            querylines = ['CHEMBL'+str(cid) for cid in cids]
            query = '\n'.join(querylines)
            data[field_name] = query
            chembl_results_url_no_domain, errdata = chembl_get_compound_id_query_result_url(data,chembl_submission_url=chembl_submission_url)
            chembl_results_url = chembl_index_php + chembl_results_url_no_domain
            return render(request,'dynadb/open_chembl.html',{'query':query,\
            'action':chembl_submission_url,'chembl_root_url':chembl_root_url,'chembl_results_url':chembl_results_url,'field_name':field_name})
            
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def delete_molecule(request,submission_id,model_id=1):
    if request.method == "POST":
        molecule_num = request.POST["molecule_num"]
        response = HttpResponse('Success.',content_type='text/plain; charset=UTF-8')
    else:
        response = HttpResponseForbidden()
    return response

def get_dynamics_files_reference_atomnum(submission_id,file_type):
    """
    Gets a reference num of atoms with a priorized reference dynamics file 
    """
    file_types = ['coor','traj']
    filetype_dbtypestext_dict = {'coor':'coor','top':'top','traj':'traj','parm':'param','other':'other', 'prt':'prt'}
    if file_type not in file_types:
        raise ValueError('Invalid file_type argument: "'+str(file_type)+'"')
    #remove file_type from reference file type files
    dbtype_preference_list = []
    dbtype_2_file_type = dict()
    for type1 in file_types:
        if type1 != file_type:
            dbtype_preference_list.append(type_inverse_search(DyndbSubmissionDynamicsFiles.file_types,searchkey=filetype_dbtypestext_dict[type1],case_sensitive=False,first_match=True))
            dbtype_2_file_type[dbtype_preference_list[-1]] = type1
    q = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id).values('filename','filepath','type')
    results = list(q)
    del q
    reffilepath = None
    reffilename = None
    ref_numatoms = None
    ref_file_type = None
    if len(results) > 0:
        type_filepaths = dict()
        filepaths = []
        for row in results:
            ctype = row['type']
            if ctype not in type_filepaths:
                type_filepaths[ctype] = dict()
                type_filepaths[ctype]['filenames'] = []
                type_filepaths[ctype]['filepaths'] = []
            type_filepaths[ctype]['filepaths'].append(row['filepath'])
            type_filepaths[ctype]['filenames'].append(row['filename'])
        del results
        for pref in dbtype_preference_list:
            if pref in type_filepaths:
                reffilepath = type_filepaths[pref]['filepaths'][0]
                reffilename = type_filepaths[pref]['filenames'][0]
                dbtype_pref = pref
                break
        if reffilepath is not None:
            ref_file_type = dbtype_2_file_type[dbtype_pref]
            ref_numatoms = get_atoms_num(reffilepath,ref_file_type)
    return (reffilepath, reffilename, ref_file_type, ref_numatoms)

def test_accepted_file_extension(ext,file_type):
    type_keys = {'coordinates', 'topology', 'trajectory', 'parameter', 'anytype', 'image', 'molecule', 'model'}
    if file_type not in type_keys:
        raise ValueError('Invalid type_file argument. Valid types are: '+', '.join(type_keys)+'.')
    if ext[0] == '.':
        ext2 = ext[1:].lower()
    else:
        ext2 = ext.lower()
    fieldname = 'is_'+file_type
    q = DyndbFileTypes.objects.filter(**{'extension':ext2,fieldname:True,'is_accepted':True})
    if len(q) > 0:
        return True
    else:
        return False

@csrf_exempt
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def upload_dynamics_files(request,submission_id,trajectory=None):
    trajectory_max_files = 200
    if hasattr(settings,'TRAJECTORY_MAX_FILES'):
        trajectory_max_files = settings.trajectory_max_files
    if trajectory is None:
        #request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,50*1024**2) #Increase size limit
        request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,100*50*1024**2) #Increase size limit
    else:
        request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,100*5*1024**3,max_files=trajectory_max_files)#Increase size limit
        #request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,2*1024**3)
    try:
        return _upload_dynamics_files(request,submission_id,trajectory=trajectory,trajectory_max_files=trajectory_max_files)
    except (RequestBodyTooLarge, FileTooLarge, TooManyFiles) as e:
        return HttpResponse(e.args[0],status=413,reason='Payload Too Large',content_type='text/plain; charset=UTF-8')
    except:
        raise    

def get_dynamics_file_types():
    file_types = OrderedDict()
    file_types['coor']=dict()
    file_types['top'] = dict()
    file_types['traj'] = dict()
    file_types['parm'] = dict()
    file_types['other'] = dict()
    file_types['prt'] = dict()
    file_types['coor']['db'] = ["is_model"]
    file_types['top']['db'] = ["is_topology"]
    file_types['traj']['db'] = ["is_trajectory"]
    file_types['parm']['db'] = ["is_parameter","is_anytype"]
    file_types['other']['db'] = ["is_anytype"]
    file_types['prt']['db'] = ["is_anytype"]
    file_types['coor']['long_name'] = "Coordinate file"
    file_types['top']['long_name'] = "Topology file"
    file_types['traj']['long_name'] = "Trajectory files"
    file_types['parm']['long_name'] = "Simulation parameters"
    file_types['other']['long_name'] = "Other files"
    file_types['prt']['long_name'] = "Simulation protocol"
    file_types['coor']['description'] = "Upload the initial coordinates file of the system in PDB format (.pdb) max 50 MB."
    file_types['top']['description'] = "Upload the file describing the topology of your system. Top (.psf, .prmtop, .top, other) max 50 MB."
    file_types['traj']['description'] = "Upload the files containing the evolution of the system coordinates with time. Traj (.dcd, .xtc) max. 2 GB."
    file_types['parm']['description'] = "Upload the file containing the force field parameters. Param (.tar.gz,.tgz) max 50 MB."
    file_types['other']['description'] = "Additional files needed for rerunning the simulation. Include here individual topology files and parameters that are not published elsewhere (e.g. resulting from optimitzation). max 50 MB."
    file_types['prt']['description'] = "Upload the file containing the simulation protocol (.zip, .tar.gz,.tgz) max 50 MB."

    fields = dict()
    fields_extension = dict()
    q = DyndbFileTypes.objects.filter(is_accepted=True)
    for key in file_types:
        file_types[key]['extension'] = []
        for field in file_types[key]['db']:
            fields_extension[field] = set()
    fields_list = fields_extension.keys()
    for field in fields_list:
        q = q | q.filter(**{field:True,'is_accepted':True})
    values_list = list(fields_list)
    values_list.append('extension')
    q=q.values(*values_list)
    result = list(q)
    for row in result:
        for field in fields_list:
            if row[field]:
                fields_extension[field].add(row['extension'])
    for key in file_types:
        for field in file_types[key]['db']:
            file_types[key]['extension'] += sorted(fields_extension[field])
    return file_types
      
file_types = get_dynamics_file_types()

def delete_uploaded_dynamic_files(submission_id,dbtype):
    dyndb_submission_dynamics_files = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype)
    dyndb_submission_dynamics_files = dyndb_submission_dynamics_files.values('filepath')
    for row in dyndb_submission_dynamics_files:
        filepath2 = row['filepath']
        if os.path.exists(filepath2):
            os.remove(filepath2)
            dyndb_submission_dynamics_files = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype)
            dyndb_submission_dynamics_files.delete()

@csrf_protect
def _upload_dynamics_files(request,submission_id,trajectory=None,trajectory_max_files=200):
    file_types = get_dynamics_file_types()
    file_type = None
    new_window = '0'
    no_js = '1'
    error = ''
    filetype_complete_names = {'coor':'coordinate','top':'topology','traj':'trajectory','parm':'parameter','other':'other', 'prt':'protocol'}
    filetype_subtypes_dict = {'coor':'pdb','top':'topology','traj':'trajectory','parm':'parameters','other':'other', 'prt':'protocol'}
    filetype_dbtypestext_dict = {'coor':'coor','top':'top','traj':'traj','parm':'param','other':'other', 'prt':'prt'}
    atomnum_check_file_types = {'coor','traj'}
    if 'new_window' in request.GET:
        new_window = request.GET['new_window']
    elif 'new_window' in request.POST:
        new_window = request.POST['new_window']
    if new_window.isdigit() and not isinstance(new_window,int):
        new_window = int(new_window)
    else:
        return HttpResponse('Invalid new_window value.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    if 'no_js' in request.GET:
        no_js = request.GET['no_js']
    elif 'no_js' in request.POST:
        no_js = request.POST['no_js']
    if no_js.isdigit() and not isinstance(no_js,int):
        no_js = int(no_js)
    else:
        return HttpResponse('Invalid new_window value.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    if 'file_type' in request.GET:
        file_type = request.GET['file_type']
    elif 'file_type' in request.POST:
        file_type = request.POST['file_type']
    if file_type == 'traj' and trajectory is None or file_type != 'traj' and trajectory is not None:
        return HttpResponseForbidden('<h1>Forbidden<h1>')
    if file_type not in file_types:
        return HttpResponse('Invalid file_type value',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    if file_type in filetype_subtypes_dict:
        subtype = filetype_subtypes_dict[file_type]
    else:
        response = HttpResponse('Unknown file type: '+str(file_type),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        return response
    accept_string = ',.'.join(file_types[file_type]['extension'])
    accept_string = '.' + accept_string
    action ='./?file_type='+file_type+'&new_window='+str(new_window)+'&no_js='+str(no_js)+'&timestamp='+str(round(time.time()*1000))
    dbtype = type_inverse_search(DyndbSubmissionDynamicsFiles.file_types,searchkey=filetype_dbtypestext_dict[file_type],case_sensitive=False,first_match=True)
    
    if request.method == "POST":
        exceptions = False
        data = dict()
        data['download_url_file'] = []
        submission_path = get_file_paths("dynamics",url=False,submission_id=submission_id)
        submission_url = get_file_paths("dynamics",url=True,submission_id=submission_id)    
        try:
            if file_type+'_delete_all' in request.POST:
                if int(request.POST[file_type+'_delete_all']):
                   delete_uploaded_dynamic_files(submission_id,dbtype)
                   response = HttpResponse("Done!",status=200,reason='OK',content_type='text/plain; charset=UTF-8')
                   return response
            if file_type in atomnum_check_file_types:
                reffilepath, reffilename, ref_file_type, ref_numatoms = get_dynamics_files_reference_atomnum(submission_id,file_type)
                prev_numatoms = ref_numatoms
            if 'filekey' in request.POST:
                filekey = request.POST['filekey']
            else:
                response = HttpResponse('Missing POST keys.'+str(file_type),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            filekey_in_files = bool(filekey not in request.FILES)    
            for upload_handler in request.upload_handlers:
                if hasattr(upload_handler,'exception'):
                    if upload_handler.exception is not None:
                        raise upload_handler.exception
            if  filekey_in_files:
                msg = 'No file was selected or cannot find molecule file reference.'
                response = HttpResponse(msg,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            if trajectory is None:
                uploadedfiles = [request.FILES[filekey]]
            else:
                uploadedfiles = request.FILES.getlist(filekey)
            if len(uploadedfiles) == 0:
                msg = 'No file was selected.'
                response = HttpResponse(msg,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response               
            elif len(uploadedfiles) > 1 and file_type != 'traj':
                msg = 'Too many files selected (Max. 1).'
                response = HttpResponse(msg,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response   
            elif file_type == 'traj' and len(uploadedfiles) > trajectory_max_files:
                msg = 'Too many files selected (Max. 200).'
                response = HttpResponse(msg,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response   
            filenum = 0
            for uploadedfile in uploadedfiles:
                n_frames = None
                rootname,fileext = os.path.splitext(uploadedfile.name)
                if fileext == '.gz':
                    rootname2,fileext2 = os.path.splitext(rootname)
                    if fileext2 == '.tar':
                        fileext = fileext2 + fileext
                        rootname = rootname2
                fileext = fileext.lower()
                fileext = fileext[1:]
                invalid_ext = False
                if fileext not in file_types[file_type]['extension']:
                    invalid_ext = True
                if invalid_ext: 
                    response = HttpResponse('Invalid extension ".'+fileext+'" for '+file_types[file_type]['long_name'].lower(),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                if fileext == 'tgz':
                    ext = 'tar.gz'
                else:
                    ext = fileext
                filename = get_file_name_submission("dynamics",submission_id,filenum,ext=ext,forceext=False,subtype=subtype)
                filepath = os.path.join(submission_path,filename)
                download_url = os.path.join(submission_url,filename)
                os.makedirs(submission_path,exist_ok=True)
                if file_type in atomnum_check_file_types:
                    if request.upload_handlers[0].activated:
                        deleteme_filepath = os.path.join(submission_path,'deleteme_'+filename)
                        save_uploadedfile(deleteme_filepath,uploadedfile)
                    else:
                        deleteme_filepath = uploadedfile.temporary_file_path()
                    try:
                        numatoms = get_atoms_num(deleteme_filepath,file_type,ext=ext)
                        n_frames = get_frames_num(deleteme_filepath,file_type,ext=ext)
                    except:
                        response = HttpResponse('Cannot parse "'+uploadedfile.name+'" as '+ext.upper()+' file.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
                    if file_type != 'traj' and ref_numatoms is not None and ref_numatoms != numatoms:
                        if ref_file_type == 'traj':
                            files_text = 'file(s)'
                        else:
                            files_text = 'file'
                        response = HttpResponse('Uploaded '+filetype_complete_names[file_type]+' file "'+uploadedfile.name+'" number of atoms ('+str(numatoms)+') differs from uploaded '+filetype_complete_names[ref_file_type]+' '+files_text+'.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
                if file_type == 'traj':
                    if filenum == 0:
                        if ref_numatoms is not None and ref_numatoms != numatoms:
                            response = HttpResponse('Uploaded trajectory file "'+uploadedfile.name+'" number of atoms ('+str(numatoms)+') differs from uploaded coordinate file.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
                        delete_uploaded_dynamic_files(submission_id,dbtype)
                    elif prev_numatoms != numatoms:
                        response = HttpResponse('Uploaded trajectory file "'+uploadedfile.name+'" number of atoms ('+str(numatoms)+') differs from "'+prev_name+'".',status=432,reason='Partial Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
                    prev_name = uploadedfile.name
                    prev_numatoms = numatoms
                (file_entry,created) = DyndbSubmissionDynamicsFiles.objects.update_or_create(submission_id=DyndbSubmission.objects.get(pk=submission_id),type=dbtype,filenum=filenum,defaults={'filename':filename,'filepath':filepath,'url':download_url,'framenum':n_frames,'to_delete':False,'is_deleted':False})
                data['download_url_file'].append(download_url)
                try:
                    if file_type in atomnum_check_file_types and request.upload_handlers[0].activated:
                        os.rename(deleteme_filepath,filepath)
                    else:
                        save_uploadedfile(filepath,uploadedfile)
                except:
                    try:
                        os.remove(filepath)
                    except:
                        pass
                    try:
                        os.remove(deleteme_filepath)
                    except:
                        pass
                    try:
                        file_entry.delete()
                    except:
                        pass
                    response = HttpResponseServerError('Cannot save uploaded file.',content_type='text/plain; charset=UTF-8')
                    return response
                finally:
                    uploadedfile.close()
                filenum += 1
            if file_type == 'traj':
                file_entries_to_delete = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype,filenum__gte=filenum)
                filepaths_to_delete = file_entries_to_delete.values_list('filepath',flat=True)
                for path in filepaths_to_delete:
                    if os.path.isfile(path):
                        os.remove(path)
                #set to delete from DyndbFilesDynamics upon dynamics submission
                file_entries_to_delete.update(filename="",filepath="",url="",framenum=None,to_delete=True,is_deleted=False)
            data['msg'] = 'File successfully uploaded.'
            response = JsonResponse(data)
            return response
        except:
            exceptions = True
            raise
        finally:
            if not exceptions:
                if new_window > 0 or no_js > 0:
                    if response.status_code != 200:
                        error = response.content.decode()
                        success = False
                    else:
                        success = True
                    return render(request,'dynadb/DYNAMICS_file_upload.html',{'action':action,'file_type':file_type,
                    'long_name':file_types[file_type]['long_name'],'description':file_types[file_type]['description'],
                    'new_window':new_window,'download_urls':data['download_url_file'],'success':success,'error':error,
                    'accept_ext':accept_string,'no_js':no_js,'get':False},status=response.status_code)
    elif request.method == "GET":
        q_uploaded_files = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype)
        q_uploaded_files = q_uploaded_files.order_by('filenum').values_list('url',flat=True)
        return render(request,'dynadb/DYNAMICS_file_upload.html',{'action':action,'file_type':file_type,
        'long_name':file_types[file_type]['long_name'],'description':file_types[file_type]['description'],
        'new_window':new_window,'success':None,'error':'','download_urls':q_uploaded_files,'accept_ext':accept_string,'no_js':no_js,'get':True})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def DYNAMICSview(request, submission_id, model_id=None):
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    initDyn={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() , 'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user ,  'id_model':model_id,'submission_id':submission_id }
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None,'id_structure_model':None, 'template_id_model':None,'model_creation_submission_id':submission_id,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user    }
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  }
                   
    def dynamics_file_table (dname, DFpk): #d_fmolec_t, dictext_id 
        fdbF={}
        fdbFobj={}
        qft=DyndbFileTypes.objects.all().values()
        ext_to_descr={'pdb': "pdb simulation coordinates file", 'psf':'psf simulation topology file', 'prm':"prm simulation parameters file", 'dcd':"dcd simulation trajectory file", 'xtc':"xtc simulation trajectory file", 'tar.gz':'parameters, protocol or other simulation files', 'zip':'parameters, protocol or other simulation files'}  
       #####  
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            if l.__dict__['extension'].rstrip() == "psf":
                dict_ext_id[l.__dict__['extension'].rstrip()]=5
            elif l.__dict__['extension'].rstrip() == "prm":
                dict_ext_id[l.__dict__['extension'].rstrip()]=15
            else:
                dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
       ##############
        for key,val  in dname.items():
            print("val\n", val)
            fext=".".join(val['path'].split(".")[1:])
            initFiles['id_file_types']=dict_ext_id[fext]
            initFiles['url']=val['url']
            initFiles['filename']="".join(val['path'].split("/")[-1])
            initFiles['filepath']=val['path']
            initFiles['description']=ext_to_descr.get(fext,"")
            print("HOLA initFiles", initFiles)
            if val['id_files'] is not None:
                initFiles['id'] = val['id_files']
            fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
            dicfdyn={}
            dicfdyn['framenum']=val['framenum']
            dicfdyn['type']=val['type']
            dicfdyn['id_dynamics']=DFpk
            if fdbF[key].is_valid():
                fdbFobj[key]=fdbF[key].save()
                dicfdyn['id_files']=fdbFobj[key].pk
                updates_files_entry_flag = False
                update_id_files_flag = True
            elif DyndbFiles.objects.filter(filename=initFiles['filename']).exists():
                prev_entryFile = DyndbFiles.objects.filter(filename=initFiles['filename'])
                updates_files_entry_flag = True
                update_id_files_flag = True
            elif DyndbFiles.objects.filter(pk==initFiles['id']).exists():
                prev_entryFile = DyndbFiles.objects.filter(pk=initFiles['id'])
                updates_files_entry_flag = True
                update_id_files_flag = False
            else:
                print("Errores en el form dyndb_Files\n ", fdbF[key].errors.as_text())
                error=("- ").join(["Error when storing File info",ext_to_descr.get(fext,fext)])
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            
            if updates_files_entry_flag:
                dicfdyn['id_files']=prev_entryFile.values_list('id',flat=True)[0]
                prev_entryFile.update(update_timestamp=timezone.now(), filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])
            if update_id_files_flag:
                sub_files_dyn_entry = DyndbSubmissionDynamicsFiles.objects.filter(pk=val['id_sub_dyn_f'])
                sub_files_dyn_entry.update(id_files=dicfdyn['id_files'])

            fdbFM = {}
            fdbFM[key]=dyndb_Files_Dynamics(dicfdyn)
            if fdbFM[key].is_valid():
                fdbFM[key].save()
            elif DyndbFilesDynamics.objects.filter(id_dynamics__submission_id=submission_id,id_files=dicfdyn['id_files'],type=dicfdyn['type']).exists():
                prev_entryFileM=DyndbFilesDynamics.objects.filter(id_dynamics__submission_id=submission_id,id_files=dicfdyn['id_files'],
                id_files__id_file_types=initFiles['id_file_types'])
                prev_entryFileM.update(id_dynamics=dicfdyn['id_dynamics'],id_files=dicfdyn['id_files'],framenum=dicfdyn['framenum'])

            else:
                error=("- ").join(["Error when storing Dynamics file info",ext_to_descr.get(fext,fext)])
                print("Errores en el form dyndb_Files_Dynamics\n ", fdbFM[key].errors.as_text())
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response

    def handle_uploaded_file(f,p,name):
        print("file name = ", f.name , "path =", p)
        f.name=name
        print("NEW name = ", f.name , "path =", p)
        path=p+"/"+f.name
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    # Dealing with POST data
    if request.method == 'POST':
        #Defining variables and dictionaries with information not available in the html form. This is needed for form instances.
        author="jmr"   #to be modified with author information. To initPF dict
        user="jmr"
        action="/dynadb/DYNAMICSfilled/"
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted
        qM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        model_id=qM.values_list('model_id',flat=True)[0]
        initDyn['id_model']=model_id
        ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
        for l in ['id_dynamics_methods', 'id_assay_types', 'id_dynamics_membrane_types','id_dynamics_solvent_types', 'software', 'solvent_num', 'timestep', 'delta', 'ff', 'ffversion', 'atom_num']:
            if request.POST[l] == '':
                error="\n\nPlease, before submission fill in all fields in the section C of the Step 4."
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        lrmc=[]
        l_checkinpostmc=[]
        print("\n",request.POST,"\n")
        for o in request.POST.keys():
            if o.split("-")[0] == 'formc':
                lrmc.append(("-").join(o.split("-")[:2]))
        lrmc=list(set(lrmc))
        print("lista lrmc ", lrmc)
        for ll in ['name', 'resname', 'numberofmol']:
            for o in lrmc:
                l_checkinpostmc.append(("-").join([o,ll]))
        print("\n\nlista lcheckinpost ", l_checkinpostmc)
        for l in  l_checkinpostmc:     
            if request.POST[l] == '':
                print("ERROR PIPOL", l)
                error="\n\nPlease, fill in the missing 'Resname' cells and click validate after submitting the form."
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        print("JJJJJJJJ")
        # Defining a dictionary "d_fdyn_t" containing choices in the table dyndb_files_dynamics (field 'type')

        d_fdyn_t={'coor':'0','top':'1','traj':'2','parm':'3','other':'3', 'prt':'4'}

        dicpost=request.POST
        lkeydyncomp=["id_molecule","molecule","name","numberofmol","resname","type"]
        indexl=[]
        indexfl=[]
        POSTimod={} #Dictionary of dyctionarys containing POST for each SIMULATION REPLICATE keys have been modified to match table fields
        #FILEmod={} #Dictionary of dyctionarys containing FILES for each SIMULATION REPLICATE keys have been modified to match table fields
        ## Crear diccionario para instanciar dyndb_dynamicsform
        # compilation of regex patterns for searching and modifying keys and make them match the table fields  
        form=re.compile('form-')
        formc=re.compile('formc-')
        for key,val in dicpost.items():
            if form.search(key):
                index=int(key.split("-")[1])
                if index not in indexl:
                    indexl.append(index)
                    POSTimod[index]={}
                POSTimod[index]["-".join(key.split("-")[2:])]=val
            else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
                if len(indexl)==0:
                    indexl.append(0)
                    POSTimod[0]={}
                POSTimod[0][key]=val 
        Pscompmod={} #Dictionary of dyctionarys containing Simulation Components for each SIMULATION REPLICATE  keys have been modified to match table fields
        dyn_ins={}
        dyn_obj={}
        dyn_objf={}
        Scom_inst={}
        Scom_obj={}
        print("lista indexl", indexl," pipol")
        indexl.sort()
        print("lista indexl", indexl," ordenada")
        file_ins={}
        filedyn_ins={}
        file_obj={}
        filedyn_obj={}
        print("\n\nINDEXL: ", indexl)
        for ii in indexl:
            file_ins[ii]={}
            filedyn_ins[ii]={}
            file_obj[ii]={}
            filedyn_obj[ii]={}
            indexcl=[]
            print("\nelemento ", ii, "en indexl")
            Scom_inst[ii]={}
            Scom_obj[ii]={}
            Pscompmod[ii]={}
            dyn_ins[ii]=dyndb_Dynamics(POSTimod[ii])
            for key,value in initDyn.items():
                dyn_ins[ii].data[key]=value
            qDe=DyndbDynamics.objects.filter(submission_id=submission_id)
            if len(qDe) == 0:
                if dyn_ins[ii].is_valid():
                    PREVIOUS_COMP=False
                    dyn_obj[ii]=dyn_ins[ii].save()
                    DFpk=dyn_obj[ii].pk
                else:
                    iii1=dyn_ins[ii].errors.as_text()
                    print("errors in the form Dynamics", ii," ", dyn_ins[ii].errors.as_text())
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
            else:
                PREVIOUS_COMP=True
                print("\n\n PREVIOUS COMPOUNDS updating dyn object")
                DFpk=qDe.values_list('id',flat=True)[0]
                qDe.update(update_timestamp=timezone.now(),delta=POSTimod[ii]['delta'], description=POSTimod[ii]['description'].strip() , ff=POSTimod[ii]['ff'].strip(), ffversion=POSTimod[ii]['ffversion'].strip() , id_dynamics_solvent_types =POSTimod[ii]['id_dynamics_solvent_types'], solvent_num =POSTimod[ii]['solvent_num'], sversion =POSTimod[ii]['sversion'].strip() , atom_num = POSTimod[ii]['atom_num'], timestep =POSTimod[ii]['timestep'], id_dynamics_methods =POSTimod[ii]['id_dynamics_methods'] , software=POSTimod[ii]['software'].strip() ,  id_dynamics_membrane_types =POSTimod[ii]['id_dynamics_membrane_types'], id_assay_types =POSTimod[ii]['id_assay_types'])
            print("\nPOSTimod",ii,POSTimod[ii])
            for key,val in POSTimod[ii].items(): # hay que modificar esto!!!!
                if formc.search(key):
                    indexc=int(key.split("-")[1]) 
                    if indexc not in indexcl:
                        indexcl.append(indexc)
                        Pscompmod[ii][indexc]={}
                        Scom_inst[ii][indexc]={}
                        Scom_obj[ii][indexc]={}
                    Pscompmod[ii][indexc][key.split("-")[2]]=val
                      # print("\nPOSTimod keys",ii,POSTimod[ii].keys())
                    print("\nkey value compmod", key , val, key.split("-")[2],"indexc ", indexc," Index ii: ", ii)
                else:
                    if key in lkeydyncomp:
                        if len(indexcl)==0:
                            print("\nno hay formc\n")
                            indexcl.append(0)
                            Scom_inst[ii][0]={}
                            Scom_obj[ii][0]={}
                            Pscompmod[ii][0]={}
                        print(key,val)
                        Pscompmod[ii][0][key]=val
            print("\nlongitud de indexcl \n",len(indexcl),"dinamica",ii) 
            print("Pscompmod", Pscompmod[ii])
            invMOL_TYPE=dict((v,k) for k, v in dict(DyndbModelComponents.MOLECULE_TYPE).items()) 
            for iii in indexcl:
                print("ii y iii", ii," ", iii)
                Pscompmod[ii][iii]['type']=invMOL_TYPE[Pscompmod[ii][iii]['typemc']]
                if PREVIOUS_COMP==False: 
                    Pscompmod[ii][iii]['id_dynamics']=dyn_obj[ii].pk
                else:
                    Pscompmod[ii][iii]['id_dynamics']=DFpk
                print("ii y iii", ii," ", iii, " Dictionary compound ", Pscompmod[ii][iii] )
            if PREVIOUS_COMP==False:
                for iii in indexcl:
                    Scom_inst[ii][iii]=dyndb_Dynamics_Components(Pscompmod[ii][iii])
                    if Scom_inst[ii][iii].is_valid():
                        Scom_obj[ii][iii]=Scom_inst[ii][iii].save(commit=False)
                        Scom_obj[ii][iii]=Scom_inst[ii][iii].save()
                    else:
                        print("Errores en el form Simulation Components ", ii, " ", Scom_inst[ii][iii].errors.as_data()) 
                        iii1=Scom_inst[ii].errors.as_text()
                        print("errors in the form Dynamics Components", ii," ", Scom_inst[ii].errors.as_text())
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
            else: 
                print("\n __________________________else")
                qDC_match_form=DyndbDynamicsComponents.objects.filter(id_dynamics__submission_id=submission_id).exclude(numberofmol=None,type=None)
                lDC_match_form=list(qDC_match_form.values('id','id_dynamics','resname','id_molecule','numberofmol'))
                qDC_empty_rows=DyndbDynamicsComponents.objects.filter(numberofmol=None,type=None)
                lempty_rows=list(qDC_empty_rows.values_list('id',flat=True))
                lenCompDB=len(lDC_match_form)
                lenform=len( Pscompmod[ii])
                used_el=[]#table lines matching lines in the form. numberof mol would be updated
                del_el=[]#db lines which no longer takes part in the updated model. Will be reusable in whatever new entry
                used_val=[]# form value matching a db entrie. The number of mol in the db will be updated if needed
                new_val=[]#new form compound to be registered. We ll use a reusable entry if available. 
                counterf=0 # it counts the compounds in the form during the loop
                BREAK1=False
                BREAK2=False
                for key,val in Pscompmod[ii].items(): #comparison between form info and dB. If different update.
                    if len(used_el)==len(lDC_match_form):
                        print("\nBREAK1 used_el == dB el; counterf==   ", counterf)
                        qel_let_fval=True #num query elements less than form lines!!!!
                        break
                    counterf=counterf+1
                    for el in lDC_match_form:
                        if len(used_val)==len(Pscompmod[ii]):
                            qel_bit_fvl=True #num query elements > than form lines!!!!
                            break
                        print("AUN      NNNNNNNNNNNNN")
                        if el in used_el:
                            continue
                        if int(el['id_molecule'])==int(val['id_molecule']) and el['resname'].strip()==val['resname'].strip() and int(el['id_dynamics'])==int(val['id_dynamics']):
                            print("\n __________________________igual")
                            if not el['numberofmol'] == val['numberofmol']:
                                qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol']) #updating entries with the same compound
                            used_el.append(el)
                            used_val.append(val)
                            break
                        if el == lDC_match_form[-1]: #that means no query element matches the form compound val, so val is a new entry
                            new_val.append(val)
                for el in lDC_match_form: # creating a list of entries to be reused with a different compound
                    print (lDC_match_form)
                    if el not in used_el:
                        del_el.append(el)      
                for key,val in Pscompmod[ii].items():  #new compound to register in the list of entries del_el
                    if val not in used_val:
                        new_val.append(val)
                print(new_val, " must be saved")
  
                print(del_el, " must be removed")
                used_new_val=[]                
                used_del_el=[]
                print ("\ndel elements dB",del_el) 
                if lenCompDB > lenform: #if so the number of elements in del_el is higher than in new_val. the el entries will be used for store the val form lines. Then 
                    for el in del_el:
                        if BREAK1:
                            break
                        if len(new_val)>0:
                            for val in new_val:
                                if val in used_new_val:
                                    continue
                                qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
                                used_new_val.append(val)
                                used_del_el.append(el)
                                if val == used_new_val[-1]:
                                    for el in del_el:
                                        if el not in used_del_el:
                                             qDC_match_form.filter(id=el['id']).update(numberofmol=None,resname=el['id'],type=None) 
                                    BREAK1=True
                                    break
                                else:
                                    break
                        else:
                            qDC_match_form.filter(id=el['id']).update(numberofmol=None,resname=el['id'],type=None) 
                else:
                    print("\n HIGHER number of form rows")
                    for val in new_val:
                        if BREAK2:
                            break
                        if len(del_el)>0:
                            for el in del_el: 
                                if el in used_del_el:
                                   continue
                                qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
                                used_new_val.append(val)
                                used_del_el.append(el)
                                if val == new_val[-1]: #this implies that lenCompDB= lenform and len(new_val)==len(del_el) so after updating the loop is finished 
                                    BREAK2=True
                                    break
                                if el == del_el[-1]:
                                    used_empty_rows=[]
                                    if len(lempty_rows) > 0 and len(lempty_rows) > len(used_empty_rows):
                                        for i in lempty_rows:
                                            if BREAK2:
                                                break
                                            for val in new_val:
                                                if val not in used_new_val:
                                                    if i not in used_empty_rows:
                                                        qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
                                                        used_new_val.append(val)
                                                        used_empty_rows.append(i)
                                                        if val == used_new_val[-1]:
                                                            BREAK2=True # all rows in the form (val) are registered... the "Break" cascade starts
                                                            break
                                                        if not i == lempty_rows[-1]:
                                                            break 
                                                        else:
                                                            continue
                                                    else:
                                                        Scom_inst=dyndb_Dynamics_Components(val)
                                                        used_new_val.append(val)
                                                        if Scom_inst.is_valid():
                                                            Scom_obj=Scom_inst.save()
                                                            if val == used_new_val[-1]:
                                                                BREAK2=True # all lines in the form (val) are registered... the "Break" cascade starts
                                                                break
                                                            continue #if there is still some row in new val list 
                                                        else:
                                                            iii1=Scom_inst.errors.as_text()
                                                            print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
                                                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                                            return response                                                                                             
                                    else:
                                        Scom_inst=dyndb_Dynamics_Components(val)
                                        if Scom_inst.is_valid():
                                            Scom_obj=Scom_inst.save()
                                            continue
                                        else:
                                            iii1=Scom_inst.errors.as_text()
                                            print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
                                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                            return response                                                                                                         
                        elif len(lempty_rows) > 0:
                            used_empty_rows=[]
                            print("PRINT empty rows____________________",lempty_rows)
                            for i in lempty_rows:
                                print("used_empty_rows", used_empty_rows)
                                if BREAK2:
                                    break
                                for val in new_val:
                                    if val not in used_new_val:
                                        if i not in used_empty_rows:
                                            qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
                                            used_new_val.append(val)
                                            used_empty_rows.append(i)
                                            print("updated to " ,val)
                                            if val == new_val[-1]:
                                                print("last val")
                                                BREAK2=True # all rows in the form (val) are registered... the "Break" cascade starts
                                                break
                                            if not i == lempty_rows[-1]:
                                                break 
                                            else:
                                                continue
                                        else:
                                            Scom_inst=dyndb_Dynamics_Components(val)
                                            used_new_val.append(val)
                                            if Scom_inst.is_valid():
                                                Scom_obj=Scom_inst.save()
                                                if val == used_new_val[-1]:
                                                    BREAK2=True # all lines in the form (val) are registered... the "Break" cascade starts
                                                    break
                                                continue #if there is still some row in new val list 
                                            else:
                                                iii1=Scom_inst.errors.as_text()
                                                print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
                                                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                                return response                                                                                             
                        else:
                            Scom_inst=dyndb_Dynamics_Components(val)
                            if Scom_inst.is_valid():
                                Scom_obj=Scom_inst.save()
                                continue
                            else:
                                iii1=Scom_inst.errors.as_text()
                                print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
                                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
                                return response                                                                                                         
            direct=settings.MEDIA_ROOT+'Dynamics/dyn'+str(submission_id) 
            print("\nDirectorio a crear ", direct)
            if not os.path.exists(direct):
                os.makedirs(direct)
            qSDF=DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,is_deleted=False)
            lfiles=list(qSDF.values('id','filepath','url','type','framenum','id_files','to_delete'))
            for f in lfiles:
                if f['to_delete']:
                    DyndbFilesDynamics.objects.filter(id_files=f['id_files']).update(id_files=None)
                    DyndbFiles.objects.filter(pk=f['id_files']).delete()
                    DyndbSubmissionDynamicsFiles.objects.filter(id_files=f['id_files']).update(to_delete=False,is_deleted=True)
                    continue
                if not isfile(f['filepath']):
                    response = HttpResponse((" ").join(["There is a simulation file which has not been succesfully saved (",f[filename],") Make the GPCRmd administrator know"]),status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                else:
                    dname={'file':{'path':f['filepath'],'url':f['url'],'type':f['type'],'framenum':f['framenum'],'id_files':f['id_files'],'id_sub_dyn_f':f['id']}}

                    ooofile= dynamics_file_table(dname,DFpk) 
                    if type(ooofile)==HttpResponse:
                        return ooofile 
        response = HttpResponse('Step 4 "Dynamics Information" form has been successfully submitted.',content_type='text/plain; charset=UTF-8')
        return response
    else:
        qDYNs=DyndbDynamics.objects.filter(submission_id=submission_id)
        qMOD=DyndbSubmissionModel.objects.filter(submission_id=submission_id).order_by('id').values('model_id')
        qMOD_first=DyndbSubmissionModel.objects.filter(submission_id=submission_id,model_id__model_creation_submission_id=submission_id)        
        ModelReuse=False
        if qMOD.exists() and not qMOD_first.exists(): #the model has been saved but is not the first one using the model 
            ModelReuse=True
        protlist=list(DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id').select_related('protein_id').values_list('int_id','protein_id__uniprotkbac','protein_id__name')) 
        if len(qDYNs)==1:
            qDYNsids=qDYNs.values_list('id',flat=True)[0]
            ddown={}
            ddown['id_dynamics_methods']= DyndbDynamicsMethods.objects.filter(dyndbdynamics=qDYNsids).values_list('id','type_name')[0]
            ddown['id_assay_types']= DyndbAssayTypes.objects.filter(dyndbdynamics=qDYNsids).values_list('id','type_name')[0]
            ddown['id_dynamics_membrane_types']=DyndbDynamicsMembraneTypes.objects.filter(dyndbdynamics=qDYNsids).values_list('id','type_name')[0]
            ddown['id_dynamics_solvent_types']=DyndbDynamicsSolventTypes.objects.filter(dyndbdynamics=qDYNsids).values_list('id','type_name')[0]
            print(qDYNs.values()[0])
            compl=[]
            ddctypel=[]
            n=0
            for tt in qDYNs.values_list('id',flat=True):
                print("ESTO ES TT",tt)
                queryDC=DyndbDynamicsComponents.objects.filter(numberofmol__gte=0,type__gte=0,id_dynamics=tt,id_molecule__dyndbsubmissionmolecule__submission_id=submission_id)
                from django.db.models import Q
                querySM=DyndbSubmissionMolecule.objects.filter(~Q(molecule_id__in=queryDC.values('id_molecule')),~Q(int_id=None),submission_id=submission_id)
                qDC=queryDC.values('id','resname','numberofmol','id_molecule','id_molecule__dyndbsubmissionmolecule__type','id_molecule__dyndbsubmissionmolecule__int_id','id_molecule__dyndbcompound__name','type').order_by('id_molecule__dyndbsubmissionmolecule__int_id')
                qSM=querySM.values('id','molecule_id','int_id','molecule_id__dyndbcompound__name','type').order_by('int_id')
                print("\n MIRA AQUI",qDC,"\n\n")
                compdcl=list(qDC)
                compsub=list(qSM)
                print("LLL",compl)
                d=0
                for l in compdcl:
                    print ("Dicttionary ", l, "\n l keys", l.keys())
                    if smol_to_dyncomp_type[l['id_molecule__dyndbsubmissionmolecule__type']] == l['type']: #compare type in the submission molecule with the one stored in model components
                        ddctypel.append(DyndbModelComponents.MOLECULE_TYPE[l['type']][1])
                    else: # if different types, the one derived from  submission molecules is the updated version 
                        print(ddctypel,"PPPPP")
                        ddctypel.append(DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l['id_molecule__dyndbsubmissionmolecule__type']]][1])
                        l['type']=DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l['id_molecule__dyndbsubmissionmolecule__type']]][0]
                        l['numberofmol']=int(l['numberofmol'])
                for l in compsub: ####POR AQUI
                    print ("Dicttionary ", l, "\n l keys", l.keys())
               # else: # if different types, the one derived from  submission molecules is the updated version 
                    ddctypel.append(DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l['type']]][1])
                    print(type(l['type']))
                    l['id_molecule__dyndbsubmissionmolecule__type']=l['type']
                    l['type']=DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l['type']]][0]
                print(compsub)        
                print(ddctypel,"PPPPP")
                compl=compdcl+compsub
            dd=dyndb_Dynamics()
            ddC =dyndb_Dynamics_Components()
            qDMT =DyndbDynamicsMembraneTypes.objects.all().order_by('id')
            qDST =DyndbDynamicsSolventTypes.objects.all().order_by('id')
            qDMeth =DyndbDynamicsMethods.objects.all().order_by('id')
            qAT =DyndbAssayTypes.objects.all().order_by('id')
            return render(request,'dynadb/DYNAMICS.html', {'dd':dd, 'ddctypel':ddctypel,'ddC':ddC, 'qDMT':qDMT, 'qDST':qDST, 'qDMeth':qDMeth, 'qAT':qAT, 'qDS':qDYNs,'compl':compl,'ddown':ddown,'submission_id':submission_id,'protlist':protlist, 'saved':True,'file_types':file_types, 'qMOD':qMOD, 'ModelReuse':ModelReuse })
        elif len(qDYNs)>1:
            response = HttpResponse((" ").join(["There are more than one dynamics objects for the same submission (",submission_id,") Make the GPCRmd administrator know"]),status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
        else:
            file_types_items = file_types.items()
            dd=dyndb_Dynamics()
            ddC =dyndb_Dynamics_Components()
            qDMT =DyndbDynamicsMembraneTypes.objects.all().order_by('id')
            qDST =DyndbDynamicsSolventTypes.objects.all().order_by('id')
            qDMeth =DyndbDynamicsMethods.objects.all().order_by('id')
            qAT =DyndbAssayTypes.objects.all().order_by('id')
            mdata = get_components_info_from_components_by_submission(submission_id,'model')
            cdata = get_components_info_from_submission(submission_id,'dynamics')
            other_int = type_inverse_search(DyndbDynamicsComponents.MOLECULE_TYPE,searchkey="other",case_sensitive=False,first_match=True)
            molecule_type_dict = dict(DyndbDynamicsComponents.MOLECULE_TYPE)
            i = 0
            for row in mdata:
                #mdata[i]['numberofmol'] = ''
                mdata[i]['readonly'] = True
                mdata[i]['int_id'] = 1 + mdata[i]['int_id']
                mdata[i]['type_int'] = model_2_dynamics_molecule_type.translate(mdata[i]['type'],as_text=False)
                if mdata[i]['type_int'] is None:
                    mdata[i]['type_int'] = other_int
                mdata[i]['type'] = model_2_dynamics_molecule_type.translate(mdata[i]['type'],as_text=True)
                mdata[i]['cryst'] = True
                i += 1
            print("llll",mdata)
            i = 0
            for row in cdata:
                cdata[i]['resname'] = ''
                cdata[i]['numberofmol'] = ''
                cdata[i]['readonly'] = False
                cdata[i]['int_id'] = 1 + cdata[i]['int_id']
                cdata[i]['type_int'] = cdata[i]['type']
                if cdata[i]['type_int'] is None:
                    cdata[i]['type_int'] = other_int
                cdata[i]['type'] = molecule_type_dict[cdata[i]['type_int']]
                cdata[i]['cryst'] = False
                i += 1
            data = mdata + cdata
            return render(request,'dynadb/DYNAMICS.html', {'dd':dd,'ddC':ddC, 'qDMT':qDMT, 'qDST':qDST, 'qDMeth':qDMeth,'protlist':protlist, 'qAT':qAT, 'submission_id' : submission_id,'data':data, 'file_types':file_types, 'ModelReuse':ModelReuse, 'qMOD':qMOD })

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def SUBMITTEDview(request,submission_id): 
        return render(request,'dynadb/SUBMITTED.html',{'submission_id':submission_id})
        
@login_required
def get_Author_Information(request): 
        return render(request,'dynadb/dynadb_Author_Information.html'  )

@login_required
def db_inputformMAIN(request, submission_id=None): 
    if submission_id is None:
        dictsubid={}
        disable_3=True
        disable_4=True
        disable_5=True
        dictsubid['user_id']=str(request.user.pk)
        fdbsub=dyndb_Submission(dictsubid)
        fdbsubobj=fdbsub.save()
        submission_id = fdbsubobj.pk
    elif is_submission_owner(request.user,submission_id):
        DSM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        DD=DyndbDynamics.objects.filter(submission_id=submission_id)        
        disable_3 = (not len(DSM))
        disable_4 = (not len(DD))
        disable_5 = (not len(DD))
    else:
        return HttpResponseRedirect(reverse('dynadb:db_inputform'))
    return render(request,'dynadb/dynadb_inputformMAIN.html', context={'submission_id':submission_id, 'disable_3':disable_3 , 'disable_4':disable_4, 'disable_5' : disable_5 } )

@login_required
def get_FilesCOMPLETE(request): 
    # MEZCLA DE TABLAS PARA HACER 
    if request.method == 'POST':
        fdb_Files1 = dyndb_Files(request.POST)
        fdb_Files2 = dyndb_Files_Dynamics(request.POST)
        fdb_Files3 = dyndb_File_Types(request.POST)
        fdb_Files4 = dyndb_Files_Model(request.POST)
        fdb_Files5 = dyndb_Files_Molecule(request.POST)
        # check whether it's valid:
        if fdb_Files1() and fdb_Files2() and  fdb_Files3() and fdb_Files4() and fdb_Files5(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/FilesCOMPLETE/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_Files1 = dyndb_Files()
        fdb_Files2 = dyndb_Files_Dynamics()
        fdb_Files3 = dyndb_File_Types()
        fdb_Files4 = dyndb_Files_Model()
        fdb_Files5 = dyndb_Files_Molecule()
        return render(request,'dynadb/dynadb_FilesCOMPLETE.html', {'fdb_Files1':fdb_Files1, 'fdb_Files2':fdb_Files2, 'fdb_Files3':fdb_Files3, 'fdb_Files4':fdb_Files4, 'fdb_Files5':fdb_Files5 })

@login_required
def get_ProteinForm(request): 
    if request.method == 'POST':
        fdb_ProteinForm = dyndb_ProteinForm(request.POST)
        # check whether it's valid:
        if fdb_ProteinForm.is_valid(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/ProteinForm/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_ProteinForm=dyndb_ProteinForm()
        return render(request,'dynadb/dynadb_ProteinForm.html', {'fdb_ProteinForm':fdb_ProteinForm} )

@login_required
def get_CompoundForm(request): 
    if request.method == 'POST':
        fdb_CompoundForm = dyndb_CompoundForm(request.POST)
        # check whether it's valid:
        if fdb_CompoundForm.is_valid(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/CompoundForm/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_CompoundForm=dyndb_CompoundForm()
        return render(request,'dynadb/dynadb_CompoundForm.html', {'fdb_CompoundForm':fdb_CompoundForm} )

@login_required   
def  get_Component(request): 
    if request.method == 'POST':
        fdb_Molecule = dyndb_Molecule(request.POST)
        fdb_CompoundForm = dyndb_CompoundForm(request.POST)
        # check whether it's valid:
        if fdb_Molecule.is_valid() and fdb_CompoundForm.is_valid():  
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/Molecule/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_Molecule=dyndb_Molecule()
        fdb_CompoundForm = dyndb_CompoundForm()
        return render(request,'dynadb/dynadb_Component.html', {'fdb_Molecule':fdb_Molecule , 'fdb_CompoundForm':fdb_CompoundForm} )

@login_required
def get_Molecule(request): 
    if request.method == 'POST':
        fdb_Molecule = dyndb_Molecule(request.POST)
        # check whether it's valid:
        if fdb_Molecule.is_valid(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/Molecule/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_Molecule=dyndb_Molecule()
        return render(request,'dynadb/dynadb_Molecule.html', {'fdb_Molecule':fdb_Molecule} )

@login_required
def get_Model(request): 
    if request.method == 'POST':
        fdb_Model = dyndb_Model(request.POST)
        # check whether it's valid:
        if fdb_Model.is_valid(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/Model/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_Model=dyndb_Model()
        return render(request,'dynadb/dynadb_Model.html', {'fdb_Model':fdb_Model} )
@login_required
def get_Dynamics(request): 
    if request.method == 'POST':
        fdb_Dynamics = dyndb_Dynamics(request.POST)
        # check whether it's valid:
        if fdb_Dynamics.is_valid(): 
            # process the data in form.cleaned_data as required
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/TF/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_Dynamics=dyndb_Dynamics()
        return render(request,'dynadb/dynadb_Dynamics.html', {'fdb_Dynamics':fdb_Dynamics} )

@login_required
def get_DyndbFilesExcFields(request):
    if request.method == 'POST':
        fdb_ProteinForm  =  dyndb_ProteinForm(request.POST)
        fdb_Other_Protein_NamesForm = dyndb_Other_Protein_NamesForm(request.POST) 
        fdb_Protein_SequenceForm = dyndb_Protein_SequenceForm(request.POST)
        fdb_Cannonical_ProteinsForm = dyndb_Cannonical_ProteinsForm(request.POST) 
        fdb_Protein_MutationsForm = dyndb_Protein_MutationsForm(request.POST)
        fdb_CompoundForm = dyndb_CompoundForm(request.POST)
        fdb_Other_Compound_Names = dyndb_Other_Compound_Names(request.POST)
        fdb_Molecule = dyndb_Molecule(request.POST) 
        fdb_Files = dyndb_Files(request.POST)
        fdb_Files_Molecule = dyndb_Files_Molecule(request.POST) 
        fdb_Complex_Exp = dyndb_Complex_Exp() 
        fdb_Complex_Protein = dyndb_Complex_Protein(request.POST) 
        fdb_Complex_Molecule = dyndb_Complex_Molecule(request.POST) 
        fdb_Complex_Molecule_Molecule = dyndb_Complex_Molecule_Molecule(request.POST) 
        fdb_Modeled_Residues = dyndb_Modeled_Residues(request.POST)
        fdb_Files_Model = dyndb_Files_Model(request.POST)
        fdb_Dynamics = dyndb_Dynamics(request.POST)
        fdb_Dynamics_tags = dyndb_Dynamics_tags(request.POST)
        fdb_Dynamics_Tags_List = dyndb_Dynamics_Tags_List(request.POST)
        fdb_Files_Dynamics = dyndb_Files_Dynamics(request.POST)
        fdb_Related_Dynamics = dyndb_Related_Dynamics(request.POST)
        fdb_Related_Dynamics_Dynamics = dyndb_Related_Dynamics_Dynamics(request.POST)
        fdb_Model = dyndb_Model(request.POST) 
        # check whether it's valid:
        if fdb_ProteinForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Protein_SequenceForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Cannonical_ProteinsForm.is_valid() and fdb_Protein_MutationsForm.is_valid() and fdb_CompoundForm.is_valid() and fdb_Other_Compound_Names.is_valid() and fdb_Molecule.is_valid() and fdb_Files.is_valid() and fdb_Files_Molecule.is_valid() and fdb_Complex_Exp.is_valid() and fdb_Complex_Protein.is_valid() and fdb_Complex_Molecule.is_valid() and fdb_Complex_Molecule_Molecule.is_valid() and fdb_Modeled_Residues.is_valid() and fdb_Files_Model.is_valid() and fdb_Dynamics.is_valid() and fdb_Dynamics_tags.is_valid() and fdb_Dynamics_Tags_List.is_valid() and fdb_Files_Dynamics.is_valid() and fdb_Related_Dynamics.is_valid() and fdb_Related_Dynamics_Dynamics.is_valid() and fdb_Model.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/TF/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_ProteinForm = dyndb_ProteinForm()
        fdb_Other_Protein_NamesForm=dyndb_Other_Protein_NamesForm() 
        fdb_Protein_SequenceForm=dyndb_Protein_SequenceForm()
        fdb_Other_Protein_NamesForm= dyndb_Other_Protein_NamesForm()
        fdb_Cannonical_ProteinsForm=dyndb_Cannonical_ProteinsForm() 
        fdb_Protein_MutationsForm=dyndb_Protein_MutationsForm()
        fdb_CompoundForm=dyndb_CompoundForm()
        fdb_Other_Compound_Names=dyndb_Other_Compound_Names()
        fdb_Molecule=dyndb_Molecule() 
        fdb_Files=dyndb_Files()
        fdb_Files_Molecule=dyndb_Files_Molecule() 
        fdb_Complex_Exp=dyndb_Complex_Exp() 
        fdb_Complex_Protein=dyndb_Complex_Protein() 
        fdb_Complex_Molecule=dyndb_Complex_Molecule() 
        fdb_Complex_Molecule_Molecule=dyndb_Complex_Molecule_Molecule() 
        fdb_Modeled_Residues=dyndb_Modeled_Residues()
        fdb_Files_Model=dyndb_Files_Model()
        fdb_Dynamics=dyndb_Dynamics()
        fdb_Dynamics_tags=dyndb_Dynamics_tags()
        fdb_Dynamics_Tags_List=dyndb_Dynamics_Tags_List()
        fdb_Files_Dynamics=dyndb_Files_Dynamics()
        fdb_Related_Dynamics=dyndb_Related_Dynamics()
        fdb_Related_Dynamics_Dynamics=dyndb_Related_Dynamics_Dynamics()
        fdb_Model = dyndb_Model() 
        return render(request,'dynadb/DYNAnameab.html', {'fdb_ProteinForm':fdb_ProteinForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Protein_SequenceForm':fdb_Protein_SequenceForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Cannonical_ProteinsForm':fdb_Cannonical_ProteinsForm, 'fdb_Protein_MutationsForm': fdb_Protein_MutationsForm, 'fdb_CompoundForm': fdb_CompoundForm, 'fdb_Other_Compound_Names':fdb_Other_Compound_Names, 'fdb_Molecule':fdb_Molecule, 'fdb_Files':fdb_Files, 'fdb_Files_Molecule':fdb_Files_Molecule, 'fdb_Complex_Exp':fdb_Complex_Exp, 'fdb_Complex_Protein':fdb_Complex_Protein, 'fdb_Complex_Molecule':fdb_Complex_Molecule, 'fdb_Complex_Molecule_Molecule':fdb_Complex_Molecule_Molecule, 'fdb_Modeled_Residues':fdb_Modeled_Residues, 'fdb_Files_Model':fdb_Files_Model, 'fdb_Dynamics':fdb_Dynamics, 'fdb_Dynamics_tags':fdb_Dynamics_tags, 'fdb_Dynamics_Tags_List':fdb_Dynamics_Tags_List, 'fdb_Files_Dynamics':fdb_Files_Dynamics, 'fdb_Related_Dynamics':fdb_Related_Dynamics, 'fdb_Related_Dynamics_Dynamics':fdb_Related_Dynamics_Dynamics, 'fdb_Model':fdb_Model})

def get_DyndbFiles(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        fdb_ProteinForm  =  dyndb_ProteinForm(request.POST)
        fdb_Other_Protein_NamesForm = dyndb_Other_Protein_NamesForm(request.POST) 
        fdb_Protein_SequenceForm = dyndb_Protein_SequenceForm(request.POST)
        fdb_Cannonical_ProteinsForm = dyndb_Cannonical_ProteinsForm(request.POST) 
        fdb_Protein_MutationsForm = dyndb_Protein_MutationsForm(request.POST)
        fdb_CompoundForm = dyndb_CompoundForm(request.POST)
        fdb_Other_Compound_Names = dyndb_Other_Compound_Names(request.POST)
        fdb_Molecule = dyndb_Molecule(request.POST) 
        fdb_Files = dyndb_Files(request.POST)
        fdb_Files_Molecule = dyndb_Files_Molecule(request.POST) 
        fdb_Complex_Exp = dyndb_Complex_Exp() 
        fdb_Complex_Protein = dyndb_Complex_Protein(request.POST) 
        fdb_Complex_Molecule = dyndb_Complex_Molecule(request.POST) 
        fdb_Complex_Molecule_Molecule = dyndb_Complex_Molecule_Molecule(request.POST) 
        fdb_Modeled_Residues = dyndb_Modeled_Residues(request.POST)
        fdb_Files_Model = dyndb_Files_Model(request.POST)
        fdb_Dynamics = dyndb_Dynamics(request.POST)
        fdb_Dynamics_tags = dyndb_Dynamics_tags(request.POST)
        fdb_Dynamics_Tags_List = dyndb_Dynamics_Tags_List(request.POST)
        fdb_Files_Dynamics = dyndb_Files_Dynamics(request.POST)
        fdb_Related_Dynamics = dyndb_Related_Dynamics(request.POST)
        fdb_Related_Dynamics_Dynamics = dyndb_Related_Dynamics_Dynamics(request.POST)
        fdb_Model = dyndb_Model(request.POST) 
        if fdb_ProteinForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Protein_SequenceForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Cannonical_ProteinsForm.is_valid() and fdb_Protein_MutationsForm.is_valid() and fdb_CompoundForm.is_valid() and fdb_Other_Compound_Names.is_valid() and fdb_Molecule.is_valid() and fdb_Files.is_valid() and fdb_Files_Molecule.is_valid() and fdb_Complex_Exp.is_valid() and fdb_Complex_Protein.is_valid() and fdb_Complex_Molecule.is_valid() and fdb_Complex_Molecule_Molecule.is_valid() and fdb_Modeled_Residues.is_valid() and fdb_Files_Model.is_valid() and fdb_Dynamics.is_valid() and fdb_Dynamics_tags.is_valid() and fdb_Dynamics_Tags_List.is_valid() and fdb_Files_Dynamics.is_valid() and fdb_Related_Dynamics.is_valid() and fdb_Related_Dynamics_Dynamics.is_valid() and fdb_Model.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/TF/')
    # if a GET (or any other method) we'll create a blank form
    else:
        fdb_ProteinForm = dyndb_ProteinForm()
        fdb_Other_Protein_NamesForm=dyndb_Other_Protein_NamesForm() 
        fdb_Protein_SequenceForm=dyndb_Protein_SequenceForm()
        fdb_Other_Protein_NamesForm= dyndb_Other_Protein_NamesForm()
        fdb_Cannonical_ProteinsForm=dyndb_Cannonical_ProteinsForm() 
        fdb_Protein_MutationsForm=dyndb_Protein_MutationsForm()
        fdb_CompoundForm=dyndb_CompoundForm()
        fdb_Other_Compound_Names=dyndb_Other_Compound_Names()
        fdb_Molecule=dyndb_Molecule() 
        fdb_Files=dyndb_Files()
        fdb_Files_Molecule=dyndb_Files_Molecule() 
        fdb_Complex_Exp=dyndb_Complex_Exp() 
        fdb_Complex_Protein=dyndb_Complex_Protein() 
        fdb_Complex_Molecule=dyndb_Complex_Molecule() 
        fdb_Complex_Molecule_Molecule=dyndb_Complex_Molecule_Molecule() 
        fdb_Modeled_Residues=dyndb_Modeled_Residues()
        fdb_Files_Model=dyndb_Files_Model()
        fdb_Dynamics=dyndb_Dynamics()
        fdb_Dynamics_tags=dyndb_Dynamics_tags()
        fdb_Dynamics_Tags_List=dyndb_Dynamics_Tags_List()
        fdb_Files_Dynamics=dyndb_Files_Dynamics()
        fdb_Related_Dynamics=dyndb_Related_Dynamics()
        fdb_Related_Dynamics_Dynamics=dyndb_Related_Dynamics_Dynamics()
        fdb_Model = dyndb_Model() 
        return render(request,'dynadb/DYNAnameab.html', {'fdb_ProteinForm':fdb_ProteinForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Protein_SequenceForm':fdb_Protein_SequenceForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Cannonical_ProteinsForm':fdb_Cannonical_ProteinsForm, 'fdb_Protein_MutationsForm': fdb_Protein_MutationsForm, 'fdb_CompoundForm': fdb_CompoundForm, 'fdb_Other_Compound_Names':fdb_Other_Compound_Names, 'fdb_Molecule':fdb_Molecule, 'fdb_Files':fdb_Files, 'fdb_Files_Molecule':fdb_Files_Molecule, 'fdb_Complex_Exp':fdb_Complex_Exp, 'fdb_Complex_Protein':fdb_Complex_Protein, 'fdb_Complex_Molecule':fdb_Complex_Molecule, 'fdb_Complex_Molecule_Molecule':fdb_Complex_Molecule_Molecule, 'fdb_Modeled_Residues':fdb_Modeled_Residues, 'fdb_Files_Model':fdb_Files_Model, 'fdb_Dynamics':fdb_Dynamics, 'fdb_Dynamics_tags':fdb_Dynamics_tags, 'fdb_Dynamics_Tags_List':fdb_Dynamics_Tags_List, 'fdb_Files_Dynamics':fdb_Files_Dynamics, 'fdb_Related_Dynamics':fdb_Related_Dynamics, 'fdb_Related_Dynamics_Dynamics':fdb_Related_Dynamics_Dynamics, 'fdb_Model':fdb_Model})

@login_required
def profile_setting(request ):
    if request.method == 'POST':
        alert_form = AlertForm(request.POST)
        notifier_form = NotifierForm(request.POST)
        if alert_form.is_valid() and notifier_form.is_valid():
            alert = alert_form.save(commit=False)
            notifier = notifier_form.save(commit=False) 
            alert.user = request.user.username
            notifier.user = request.user.username
            notifier.save()
            alert.save()
            return HttpResponseRedirect(reverse('profile_setting'))
    extra_context = {
        'alert_form': AlertForm()}
    return TemplateView(request,'dynadb/pruebamult_template.html', extra_context)

@login_required
def sub_sim(request):
    return render(request, 'dynadb/sub_sim_form.html')

@login_required
def get_formup(request):
    FormupSet=formset_factory(Formup, extra=2)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formset = FormupSet(request.POST)
        if formset.is_valid():
            formset=formset.clean()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/thanks/')
    # if a GET (or any other method) we'll create a blank form
    else:
        formset = FormupSet()
    return render(request, 'dynadb/form.html', {'formset': formset})

@login_required
def get_name(request):
    NameFormSet=formset_factory(NameForm, extra=1)
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        formset = NameFormSet(request.POST)
        # check whether it's valid:
        if formset.is_valid():
            formset=formset.clean()
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/thanks/')
    # if a GET (or any other method) we'll create a blank form
    else:
        formset = NameFormSet()
    return render(request, 'dynadb/name.html', {'formset': formset})

def check_compound_entry_exist(pubchem_cid, chemblid, sinchikey, inchikey):
    qdcompound=DyndbCompound.objects.filter(pubchem_cid=uniprotkbac).filter(chemblid=chemblid)
    lpkqdcompound=qdcompound.values_list('pk',flat=True)
    qdmolecule=DyndbMolecule.objects.filter(pk__in=lpkqdcompound).filter(inchikey=inchikey)
    q=DyndbMolecule.objects.filter(pk__in=lpkqdcompound,)
    if len(qdcompound.values())==0:
        browse_protein_response={'Message':"There is not protein in the db matching the UniProtKB AC and the isoform number of the one is being processed",'id_protein':[]}
        return browse_protein_response 
    lpkm=[]
    lpkw=[]
    for el in qDP.values():
        if el['is_mutated']:
            lpkm.append(el['id'])
        else:
            lpkw.append(el['id'])   
    print("lista de pk mutated =",lpkm)   
    print("lista de pk wild-type =",lpkw)   
    lm_match_seq=[]
    print("MUTADA ",is_mutated)
    if is_mutated: 
        qPS=DyndbProteinSequence.objects.filter(pk__in=lpkm)
        print("query PS len",len(qPS.values()))
        if len(qPS.values())<len(lpkm):
            browse_protein_response={'Message':"ERROR: There is one or more entries of mutant proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for at least one of them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkm),'id_protein':[]}
            return browse_protein_response 
        for elm in qPS.values():
            print("PRUEBA ",elm['sequence'])
            if sequence==elm['sequence']:
                print(elm['id_protein_id']) 
                lm_match_seq.append(elm['id_protein_id'])
        if len(lm_match_seq)==0:
            browse_protein_response={'Message':"There is not any mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)==1:
            browse_protein_response={'Message':"There is a mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)>1:
            browse_protein_response={'Message':"ERROR: There are several mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed... This should be checked and fixed by removing redundant entries from the database. The DyndbProtein.pk values are "+str(lm_match_seq),'id_protein':lm_match_seq}
            return browse_protein_response 
    else:
        qPS=DyndbProteinSequence.objects.filter(pk__in=lpkw)
        print("length QUERY ",len(qPS.values()))
        if len(qPS.values())<len(lpkw):
            browse_protein_response={'Message':"ERROR: There is one or more wild type proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkw)+"\nIn addition if there are more than one pk several entries exists for the same isoform and UniProtKB AC which is redundant... fix this if it occurs",'id_protein':[]}
            return browse_protein_response 
        for elm in qPS.values():
            if sequence==elm['sequence']:
                lm_match_seq.append(elm['id_protein_id'])
        if len(lm_match_seq)==0:
            browse_protein_response={'Message':"There is not any wild type sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)==1:
            browse_protein_response={'Message':"There is a wild type sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)>1:
            browse_protein_response={'Message':"ERROR: There are several mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed... This should be checked and fixed by removing redundant entries from the database. The DyndbProtein.pk values are "+str(lm_match_seq),'id_protein':lm_match_seq}
            return browse_protein_response 

def check_protein_entry_exist(uniprotkbac,  is_mutated, sequence, isoform=None):
    if isoform=="":
       qDP=DyndbProtein.objects.filter(uniprotkbac=uniprotkbac)
    else:
       qDP=DyndbProtein.objects.filter(uniprotkbac=uniprotkbac).filter(isoform=isoform)
    if len(qDP.values())==0:
        browse_protein_response={'Message':"There is not protein in the db matching the UniProtKB AC and the isoform number of the one is being processed",'id_protein':[]}
        return browse_protein_response 
    lpkm=[]
    lpkw=[]
    for el in qDP.values():
        if el['is_mutated']:
            lpkm.append(el['id'])
        else:
            lpkw.append(el['id'])   
    print("lista de pk mutated =",lpkm)   
    print("lista de pk wild-type =",lpkw)   
    lm_match_seq=[]
    if is_mutated: 
        qPS=DyndbProteinSequence.objects.filter(pk__in=lpkm)
        print("MUTADA ",is_mutated)
        print("query PS len",len(qPS.values()))
        if len(qPS.values())<len(lpkm):
            browse_protein_response={'ERROR':True,'Message':"ERROR: There is one or more entries of mutant proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkm),'id_protein':[]}
            return browse_protein_response 
        for elm in qPS.values():
            print("PRUEBA ",elm['sequence'])
            print("PRUEBA ",sequence)
            if sequence==elm['sequence']:
                print(elm['id_protein_id']) 
                lm_match_seq.append(elm['id_protein_id'])
        if len(lm_match_seq)==0:
            browse_protein_response={'Message':"There is not any mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)==1:
            browse_protein_response={'Message':"There is a mutant sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)>1:
            browse_protein_response={'ERROR':True,'Message':"ERROR: There are several mutant sequences in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed... This should be checked and fixed by removing redundant entries from the database. The DyndbProtein.pk values are "+str(lm_match_seq)+". Please, make the GPCRmd database admininstrator know.",'id_protein':lm_match_seq}
            return browse_protein_response 
    else:
        qPS=DyndbProteinSequence.objects.filter(pk__in=lpkw)
        print("length QUERY ",len(qPS.values()))
        if len(qPS.values())<len(lpkw):
            if len(qPS.values())==0:
                browse_protein_response={'ERROR':True,'Message':"ERROR: There is one or more wild type proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkw)+".\nIn addition if there are more than one pk, several entries exist for the same isoform and UniProtKB AC. This is redundant. Please, make the GPCRmd database admininstrator know.",'id_protein':lpkw}
                return browse_protein_response 
            if len(qPS.values())>0:
                browse_protein_response={'ERROR':True,'Message':"ERROR: There are several repeated entries in the Protein table for the wild type protein matching the UniProtKB AC and the isoform number of the one is being processed. This should be checked and fixed. Please make the database administrator know. The pk of these entries in the Protein table are "+str(lpkw)+"\n",'id_protein':lpkw}
                return browse_protein_response 
        for elm in qPS.values():
            if sequence==elm['sequence']:
                lm_match_seq.append(elm['id_protein_id'])
        if len(lm_match_seq)==0:
            browse_protein_response={'Message':"There is not any wild type sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)==1:
            browse_protein_response={'Message':"There is a wild type sequence in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed",'id_protein':lm_match_seq}
            return browse_protein_response 
        if len(lm_match_seq)>1:
            browse_protein_response={'ERROR':True,'Message':"ERROR: There are several entries in the db matching the UniProtKB AC, the isoform number and the sequence of the one is being processed... This should be checked and fixed by removing redundant entries from the database. The DyndbProtein.pk values are "+str(lm_match_seq)+"Please make the database administrator know. " ,'id_protein':lm_match_seq}
            return browse_protein_response 

@textonly_500_handler
def PROTEINv_get_data_upkb (request, uniprotkbac=None):
    KEYS = set(('entry','entry name','organism','length','name','aliases','sequence','isoform','speciesid'))
    if request.method == 'POST' and 'uniprotkbac' in request.POST.keys():
      uniprotkbac = request.POST['uniprotkbac']
    if uniprotkbac is not None:
      if valid_uniprotkbac(uniprotkbac):
        if uniprotkbac.find('-') < 0:
          uniprotkbac_noiso = uniprotkbac
          isoform = None
        else:
          uniprotkbac_noiso,isoform = uniprotkbac.split('-')
        data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,accession,organism_name,length,')
        if errdata == dict():
          if data == dict():
            response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain; charset=UTF-8')
            return response
          if data['Entry'] != uniprotkbac_noiso and isoform is not None:
            response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain; charset=UTF-8')
            return response
          data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry name'].split('_')[1])
          time.sleep(10)
          namedata,errdata = retreive_protein_names_uniprot(uniprotkbac_noiso)
          if errdata == dict():
            name, other_names = get_other_names(namedata)
            data['Name'] = name
            data['Aliases'] = ';'.join(other_names)
            time.sleep(10)
            seqdata,errdata = retreive_fasta_seq_uniprot(uniprotkbac)
            if errdata == dict():
              if seqdata['sequence'] == '':
                seqdata['sequence'] = 'Sequence not available for ' + uniprotkbac+'.'
              data['Sequence'] = seqdata['sequence']
              if uniprotkbac_noiso == uniprotkbac:
                time.sleep(10)
                dataiso,errdata = retreive_isoform_data_uniprot(data['Entry'])
                if errdata == dict():
                  if dataiso == dict():
                    data['Isoform'] = '1'
                  else:
                    data['Isoform'] = dataiso['Displayed'].split('-')[1]
              else:
                data['Isoform'] = isoform
        if 'Error' in errdata.keys():
          if errdata['ErrorType'] == 'HTTPError':
            if errdata['status_code'] == 404 or errdata['status_code'] == 410:
              response = HttpResponseNotFound('No data found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain; charset=UTF-8')
            else:
              response = HttpResponse('Problem downloading from UniProtKB:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason'],status=502,content_type='text/plain; charset=UTF-8')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from UniProtKB:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain; charset=UTF-8')
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain; charset=UTF-8')
          else:
            response = HttpResponse('Cannot connect to UniProt server:\n'+errdata['reason'],status=504,content_type='text/plain; charset=UTF-8')
        else:
          datakeys = set([i.lower() for i in data.keys()])
          if datakeys == KEYS:
            response = data 
          else:
            response = HttpResponse('Invalid response from UniProtKB.',status=502,content_type='text/plain; charset=UTF-8')
      else:
        response = HttpResponse('Invalid UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    else:
      response = HttpResponse('Missing UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
    return response

def protein_get_data_upkb2( uniprotkbac):
    KEYS = set(('entry','entry name','organism','length','name','aliases','sequence','isoform','speciesid'))
    print("uniprotkbac=",uniprotkbac) 
    uniprotkbac_noiso = uniprotkbac #
    isoform = 1
    print("HOLA PIPOL  ", uniprotkbac_noiso)
    data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,accession,organism_name,length,')
    print(data)
    print(errdata)
    if errdata == dict():
        data['speciesid'], data['Organism'] = get_uniprot_species_id_and_screen_name(data['Entry Name'].split('_')[1])
        time.sleep(10)
        namedata,errdata = retreive_protein_names_uniprot(uniprotkbac_noiso)
        if errdata == dict():
            name, other_names = get_other_names(namedata)
            data['Name'] = name
            data['Aliases'] = ';'.join(other_names)
            time.sleep(10)
            seqdata,errdata = retreive_fasta_seq_uniprot(uniprotkbac)
            if errdata == dict():
                if seqdata['sequence'] == '':
                    seqdata['sequence'] = 'Sequence not available for ' + uniprotkbac+'.'
                data['Sequence'] = seqdata['sequence']
                if uniprotkbac_noiso == uniprotkbac:
                    time.sleep(10)
                    dataiso,errdata = retreive_isoform_data_uniprot(data['Entry'])
                    if errdata == dict():
                      if dataiso == dict():
                        data['Isoform'] = '1'
                      else:
                        data['Isoform'] = dataiso['Displayed'].split('-')[1]
                else:
                    data['Isoform'] = isoform
    print(data)
    print(errdata)
    return data

def PROTEINfunction(postd_single_protein, number_of_protein, submission_id):
    print("Function Parameters:"   )
    print("postd_single_protein", postd_single_protein)
    print("number_of_protein ", number_of_protein)
    print("submission_id ", submission_id)
    author="jmr"   #to be modified with author information. To initPF dict
    now=timezone.now()
#  inintPF dictionary containing fields of the form dynadb_ProteinForm not
#  available in the request.POST
#  initOPN dictionary dyndb_Other_Protein_NamesForm. To be updated in the
#  view. Not depending on is_mutated field in dynadb_ProteinForm 
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
    initOPN={'id_protein':'1','other_names':'Lulu' } #other_names should be updated from UniProtKB Script Isma
    print("HASTA AQUI 1")
    form=re.compile('form-')
    dictpost=postd_single_protein
    dictprot={}
    dictOPN={}
    indexl=[]
    nummutl={} # Dictionary of index lists designating the mutation line for every mutated protein
    for key,val in dictpost.items():
        if form.search(key):   #if the form- prefix is found several proteins are submitted in the HTML
            index=int(key.split("-")[1]) #index stand for the number of protein
            if index not in indexl:
                indexl.append(index)
                dictprot[index]={} #a dictprot dictionary is created per each protein in the form
            nkey="-".join(key.split("-")[2:])   # HTML labels (keys in dictpost) modified by JavaScript are reset to match the key in the models 
        else: 
            if len(indexl)==0:
                index=0
                indexl.append(0)
                dictprot[0]={}
            nkey=key # the keys does not have to be modifyied as a single protein has been submitted in the html form and labels match the models 
        dictprot[index][nkey]=val 
    print(dictprot)
#   List of dictionaries used for filling tables
    fdbPF={}
    fdbSP={}
    fdbPS={}
    fdbPM={}
    fdbCaP={}
    fdbPCaP={}
    dictSP={}
    dictPM={}
    listON={}
    fdbOPN={}
    formPF={}
    formSP={}
    formPS={}
    formOPN={}
    formCaP={} 
    initPS={}
    initPM={}
    dictCP={}
    fdbCP={} #dyndb_Complex_Protein
    auxdictprot={}
    fdbPFaux={}
    formPFaux={}   
    dictSPaux={}  
    fdbSPaux={}
    fdbPSaux={}
    fdbCaPaux={}
    fdbPCaPaux={}
    initPSaux={}
    qCanProt={}
    qCaP={}
    print("HASTA AQUI 2")
    indexl.sort()
    for ii in indexl:
        if 'is_mutated' in dictprot[ii].keys():
            is_mutated_val=True
        else:
            is_mutated_val=False
        #### Check if the Protein in the HTML is already in the database 
        browse_protein_response=check_protein_entry_exist(dictprot[ii]['uniprotkbac'],is_mutated_val,dictprot[ii]['sequence'],dictprot[ii]['isoform'])#### POR AQUI!!!!!!!!!!!!!! 
        print("Valor funcion ", browse_protein_response)
        if len(browse_protein_response['id_protein'])==1:
            print(browse_protein_response['Message'])
            dictSP[ii]={'submission_id':int(submission_id), 'protein_id':int(browse_protein_response['id_protein'][0]), 'int_id':ii} #int_id is 0 for the protein #1, 1 for the protein #2, ...
            print(dictSP[ii])
            fdbSP[ii]=dyndb_Submission_Protein(dictSP[ii])
            if fdbSP[ii].is_valid():
                fdbSP[ii].save()
            else:
                iii1=fdbSP[ii].errors.as_data()
                print("fdbSP[",ii,"] no es valido")
                print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n")
            if ii==indexl[-1]:#if ii is the last element of the list indexl
                print(browse_protein_response['Message'])
                break
            else:
                print(browse_protein_response['Message'])
                continue
        else:
            if len(browse_protein_response['id_protein'])>1:
                print(browse_protein_response['Message'])
                response = HttpResponse(browse_protein_response['Message'],content_type='text/plain; charset=UTF-8')
                return response
# If the protein ii is not found in our database create a new entry....  
# A protein is a receptor when its uniprotkbac is found in the table Protein of Gloriam!!!!
        print("valor ii=", ii, "dictprot[ii]=\n", dictprot[ii])
        initPF['id_uniprot_species']=1
        p=Protein.objects.filter(accession=dictprot[ii]['uniprotkbac'])
        if len(p.values())==1:
            initPF['receptor_id_protein']=p.values_list('id')[0][0]
            print(initPF)
        elif len(p.values())==0:
            initPF['receptor_id_protein']=None
        fdbPF[ii]=dyndb_ProteinForm(dictprot[ii])
#  Fill the empty fields in the fdbPF instance with data from the initPF dictionary
        for key,value in initPF.items():
            fdbPF[ii].data[key]=value
# Check whether the fdbPF instance of dyndb_ProteinForm is valid and save formPF entry in the database:
        if fdbPF[ii].is_valid(): 
            formPF[ii]=fdbPF[ii].save()
            print("\n primary  key: ", formPF[ii].pk )
        else:
            iii1=fdbPF[ii].errors.as_data()
            print("fdbPF",ii," no es valido")
            print("!!!!!!Errores despues del fdbPF[",ii,"]\n",iii1,"\n")
# Fill the submission protein table  (Submission PROTEIN dictionary dictSP) 
        dictSP[ii]={'submission_id':int(submission_id), 'protein_id':formPF[ii].pk, 'int_id':ii} #int_id is 0 for the protein #1, 1 for the protein #2, ...
        print("dictSP[ii]=\n",dictSP[ii])
        fdbSP[ii]=dyndb_Submission_Protein(dictSP[ii])
        if fdbSP[ii].is_valid():
            fdbSP[ii].save()
        else:
            iii1=fdbSP[ii].errors.as_data()
            print("fdbSP[",ii,"] no es valido")

            print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n")
# Create a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
        if 'sequence' not in dictprot[ii].keys():
            dictprot[ii]['sequence']="TOTO"
            print("No Sequence found (NORMAL)")
        if 'is_mutated' in fdbPF[ii].data: 
            dictPM[ii]={}
            nummutl[ii]=[]
            fdbPM[ii]={}
            print("ITS MUTATED")
            ##### Let's search for form fields ending in a number which stand for fields belonging to the dyndbProteinMutations models
            ##### the fields corresponding to a mutation [nummunt] in a protein [ii] will be stored in the dictionary dictPM[ii][nummut]
            for k,v in dictprot[ii].items():
                try:
                    nummut=int(k.split("-")[-1])
                    key=("").join(k.split("-")[:-1])
                except:
                    continue
                if nummut not in nummutl[ii]:
                    nummutl[ii].append(nummut)
                    dictPM[ii][nummut]={}
                dictPM[ii][nummut][key]=v
            print ("nummutl ", nummutl)
# Let's create the field 'id_protein' in dyndb_Protein_MutationsForm so that an entry could be registered in the version not supporting Mutations scripts
            mseq=dictprot[ii]['msequence']
            seq=dictprot[ii]['sequence']
            lmseq=len(mseq)
            initPS[ii]={'id_protein':formPF[ii].pk,'sequence':mseq,'length':lmseq} 
            if mseq is None:
                response = HttpResponse('Mutated sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            if seq is None:
                response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            #####  For each nummut (i.e. number of mutation in an specific protein ii) a dyndb_Protein_MutationsForm instace should be created to save data in the database.
            for nm in nummutl[ii]:
                dictPM[ii][nm]['id_protein']=formPF[ii].pk
            #####  Como en mi version no hay datos de mutaciones se los doy con el diccionario initPM[ii] SOLO  UNA PARA PROBAR
                if len(dictPM[ii][nm]) == 1:    # solo hay la id_protein en dictPM[ii][nm]
                    print ("len(dictPM[ii][nm]) ", len(dictPM[ii][nm])) 
                else:
                    fdbPM[ii][nm] = dyndb_Protein_MutationsForm(dictPM[ii][nm])
                    print("mutation #",ii," ",dictPM[ii][nm])
                if fdbPM[ii][nm].is_valid():
                    print("PM is valid")
                    fdbPM[ii][nm].save()
                else:
                    iii1=fdbPM[ii][nm].errors.as_data()
                    print("fdbPM[",ii,"][",nm,"] no es valido")
                    print("!!!!!!Errores despues del fdbPM[",ii,"][",nm,"]\n",iii1,"\n")
        else: #PROTEIN is not mutated!!!!!!!!!
            seq=dictprot[ii]['sequence']
            lseq=len(seq)
            initPS[ii]={'id_protein':formPF[ii].pk,'sequence':seq,'length':lseq} 
            if seq is None:
                response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
# ###   Intance of the forms depending on the is_mutated value in dyndb_ProteinForm
        fdbPS[ii] = dyndb_Protein_SequenceForm(initPS[ii])
        print("\n\nSEQUENCE INSTANCE\n\n")
        if fdbPS[ii].is_valid():
            fdbPS[ii].save()
            print ("hasta aqui")
        else:
            iii1=fdbPS[ii].errors.as_data()
            print("fdbPS[",ii,"] no es valido")
            print("!!!!!!Errores despues del fdbPS[",ii,"] \n",iii1,"\n")
        #### Check if canonical Protein has been already submitted to the database. 
        #### First we browse the non mutated proteins matching UniProtKbac. We have to decide if we want CANONICAL or WILDTYPE (WILDTYPE involves one entry per isoform in DyndbCannonicalProtein and add a constrain in the query:filter(isoform=isoform).
        qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=dictprot[ii]['uniprotkbac']).exclude(is_mutated=True).exclude(id=formPF[ii].pk) # BUSCA CANONICAL PROTEIN !!!        
        lqid=[] #list of id in the query (not mutated proteins with the same UniProtKB AC than the new one without including it)
        for el in qCanProt[ii].values():
            lqid.append(el['id'])
        qCaP[ii]=DyndbCannonicalProteins.objects.filter(pk__in=lqid)
        if len(qCaP[ii].values())==0: #no Cannonical Protein exists for this UniProtKBAC in our database
            auxdictprot[ii]={}
            dunikb=protein_get_data_upkb2(uniprotkbac=dictprot[ii]['uniprotkbac']) #Request the data of the canonical protein in the UniProtKB DB
            print("PPPPPPP dunikb",dunikb)
            translate={'Entry':'uniprotkbac','Isoform':'isoform','Name':'name','Aliases':'other_names','Sequence':'sequence','Organism':'id_species_autocomplete','speciesid':'id_species'} #dictionary for the translation between the data in uniprot and the data in our tables
            for key,val in translate.items():
                auxdictprot[ii][val]=dunikb[key]
# #         We have to check if the current Protein entry matches the cannonical sequence. If not a new entry for the canonical sequence must be tracked. 
            if auxdictprot[ii]['sequence']!=initPS[ii]['sequence']:
                  # auxdictprot[ii]['sequence'] stands for the canonical sequence from UniProtKB DB
                  # initPS[ii]['sequence'] stands for the sequence of the protein to be tracked (either wild type or mutant depending on the field is_mutated)
               #Let's create entries in DyndbProtein, DyndbProteinSequence, DyndbSubmissionProtein, 
                auxdictprot[ii]['is_mutated']=False
                initPF['id_uniprot_species']=auxdictprot[ii]['id_species']
                for key,value in initPF.items():
                    auxdictprot[ii][key]=value
                fdbPFaux[ii]=dyndb_ProteinForm(auxdictprot[ii])
                DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=auxdictprot[ii]['id_species'])
                if fdbPFaux[ii].is_valid(): 
                    formPFaux[ii]=fdbPFaux[ii].save()
                    print("\n primary  key aux: ", formPFaux[ii].pk )
                else:
                    iii1=fdbPFaux[ii].errors.as_data()
                    print("fdbPFaux",ii," no es valido")
                    print("!!!!!!Errores despues del fdbPFaux[",ii,"]\n",iii1,"\n")
                dictSPaux[ii]={'int_id':None, 'submission_id':int(submission_id), 'protein_id':formPFaux[ii].pk}
                              #int_id is Null because the entry has been generated automatically to find a cannonical sequence corresponding 
                              #to the user uploaded mutant protein,                                                             
                fdbSPaux[ii]=dyndb_Submission_Protein(dictSPaux[ii])
                if fdbSPaux[ii].is_valid():
                    fdbSPaux[ii].save()
                else:
                    iii1=fdbSPaux[ii].errors.as_data()
                    print("fdbSPaux[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbSPaux[",ii,"]\n",iii1,"\n")
# Createe a  a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
                if len(auxdictprot[ii]['other_names'])> 0:
                    listON[ii]=auxdictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
                    listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
                    dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
                    fdbOPN[ii]={}
                    numON=0
                    for on in listON[ii]:
                        numON=numON+1
                        dictOPN[ii][numON]={}
                        fdbOPN[ii][numON]={}
                        dictOPN[ii][numON]['other_names']=on
                        dictOPN[ii][numON]['id_protein']=formPFaux[ii].pk
                        fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
                        if fdbOPN[ii][numON].is_valid():
                            fdbOPN[ii][numON].save()
                        else:
                            iii1=fdbOPN[ii][numON].errors.as_data()
                            print("fdbOPN[",ii,"] no es valido")
                            print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
                else:
                    print("NO OTHER NAMES have been found\n")
                seq=auxdictprot[ii]['sequence']
                lseq=len(seq)
                initPSaux[ii]={'id_protein':formPFaux[ii].pk,'sequence':auxdictprot[ii]['sequence'],'length':lseq}
                fdbPSaux[ii] = dyndb_Protein_SequenceForm(initPSaux[ii])
                if fdbPSaux[ii].is_valid():
                    fdbPSaux[ii].save()
                    print ("hasta aqui")
                else:
                    iii1=fdbPSaux[ii].errors.as_data()
                    print("fdbPSaux[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbPSaux[",ii,"] \n",iii1,"\n")
                #Filling the dyndb_Cannonical_Protein entry for the cannonical protein corresponding to the mutant in the form!!!! 
                fdbCaPaux[ii]=dyndb_Cannonical_ProteinsForm({'id_protein':formPFaux[ii].pk})
                if fdbCaPaux[ii].is_valid():
                    fdbCaPaux[ii].save()
                else:
                    iii1=fdbCaPaux[ii].errors.as_data()
                    print("fdbCaPaux[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbCaPaux[",ii,"]\n",iii1,"\n") 
                ### NOTe this fdbPCaPaux corresponds to the Cannonical protein created automatically in the view!!!
                fdbPCaPaux[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':formPFaux[ii].pk,'id_protein':formPFaux[ii].pk})
                    #id_protein is the fk pointing to dyndb_Protein. formPFaux[ii].pk is the dyndb_Protein.pk in the Created cannonical entry!!!   
                    #id_cannonical_protein is the fk to dyndb_Cannonical_Protein. formPFaux[ii].pk is also the dyndb_Cannonical_Protein.pk    
                if fdbPCaPaux[ii].is_valid(): 
                    fdbPCaPaux[ii].save()
                else:
                    iii1=fdbPCaPaux[ii].errors.as_data()
                    print("fdbPCaPaux[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbPCaPaux[",ii,"]\n",iii1,"\n") 
                vformPFPCaP=formPFaux[ii].pk## For completing the dyndbProteinCanonicalProtein table!!!! If the Canonical sequence has been retrieved from Uniprot and not from the HTML form definition 
            else: ###### If the protein in the form is the canonical protein as its sequence matches the one from the UniProtKB DB
            #Filling the dyndb_Cannonical_Protein in the case of having a cannonical protein in the form!!!! 
                DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=auxdictprot[ii]['id_species'])
                vformPFPCaP=formPF[ii].pk##  For completing the dyndbProteinCanonicalProtein table!!!! If sequence in the form is the Canonical Sequence!!!! Otherwise the value is taken from the UniProtKB entry
                fdbCaP[ii]=dyndb_Cannonical_ProteinsForm({'id_protein':formPF[ii].pk})
                if fdbCaP[ii].is_valid():
                    fdbCaP[ii].save()
                else:
                    iii1=fdbCaP[ii].errors.as_data()
                    print("fdbCaPaux[",ii,"] no es valido")
                    print("!!!!!!Errores despues del fdbCaPaux[",ii,"]\n",iii1,"\n") 
#           #if the protein in the form is the canonical protein as its sequence matches the one from the UniProtKB DB It is needed to keep track of the
            # other names in the form. REMEMBER OTHER NAMES are only filled for the Canonical Protein!!!!
# Create a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
                if len(dictprot[ii]['other_names'])> 0:
                    listON[ii]=dictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
                    listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
                    dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
                    fdbOPN[ii]={}
                    numON=0
                    for on in listON[ii]:
                        numON=numON+1
                        dictOPN[ii][numON]={}
                        fdbOPN[ii][numON]={}
                        dictOPN[ii][numON]['other_names']=on
                        dictOPN[ii][numON]['id_protein']=formPF[ii].pk
                        fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
                        if fdbOPN[ii][numON].is_valid():
                            fdbOPN[ii][numON].save()
                        else:
                            iii1=fdbOPN[ii][numON].errors.as_data()
                            print("fdbOPN[",ii,"] no es valido")
                            print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
                else:
                    print("NO OTHER NAMES have been found\n")
      ### NOTe this fdbPCaP corresponds to the protein created from the POST info!!!
            fdbPCaP[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':vformPFPCaP,'id_protein':formPF[ii].pk})
                #id_protein is the fk pointing to dyndb_Protein. formPF[ii].pk is the dyndb_Protein.pk in the mutant protein Entry!!!!   
                #id_cannonical_protein is the fk to dyndb_Cannonical_Protein. formPFaux[ii].pk is the dyndb_Cannonical_Protein.pk!!!!    
            if fdbPCaP[ii].is_valid(): 
                fdbPCaP[ii].save()
            else:
                iii1=fdbPCaP[ii].errors.as_data()
                print("fdbPCaP[",ii,"] no es valido")
                print("!!!!!!Errores despues del fdbPCaP[",ii,"]\n",iii1,"\n") 
        else: # One or More Canonical Protein entries have been retrieved from the query qCanProt. (Just one entry should be retrived!!!!)
            DyndbProtein.objects.filter(id=formPF[ii].pk).update(id_uniprot_species=auxdictprot[ii]['id_species'])
            if len(qCaP[ii].values()) > 1:
                print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                print("OJO!!!!!!!!!!Several Canonical Protein entries exist in the DB")
                print("Several Canonical Protein entries with UNIPROTKBAC=",qCanProt[ii].filter(pk__in=qCaP[ii].values()),"exist in the DB")
       # the dyndb_Cannonical_Protein already exists so it is not created again!!!!! let's create dyndb_Protein_Cannonical_Protein entry
       # from info contained in the query qCanProt (qCanProt.values()[0]['id']) this is the id of the first and only element in the query
            if len(qCaP[ii].values()) == 1:
                fdbPCaP[ii]=dyndb_Protein_Cannonical_Protein({'id_cannonical_proteins':qCaP[ii].values()[0]['id_protein_id'],'id_protein':formPF[ii].pk})
            if fdbPCaP[ii].is_valid():
                fdbPCaP[ii].save()
            else:
                iii1=fdbPCaP[ii].errors.as_data()
                print("fdbPCaP[",ii,"] no es valido")
                print("!!!!!!Errores despues del fdbCaP[",ii,"]\n",iii1,"\n") 
        # redirect to a new URL:
    return  

def get_file_url_root():
    ''' Function that defines root URL for served files.
    Edit to change file URLs.'''
    url_prefix = "/dynadb/"
    return join_path(url_prefix,settings.MEDIA_URL,relative=False,url=True)

def get_file_paths(objecttype,url=False,submission_id=None,return_main_submission_dict=False,):
    ''' Function that defines file paths and URLs for served files.
    Edit to change file path and URLs.'''
    filepathdict = dict()
    #define objects
    filepathdict['molecule'] = dict()
    filepathdict['model'] = dict()
    filepathdict['dynamics'] = dict()
    filepathdict['summary'] = dict()
    #define main folders
    filepathdict['molecule']['main'] = "Molecule"
    filepathdict['model']['main'] = "Model"
    filepathdict['dynamics']['main'] = "Dynamics"
    filepathdict['summary']['main'] = "Summary"
    #define submission folders
    filepathdict['molecule']['submission'] = "mol"
    filepathdict['model']['submission'] = "model"
    filepathdict['dynamics']['submission'] = "dyn"
    filepathdict['summary']['submission'] = "sum"
    if return_main_submission_dict:
        main_submission_dict= dict()
        for key in filepathdict:
            main_submission_dict[filepathdict[key]['main']] = {'object_type':key,'submission':filepathdict[key]['submission']}
        return main_submission_dict
    if url:
        root = get_file_url_root()
    else:
        root = settings.MEDIA_ROOT
        # root = "/"
    path = join_path(root,filepathdict[objecttype]['main'],relative=False,url=url)
    if submission_id is not None:
        submission_folder = filepathdict[objecttype]['submission']+str(submission_id)
        path = join_path(path,submission_folder,relative=False,url=url)
    if url:
        path += '/'
    else:
        path += os.path.sep
    return path
    
def file_url_to_file_path(url):
    url_root = normpath(get_file_url_root())
    file_root = normpath(settings.MEDIA_ROOT[:-1])
    nurl = normpath(url)
    if nurl.find(url_root) == 0:
        relative_url = nurl[len(url_root)+1:]
        return os.path.join(file_root,relative_url)
    else:
        raise ValueError("Invalid URL '"+nurl+"' .Path must be contained in '"+url_root+"' URL.")

def get_file_name_dict():
    filenamedict = dict()
    #define objects
    filenamedict['molecule'] = dict()
    filenamedict['model'] = dict()
    filenamedict['dynamics'] = dict()
    filenamedict['summary'] = dict()
    #define part(icles)
    filenamedict['molecule']['part'] = "mol"
    filenamedict['model']['part'] = "model"
    filenamedict['dynamics']['part'] = None
    filenamedict['summary']['part'] = "sum"
    #define subtypes
    filenamedict['molecule']['subtypes'] = dict()
    filenamedict['molecule']['subtypes']["image"] = dict()
    filenamedict['molecule']['subtypes']["molecule"] = dict()
    filenamedict['molecule']['subtypes']["log"] = dict()
    filenamedict['model']['subtypes'] = dict()
    filenamedict['model']['subtypes']["pdb"] = dict()
    filenamedict['model']['subtypes']["log"] = dict()
    filenamedict['dynamics']['subtypes'] = dict()
    filenamedict['dynamics']['subtypes']["pdb"] = dict()
    filenamedict['dynamics']['subtypes']["topology"] = dict()
    filenamedict['dynamics']['subtypes']["trajectory"] = dict()
    filenamedict['dynamics']['subtypes']["parameters"] = dict()
    filenamedict['dynamics']['subtypes']["protocol"] = dict()
    filenamedict['dynamics']['subtypes']["other"] = dict()
    filenamedict['dynamics']['subtypes']["log"] = dict()
    filenamedict['summary']['subtypes'] = dict()
    filenamedict['summary']['subtypes']['summary']=dict()
    #define file ext(ensions)
    filenamedict['molecule']['subtypes']["image"]["ext"] = ["png"]
    filenamedict['molecule']['subtypes']["molecule"]["ext"] = ["sdf","mol"]
    filenamedict['molecule']['subtypes']["log"]["ext"] = ["log"]
    filenamedict['model']['subtypes']["pdb"]["ext"] = ["pdb"]
    filenamedict['model']['subtypes']["log"]["ext"] = ["log"]
    filenamedict['dynamics']['subtypes']["pdb"]["ext"] = ["pdb"]
    filenamedict['dynamics']['subtypes']["topology"]["ext"] = ["psf","prmtop","top"]
    filenamedict['dynamics']['subtypes']["trajectory"]["ext"] = ["xtc","dcd"]
    filenamedict['dynamics']['subtypes']["parameters"]["ext"] = ["prm","tar.gz"]
    filenamedict['dynamics']['subtypes']["protocol"]["ext"] = ["zip","tar.gz"]
    filenamedict['dynamics']['subtypes']["other"]["ext"] = ["tar.gz"]
    filenamedict['dynamics']['subtypes']["log"]["ext"] = ["log"]
    filenamedict['summary']['subtypes']['summary']['ext']=['txt']
    #define subtype part(icles)
    filenamedict['dynamics']['subtypes']["pdb"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["topology"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["trajectory"]["part"] = "trj"
    filenamedict['dynamics']['subtypes']["parameters"]["part"] = "prm"
    filenamedict['dynamics']['subtypes']["other"]["part"] = "oth"
    filenamedict['dynamics']['subtypes']["protocol"]["part"] = "prt"
    filenamedict['dynamics']['subtypes']["log"]["part"] = "dyn"
    return filenamedict
filenamedict = get_file_name_dict()

def get_file_name_particles(objecttype,ext=None,forceext=False,subtype=None,imgsize=300):
    subtypes = filenamedict[objecttype]['subtypes'].keys()
    if subtype is None:
        subtypeslen = len(subtypes)
        if subtypeslen  > 1 :
            raise ValueError("a subtype must be specified for objecttype '"+objecttype+"'.")   
        elif subtypeslen == 1:
            subtype = subtypes.pop()
        else:
            raise ValueError("No subtypes found for objecttype '"+objecttype+\
        "'. Please, check get_file_name_dict() definition.")
    exts = filenamedict[objecttype]['subtypes'][subtype]["ext"]
    if filenamedict[objecttype]['part'] is None:
        part = filenamedict[objecttype]['subtypes'][subtype]['part']
    else:
        part = filenamedict[objecttype]['part']
    if ext is None:
        extslen = len(exts)
        if extslen  > 1:
            raise ValueError("a file extension must be specified for objecttype '"+objecttype+":"+subtype+"' using 'ext' keyword.")
        elif extslen == 1:
            extf = exts[0]
    else:
        extf = ext.lower()
    if not forceext and extf not in exts :
        raise ValueError(extf+" is not a valid file extension for objecttype '"+objecttype+":"+subtype+"'.\
        To force the use of this extension use the 'forceext' keyword.")
    if subtype == "image":
        sizepart='_'+str(imgsize)
    else:
        sizepart = ''
    return(part,sizepart,extf)

def get_file_name_submission(objecttype,submission_id,formid,ref=False,ext=None,forceext=False,subtype=None,imgsize=300):
    part,sizepart,extf = get_file_name_particles(objecttype,ext=ext,forceext=forceext,subtype=subtype,imgsize=imgsize)
    if ref:
        refpart='ref_'
    else:
        refpart=''
    filename = 'tmp_'+part+'_'+str(formid)+'_'+refpart+str(submission_id)+sizepart+'.'+extf
    return filename
    
def get_file_name(objecttype,fileid,objectid,ext=None,forceext=False,subtype=None,imgsize=300):
    part,sizepart,extf = get_file_name_particles(objecttype,ext=ext,forceext=forceext,subtype=subtype,imgsize=imgsize)
    filename = str(fileid)+'_'+part+'_'+str(objectid)+sizepart+'.'+extf
    return filename
        
def join_path(*args,relative=False,url=False):
    path = ''
    first_slashre = re.compile(r'^[/\\]+')
    if relative:
        first_slash = ''
    else:
        if url:
            first_slash = '/'
        else:
            first_slash = os.path.sep 
    for arg in args:
        arg_no_slash = first_slashre.sub('',arg)
        path = os.path.join(path,arg_no_slash)
    if url:
        path = path.replace(os.path.sep,'/')
    path = first_slash+path
    return path
    
def SMALL_MOLECULEfunction(postd_single_molecule, number_of_molecule, submission_id):
    print("Submission_id:  ",submission_id)
    user="jmr"
    def molec_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        print("inside the function molec_file_table")
        print(dname)
        fdbF={}
        fdbFobj={}
        for key,val  in dname.items():
            print("val\n", val)
            fext="".join(val['path'].split(".")[1:])
            initFiles['id_file_types']=dict_ext_id[fext]
            initFiles['url']=val['url']
            initFiles['filename']="".join(val['path'].split("/")[-1])
            initFiles['filepath']=val['path']
            if key == "dnamesdf":
                initFiles['description']="sdf/mol2 requested in the molecule form"
            else:
                initFiles['description']="png image file of the molecule"
            print("HOLA initFiles", initFiles)
            fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
            dicfmole={}
            fdbFM={}
            if fdbF[key].is_valid():
                fdbFobj[key]=fdbF[key].save()
                if initFiles['id_file_types']==19:
                    dicfmole['type']=d_fmolec_t['Image 300px'] #Molecule
                elif initFiles['id_file_types']==20:
                    dicfmole['type']=d_fmolec_t['Molecule'] #Molecule
                dicfmole['id_molecule']=MFpk
                dicfmole['id_files']=fdbFobj[key].pk
                fdbFM[key]=dyndb_Files_Molecule(dicfmole)
                if fdbFM[key].is_valid():
                    fdbFM[key].save()
                else:
                    print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[key].errors.as_text())
            else:
                print("Errores en el form dyndb_Files\n ", fdbF[key].errors.as_text())
    author="jmr"   #to be modified with author information. To initPF dict
    now=timezone.now()
    onames="Pepito; Juanito; Herculito" #to be modified... scripted
    initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
    initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
    initON={'other_names': onames,'id_compound':None} 
    dicpost=postd_single_molecule
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
    ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
    ft=DyndbFileTypes.objects.all()
    dict_ext_id={}
    for l in ft:
        dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
        print (l.__dict__['extension'].rstrip())
    d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
    dictmol={}
    fieldsmol=["id_compound","description","net_charge","inchi","inchikey","inchicol","smiles"]
    dictON={}
    fieldsON=["other_names"]
    dictcomp={}
    fieldscomp=["name","iupac_name","pubchem_cid","chemblid","sinchi","sinchikey","std_id_molecule","id_ligand"]
    dictfmol={} 
    fieldsPMod={"is_present","type"}
    dictPMod={}
    form=re.compile('form-')
    indexl=[]
    nl=0 #counter of pairs in dicpost.items()
    for key,val in dicpost.items():
        nl=nl+1
        if form.search(key):
            index=int(key.split("-")[1])
            if index not in indexl:
                indexl.append(index)
                dictmol[index]={}
                dictON[index]={}
                dictcomp[index]={}
                dictPMod[index]={}
            nkey="-".join(key.split("-")[2:])  
        else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
            if len(indexl)==0:
                index=0
                indexl.append(0)
                dictmol[0]={}
                dictON[0]={}
                dictcomp[0]={}
                dictPMod[index]={}
            nkey=key
        dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
        dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
        for k,v in dfieldtype.items():
            if nkey in v:
                dfielddict[k][index][nkey]=val
                break
        continue 
    indexl.sort()
    print(indexl)
    indexfl=[]
    fdbMF={}
    fdbMFobj={}
    fdbCF={}
    fdbCFobj={}
    fdbON={}
    fdbONobj={}
    dON={}
    on=0
    print("ANTES SORT",indexfl, indexl)
    if len(indexl) > 1:
        indexli=list(map(int,indexl))
        indexl=sorted(indexli)
    dicfmole={}
    fdbF={}
    fdbFobj={}
    fdbFM={}
    fdbSM={}
    fdbFMobj={}
    Std_id_mol_update={}
    NewCompoundEntry={}
    print("\nPRUEBAfallo\n")
    #Molecules in the  submission if has been used before.
    qSm=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    if qSm.exists():
        prev_Mol_in_Sub_exists=True
        qSMstd=DyndbCompound.objects.filter(std_id_molecule__in=qSm.values('molecule_id')).values_list('std_id_molecule',flat=True) #list of molecules which are std molecules submitted in this sumbission
    else:
        prev_Mol_in_Sub_exists=False
    print("\nPRUEBAfallo\n")
    for ii in indexl:
        Std_id_mol_update[ii]=True
        print("len(Std_id_mol_update)= ",len(Std_id_mol_update), "ii", ii, "indexl ",indexl)
        fdbCF[ii]={}
        fdbCFobj[ii]={}
        fdbMF[ii]={}
        fdbSM[ii]={}
        fdbMFobj[ii]={}
        fdbON[ii]={}
        fdbONobj[ii]={}
        dON[ii]={}
        #### Check if the molecule is already in our Database. If so the standar molecule shoud be as well!!!!! 
        qMF=DyndbMolecule.objects.filter(inchikey=dictmol[ii]['inchikey']).filter(inchi=dictmol[ii]['inchi'].split('=')[1])
        if qMF.exists():
            print(dictmol[ii]['inchikey'])
            print("\nQuery Molecule antes aux\n ",qMF)
        else:
            print("PPPPP")
        if dictcomp[ii]['pubchem_cid']!='':
            qCFStdFormExist=DyndbCompound.objects.filter(pubchem_cid=dictcomp[ii]['pubchem_cid']) #if std form of the molecule is in the database. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be link to the DyndbCompound entry
            print("PPPPP1")
        elif dictcomp[ii]['chemblid']!='':
            qCFStdFormExist=DyndbCompound.objects.filter(chemblid=dictcomp[ii]['chemblid']) #if std form of the molecule is in the database. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
            print("PPPPP2")
        else: 
            qCFStdFormExist=DyndbCompound.objects.filter(sinchikey=dictcomp[ii]['sinchikey']).filter(sinchi=dictcomp[ii]['sinchi']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
            print("PPPPP3")
        if qMF.exists():
            print("len", len(qMF.values()))
            if len(qMF.values())==1: #there is a entry matching this molecule
                if int(dictPMod[ii]['type'])>5:
                    dictPMod[ii]['not_in_model']=True
                else:
                    dictPMod[ii]['not_in_model']=False     
                dictPMod[ii]['int_id']=ii
                dictPMod[ii]['submission_id']=submission_id
                MFpk=qMF.values_list('id',flat=True)[0]
                dictPMod[ii]['molecule_id']=MFpk
                if prev_Mol_in_Sub_exists:
                    qSMol=qSm.filter(molecule_id=MFpk,int_id=ii)
                    print("antes de comprobar si la submission esta hecha previamente")
                    if qSMol.exists():
                        print("En efecto, la submission esta hecha previamente")
                    continue 
                    if qSm.filter(int_id=ii,not_in_model=None,molecule_id=None).exists():
                        qSm.filter(int_id=ii,not_in_model=None,molecule_id=None).update(molecule_id=MFpk,not_in_model=dictPMod[ii]['not_in_model'])
                        continue
                fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
                if fdbSM[ii].is_valid(): # only the submission molecule table should be filled!!!!
                    fdbSM[ii].save()
                else:    
                    iii1=fdbSM[ii].errors.as_text()
                    print("fdbSM",ii," no es valido")
                    print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
         
                if ii==indexl[-1]:#if ii is the last element of the list indexl
                    print("Molecule #", ii, "has been found in our database")
                    break
                else:
                    print("Molecule #", ii, "has been found in our database")
                    continue
         
            elif len(qMF.values())>1:
                response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
                return response
#####   No entry in the GPCRmd DB has been found for the molecule ii... Maybe the Compound and, therefore, the std molecule entries are !!!
#####   Use of functions retrieving std_molecule info from external sources!!!! It is needed for updating
        molid=ii 
        print ("\nmolid=",molid)
        submission_path_nofile = get_file_paths("molecule",url=False,submission_id=submission_id)
        submission_url_nofile = get_file_paths("molecule",url=True,submission_id=submission_id)
        namerefsdf = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
        namerefpng = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image")
        namesdf = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")
        namepng = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="png",forceext=False,subtype="image")
        print("antes INFOstdMOL")
        path_namefsdf=("").join([submission_path_nofile, namesdf])
        path_namefpng=("").join([submission_path_nofile, namepng])
        path_namefrefsdf=("").join([submission_path_nofile, namerefsdf])
        path_namefrefpng=("").join([submission_path_nofile, namerefpng])
        url_namefrefsdf=("").join([submission_url_nofile, namerefsdf])
        url_namefrefpng=("").join([submission_url_nofile, namerefpng])
        url_namefsdf=("").join([submission_url_nofile, namesdf])
        url_namefpng=("").join([submission_url_nofile, namepng])
        INFOstdMOL=generate_molecule_properties2(submission_id,molid) #:INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
        print("AAAAa",INFOstdMOL.items())
        sinchi_fixed=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
        INFOstdMOL['sinchi']['sinchi']=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
        INFOstdMOL['inchi']['inchi']=INFOstdMOL['inchi']['inchi'].split('=')[1]
########     check if the molecule ii is actually the standard form of the molecule. If this specific form of the molecule is not in the database (DyndbMolecule) but other molecules corresponding the same compound are, the one we are dealing with won`t be the standard as it is previously recorded when the first molecule corresponding the compound was registered. So, if there is no any entry in the DyndbCompound table matching the sinchikey of the molecule in the form, still will be possible that the current entry would be the standard form.
        if len(qCFStdFormExist.values())==1: #The compound and the standard form of the current molecule is in the database (Only fill the current non standard molecule)
            print("Compound entry matching SInChIKey and SInChI has been found in GPCRmd database")
            CFpk=qCFStdFormExist.values_list('id',flat=True)[0]	
            Std_id_mol_update[ii]=False
        elif len(qCFStdFormExist.values())>1: #the compound is found more than once in the database
            response("Several Compound entries have been found in the DATABASE. Please, report this ERROR to the GPCRmd database administrator",status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
            return response
        elif len(qCFStdFormExist.values())==0: #Neither the compound nor the standard form of the molecule are in the database
            Std_id_mol_update[ii]=True
            NewCompoundEntry[ii]=True #this flag is needed in case the Compound entry need to be deleted (not if the entry existed previosly) if further steps of the submission fail
            print("No compound entry has been found in GPCRmd DB")
     #### No compound entry has been found in GPCRmd DB.Keep track of the Compound in the DyndbCompound table and the aliases in the DyndbOtherCompoundNames
            #### DyndbCompound
            for key,val in initCF.items():
                if key not in dictcomp[ii].keys():
                    dictcomp[ii][key]=val
                if key == "sinchi":
                    dictcomp[ii][key]=sinchi_fixed
            fdbCF[ii]=dyndb_CompoundForm(dictcomp[ii]) 
            if fdbCF[ii].is_valid():
                fdbCFobj[ii]=fdbCF[ii].save()
                CFpk=fdbCFobj[ii].pk
            else:
                iii1=fdbCF[ii].errors.as_text()
                print("Errores en el form dyndb_CompoundForm\n ", fdbCF[ii].errors.as_text())
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
            #### DyndbOtherCompoundNames 
            ONlist=dictON[ii]["other_names"].split(";")
            for el in ONlist:
                on=on+1
                dON[ii][on]={}
                dON[ii][on]["other_names"]=el
                dON[ii][on]["id_compound"]=CFpk
                fdbON[ii][on]=dyndb_Other_Compound_Names(dON[ii][on]) 
                if fdbON[ii][on].is_valid():
                    fdbON[ii][on].save()
                else:
                    iii1=fdbON[ii][on].errors.as_text()
                    print("Errores en el form dyndb_Other_Compound_Names\n ", fdbON[ii][on].errors.as_text())
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbCompound.objects.filter(id=CFpk).delete()
                    return response
### Get the standard Molecule by providing the SInChIKey to the PubChem or CHEMBL databases if the molecule is actually the standard form of the molecule.
####      DyndbCompound and DyndbOtherCompoundNames tables have been filled. Then entries for the std molecule should be registered in DyndbMolecule and DyndbSubmissionMolecule
            print("COMPROBAR ",INFOstdMOL)
            if 'msg' in INFOstdMOL.keys():
                print("HttpResponse(INFOstdMOL['msg'])" )
                print("HttpResponse(", INFOstdMOL['msg'], ")" )
                return HttpResponse(INFOstdMOL['msg'],status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8') 
 #### Check if inchi of the standard molecule matches the inchi in the current entry (HTML form)         
            print("COMPROBAR ",INFOstdMOL)
            print("LLLLLLLLLLLl")
            if INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'].split('=')[1]: #Both molecules are the standard molecule so one entry is saved
                print("The molecule ",ii, "is actually the standard molecule")
                dictmol[ii]['description']="Standard form"
            else:
                auxdictmol={}
                print("The molecule ",ii, "is not the standard molecule. The standard one will be saved right now!!!!")
                for key,val in INFOstdMOL.items():# HAY QUE INTRODUCIR LOS DATOS DEL SCRIPT PARA PODER CREAR UN DICCIONARIO PARA LA INSTANCIA!!!
                    print("\nAQUI ",key,val)
                    if type(val)==dict:
                        auxdictmol[key]=val[key]
                        print("\nauxdictmol inchi ", auxdictmol[key] )
                         #   "Problem while generating inchi:\n"+ msg   
                    if key == 'charge':
                        auxdictmol['net_charge']=val 
                    if key in dfieldtype['0']:
                        if key == 'inchikey':
                            auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
                            nrep_inchikey=len(DyndbMolecule.objects.filter(inchikey=val))
                            if nrep_inchikey >= 1:
                                auxdictmol['inchicol']=nrep_inchikey+1
                            else:
                                auxdictmol['inchicol']=1
                        elif key == 'sinchi':
                            auxdictmol['sinchi']=INFOstdMOL['sinchi']['sinchi']
                        elif key == 'inchi':
                            auxdictmol['inchi']=INFOstdMOL['inchi']['inchi']
                        else:
                            auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
                for key,val in initMF.items():
                    if key not in auxdictmol.keys():
                        auxdictmol[key]=val  ##### completion of the dictionary
                auxdictmol['id_compound']=CFpk
                auxdictmol['description']="Standard form"
                fdbMFaux=dyndb_Molecule(auxdictmol)
                print("\n\n resultado auxdicmol", auxdictmol  )
                if fdbMFaux.is_valid():
                    fdbMFauxobj=fdbMFaux.save()
                    MFauxpk=fdbMFauxobj.pk
                else:
                    print("Errores en el form dyndb_Molecule aux\n ", fdbMFaux.errors.as_text())
                    iii1=fdbMFaux.errors.as_text()
                    response = HttpResponse((" ").join([iii1," aux"]),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                    DyndbCompound.objects.filter(id=CFpk).delete()
                    return response
            #### Entry in DyndbSubmissionMolecule corresponding to the standard molecule 
                auxdictPMod={}
                auxdictPMod['not_in_model']=True
                auxdictPMod['int_id']=None
                auxdictPMod['submission_id']=submission_id
                auxdictPMod['molecule_id']=MFauxpk
                fdbSMaux=dyndb_Submission_Molecule(auxdictPMod)
                if fdbSMaux.is_valid(): # only the submission molecule table should be filled!!!!
                    fdbSMaux.save()
                else:    
                    iii1=fdbSMaux.errors.as_text()
                    print("fdbSMaux",ii," no es valido")
                    print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
                    response = HttpResponse((" ").join([iii1," aux"]),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=1)#needed for removing the next  DyndbMolecule entry
                    DyndbMolecule.objects.filter(id=MFauxpk).delete()
                    DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                    DyndbCompound.objects.filter(id=CFpk).delete()
                    return response
                dnameref={'dnamesdf':{'path':path_namefrefsdf,'url':url_namefrefsdf},'dnamepng':{'path':path_namefrefpng,'url':url_namefrefpng}}
                print("AUX",dnameref)
                oooref=molec_file_table(dnameref,MFauxpk)
       #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule 
                # In this block the condition INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'] is false. Then the std molecule pk is MFauxpk and the flag Std_id_mol_update is set
                # to False in order to avoid subsequents updates when the molecule in the form (not standard) would be entried.
                DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFauxpk) 
                Std_id_mol_update[ii]=False
   #       The code enclosed in this section is common for cases in which a previous compound entry existed and cases where the Compound entry has been registered in this submission!!!  
        print("\n\n")
        for key,val in initMF.items():
            if key not in dictmol[ii].keys():
                dictmol[ii][key]=val
                print(dictmol[ii][key], val)
        dictmol[ii]['id_compound']=CFpk
        aaa=dictmol[ii]['inchi'].split('=')[1]
        print(aaa)
        dictmol[ii]['inchi']=aaa
       #####AQUI ME QUEDE!!!! 
        fdbMF[ii]=dyndb_Molecule(dictmol[ii])
        if fdbMF[ii].is_valid():
            fdbMFobj[ii]=fdbMF[ii].save()
            MFpk=fdbMFobj[ii].pk
        else:
            iii1=fdbMF[ii].errors.as_text()
            print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_text())
            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            if ii in NewCompoundEntry :
                if NewCompoundEntry[ii]==True:
                    DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=1)#needed for removing the next  DyndbMolecule entry
                    DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).values_list('id_files',flat=True)).delete()
                    DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).delete()
                    DyndbSubmissionMolecule.objects.filter(molecule_id=MFauxpk).delete()
                    DyndbMolecule.objects.filter(id=MFauxpk).delete()
                    DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                    DyndbCompound.objects.filter(id=CFpk).delete()
                return response
        dname={'dnamesdf':{'path':path_namefsdf,'url':url_namefsdf},'dnamepng':{'path':path_namefpng,'url':url_namefpng}}
        print(dname)
        ooo= molec_file_table(dname,MFpk)
       #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule
       # if the Std_id_mol_update flag is set to True the molecule in the form is the standard one and the std_id_molecule field in DyndbCompound should be update with MFpk
        if ii in Std_id_mol_update: 
            if Std_id_mol_update[ii]:
                DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFpk) 
                Std_id_mol_update[ii]=False
        if int(dictPMod[ii]['type'])>5:
            dictPMod[ii]['not_in_model']=True
        else:
            dictPMod[ii]['not_in_model']=False     
        dictPMod[ii]['int_id']=ii
        dictPMod[ii]['submission_id']=submission_id
        dictPMod[ii]['molecule_id']=MFpk
        fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
        if fdbSM[ii].is_valid():
            fdbSM[ii].save()
            response= HttpResponse("SUCCESS",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        else:    
            iii1=fdbSM[ii].errors.as_text()
            print("fdbSM",ii," no es valido")
            print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFpk).values_list('id_files',flat=True)).delete()
            DyndbFilesMolecule.objects.filter(id_molecule=MFpk).delete()
            DyndbMolecule.objects.filter(id=MFpk).delete()
            if NewCompoundEntry[ii]==True:
                DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=1)#needed for removing the next  DyndbMolecule entry
                DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).values_list('id_files',flat=True)).delete()
                DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).delete()
                DyndbSubmissionMolecule.objects.filter(molecule_id=MFauxpk).delete()
                DyndbMolecule.objects.filter(id=MFauxpk).delete()
                DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                DyndbCompound.objects.filter(id=CFpk).delete()
            return response
    moleculelist=str(indexl)

    response = HttpResponse("Step 2 \"Small Molecule Information\" form has been successfully submitted.",content_type='text/plain; charset=UTF-8')
    return response

def generate_molecule_properties2(submission_id,molid):
    pngsize = 300
    RecMet = False
    formre = re.compile('^form-(\d+)-')
    data={}
    data['sinchi']={}
    data['inchi']={}
    submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
    submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
    sdfnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
    file=Path(("").join([submission_path,sdfnameref]))
    if file.is_file():
        uploadfile=open(os.path.join(submission_path,sdfnameref),'rb')
    else:
        uploadfile=open(os.path.join(submission_path,get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")),'rb')
    mol = open_molecule_file(uploadfile)
    print(sdfnameref)
    print("TTT") 
    try:
        sinchi,code,msg = generate_inchi(mol,FixedH=False,RecMet=False)
        print("\nSINCHI",code)
        print("TTT") 
        if code > 1:
             data['msg'] ='Error while computing Standard InChI:\n'+msg
             return(data)
        data['sinchi']['sinchi'] = sinchi
        data['sinchi']['code'] = code
        data['inchi'] = dict()
        inchi,code,msg = generate_inchi(mol,FixedH=True,RecMet=RecMet)
        print("\nINCHI",code)
        if code > 1:
             data['msg'] ='Error while computing InChI:\n'+msg
             return(data)
        data['inchi']['inchi'] = inchi
        data['inchi']['code'] = code
        print(" data['inchi']['code'] = code")
    except:
        data['msg'] ='Error while computing InChI.'
    print("AAAAAAAAAAAAAAAAAA\n")
    data['smiles'] = generate_smiles(mol,logfile=sys.__stderr__)
    print(data['smiles'], "= generate_smiles(mol,logfile=sys.__stdout__)")
    print("AAAAAAAAAAAAAAAAAA\n")
    data['charge'] = get_net_charge(mol)
    print("data['charge'] = get_net_charge(mol)")
    try:    
        data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])
        print("   data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])")
        data['inchikey'] = generate_inchikey(data['inchi']['inchi'])
        print("data['inchikey'] = generate_inchikey(data['inchi']['inchi'])")
        data['inchicol'] = 1
        data['inchicol'] = 1
    except:
        data['msg'] ='Error while computing InChIKey.'
    uploadfile.close()
    return data

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed
def SMALL_MOLECULEview(request, submission_id):
    user="jmr"   #to be modified with author information. To initPF dict
    print("Submission_id:  ",submission_id)
    def molec_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        print("inside the function molec_file_table")
        print(dname)
        fdbF={}
        fdbFobj={}
        for key,val  in dname.items():
            print("val\n", val)
            fext="".join(val['path'].split(".")[1:])
            initFiles['id_file_types']=dict_ext_id[fext]
            initFiles['url']=val['url']
            initFiles['filename']="".join(val['path'].split("/")[-1])
            initFiles['filepath']=val['path']
            if key == "dnamesdf":
                initFiles['description']="sdf/mol2 requested in the molecule form"
            else:
                initFiles['description']="png image file of the molecule"
            print("HOLA initFiles", initFiles)
            fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
            dicfmole={}
            fdbFM={}
            if fdbF[key].is_valid():
                fdbFobj[key]=fdbF[key].save()
                if initFiles['id_file_types']==19:
                    dicfmole['type']=d_fmolec_t['Image 300px'] #Molecule
                elif initFiles['id_file_types']==20:
                    dicfmole['type']=d_fmolec_t['Molecule'] #Molecule
                dicfmole['id_molecule']=MFpk
                dicfmole['id_files']=fdbFobj[key].pk
                fdbFM[key]=dyndb_Files_Molecule(dicfmole)
                if fdbFM[key].is_valid():
                    fdbFM[key].save()
                else:
                    prev_entryFileM=DyndbFilesMolecule.objects.filter(id_molecule__dyndbsubmissionmolecule__submission_id=submission_id,id_molecule__dyndbsubmissionmolecule__int_id=ii)
                    prev_entryFileM.update(id_model=dicfmole['id_molecule'],id_files=dicfmole['id_files'])
                    print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[key].errors.as_text())
            else:
                prev_entryFile=DyndbFiles.objects.filter(dyndbfilesmolecule__id_molecule__dyndbsubmissionmolecule__submission_id=submission_id,dyndbfilesmolecule__id_molecule__dyndbsubmissionmolecule__int_id=ii)
                prev_entryFile.update(update_timestamp=timezone.now(),last_update_by_dbengine=user,filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])
                print("\n ENTRADA File EXISTENTE ACTUALIZADA")
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    print("HOLA  ", def_user)
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    author="jmr"   #to be modified with author information. To initPF dict
    now=timezone.now()
    onames="Pepito; Juanito; Herculito" #to be modified... scripted
    initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
    initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
    initON={'other_names': onames,'id_compound':None} 
    dicpost=request.POST    #postd_single_molecule
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() , 'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user, 'submission_id':submission_id }
    ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
    ft=DyndbFileTypes.objects.all()
    dict_ext_id={}
    for l in ft:
        dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
        print (l.__dict__['extension'].rstrip())
    d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
    if request.method == 'POST':
        print (request.POST.items())
        # if reuse model the submission molecule table is filled with the components of the model in the present submission
        if "model_id" in request.POST.keys():
            print("MODEL_ID = ",request.POST['model_id'])
            Update_molec=False
            model_id=request.POST['model_id']
            qSmolec_model_this_sub=DyndbSubmissionMolecule.objects.filter(not_in_model=False,submission_id=submission_id).exclude(int_id=None).exclude(molecule_id=None).exclude(not_in_model=None)
            qSprot_model_this_sub =DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(protein_id=None).exclude(int_id=None)
            print("qSprot_model_this_sub", qSprot_model_this_sub.values(), "zero values ok")
            qSprot_empty_rows=DyndbSubmissionProtein.objects.filter(protein_id=None,int_id=None)
            lProtreused_empty_rows=[]
            qMODEL_first =DyndbSubmissionModel.objects.filter(model_id=model_id,submission_id=F('model_id__model_creation_submission_id')).exclude(model_id=None)
            qsubmission_id=qMODEL_first.values_list('submission_id',flat=True)[0]
            qSmolec_model_first_sub =qMODEL_first.filter(submission_id__dyndbsubmissionmolecule__not_in_model=False)
            print("qSmolec_model_first_sub", qSmolec_model_first_sub.values(),"should appear anything")
            print("2 MODEL_ID qSProtempty " , qSprot_empty_rows)
            if not qSprot_model_this_sub.exists():
                qSprot_model_first_sub=list(qMODEL_first.filter(submission_id=qsubmission_id,submission_id__dyndbsubmissionprotein__submission_id=qsubmission_id,submission_id__dyndbsubmissionprotein__protein_id__gt=0,submission_id__dyndbsubmissionprotein__int_id__gte=0).annotate(int_id=F('submission_id__dyndbsubmissionprotein__int_id'),protein_id=F('submission_id__dyndbsubmissionprotein__protein_id'),name=F('submission_id__dyndbsubmissionprotein__protein_id__name')).values())
                print("LLL",qSprot_model_first_sub)
                for entry in  qSprot_model_first_sub:
                    entry['submission_id']=submission_id
                    entry['submission_id_id']=submission_id
                    entry['protein_id']=int(entry['protein_id'])
                    entry['int_id']=int(entry['int_id'])
                    print(entry)
                    SProtreuse=dyndb_Submission_Protein(entry)
                    if qSprot_empty_rows.exists():
                        for rows in qSprot_empty_rows:
                            if not rows.id in lProtreused_empty_rows:
                                print("\n first", qSprot_empty_rows.values())
                                qSprot_empty_rows.filter(id=rows.id).update(submission_id=int(submission_id),int_id=int(entry['int_id']),protein_id=int(entry['protein_id'])) 
                                lProtreused_empty_rows.append(rows.id) 
                                break
                    else:
                        if SProtreuse.is_valid(): # only the submission molecule table should be filled!!!!
                            SProtreuse.save()
                        else:    
                            iii1=SProtreuse.errors.as_text()
                            print("SProtreuse ", entry," no es valido")
                            print("!!!!!!Errores despues del SProtreuse\n",iii1,"\n")
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
            if qSmolec_model_this_sub.exists():
                if len(qSmolec_model_this_sub) == len(qSmolec_model_first_sub):
                    if len(qSmolec_model_this_sub.filter(molecule_id__in=qSmolec_model_first_sub.values('submission_id__dyndbsubmissionmolecule__molecule_id')))==len(qSmolec_model_first_sub):
                        Update_molec=False
                    else:
                        Update_molec=True
                else:
                    Update_molec=True
            else:
                Update_molec=True
            if Update_molec:
                if qSmolec_model_this_sub.exists():
                     qSmolec_model_this_sub.update(not_in_model=None,int_id=None,molecule_id=None) 
                
                Submol_in_reuseM=list(qSmolec_model_first_sub.annotate(not_in_model=F('submission_id__dyndbsubmissionmolecule__not_in_model'),type=F('submission_id__dyndbsubmissionmolecule__type'),int_id=F('submission_id__dyndbsubmissionmolecule__int_id'),molecule_id=F('submission_id__dyndbsubmissionmolecule__molecule_id')).values())
                for mol_in_model in Submol_in_reuseM:
                    mol_in_model['submission_id']=submission_id
                    SMolreuse=dyndb_Submission_Molecule(mol_in_model)
                 
                    if SMolreuse.is_valid(): # only the submission molecule table should be filled!!!!
                        SMolreuse.save()
                    else:    
                        iii1=SMolreuse.errors.as_text()
                        print("SMolreuse ", mol_in_model," no es valido")
                        print("!!!!!!Errores despues del SMolreuse\n",iii1,"\n")
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
        dictmol={}
        fieldsmol=["id_compound","description","net_charge","inchi","inchikey","inchicol","smiles"]
        dictON={}
        fieldsON=["other_names"]
        dictcomp={}
        fieldscomp=["name","iupac_name","pubchem_cid","chemblid","sinchi","sinchikey","std_id_molecule","id_ligand"]
        dictfmol={} 
        fieldsPMod={"is_present","type"}
        dictPMod={}
        form=re.compile('form-')
        indexl=[]
        nl=0 #counter of pairs in dicpost.items()
        dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
        dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
        print(request.POST.keys())
        lrp=[]
        l_checkinpost=[]
        for o in request.POST.keys():
            if o.split("-")[0] == 'form':
                lrp.append(("-").join(o.split("-")[:2]))
        lrp=list(set(lrp))
        print("lista lrp ", lrp)
        for ll in ['name', "net_charge","inchi","inchikey","smiles","sinchikey","type" ]:
            for o in lrp:
                l_checkinpost.append(("-").join([o,ll]))
        print("\n\nlista lcheckinpost ", l_checkinpost)
        for l in  l_checkinpost:     
            if request.POST[l] == '':
                if l==("").join(["form-",l.split('-')[1],"-type"]):
                    print("ERROR PIPOL", l)
                    error=("").join(["\nPlease, pay attention to the section B in the SMOL #",str(int(l.split('-')[1])+1)," object.\n\nChoose the radio button option that indicates wether the molecule belongs to the crystal or not. Then specify the role of the molecule by selecting the corresponding type in the active dropdown menu placed to the right of the selected radio button"])
                    response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                error=("").join(["\nPlease, before submission fill every field manually (unlocked fields) or by retrieving data from the sdf/mol files, PubChem and CheMBL(locked fields) in the different sections of the Step 2.\n\nPay attention to the SMOL #",str(int(l.split('-')[1])+1)," object"])
                response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response
        print(dictmol)
        for key,val in dicpost.items():
            print("key",key," ",val)
            nl=nl+1
            if form.search(key):
                index=int(key.split("-")[1])
                if index not in indexl:
                    indexl.append(index)
                    dictmol[index]={}
                    dictON[index]={}
                    dictcomp[index]={}
                    dictPMod[index]={}
                nkey="-".join(key.split("-")[2:])  
            else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
                if len(indexl)==0:
                    index=0
                    indexl.append(0)
                    dictmol[0]={}
                    dictON[0]={}
                    dictcomp[0]={}
                    dictPMod[index]={}
                nkey=key
            for k,v in dfieldtype.items():
                if nkey in v:
                    dfielddict[k][index][nkey]=val
                    break
            continue 
        indexl.sort()
        print("COMPARA indexl")
        print(indexl)
        if "model_id" in request.POST.keys():
            extra_form_index=indexl[-1]
            ll=extra_form_index
            if dictmol[ll]['net_charge']=='' and dictmol[ll]['inchi']=='' and  dictmol[ll]['inchikey']=='' :
                 indexl=indexl[0:-1]
        print(indexl)
        print("\nPOST", request.POST, "\n",indexl)
        indexfl=[]
        fdbMF={}
        fdbMFobj={}
        fdbCF={}
        fdbCFobj={}
        fdbON={}
        fdbONobj={}
        dON={}
        on=0
        print("ANTES SORT",indexfl, indexl)
        if len(indexl) > 1:
            indexli=list(map(int,indexl))
            indexl=sorted(indexli)
        dicfmole={}
        fdbF={}
        fdbFobj={}
        fdbFM={}
        fdbSM={}
        fdbFMobj={}
        Std_id_mol_update={}
        NewCompoundEntry={}
        prev_Mol_in_Sub_exists=False
        print("\nPRUEBAfallo\n")
        #Molecules in the  submission if has been used before.
        qSm=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
        qSubreuse=DyndbSubmissionMolecule.objects.filter(int_id=None,molecule_id=None) #entry list to be reused
        qSm_moll=qSm.exclude(molecule_id=None,not_in_model=None,type=None)
        lqSubreuse_used=[] 
        if qSm.exists():
            prev_Mol_in_Sub_exists=True
            if len(qSm.exclude(int_id=None,type=None))>len(indexl) and len(indexl)>1:
                molec_to_Checkfordeletion=list(qSm.exclude(int_id__in=indexl).exclude(int_id=None,type=None).values_list('molecule_id','int_id'))
                for (mol_id,int_id) in molec_to_Checkfordeletion:
                    print("OJO",mol_id,int_id)
                    print(type(mol_id),"   int_id= ",int_id,"  type(int_id)=", type(int_id))
                    if mol_id != None and int_id != None:
                        deleteModelbyUpdateMolecule(mol_id,int_id,submission_id)
                        if qSm.filter(molecule_id=int(mol_id),int_id=int(int_id)).exists():
                              
                            updatedsub=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=int(int_id)).update(molecule_id=None,not_in_model=None,type=None)
                            print("updated", updatedsub.values())
                        print("Molecula ",mol_id," ha sido enviada a la funcion deleteModelbyUpdateMolecule para ver si puede ser borrada")
        else:
            prev_Mol_in_Sub_exists=False
        print("\nPRUEBAfallo\n")
        for ii in indexl:
            molid=ii 
            # Delete molecule DB if there is no molecule in the form molecule # 
            if dictmol[ii]['net_charge']=='' and dictmol[ii]['inchi']=='' and  dictmol[ii]['inchikey']=='' :
                print("Molecule #",ii+1," Item is empty!!!")
                if qSm_moll.filter(int_id=ii).exists():
                    print("list ",qSm_moll.filter(int_id=ii))
                    deleteModelbyUpdateMolecule(qSm_moll.filter(int_id=ii).values_list('molecule_id',flat=True)[0],ii,submission_id)
                    continue
            print("MOLID ",molid," INDEXL",indexl)
            if 'model_id' in request.POST.keys():
                if qSmolec_model_first_sub.filter(submission_id__dyndbsubmissionmolecule__int_id=molid).exists(): #the ii molecule is involved in the model to be reuse. files are in the folder of the first submission of the model!
                    INFOstdMOL=generate_molecule_properties2(qsubmission_id,molid) #:INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
                else: #molecules not in the model: files generated in this submission!!!
                    INFOstdMOL=generate_molecule_properties2(submission_id,molid) #:INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
            else: #molecules not in the model: files generated in this submission!!!
                INFOstdMOL=generate_molecule_properties2(submission_id,molid) #:INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
            print("\nPRUEBAfallo\n")
            print("AAAAa",INFOstdMOL.items())
            sinchi_fixed=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
            INFOstdMOL['sinchi']['sinchi']=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
            INFOstdMOL['inchi']['inchi']=INFOstdMOL['inchi']['inchi'].split('=')[1]
            Std_id_mol_update[ii]=True
            print("len(Std_id_mol_update)= ",len(Std_id_mol_update), "ii", ii, "indexl ",indexl)
            fdbCF[ii]={}
            fdbCFobj[ii]={}
            fdbMF[ii]={}
            fdbSM[ii]={}
            fdbMFobj[ii]={}
            fdbON[ii]={}
            fdbONobj[ii]={}
            dON[ii]={}
            #### Check if the molecule is already in our Database. If so the standar molecule shoud be as well!!!!! 
            qMF=DyndbMolecule.objects.filter(inchikey=dictmol[ii]['inchikey']).filter(inchi=dictmol[ii]['inchi'].split('=')[1])
            if qMF.exists():
                MFpk=qMF.values_list('id',flat=True)[0]
                print("\nMOLECULE EXISTS IN THE DB\n")
                if qSm.filter(int_id=ii).exists():
                    if not qMF.filter(dyndbsubmissionmolecule__submission_id=submission_id,dyndbsubmissionmolecule__int_id=ii).exists():
                        #that means the molecule in the db for this submission is not the one in the form and the first has to be checked for deletion
                        deleteModelbyUpdateMolecule(qSm.filter(int_id=ii).values_list('molecule_id',flat=True)[0],ii,submission_id)
                        DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=ii).update(molecule_id=None,not_in_model=None)
                        print("Previously submitted molecule in the database not matching the one in the form!!! TTPPPPP")
                        print(dictmol[ii]['inchikey'])
                        print("\nQuery Molecule antes aux\n ",qMF)
                    else:
                        print("PRINT",qSm.filter(int_id=ii).values())
                        print("PRINT",dictPMod[ii]['type'])
                        if not qSm.filter(type=int(dictPMod[ii]['type']),int_id=ii).exists():
                            if int(dictPMod[ii]['type']) > 5:
                                print("llll")
                                qSm.filter(int_id=ii).update(type=dictPMod[ii]['type'],not_in_model=True)
                            else:
                                qSm.filter(int_id=ii).update(type=dictPMod[ii]['type'],not_in_model=False)
                            print("The molecule ", ii," in the form already appears in the db to be involved in this submission, but type and possibly presence in model have been modified")
                        else:
                            print("The molecule ", ii," in the form already appears in the db to be involved in this submission")
                            #continue
                else:
                    qSreuse=DyndbSubmissionMolecule.objects.filter(int_id=None,molecule_id=None)
                    if qSreuse.exists():
                        for row_to_update in qSreuse:
                            print("INTENTANDO UPDATE,",qSreuse.values()[0],"type ",type(dictPMod[ii]['type'])," ",dictPMod[ii]['type'] )
                            lll=int(str(dictPMod[ii]['type']))
                            if lll >5:
                                not_in_model=True
                            else:
                                not_in_model=False
                            
                            qSreuse.filter(id=qSreuse.values_list('id',flat=True)[0]).update(int_id=ii,submission_id=submission_id,molecule_id=MFpk,type=int(dictPMod[ii]['type']),not_in_model=not_in_model)
                            print("INTENTANDO UPDATE,",qSreuse.values()[0],"type ",type(dictPMod[ii]['type'])," ",dictPMod[ii]['type'] )
                            print("MMMMAAAMMMM")
                            break
            else:
                dictmol[ii]['molecule_creation_submission_id']=submission_id
                if qSm.filter(int_id=ii).exists():
                    print("There is a molecule in the database with this submission_id and int_id not matching the one in the form which in addition is not contained in the db!!! TTPPPPP")
                    deleteModelbyUpdateMolecule(qSm.filter(int_id=ii).values_list('molecule_id',flat=True)[0],ii,submission_id)
            #generation of the sinchi
            if 'pubchem_cid' in dictcomp[ii].keys():
                if dictcomp[ii]['pubchem_cid']!='':
                    print("a")
                    qCFStdFormExist=DyndbCompound.objects.filter(pubchem_cid=dictcomp[ii]['pubchem_cid']) #if std form of the molecule is in the database. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be link to the DyndbCompound entry
                else:
                    qCFStdFormExist=DyndbCompound.objects.filter(sinchikey="Ñ")# Query with no result
                    print("Pubchem value =''")
            elif 'chemblid' in dictcomp[ii].keys():
                if dictcomp[ii]['chemblid']!='':
                    print("b")
                    qCFStdFormExist=DyndbCompound.objects.filter(chemblid=dictcomp[ii]['chemblid']) #if std form of the molecule is in the database. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
                    print("PPPPP2")
                else:
                    qCFStdFormExist=DyndbCompound.objects.filter(sinchikey="Ñ")# Query with no result
                    print("Pubchem value =''")
            else: 
                if 'sinchi' not in dictcomp[ii].keys():
                    print("c")
                    qCFStdFormExist=DyndbCompound.objects.filter(sinchikey="Ñ")# Query with no result
                    print("\nNo hay qCFStdFormExist")
                else:
                    print("d")
                    qCFStdFormExist=DyndbCompound.objects.filter(sinchikey=dictcomp[ii]['sinchikey']).filter(sinchi=dictcomp[ii]['sinchi']) #if the std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
                print("\hay qCFStdFormExist")
            if qCFStdFormExist.exists():
                print("PPPPP3")
            else:
                print("PPPPP4")
            if qMF.exists():
                print("len", len(qMF.values()))
                if len(qMF.values())==1: #there is a entry matching this molecule
                    if int(dictPMod[ii]['type'])>5:
                        dictPMod[ii]['not_in_model']=True
                    else:
                        dictPMod[ii]['not_in_model']=False     
                    dictPMod[ii]['int_id']=ii
                    dictPMod[ii]['submission_id']=submission_id
                    dictPMod[ii]['molecule_id']=MFpk
                    if prev_Mol_in_Sub_exists:
                        qSMol=qSm.filter(molecule_id=MFpk,int_id=ii)
                        print("antes de comprobar si la submission esta hecha previamente  ", MFpk)
                        if qSMol.exists():
                            print("En efecto, la submission esta hecha previamente con la misma molecula en el form")
                            continue 
                        if qSm.filter(int_id=ii,not_in_model=None,molecule_id=None).exists():

                            qSm.filter(int_id=ii,not_in_model=None,molecule_id=None).update(molecule_id=MFpk,not_in_model=dictPMod[ii]['not_in_model'],type=dictPMod[ii]['type'])
                            print("\nHay update?\n")
                            continue
                    fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
                    print("PPPPPPPP", fdbSM[ii].__dict__['data'], "KKKKKKKKKK  ",fdbSM[ii].__dict__['fields'])
                    if qSubreuse.exists():
                        for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                            qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=int(dictPMod[ii]['int_id']),molecule_id=int(dictPMod[ii]['molecule_id']),not_in_model=dictPMod[ii]['not_in_model']) 
                            lqSubreuse_used.append(rows.id) 
                            break
                    else:
                        if fdbSM[ii].is_valid(): # only the submission molecule table should be filled!!!!
                            fdbSM[ii].save()
                        else:    
                            iii1=fdbSM[ii].errors.as_text()
                            print("fdbSM",ii," no es valido")
                            print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
                    if ii==indexl[-1]:#if ii is the last element of the list indexl
                        print("Molecule #", ii, "has been found in our database")
                        response = HttpResponse("Step 2 \"Small Molecule Information\" form has been successfully submitted.",content_type='text/plain; charset=UTF-8')
                        return response
                        #break
                    else:
                        print("Molecule #", ii, "has been found in our database")
                        continue
                elif len(qMF.values())>1:
                    response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
                    return response
            else:
                print("The Molecule does not exists")
            #########   No entry in the GPCRmd DB has been found for the molecule ii... Maybe the Compound and, therefore, the std molecule entries are !!!
            #########   Use of functions retrieving std_molecule info from external sources!!!! It is needed for updating
            molid=ii 
            print ("\nmolid=",molid)
            submission_path_nofile = get_file_paths("molecule",url=False,submission_id=submission_id)
            submission_url_nofile = get_file_paths("molecule",url=True,submission_id=submission_id)
            namerefsdf = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
            namerefpng = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image")
            namesdf = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")
            namepng = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="png",forceext=False,subtype="image")
            print("antes INFOstdMOL")
            path_namefsdf=("").join([submission_path_nofile, namesdf])
            path_namefpng=("").join([submission_path_nofile, namepng])
            path_namefrefsdf=("").join([submission_path_nofile, namerefsdf])
            path_namefrefpng=("").join([submission_path_nofile, namerefpng])
            url_namefrefsdf=("").join([submission_url_nofile, namerefsdf])
            url_namefrefpng=("").join([submission_url_nofile, namerefpng])
            url_namefsdf=("").join([submission_url_nofile, namesdf])
            url_namefpng=("").join([submission_url_nofile, namepng])
            ############     check if the molecule ii is actually the standard form of the molecule. If this specific form of the molecule is not in the database (DyndbMolecule) but other molecules corresponding the same compound are, the one we are dealing with won`t be the standard as it is previously recorded when the first molecule corresponding the compound was registered. So, if there is no any entry in the DyndbCompound table matching the sinchikey of the molecule in the form, still will be possible that the current entry would be the standard form.
            if qCFStdFormExist.exists():
                if len(qCFStdFormExist.values())==1: #The compound and the standard form of the current molecule is in the database (Only fill the current non standard molecule)
                    print("Compound entry matching SInChIKey and SInChI has been found in GPCRmd database")
                    CFpk=qCFStdFormExist.values_list('id',flat=True)[0]	
                    Std_id_mol_update[ii]=False
                elif len(qCFStdFormExist.values())>1: #the compound is found more than once in the database
                    response=HttpResponse("Several Compound entries have been found in the DATABASE. Please, report this ERROR to the GPCRmd database administrator",status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
                    return response
            else: #Neither the compound nor the standard form of the molecule are in the database
                Std_id_mol_update[ii]=True
                NewCompoundEntry[ii]=True #this flag is needed in case the Compound entry need to be deleted (not if the entry existed previosly) if further steps of the submission fail
                print("No compound entry has been found in GPCRmd DB")
                #### No compound entry has been found in GPCRmd DB.Keep track of the Compound in the DyndbCompound table and the aliases in the DyndbOtherCompoundNames
                #### DyndbCompound
                for key,val in initCF.items():
                    if key not in dictcomp[ii].keys():
                        dictcomp[ii][key]=val
                    if key == "sinchi":
                        dictcomp[ii][key]=sinchi_fixed
                if dictcomp[ii]['iupac_name']=="":
                    dictcomp[ii]['iupac_name']="Not available"
                fdbCF[ii]=dyndb_CompoundForm(dictcomp[ii]) 
                if fdbCF[ii].is_valid():
                    fdbCFobj[ii]=fdbCF[ii].save()
                    CFpk=fdbCFobj[ii].pk
                else:
                    iii1=fdbCF[ii].errors.as_text()
                    print("Errores en el form dyndb_CompoundForm\n ", fdbCF[ii].errors.as_text())
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                #### DyndbOtherCompoundNames 
                ONlist=[]
                ONlist=dictON[ii]["other_names"].split(";")
                print("ONLIST ",ONlist,"len",len(ONlist))
                if ONlist[0] == '':
                    ONlist[0]=dictcomp[ii]['name']
                print("ONLIST ",ONlist)
                for el in ONlist:
                    on=on+1
                    dON[ii][on]={}
                    dON[ii][on]["other_names"]=el
                    dON[ii][on]["id_compound"]=CFpk
                    fdbON[ii][on]=dyndb_Other_Compound_Names(dON[ii][on])
                    if fdbON[ii][on].is_valid():
                        fdbON[ii][on].save()
                    elif not fdbON[ii][on].validate_unique():
                        print('Synonym skipped as duplicated:',el)
                        continue
                    else:
                        iii1=fdbON[ii][on].errors.as_text()
                        print("Errores en el form dyndb_Other_Compound_Names\n ", fdbON[ii][on].errors.as_text())
                        response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        DyndbCompound.objects.filter(id=CFpk).delete()
                        return response
                #### ## Get the standard Molecule by providing the SInChIKey to the PubChem or CHEMBL databases if the molecule is actually the standard form of the molecule.
                ########      DyndbCompound and DyndbOtherCompoundNames tables have been filled. Then entries for the std molecule should be registered in DyndbMolecule and DyndbSubmissionMolecule
                print("COMPROBAR ",INFOstdMOL)
                if 'msg' in INFOstdMOL.keys():
                    print("HttpResponse(INFOstdMOL['msg'])" )
                    print("HttpResponse(", INFOstdMOL['msg'], ")" )
                    return HttpResponse(INFOstdMOL['msg'],status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8') 
                ####### Check if inchi of the standard molecule matches the inchi in the current entry (HTML form)         
                ###### In the case the compound neither have Pubchem nor chembl entry, the std molecule is not required. If no std sdf file has been obtained std molecule info is not registered
                ##### Path_namefrefsdf stand for the path and name of the file in the file system in case it exists. 
                print("COMPROBAR ",INFOstdMOL)
                print("LLLLLLLLLLLl")
                Path_namefrefsdf=Path(path_namefrefsdf)
                if Path_namefrefsdf.is_file():
                    print("is_file")
                    if INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'].split('=')[1]: #Both molecules are the standard molecule so one entry is saved
                        print("The molecule ",ii, "is actually the standard molecule")
                        dictmol[ii]['description']="Standard form"
                    else:
                        auxdictmol={}
                        print("The molecule ",ii, "is not the standard molecule. The standard one will be saved right now!!!!")
                        for key,val in INFOstdMOL.items():# HAY QUE INTRODUCIR LOS DATOS DEL SCRIPT PARA PODER CREAR UN DICCIONARIO PARA LA INSTANCIA!!!
                            print("\nAQUI ",key,val)
                            if type(val)==dict:
                                auxdictmol[key]=val[key]
                                print("\nauxdictmol inchi ", auxdictmol[key] )
                                 #   "Problem while generating inchi:\n"+ msg   
                            if key == 'charge':
                                auxdictmol['net_charge']=val 
                            if key in dfieldtype['0']:
                                if key == 'inchikey':
                                    auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
                                    nrep_inchikey=len(DyndbMolecule.objects.filter(inchikey=val))
                                    if nrep_inchikey >= 1:
                                        auxdictmol['inchicol']=nrep_inchikey+1
                                    else:
                                        auxdictmol['inchicol']=1
                                elif key == 'sinchi':
                                    auxdictmol['sinchi']=INFOstdMOL['sinchi']['sinchi']
                                elif key == 'inchi':
                                    auxdictmol['inchi']=INFOstdMOL['inchi']['inchi']
                                else:
                                    auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
                        for key,val in initMF.items():
                            if key not in auxdictmol.keys():
                                auxdictmol[key]=val  ##### completion of the dictionary
                        auxdictmol['id_compound']=CFpk
                        auxdictmol['description']="Standard form"
                        fdbMFaux=dyndb_Molecule(auxdictmol)
                        print("\n\n resultado auxdicmol", auxdictmol  )
                        if fdbMFaux.is_valid():
                            fdbMFauxobj=fdbMFaux.save()
                            MFauxpk=fdbMFauxobj.pk
                        else:
                            print("Errores en el form dyndb_Molecule aux\n ", fdbMFaux.errors.as_text())
                            iii1=fdbMFaux.errors.as_text()
                            response = HttpResponse((" ").join([iii1," aux"]),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                            DyndbCompound.objects.filter(id=CFpk).delete()
                            return response
                           #### Entry in DyndbSubmissionMolecule corresponding to the standard molecule 
                        auxdictPMod={}
                        auxdictPMod['not_in_model']=True
                        auxdictPMod['int_id']=None
                        auxdictPMod['submission_id']=submission_id
                        auxdictPMod['molecule_id']=MFauxpk
                        fdbSMaux=dyndb_Submission_Molecule(auxdictPMod)
                        if qSubreuse.exists():
                            for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                                qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=None,molecule_id=int(auxdictPMod[ii]['molecule_id']),not_in_model=True) 
                                lqSubreuse_used.append(rows.id) 
                                break
                        else:    
                            if fdbSMaux.is_valid(): # only the submission molecule table should be filled!!!!
                                fdbSMaux.save()
                            else:    
                                iii1=fdbSMaux.errors.as_text()
                                print("fdbSMaux",ii," no es valido")
                                print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
                                response = HttpResponse((" ").join([iii1," aux"]),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                                DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=1)#needed for removing the next  DyndbMolecule entry
                                DyndbMolecule.objects.filter(id=MFauxpk).delete()
                                DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                                DyndbCompound.objects.filter(id=CFpk).delete()
                                return response
                        dnameref={'dnamesdf':{'path':path_namefrefsdf,'url':url_namefrefsdf},'dnamepng':{'path':path_namefrefpng,'url':url_namefrefpng}}
                        print("AUX",dnameref)
                        oooref=molec_file_table(dnameref,MFauxpk)
                        ##### ## the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule 
                        # In this block the condition INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'] is false. Then the std molecule pk is MFauxpk and the flag Std_id_mol_update is set
                        # to False in order to avoid subsequents updates when the molecule in the form (not standard) would be entried.
                        DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFauxpk) 
                        Std_id_mol_update[ii]=False
                else:#neither found in pubmed nor in chembl ... no std reference molecule--> no update compound table
                    Std_id_mol_update[ii]=False
                    print ("the file", path_namefrefsdf,"does not exist")
            ## The code enclosed in this section is common for cases in which a previous compound entry existed and cases where the Compound entry has been registered in this submission!!!  
            print("\n\n")
            for key,val in initMF.items():
                if key not in dictmol[ii].keys():
                    dictmol[ii][key]=val
                    print(dictmol[ii][key], val)
            dictmol[ii]['id_compound']=CFpk
            aaa=dictmol[ii]['inchi'].split('=')[1]
            dictmol[ii]['inchi']=aaa
           #####AQUI ME QUEDE!!!! 
            fdbMF[ii]=dyndb_Molecule(dictmol[ii])
            if fdbMF[ii].is_valid():
                fdbMFobj[ii]=fdbMF[ii].save()
                MFpk=fdbMFobj[ii].pk
            else:
                iii1=fdbMF[ii].errors.as_text()
                print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_text())
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                if NewCompoundEntry[ii]==True:
                    DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=1)#needed for removing the next  DyndbMolecule entry
                    DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).values_list('id_files',flat=True)).delete()
                    DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).delete()
                    DyndbSubmissionMolecule.objects.filter(molecule_id=MFauxpk).delete()
                    DyndbMolecule.objects.filter(id=MFauxpk).delete()
                    DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                    DyndbCompound.objects.filter(id=CFpk).delete()
                return response
 
            dname={'dnamesdf':{'path':path_namefsdf,'url':url_namefsdf},'dnamepng':{'path':path_namefpng,'url':url_namefpng}}
            print(dname,"")
            ooo= molec_file_table(dname,MFpk)
           #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule
           # if the Std_id_mol_update flag is set to True the molecule in the form is the standard one and the std_id_molecule field in DyndbCompound should be update with MFpk
            if Std_id_mol_update[ii]:
                DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFpk) 
                Std_id_mol_update[ii]=False
            if int(dictPMod[ii]['type'])>5:
                dictPMod[ii]['not_in_model']=True
            else:
                dictPMod[ii]['not_in_model']=False     
            dictPMod[ii]['int_id']=ii
            dictPMod[ii]['submission_id']=submission_id
            dictPMod[ii]['molecule_id']=MFpk
            # force an update in case int_id is already in use
            try:
                qsubmol_id = DyndbSubmissionMolecule.objects.get(submission_id=int(submission_id),
                     int_id=int(dictPMod[ii]['int_id'])).id
                dictPMod[ii]['id']=submol_id
            except DyndbSubmissionMolecule.DoesNotExist:
                pass
            fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
            if qSubreuse.exists():
                for rows in qSubreuse.exclude(id__in=lqSubreuse_used):
                    qSubreuse.filter(id=rows.id).update(submission_id=int(submission_id),int_id=int(dictPMod[ii]['int_id']),molecule_id=int(dictPMod[ii]['molecule_id']),not_in_model=dictPMod[ii]['not_in_model']) 
                    lqSubreuse_used.append(rows.id) 
                    break
            else:
                if fdbSM[ii].is_valid():
                    fdbSM[ii].save()
                    response= HttpResponse("SUCCESS",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                else:    
                    iii1=fdbSM[ii].errors.as_text()
                    print("fdbSM",ii," no es valido")
                    print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
                    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFpk).values_list('id_files',flat=True)).delete()
                    DyndbMolecule.objects.filter(id=MFpk).delete()
                    if ii in NewCompoundEntry:
                        if NewCompoundEntry[ii]==True:
                            DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=None)#needed for removing the next  DyndbMolecule entry
                            DyndbMolecule.objects.filter(id=MFpk).delete()
                            DyndbFiles.objects.filter(id__in=DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).values_list('id_files',flat=True)).delete()
                            DyndbFilesMolecule.objects.filter(id_molecule=MFauxpk).delete()
                            DyndbSubmissionMolecule.objects.filter(molecule_id=MFauxpk).delete()
                            DyndbMolecule.objects.filter(id=MFauxpk).delete()
                            DyndbOtherCompoundNames.objects.filter(id_compound=CFpk).delete()
                            DyndbCompound.objects.filter(id=CFpk).delete()
                        else:
                            DyndbMolecule.objects.filter(id=MFpk).delete()
                    else:
                        DyndbMolecule.objects.filter(id=MFpk).delete()
                    return response
        moleculelist=str(indexl)
        response = HttpResponse("Step 2 \"Small Molecule Information\" form has been successfully submitted.",content_type='text/plain; charset=UTF-8')
        return response
    else:
        qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).order_by('int_id').filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url'))
        print("\nlen QSUB", len(qSub))
        print("QSUB", qSub.values())
        if len(qSub)>0:
            labtypel=[]
            print(qSub)  ######POR AQUI!!!! ORDENAR POR INT_ID LA QUERY qMOL!!! 
            int_id=[]
            int_id0=[]
            alias=[]
            qCOMP=[]
            qMOL=[]
            imp=[]
            Type=[]
            url=[]
            urlstd=[]
            for l in qSub:
                url.append(str(l.url).strip())
                urlstd.append(str(l.urlstd).strip())
                labtype=l.COMPOUND_TYPE[l.type]
                labtypel.append(labtype) 
                if  not l.not_in_model:
                    imp.append(True)
                else:
                    imp.append(False)
  
                int_id.append(l.int_id+1)
                int_id0.append(l.int_id)
                typt=l.type
                Type.append(typt)
                qmol=DyndbMolecule.objects.filter(id=l.molecule_id.id)[0]
                qMOL.append(qmol)
                qCOMPtt=DyndbCompound.objects.filter(id=qmol.id_compound.id)[0] # VERIFICAR!!!!!!!!!!!!!!!!!!!
                qALIAS=DyndbOtherCompoundNames.objects.filter(id_compound=qmol.id_compound.id)
                llo=("; ").join(qALIAS.values_list('other_names',flat=True))
                alias.append(llo) 
                qCOMP.append(qCOMPtt) 
            listExtraMolColapse=list(range(len(qCOMP),40))
            fdbSub = dyndb_Submission_Molecule()
            return render(request,'dynadb/SMALL_MOLECULE.html', {'url':url,'urlstd':urlstd,'fdbSub':fdbSub,'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'list':listExtraMolColapse, 'saved':True,'colorlist':color_label_forms})
        else:    
            labtypel=[]
            int_id=[]
            int_id0=[]
            alias=[]
            qCOMP=[]
            qMOL=[]
            imp=[]
            Type=[]
            int_id.append(1)
            int_id0.append(0)
            typt=""
            Type.append(typt)
            qmol=""
            qMOL.append(qmol)
            qCOMPtt="" # VERIFICAR!!!!!!!!!!!!!!!!!!!
            qALIAS=""
            alias.append("") 
            qCOMP.append("") 
            print(alias)
            print(qCOMP)
            print(qMOL)
            fdbSub = dyndb_Submission_Molecule()
    return render(request,'dynadb/SMALL_MOLECULE.html', {'qMOL':qMOL,'fdbSub':fdbSub,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'model_id':False,'colorlist':color_label_forms})

def save_uploadedfile(filepath,uploadedfile):
    if not settings.MEDIA_ROOT[:-1] in filepath: 
        filepath = settings.MEDIA_ROOT[:-1] + filepath
    with open(filepath,'wb') as f:
        if uploadedfile.multiple_chunks:
            for chunk in uploadedfile.chunks():
                f.write(chunk)
        else:
            f.write(uploadedfile.read())
        f.close()
def type_inverse_search(type_matrix,searchkey=None,case_sensitive=False,first_match=True,searchkey_is_regex=False):
    inverse_type = dict()
    if  searchkey is None:
        dore = False
    else:
        dore = True
        if case_sensitive:
            flags = 0
        else:
            flags=re.IGNORECASE
        searchkey2 = searchkey
        if not searchkey_is_regex:
            searchkey2 = re.escape(searchkey2)
        researchkey = re.compile(searchkey2,flags=flags)
    for row in type_matrix:
        internal_val = row[0]
        text = row[1]
        if dore:
            m = researchkey.search(text)
            if m:
                if first_match:
                    return internal_val
                else:
                    inverse_type[text] = internal_val
        else:
            inverse_type[text] = internal_val
                
    if first_match and dore:
        if searchkey_is_regex:
            raise ValueError("Object in first argument doesn't have text that matches the pattern '"+searchkey+"'.")
        else:
            raise ValueError("Object in first argument doesn't have text '"+searchkey+"'.")
    else:
        return inverse_type

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    #columns = [col._asdict()['name'] for col in cursor.description]
    columns = [col.name for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def submission_summaryiew(request,submission_id):
#protein section
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id')
    int_id=[]
    int_id0=[]
    alias=[]
    mseq=[]
    wseq=[]
    MUTations=[]
    sci_na_codel=[]
    qPROT=[]
    for l in qSub:
        sci_name=list(DyndbUniprotSpecies.objects.filter(id= l.protein_id.id_uniprot_species_id).values_list('scientific_name','code')[0])
        if sci_name[0]==None:
            sci_name[0]=''
        if sci_name[1]==None:
            sci_name[1]=''
        sci_na_code=("").join([sci_name[0]," (",sci_name[1],")"])
        sci_na_codel.append(sci_na_code)
        qprot=DyndbProtein.objects.filter(id=l.protein_id_id)[0]
        qPROT.append(qprot)
        int_id.append(l.int_id +1) 
        int_id0.append(l.int_id) 
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
            llsm=qSEQ
            mseq.append(llsm)
            qpCp=DyndbProteinCannonicalProtein.objects.filter(id_protein=l.protein_id).values_list('id_cannonical_proteins',flat=True)[0]
            llsw=DyndbProteinSequence.objects.filter(id_protein=qpCp).values_list('sequence',flat=True)[0]
            qPMut=DyndbProteinMutations.objects.filter(id_protein=l.protein_id)
            MUTations.append(qPMut)
        else:
            llsw=qSEQ
            mseq.append('')
            MUTations.append('')
        wseq.append(llsw) 
        qALIAS=DyndbOtherProteinNames.objects.filter(id_protein=l.protein_id)
        llo=("; ").join(qALIAS.values_list('other_names',flat=True))
        alias.append(llo) 
#small molecule section
    qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).order_by('int_id').filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'))
    labtypels=[]
    print(qSub)  ######POR AQUI!!!! ORDENAR POR INT_ID LA QUERY qMOL!!! 
    int_ids=[]
    int_ids0=[]
    aliass=[]
    qCOMP=[]
    qMOL=[]
    imps=[]
    Types=[]
    urls=[]
    for l in qSub:
        urls.append(str(l.url).strip())
        labtypes=l.COMPOUND_TYPE[l.type]
        labtypels.append(labtypes) 
        if  not l.not_in_model:
            imps.append(True)
        else:
            imps.append(False)

        int_ids.append(l.int_id+1)
        int_ids0.append(l.int_id)
        typt=l.type
        Types.append(typt)
        qmol=DyndbMolecule.objects.filter(id=l.molecule_id.id)[0]
        qMOL.append(qmol)
        qCOMPtt=DyndbCompound.objects.filter(id=qmol.id_compound.id)[0] # VERIFICAR!!!!!!!!!!!!!!!!!!!
        qCOMP.append(qCOMPtt) 
    print("LABTYPES",labtypels)
    print("int_ids0",int_ids0)
    fdbSubs = dyndb_Submission_Molecule()
#model section
    qModel=DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id)
    p=qModel
    Typeval=p.values()[0]['type']
    TypeM=p.model.MODEL_TYPE[Typeval][1]
    STypeval=p.values()[0]['source_type']
    SType=p.model.SOURCE_TYPE[STypeval][1]
    model_id=qModel.values_list('id',flat=True)[0]
#dynamics section
    qDS=DyndbDynamics.objects.filter(submission_id=submission_id)
    dyn_id = qDS[0].id
    ddown={}
    ddown['id_dynamics_methods']= DyndbDynamicsMethods.objects.filter(dyndbdynamics__submission_id=submission_id).values_list('type_name',flat=True)[0]
    ddown['id_assay_types']= DyndbAssayTypes.objects.filter(dyndbdynamics__submission_id=submission_id).values_list('type_name',flat=True)[0]
    ddown['id_dynamics_membrane_types']=DyndbDynamicsMembraneTypes.objects.filter(dyndbdynamics__submission_id=submission_id).values_list('type_name',flat=True)[0]
    ddown['id_dynamics_solvent_types']=DyndbDynamicsSolventTypes.objects.filter(dyndbdynamics__submission_id=submission_id).values_list('type_name',flat=True)[0]
    data = get_components_info_from_components_by_submission(submission_id,'dynamics')
    other_int = type_inverse_search(DyndbDynamicsComponents.MOLECULE_TYPE,searchkey="other",case_sensitive=False,first_match=True)
    molecule_type_dict = dict(DyndbDynamicsComponents.MOLECULE_TYPE)
    i = 0
    for row in  data:
        data[i]['readonly'] = True
        data[i]['int_id'] = 1 + data[i]['int_id']
        data[i]['type_int'] = model_2_dynamics_molecule_type.translate(data[i]['type'],as_text=False)
        if data[i]['type_int'] is None:
            data[i]['type_int'] = other_int
        data[i]['type'] = model_2_dynamics_molecule_type.translate(data[i]['type'],as_text=True)
        i += 1
    compl=[]
    dctypel=[]
    for tt in qDS.values_list('id',flat=True):
        qDC=DyndbDynamicsComponents.objects.filter(id_dynamics=tt).exclude(type=None,numberofmol=None).order_by('id')
        compl.append(qDC)
        d=0
        l_ord_mol=[]
        lcompname=[]
        for l in qDC:
            dctype=DyndbDynamicsComponents.MOLECULE_TYPE[l.type][1]
            dctypel.append(dctype)
            d=d+1
            id_t = DyndbMolecule.objects.filter(id=l.id_molecule_id).values_list('id_compound',flat=True)[0]
            qName=DyndbCompound.objects.filter(id=id_t).values_list('name',flat=True)[0]
            lcompname.append(qName)
            l_ord_mol.append(d)
    dd=dyndb_Dynamics()
    ddC =dyndb_Dynamics_Components()
    qDMT =DyndbDynamicsMembraneTypes.objects.all().order_by('id')
    qDST =DyndbDynamicsSolventTypes.objects.all().order_by('id')
    qDMeth =DyndbDynamicsMethods.objects.all().order_by('id')
    qAT =DyndbAssayTypes.objects.all().order_by('id')
    submission_path = get_file_paths("summary",url=False,submission_id=submission_id)
    submission_url = get_file_paths("summary",url=True,submission_id=submission_id)    
    filename = get_file_name_submission("summary",submission_id,0,ext='txt',forceext=False,subtype='summary')
    summarypath = os.path.join(submission_path,filename)
    summaryurl = os.path.join(submission_url,filename)
    fh= HttpResponse("",content_type='text/plain; charset=UTF-8',)
    fh.charset="UTF-8"
    if not os.path.exists(submission_path):
        os.makedirs(submission_path)
    with open(summarypath,'w') as fh:
        i=0      
        fh.write("".join(["\tPROTEINS INVOLVED IN THE SUBMISSION ",str(submission_id),"\n\n"])) 
        for prot in qPROT:
            i=i+1
            if prot.is_mutated:
                fh.write("".join(["\t\tPROTEIN #",str(i),"\t(Mutant Protein)"])) 
            else:
                fh.write("".join(["\t\tPROTEIN #",str(i)])) 
            fh.write("".join(["\n\t\tName:  ", prot.name])) 
            fh.write("".join(["\n\t\tSpecies:  ", sci_na_codel[i-1]])) 
            fh.write("".join(["\n\t\tUniProtKB AC:  ", prot.uniprotkbac]))
            fh.write("".join(["\n\t\tIsoform:  ", str(prot.isoform),"\n"]))
            if prot.is_mutated:
                fh.write(str("\t\tMutations:\n"))
                for mut in MUTations[i-1]:
                    fh.write("".join(["\t\t\tResid: ", str(mut.resid),"\tResletter from: ",  mut.resletter_from,"\tResletter to: ",  mut.resletter_to,"\n"]))
                    if mut == MUTations[i-1][len(MUTations[i-1])-1]:
                        fh.write("\n")
            else:
                fh.write("\n")
        fh.write("".join(["\tSMALL MOLECULES INVOLVED IN THE SUBMISSION ",str(submission_id),"\n"])) 
        i=0   
        print(int_id)
        for mol in qMOL:
            i=i+1
            fh.write("".join(["\n\t\tSMALL MOLECULE #",str(int_ids[i-1])])) 
            fh.write("".join(["\n\t\tName:  ", mol.id_compound.name])) 
            fh.write("".join(["\n\t\tNet charge:  ", str(mol.net_charge), "\tPubChem cid:  ", str(mol.id_compound.pubchem_cid)])) 
            if qSub.filter(molecule_id=mol.id).values_list("not_in_model",flat=True)[0]: 
               fh.write("".join(["\n\t\tBulk Molecule:  ",str(DyndbSubmissionMolecule.COMPOUND_TYPE[qSub.filter(molecule_id=mol).values_list('type',flat=True)[0]][1])]))
            else:
               fh.write("".join(["\n\t\tCrystalized Molecule:  ",str(DyndbSubmissionMolecule.COMPOUND_TYPE[qSub.filter(molecule_id=mol).values_list('type',flat=True)[0]][1])]))
            fh.write("\n")
        pp=p[0]
        fh.write("".join(["\n\tMODEL INVOLVED IN THE SUBMISSION ",str(submission_id),"\n"])) 
        fh.write("".join(["\n\t\tMODEL ID:  ",str(model_id)])) 
        fh.write("".join(["\n\t\tName:  ", pp.name])) 
        fh.write("".join(["\n\t\tPDB ID:  ", pp.pdbid])) 
        fh.write("".join(["\n\t\tSource type:  ", DyndbModel.SOURCE_TYPE[pp.source_type][1]])) 
        fh.write("".join(["\n\t\tDescription:  ", pp.description,"\n"])) 
        fh.write("".join(["\n\tSIMULATION SUBMITTED IN THE SUBMISSION ",str(submission_id),"\n"])) 
        fh.write("".join(["\n\t\tSIMULATION COMPONENTS\n\n"])) 
        i=0      
        for prot in qPROT:
            i=i+1
            if prot.is_mutated:
                fh.write("".join(["\t\tPROTEIN #",str(i),"\tName:  ", prot.name, "\tUniProtKB AC:  ", prot.uniprotkbac, "\t(Mutant Protein)\n"])) 
            else:
                fh.write("".join(["\t\tPROTEIN #",str(i),"\tName:  ", prot.name, "\tUniProtKB AC:  ", prot.uniprotkbac,"\n"   ])) 
        i=0
        for comp in qDC:
            if qSub.filter(molecule_id=comp.id_molecule).values("not_in_model")[0]['not_in_model']:
                print("VALUE cryst ",qSub.filter(molecule_id=comp.id_molecule).values("not_in_model")[0]['not_in_model'])
                fh.write("".join(["\n\t\tResname:  ",comp.resname,"\tMolecule:  ", str(l_ord_mol[i]), "\tNum of mol:  ", str(comp.numberofmol),"    \tType:  ", DyndbDynamicsComponents.MOLECULE_TYPE[comp.type][1],"\tCryst:  ", "No ","  Name:  ", lcompname[i]]))
            else:
                print("VALUE cryst ----- ",qSub.filter(molecule_id=comp.id_molecule).values("not_in_model")[0]['not_in_model'])
                fh.write("".join(["\n\t\tResname:  ",comp.resname,"\tMolecule:  ", str(l_ord_mol[i]), "\tNum of mol:  ", str(comp.numberofmol),"    \tType:  ", DyndbDynamicsComponents.MOLECULE_TYPE[comp.type][1],"\tCryst:  ", "Yes","  Name:  ", lcompname[i]]))
            i=i+1
        qDSs=qDS[0]
        fh.write("\n")
        fh.write("".join(["\n\t\tSIMULATION DETAILS\n "])) 
        fh.write("".join(["\n\t\tMethod: ", qDSs.id_dynamics_methods.type_name])) 
        fh.write("".join(["\n\t\tSoftware: ", qDSs.software])) 
        fh.write("".join(["\n\t\tSoftware version: ", qDSs.sversion])) 
        fh.write("".join(["\n\t\tForce Field: ", qDSs.ff])) 
        fh.write("".join(["\n\t\tFF version: ", qDSs.ffversion])) 
        fh.write("".join(["\n\t\tAssay Type: ", qDSs.id_assay_types.type_name])) 
        fh.write("".join(["\n\t\tMembrane type: ", qDSs.id_dynamics_membrane_types.type_name])) 
        fh.write("".join(["\n\t\tSolvent type: ", qDSs.id_dynamics_solvent_types.type_name])) 
        fh.write("".join(["\n\t\tSolvent num: ", str(qDSs.solvent_num)])) 
        fh.write("".join(["\n\t\tNum. atoms: ", str(qDSs.atom_num)])) 
        fh.write("".join(["\n\t\tTime step: ", str(qDSs.timestep)])) 
        fh.write("".join(["\n\t\tDelta: ", str(qDSs.delta)])) 
        fh.write("".join(["\n\t\tAdditional Info: ", qDSs.description]))
        submission_closed = DyndbSubmission.objects.filter(pk=submission_id).values_list('is_closed',flat=True)
    return render(request,'dynadb/SUBMISSION_SUMMARY.html', { 'dynid': dyn_id, 'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id' : submission_id,'urls':urls,'fdbSubs':fdbSubs,'qMOL':qMOL,'labtypels':labtypels,'Types':Types,'imps':imps,'qCOMP':qCOMP,'int_ids':int_ids,'int_ids0':int_ids0,'p':p,'SType':SType,'TypeM':TypeM, 'ddown':ddown,'qDC':qDC, 'dctypel':dctypel, "lcompname":lcompname, 'lcompname':l_ord_mol, 'compl':compl, 'qDS':qDS, 'data':data, 'model_id':model_id, 'SUMMARY':True, 'urlsummary':summaryurl,'submission_closed':submission_closed})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def protein_summaryiew(request,submission_id):
#protein section
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).order_by('int_id')
    int_id=[]
    int_id0=[]
    alias=[]
    mseq=[]
    wseq=[]
    MUTations=[]
    sci_na_codel=[]
    qPROT=[]
    for l in qSub:
        sci_name=list(DyndbUniprotSpecies.objects.filter(id= l.protein_id.id_uniprot_species_id).values_list('scientific_name','code')[0])
        sci_na_code=("").join([sci_name[0]," (",sci_name[1],")"])
        sci_na_codel.append(sci_na_code)
        qprot=DyndbProtein.objects.filter(id=l.protein_id_id)[0]
        qPROT.append(qprot)
        int_id.append(l.int_id +1) 
        int_id0.append(l.int_id) 
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
            llsm=qSEQ
            mseq.append(llsm)
            qpCp=DyndbProteinCannonicalProtein.objects.filter(id_protein=l.protein_id).values_list('id_cannonical_proteins',flat=True)[0]
            llsw=DyndbProteinSequence.objects.filter(id_protein=qpCp).values_list('sequence',flat=True)[0]
            qPMut=DyndbProteinMutations.objects.filter(id_protein=l.protein_id)
            MUTations.append(qPMut)
        else:
            llsw=qSEQ
            mseq.append('')
            MUTations.append('')
        wseq.append(llsw) 
        qALIAS=DyndbOtherProteinNames.objects.filter(id_protein=l.protein_id)
        llo=("; ").join(qALIAS.values_list('other_names',flat=True))
        alias.append(llo) 
    return render(request,'dynadb/PROTEIN_SUMMARY.html', { 'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id' : submission_id, 'minisummary':True})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def molecule_summaryiew(request,submission_id):
#small molecule section
    qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).order_by('int_id').filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'))
    labtypels=[]
    print(qSub)  ######POR AQUI!!!! ORDENAR POR INT_ID LA QUERY qMOL!!! 
    int_ids=[]
    int_ids0=[]
    qCOMP=[]
    qMOL=[]
    imps=[]
    Types=[]
    urls=[]
    for l in qSub:
        urls.append(str(l.url).strip())
        labtypes=l.COMPOUND_TYPE[l.type]
        labtypels.append(labtypes) 
        if  not l.not_in_model:
            imps.append(True)
        else:
            imps.append(False)
        int_ids.append(l.int_id+1)
        int_ids0.append(l.int_id)
        typt=l.type
        Types.append(typt)
        qmol=DyndbMolecule.objects.filter(id=l.molecule_id.id)[0]
        qMOL.append(qmol)
        qCOMPtt=DyndbCompound.objects.filter(id=qmol.id_compound.id)[0] # VERIFICAR!!!!!!!!!!!!!!!!!!!
        qCOMP.append(qCOMPtt) 
    fdbSubs = dyndb_Submission_Molecule()
    return render(request,'dynadb/SMALL_MOLECULE_SUMMARY.html', { 'submission_id' : submission_id,'urls':urls,'fdbSubs':fdbSubs,'qMOL':qMOL,'labtypels':labtypels,'Types':Types,'imps':imps,'qCOMP':qCOMP,'int_ids':int_ids,'int_ids0':int_ids0, 'minisummary':True})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def model_summaryiew(request,submission_id):
#model section
    qModel=DyndbModel.objects.filter(dyndbsubmissionmodel=submission_id)
    print("qModel",qModel)
    p=qModel
    print("p ", p)
    Typeval=p.values()[0]['type']
    TypeM=p.model.MODEL_TYPE[Typeval][1]
    STypeval=p.values()[0]['source_type']
    SType=p.model.SOURCE_TYPE[STypeval][1]
    return render(request,'dynadb/MODEL_SUMMARY.html', { 'p':p,'SType':SType,'TypeM':TypeM, 'minisummary':True}   )

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def close_submission(request,submission_id):
    redirect_url = reverse('accounts:memberpage')
    if request.method == 'POST':
        try:
            validate_submission(submission_id)
        except SubmissionValidationError as e:
            return HttpResponse('Internal Server Error',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
        except Exception:
            return HttpResponse('Error while validating submission.',status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
        try:
            DyndbSubmission.objects.filter(pk=submission_id).update(is_closed=True)
        except Exception:
            return HttpResponse('Error while closing submission.',status=500,reason='Internal Server Error',content_type='text/plain; charset=UTF-8')
        return HttpResponse(redirect_url,content_type='text/plain; charset=UTF-8')
    elif request.method == 'GET':
        return HttpResponse('Method GET Not Allowed',status=405,reason='Method Not Allowed',content_type='text/plain; charset=UTF-8')

def validate_submission(submission_id):
    trajectory_max_files = 200
    if hasattr(settings,'TRAJECTORY_MAX_FILES'):
        trajectory_max_files = settings.trajectory_max_files
    if not DyndbSubmission.objects.filter(pk=submission_id).exists():
        raise SubmissionValidationError('Submission does not exists.')
    # check if dynamics exists and retrieve model ID
    qdyn = DyndbDynamics.objects.filter(submission_id=submission_id)
    qdyn = qdyn.values('pk','id_model')
    if len(qdyn) > 0:
        dyn_id = qdyn[0]['pk']
        model_id = qdyn[0]['id_model']
    else:
        raise SubmissionValidationError('Submission has no dynamics information.')
    if model_id is None:
        raise SubmissionValidationError('Submission has no complex structure information.')
    if not DyndbSubmissionModel.objects.filter(submission_id=submission_id,model_id=model_id).exists():
        raise ValueError('Submission model ID does not match dynamics model ID or does not exists.')
    # check the number of dynamics files
    coortype_int = type_inverse_search(DyndbFilesDynamics.file_types,searchkey='coor',case_sensitive=False,first_match=True)
    trajtype_int = type_inverse_search(DyndbFilesDynamics.file_types,searchkey='traj',case_sensitive=False,first_match=True)
    toptype_int = type_inverse_search(DyndbFilesDynamics.file_types,searchkey='top',case_sensitive=False,first_match=True)
    prmtype_int = type_inverse_search(DyndbFilesDynamics.file_types,searchkey='p(arm?|rm)',case_sensitive=False,\
    first_match=True,searchkey_is_regex=True)
    othertype_int = type_inverse_search(DyndbFilesDynamics.file_types,searchkey='other',case_sensitive=False,first_match=True)
    mandatory_types_int = {coortype_int,trajtype_int}
    qfilesdyn = DyndbFilesDynamics.objects.filter(id_dynamics=dyn_id)
    qfilesdyn = qfilesdyn.annotate(count=Count('type'))
    qfilesdyn = qfilesdyn.values('type','count')
    for filetype in qfilesdyn:
        filetype_int = filetype['type']
        count = filetype['count']
        if filetype_int in mandatory_types_int and count < 1:
            raise SubmissionValidationError('Dynamics has no %s file.' % (DyndbFilesDynamics.file_types[filetype_int].lower()))
        elif filetype_int == trajtype_int and count > trajectory_max_files:
            raise SubmissionValidationError('Dynamics has too many (%d) %s files. Max(%d)' % \
        (count,DyndbFilesDynamics.file_types[filetype_int].lower(),trajectory_max_files))
        elif count > 1:
            raise SubmissionValidationError('Dynamics has more than one %s file.' % \
        (DyndbFilesDynamics.file_types[filetype_int].lower()))
    # get molecules ID in submission
    sub_bulk_compound_types_dict = type_inverse_search(DyndbSubmissionMolecule.COMPOUND_TYPE,searchkey='bulk',\
    case_sensitive=False,first_match=False)
    sub_ligand_compound_types_dict = type_inverse_search(DyndbSubmissionMolecule.COMPOUND_TYPE,searchkey='lig',\
    case_sensitive=False,first_match=False)
    sub_bulk_compound_types_int = set(sub_bulk_compound_types_dict.values())
    sub_ligand_compound_types_int = set(sub_ligand_compound_types_dict.values())
    qsubmol = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    qsubmol = qsubmol.values('molecule_id','type', 'not_in_model')
    sub_bulk_mols = []
    sub_model_mols = []
    sub_ligand_mols = []
    sub_molecule_id_type = {}
    for molecule in qsubmol:
        moltype = molecule['type']
        molid = molecule['molecule_id']
        not_in_model = molecule['not_in_model']
        sub_molecule_id_type[molid] = moltype
        if moltype not in sub_bulk_compound_types_int and not not_in_model:
            sub_model_mols.append(molid)
            if moltype in sub_ligand_compound_types_int:
                sub_ligand_mols.append(molid)
        elif moltype in sub_bulk_compound_types_int and not_in_model:
            sub_bulk_mols.append(molid)
        else:
            raise ValueError('Error while determining if molecule ID: %d is in bulk.' % (molecule['molecule_id']))
    sub_bulk_mols = set(sub_bulk_mols)
    sub_model_mols = set(sub_model_mols)
    sub_ligand_mols = set(sub_ligand_mols)
    sub_bulk_mol_num = len(sub_bulk_mols)
    sub_model_mol_num = len(sub_model_mols)
    sub_ligand_mol_num = len(sub_ligand_mols)
    # check submission proteins
    qsubprot = DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    qsubprot = qsubprot.annotate(receptor_id=F('protein_id__receptor_id_protein'))
    qsubprot = qsubprot.values_list('protein_id','receptor_id','int_id')
    sub_prots_int_id_1 = dict()
    receptor_num = 0
    for protid, receptor_id, int_id in qsubprot:
        sub_prots_int_id_1[protid] = int_id + 1
        if receptor_id is not None:
            receptor_num =+ 1
    sub_prots = set(sub_prots_int_id_1.keys())
    sub_prot_num = len(sub_prots)
    if sub_prot_num == 0:
        raise SubmissionValidationError('Submission has no proteins.')
    if receptor_num == 0:
        raise SubmissionValidationError('Submission has no GPCRs.')
    # check if complex or apoform model type are correctly assigned acording to submission tables
    apo_int = type_inverse_search(DyndbModel.MODEL_TYPE,searchkey='apo',case_sensitive=False,first_match=True)
    complex_int = type_inverse_search(DyndbModel.MODEL_TYPE,searchkey='complex',case_sensitive=False,first_match=True)
    qmodel = DyndbModel.objects.filter(pk=model_id)
    qmodel = qmodel.values('type','id_protein','id_complex_molecule')
    modeltype = qmodel[0]['type']
    id_protein = qmodel[0]['id_protein']
    id_complex_mol = qmodel[0]['id_complex_molecule']
    if modeltype == apo_int and id_protein is not None and id_complex_mol is None:
        if sub_prot_num > 1:
            raise SubmissionValidationError('Submission has more than one protein, ' + \
            'but complex structure type is a protein apoform.')
        if qsubprot[0]['protein_id'] != id_protein:
            raise SubmissionValidationError('Submitted protein does not match with complex structure ' + \
            'protein apoform. Please, update your complex structure information.')
        if sub_ligand_mol_num > 1:
            raise SubmissionValidationError('Submission has molecules defined as ligands, ' + \
            'but complex structure type is a protein apoform.')
    elif modeltype == complex_int and id_protein is None and id_complex_mol is not None:
        if sub_prot_num == 1 and sub_model_mol_num == 0:
            raise SubmissionValidationError('Submission has only one protein and no ligands, ' + \
            'but complex structure type is a protein complex or a protein-ligand complex.')
    else:
        raise ValueError('Error while reading complex structure type.')
    #check complex_molecule
    if id_complex_mol is not None:
        qcomplexmol = DyndbComplexMolecule.objects.filter(pk=id_complex_mol)
        qcomplexmol =  qcomplexmol.values_list('id_complex_exp',flat=True)
        if len(qcomplexmol) > 0:
            id_complex_exp = qcomplexmol[0]
        else:
            raise ValueError('Error complex molecule with ID: %d does not exist.' % id_complex_mol)
        # check complex_protein
        qcomplex_prot = DyndbComplexProtein.objects.filter(id_complex_exp=id_complex_exp)
        complex_prots = set(qcomplex_prot.values_list('id_protein',flat=True))
        if sub_prots != complex_prots:
            raise SubmissionValidationError('Mismatch between declared proteins and proteins present ' + \
            'in the complex. Please, update your crystal structure information.')
        # check complex_molecule
        qcomplex_mol = DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_mol)
        qcomplex_mol = qcomplex_mol.annotate(id_compound=F('id_molecule__id_compound'))
        qcomplex_mol = qcomplex_mol.values('id_molecule','id_compound')
        complex_mols = set([row['id_molecule'] for row in qcomplex_mol])
        complex_mol_compounds = set([row['id_compound'] for row in qcomplex_mol])
        if sub_ligand_mols != complex_mols:
            raise SubmissionValidationError('Mismatch between declared ligand molecules and ligands present ' + \
            'in the complex. Please, update your crystal structure information.')
        # check complex_compound
        qcomplex_compound = DyndbComplexCompound.objects.filter(id_complex_exp=id_complex_exp)
        complex_compounds = set(qcomplex_compound.values_list('id_compound',flat=True))
        if complex_mol_compounds != complex_compounds:
            raise ValueError('Mismatch between complex molecule molecules and experimental complex compounds.')
    #check model_components vs submission tables
    qmodel_comp = DyndbModelComponents.objects.filter(id_model=model_id)
    qmodel_comp = qmodel_comp.values('id_molecule','type','resname')
    model_comp_resnames = {}
    for molecule in qmodel_comp:
        id_molecule = molecule['id_molecule']
        type_int = molecule['type']
        if smol_to_modelcomp_type[sub_molecule_id_type[id_molecule]] != type_int:
            raise SubmissionValidationError('Mismatch between declared molecule type and crystal ' + \
            'structure components molecule type. Please, update your complex structure information.')
        if id_molecule not in model_comp_resnames:
            model_comp_resnames[id_molecule] = set()
        model_comp_resnames[id_molecule].add(molecule['resname'])
    if sub_model_mols != model_comp_resnames.keys():
            raise SubmissionValidationError('Mismatch between declared crystal molecules and ' + \
            'crystal structure components. Please, update your complex structure information.')
    #check dynamics_components vs submission tables
    qdyn_comp = DyndbDynamicsComponents.objects.filter(id_dynamics=dyn_id)
    qdyn_comp = qdyn_comp.values('id_molecule','type','resname')
    dyn_comp_resnames = {}
    for molecule in qdyn_comp:
        id_molecule = molecule['id_molecule']
        type_int = molecule['type']
        if smol_to_dyncomp_type[sub_molecule_id_type[id_molecule]] != type_int:
            raise SubmissionValidationError('Mismatch between declared molecule type and dynamics ' + \
            'components molecule type. Please, update your dynamics information.')
        if id_molecule not in dyn_comp_resnames.keys():
            dyn_comp_resnames[id_molecule] = set()
        dyn_comp_resnames[id_molecule].add(molecule['resname'])
    dyn_comp_molids = set(dyn_comp_resnames.keys())
    model_comp_molids = set(model_comp_resnames.keys())
    if sub_model_mols.union(sub_bulk_mols) != dyn_comp_molids:
            raise SubmissionValidationError('Mismatch between declared molecules and dynamics components. ' + \
            'Please, update your dynamics information.')
    #check model_components vs check dynamics_components
    if not model_comp_molids.issubset(dyn_comp_molids):
                    raise SubmissionValidationError('Mismatch between crystal structure components and .' + \
            'dynamics components. Please, update your complex structure and/or your dynamics information.')
    for molid,resname_list in model_comp_resnames.items():
        if not resname_list.issubset(dyn_comp_resnames[molid]):
            raise SubmissionValidationError('Mismatch between crystal structure components residue names and ' + \
            'dynamics components residue names. Please, update your complex structure and/or your dynamics information.')
    #check model pdb file exists
    qmodelfile = DyndbFilesModel.objects.filter(id_model=model_id)
    if not qmodelfile.exists():
        raise SubmissionValidationError('Missing complex structure PDB file.' + \
        'Please, update your complex structure and/or your dynamics information.')
    #check min protein fragments
    qmodelres = DyndbModeledResidues.objects.filter(id_model=model_id)
    modeled_res_prot_ids = set(qmodelres.values_list('id_protein',flat=True))
    if not modeled_res_prot_ids.issubset(sub_prots):
                raise SubmissionValidationError('Modeled residues information contains fragments about ' + \
                'non-declared proteins. Please, update your complex structure information.')
    diff_prot = sub_prots.difference(modeled_res_prot_ids)
    if diff_prot != set():
        raise SubmissionValidationError('Modeled residues information missing for proteins #%s. ' + \
        'Please, update your complex structure information.' % ', #'.join([str(i) for i in diff_prot]))
    
def parse_submission_files_path(url_path=None,obj_folder=None,submission_folder=None,path=None,prefix=None):
    ''' Function to parse submission file URLs. 
    Full url is "[VIEW_URL]/obj_folder/submission_folder/path" 
    Returns (url_path,obj_folder,submission_folder,path,prefix,submission_id,object_type) or None
    if an invalid path is provided. '''
    if url_path is not None:
        if prefix is None:
            url_prefix = r''
        else:
            url_prefix = re.escape(prefix)
        repath = re.compile(url_prefix+r'/(?P<obj_folder>[^/\\]+)/(?P<submission_folder>[^/\\]+)(?:/(?P<path>.*))?$')
        m = repath.search(url_path)
        if m:
            obj_folder,submission_folder,path = m.groups()
        else:
            raise ValueError('Invalid path: "'+str(url_path)+'"')
    elements = [get_file_url_root(),obj_folder,submission_folder,path]
    if path is None:
        elements = elements[:-1]
    url_path = os.path.join(*elements)
    main_submission_dict = get_file_paths('',return_main_submission_dict = True)
    if obj_folder in main_submission_dict:
        prefix = main_submission_dict[obj_folder]['submission']
        object_type = main_submission_dict[obj_folder]['object_type']
        #check submission folder path for the second element and extract submission ID
        if submission_folder.find(prefix) == 0:
            submission_id = submission_folder.replace(prefix,"")
            if submission_id.isdigit():
                submission_id = int(submission_id)
                return (url_path,obj_folder,submission_folder,path,prefix,submission_id,object_type)
    return None

def url_normalize_path(url,query=False,params=False,fragment=False):
    up = urllib.parse.urlparse(url)
    q = ''
    p = ''
    f = ''
    if query:
        q = up.query
    if params:
        p = up.params
    if fragment:
        f = up.fragment
    return urllib.parse.urlunparse((up[0],up[1],os.path.normpath(up[2]),q,p,f))

def url_equal(url1,url2):
    nu1 = url_normalize_path(url1)
    nu2 = url_normalize_path(url2)
    return bool(nu1 == nu2) 

def serve_submission_files_no_login(request,obj_folder,submission_folder,path):
    filepath = file_url_to_file_path(request.path)
    return sendfile(request,filepath)

@login_required
def serve_submission_files(request,obj_folder,submission_folder,path):
    ''' Function to serve private files using django-sendfile module.
    Full url is "[VIEW_URL]/obj_folder/submission_folder/path" '''
    filepath = file_url_to_file_path(request.path)
    if not settings.QUERY_CHECK_PUBLISHED or is_allowed_directory(request.user,obj_folder=obj_folder,
    submission_folder=submission_folder,path=path,allow_submission_dir=True): 
        return sendfile(request,filepath)
    else: 
        parsed_url = parse_submission_files_path(obj_folder=obj_folder,submission_folder=submission_folder,
        path=path)
        if parsed_url:
            url_path,obj_folder,submission_folder,path,prefix,submission_id,object_type = parsed_url
            if obj_folder == "Molecule":
                q_non_published = DyndbSubmission.objects.filter(user_id=request.user,is_published=False,
                dyndbsubmissionmolecule__molecule_id__is_published=False)
                shared_molecules_url = q_non_published.values_list('dyndbsubmissionmolecule__molecule_id__'+\
                'dyndbfilesmolecule__id_files__url',flat=True)
                n_url_path = url_normalize_path(url_path)    
                for u in shared_molecules_url:
                    if n_url_path == url_normalize_path(u):
                        return sendfile(request,filepath)
    raise PermissionDenied

def is_allowed_directory(user,url_path=None,obj_folder=None,submission_folder=None,path=None,
    prefix=None,allow_submission_dir=False):
    parsed_url = parse_submission_files_path(url_path=url_path,obj_folder=obj_folder,
    submission_folder=submission_folder,path=path,prefix=prefix)
    if parsed_url:
        url_path,obj_folder,submission_folder,path,prefix,submission_id,object_type = parsed_url 
        #check user permissions
        if is_submission_owner(user,submission_id=submission_id):
            allowed_directory = get_file_paths(object_type,submission_id=submission_id,url=False)
            filepath = file_url_to_file_path(url_path)       
            if allow_submission_dir:
                allowed_directory = os.path.realpath(allowed_directory)
                filepath = os.path.realpath(filepath)
                if os.path.isdir(filepath) and allowed_directory == filepath:
                    return True
                return in_directory(filepath, allowed_directory)
    return False
    
def in_directory(file, directory):
    #make both absolute    
    directory = os.path.join(os.path.realpath(directory), '')
    file = os.path.realpath(file)
    #return true, if the common prefix of both is equal to directory
    #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return os.path.commonprefix([file, directory]) == directory

@csrf_exempt
def mdsrv_redirect(request,path):
    if hasattr(settings, 'MDSRV_REVERSE_PROXY'):
        if settings.MDSRV_REVERSE_PROXY == 'ALL' or settings.MDSRV_REVERSE_PROXY == 'POST' and request.method in {'POST','PUT'}:
            content_type = None
            path_segments = path.split('/')
            if path_segments[0] == 'dir':
                content_type = 'application/json'
            elif path_segments[0] == 'traj' and len(path_segments) > 2:
                if path_segments[1] == 'frame' or path_segments[1] == 'path':
                    content_type = 'application/octet-stream'
                elif path_segments[1] == 'numframes':
                    content_type = 'text/plain; charset=UTF-8'
            proxyview = ProxyView.as_view(upstream=settings.MDSRV_UPSTREAM)
            response = proxyview(request,request.path)
            if content_type is not None:
                response['Content-Type'] = content_type
            return response
    response = HttpResponse()
    response['Location'] = "/mdsrv_redirect/"+path+request.META['QUERY_STRING']
    response.status_code = 200
    # need to destroy get_host() to stop django
    # rewriting our location to include http, so that
    # mod_wsgi is able to do the internal redirect
    request.get_host = lambda: ''
    request.build_absolute_uri = lambda location: location
    return response

@csrf_exempt
@textonly_404_handler
@textonly_500_handler
def mdsrv_redirect_prelogin(request,path,path_dir):
    # path is None and path_dir=file_path if the requested file is in the public directory
    if path is None:
        url_path = path_dir
        return mdsrv_redirect(request,url_path)
    # path == file_path if the requested file is not in the public directory
    else:
        url_path = path
        if not settings.QUERY_CHECK_PUBLISHED:
            return mdsrv_redirect(request,url_path)
        # Do you allow to see unpublished files in GPCR VIEWER?
        allow_dir = True
        return mdsrv_redirect_login(request,url_path,allow_dir)

@login_required
def mdsrv_redirect_login(request,url_path,allow_dir):
    if not is_allowed_directory(request.user,url_path=request.path,prefix='_DB',allow_submission_dir=allow_dir):
        return HttpResponseForbidden("Forbidden (403).",content_type='text/plain; charset=UTF-8')
    return mdsrv_redirect(request,url_path)

def reset_permissions(request):
    try:
        from django.core.cache import cache
        cache.clear()
        import os
        os.system('find '+ settings.MEDIA_ROOT +' -type d -exec chmod 770 {} \;')
        os.system('find'+  settings.MEDIA_ROOT +' -type f -exec chmod 660 {} \;')
    except Exception as e:
        print(str(e))
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
    return HttpResponse('Done!',content_type='text/plain; charset=UTF-8')
    
from django.conf import settings
from modules.dynadb.views import join_path

def get_precomputed_file_path(objecttype,comp_type=None,url=False):
    precomputed_folder = "Precomputed"
    if url:
        root = get_file_url_root()
    else:
        root = settings.MEDIA_ROOT
    filepathdict = dict()
    #define objects
    filepathdict['flare_plot'] = dict()
    #define main folders
    filepathdict['flare_plot']['main'] = "flare_plot"
    filepathdict['flare_plot']['type'] = dict()
    #define computation type = folder
    filepathdict['flare_plot']['type']['hbonds'] = "hbonds"
    filepathdict['flare_plot']['type']['sb'] = 'sb'
    filepathdict['flare_plot']['type']['pc'] = 'pc'
    filepathdict['flare_plot']['type']['ps'] = 'ps'
    filepathdict['flare_plot']['type']['ts'] = 'ts'
    filepathdict['flare_plot']['type']['vdw'] = 'vdw'
    filepathdict['flare_plot']['type']['hb'] = 'hb'
    filepathdict['flare_plot']['type']['wb'] = 'wb'
    filepathdict['flare_plot']['type']['wb2'] = 'wb2'
    filepathdict['flare_plot']['type']['hp'] = 'hp'
    path1 = join_path(root,precomputed_folder,filepathdict[objecttype]['main'],relative=False,url=url)
    path = join_path(path1,filepathdict[objecttype]['type'][comp_type],relative=False,url=url) 
    if url:
        path += '/'
    else:
        path += os.path.sep
    return path

def search_in_treeData(classifli,myslug):#gpcrclassif_fams,myfam_slug
    namefound=False
    for nlevel in range(0,len(classifli)):
        thisslug= classifli[nlevel]["slug"]
        if myslug==thisslug:
            namefound=True
            return(nlevel)
    return(False)

def datasets(request):
    consideredgpcrs_path= settings.MEDIA_ROOT +'Precomputed/Summary_info/considered_gpcrs.data'
    with open(consideredgpcrs_path, 'rb') as filehandle:  
        gpcrclassif = pickle.load(filehandle)
    others_gpcrclassif=copy.deepcopy(gpcrclassif)
    dynall=DyndbDynamics.objects.filter(is_published=True) #all().exclude(id=5) #I think dyn 5 is wrong
    dynprot=dynall.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
    dynprot=dynprot.annotate(fam_slug2=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
    dynprot=dynprot.annotate(dyn_id=F('id'))
    dynprot = dynprot.annotate(pdb_namechain=F("id_model__pdbid"))
    dynprot=dynprot.annotate(modelname=F('id_model__name'))
    dynprot=dynprot.annotate(modeltype=F('id_model__type'))
    dynprot=dynprot.annotate(user_id=F('submission_id__user_id__id'))
    dynprot=dynprot.annotate(user_fname=F('submission_id__user_id__first_name'))
    dynprot=dynprot.annotate(user_lname=F('submission_id__user_id__last_name'))
    dynprot=dynprot.annotate(user_institution=F('submission_id__user_id__institution'))
    dynall_values=dynprot.values("dyn_id","fam_slug","fam_slug2","pdb_namechain","modelname","modeltype","user_id","user_fname","user_lname","user_institution")
    dyn_dict={}
    for dyn in dynall_values:
        dyn_id=dyn["dyn_id"]
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
        is_hm=False
        dyn_id=dyn["dyn_id"]
        pdbid=dyn["pdb_namechain"].split(".")[0]
        if pdbid:
            if pdbid == "HOMO":
                is_hm=True
        prot_slug=dyn["fam_slug"]
        if not prot_slug:
            prot_slug=dyn["fam_slug2"]
        if prot_slug:
            fam_slug=prot_slug[:-8]
            subtype_slug=prot_slug[:-4]
            class_slug=prot_slug[:3]
            dyn_dict[dyn_id]["fam_slug"]=fam_slug
            dyn_dict[dyn_id]["subtype_slug"]=subtype_slug
            dyn_dict[dyn_id]["class_slug"]=class_slug
            dyn_dict[dyn_id]["prot_slug"]=prot_slug
        dyn_dict[dyn_id]["is_hm"]=is_hm
        dyn_dict[dyn_id]["pdbid"]=pdbid
        dyn_dict[dyn_id]["modelname"]=dyn["modelname"]
        if dyn["modeltype"]==0:
            modeltype="Apoform"
        else:
            modeltype="Complex"
        dyn_dict[dyn_id]["modeltype"]=modeltype
        user_id=dyn["user_id"]
        is_gpcrmd=False
        if int(dyn_id) in range(4,11):
            author="GPCR drug discovery group (Pompeu Fabra University)"
        elif user_id in {1, 3, 5, 12, 14}:
            is_gpcrmd=True
            author="GPCRmd community"
        else:
            author ="%s %s, %s" % (dyn["user_fname"],dyn["user_lname"],dyn["user_institution"])
        dyn_dict[dyn_id]["is_gpcrmd"]=is_gpcrmd
        dyn_dict[dyn_id]["author"]=author
        
    # Counters for the statistics  
    data_gpcrmdcom = 0 
    data_indv = 0
    for dyn_id,dyndata in dyn_dict.items():
        context={}
        myclass_slug=dyndata["class_slug"]
        myfam_slug=dyndata["fam_slug"]
        mysubtype_slug=dyndata["subtype_slug"]
        myprot_slug=dyndata["prot_slug"]
        modelname=dyndata["modelname"]
        modeltype=dyndata["modeltype"]
        author=dyndata["author"]
        mymodelname="<b>%s:</b> %s" %(modeltype,modelname)
        pdbid=dyndata["pdbid"]
        nclass=search_in_treeData(gpcrclassif,myclass_slug)
        if nclass is False:
            continue
        gpcrclassif_fams=gpcrclassif[nclass]["children"]
        nfam=search_in_treeData(gpcrclassif_fams,myfam_slug)
        if nfam is False:
            continue
        gpcrclassif_sf=gpcrclassif_fams[nfam]["children"]
        nsf=search_in_treeData(gpcrclassif_sf,mysubtype_slug)
        if nsf is False:
            continue
        gpcrclassif_prot=gpcrclassif_sf[nsf]["children"]
        npr=search_in_treeData(gpcrclassif_prot,myprot_slug)
        if npr is False:
            continue
        if dyndata["is_gpcrmd"]:
            gpcrpdbdict=gpcrclassif_prot[npr]["children"]
            if pdbid not in gpcrpdbdict:
                gpcrpdbdict[pdbid]=[]
            gpcrpdbdict[pdbid].append((dyn_id,mymodelname))
            gpcrclassif[nclass]["has_sim"]=True
            gpcrclassif_fams[nfam]["has_sim"]=True
            gpcrclassif_sf[nsf]["has_sim"]=True
            gpcrclassif_prot[npr]["has_sim"]=True
            data_gpcrmdcom += 1
        else:
            o_gpcrclassif_fams=others_gpcrclassif[nclass]["children"]
            o_gpcrclassif_sf=o_gpcrclassif_fams[nfam]["children"]
            o_gpcrclassif_prot=o_gpcrclassif_sf[nsf]["children"]
            o_gpcrpdbdict=o_gpcrclassif_prot[npr]["children"]
            if pdbid not in o_gpcrpdbdict:
                o_gpcrpdbdict[pdbid]=[]
            o_gpcrpdbdict[pdbid].append((dyn_id,mymodelname,author))
            o_gpcrpdbdict[pdbid]=sorted(o_gpcrpdbdict[pdbid], key=lambda x: x[1])
            others_gpcrclassif[nclass]["has_sim"]=True
            o_gpcrclassif_fams[nfam]["has_sim"]=True
            o_gpcrclassif_sf[nsf]["has_sim"]=True
            o_gpcrclassif_prot[npr]["has_sim"]=True   
            data_indv += 1
         
    context["gpcrclassif"]= gpcrclassif
    context["others_gpcrclassif"]=others_gpcrclassif
    gpcrmdtree_path= settings.MEDIA_ROOT+"Precomputed/Summary_info/gpcrmdtree.data"
    with open(gpcrmdtree_path, 'rb') as filehandle:  
        tree_data = pickle.load(filehandle)
    context['tree_data']=json.dumps(tree_data)
    #print(json.dumps(tree_data))
    # Get contribution statistics on GPCRmd
    stats_dataset= [["Contributor", "Num"],
                    ["GPCRmd community", data_gpcrmdcom],
                    ["Individual", data_indv]
                    ]
    context["stats_dataset"]=json.dumps(stats_dataset)
    context["total_stats_dataset"]=data_gpcrmdcom + data_indv
    return render(request, 'dynadb/datasets.html', context)

def searchtable_data(dynobj,nongpcr=True):
    dynprot = dynobj.annotate(dyn_id=F('id'))
    dynprot = dynprot.annotate(pdb_namechain=F("id_model__pdbid"))
    dynprot = dynprot.annotate(dyncomp_resname=F("dyndbdynamicscomponents__resname"))
    dynprot = dynprot.annotate(dyncomp_type=F("dyndbdynamicscomponents__type"))
    dynprot = dynprot.annotate(dyncomp_id=F("dyndbdynamicscomponents__id_molecule_id"))
    dynprot = dynprot.annotate(comp_name=F("id_model__dyndbmodelcomponents__id_molecule__id_compound__name"))
    dynprot = dynprot.annotate(molecule_id=F("id_model__dyndbmodelcomponents__id_molecule_id"))
    dynprot = dynprot.annotate(comp_type=F("id_model__dyndbmodelcomponents__type"))
    dynprot=dynprot.annotate(mysoftware=F('software'))
    dynprot=dynprot.annotate(software_version=F('sversion'))
    dynprot=dynprot.annotate(forcefield=F('ff'))
    dynprot=dynprot.annotate(forcefield_version=F('ffversion'))
    dynprot=dynprot.annotate(uniprot=F('id_model__id_protein__uniprotkbac'))
    dynprot=dynprot.annotate(uniprot2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__uniprotkbac'))
    dynprot=dynprot.annotate(protname=F('id_model__id_protein__name'))
    dynprot=dynprot.annotate(protname2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__name'))
    dynprot=dynprot.annotate(protid=F('id_model__id_protein_id'))
    dynprot=dynprot.annotate(protid2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein_id'))
    dynprot=dynprot.annotate(species=F('id_model__id_protein__id_uniprot_species__scientific_name'))
    dynprot=dynprot.annotate(species2=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__id_uniprot_species__scientific_name'))
    dynprot=dynprot.annotate(fam_slug=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family_id__slug'))
    dynprot=dynprot.annotate(fam_slug2=F('id_model__id_protein__receptor_id_protein__family_id__slug'))
    dynprot=dynprot.annotate(fam_name=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family__parent__name'))
    dynprot=dynprot.annotate(fam_name2=F('id_model__id_protein__receptor_id_protein__family__parent__name'))
    dynprot=dynprot.annotate(class_name=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__family__parent__parent__parent__name'))
    dynprot=dynprot.annotate(class_name2=F('id_model__id_protein__receptor_id_protein__family__parent__parent__parent__name'))
    dynprot=dynprot.annotate(uprot_entry=F('id_model__id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__receptor_id_protein__entry_name'))
    dynprot=dynprot.annotate(uprot_entry2=F('id_model__id_protein__receptor_id_protein__entry_name'))
    dynprot=dynprot.annotate(modelname=F('id_model__name'))
    dynprot=dynprot.annotate(modeltype=F('id_model__type'))
    dynprot=dynprot.annotate(user_id=F('submission_id__user_id__id'))
    dynprot=dynprot.annotate(is_gpcrmd_community=F('submission_id__is_gpcrmd_community'))
    dynprot=dynprot.annotate(user_fname=F('submission_id__user_id__first_name'))
    dynprot=dynprot.annotate(user_lname=F('submission_id__user_id__last_name'))
    dynprot=dynprot.annotate(user_institution=F('submission_id__user_id__institution'))
    dynall_values=dynprot.values("dyn_id","fam_slug","fam_slug2","modelname","modeltype","user_id","user_fname","user_lname","is_gpcrmd_community","user_institution","uniprot","uniprot2","protname","protname2","species","species2","mysoftware","software_version","forcefield","forcefield_version","pdb_namechain","comp_name","dyncomp_resname","comp_type","fam_name","fam_name2","class_name","class_name2","protid","protid2","molecule_id","atom_num","dyncomp_type","dyncomp_id","uprot_entry","uprot_entry2")
    dyn_dict = {}
    for dyn in dynall_values:
        dyn_id=dyn["dyn_id"]
        if dyn_id not in dyn_dict:
            dyn_dict[dyn_id]={}
            dyn_dict[dyn_id]["dyn_id"]=dyn_id
            dyn_dict[dyn_id]["lig_li"]=set()
            dyn_dict[dyn_id]["uniprot"]=set()
            dyn_dict[dyn_id]["uprot_entry"]=set()
            dyn_dict[dyn_id]["memb_comp"]=set()
            dyn_dict[dyn_id]["simtime"]=0
        dyn_dict[dyn_id]["atom_num"]=dyn["atom_num"]
        pdb_namechain=dyn["pdb_namechain"]
        is_hm=False
        if pdb_namechain=="HOMO":
            pdb_namechain="Homology model"
            is_hm=True
        else:
            pdbid=pdb_namechain.split(".")[0]
            dyn_dict[dyn_id]["pdbid"]=pdbid
            dyn_dict[dyn_id]["state"]=pdb_state.get(pdbid)
        dyn_dict[dyn_id]["pdb_namechain"]=pdb_namechain
        dyn_dict[dyn_id]["is_hm"]=is_hm
        mol_id=dyn["molecule_id"]
        if dyn["comp_type"]==1:
            molname=dyn["comp_name"].capitalize()
            dyn_dict[dyn_id]["lig_li"].add((molname,mol_id,False))
        if dyn["dyncomp_type"]==2:
            dyn_dict[dyn_id]["memb_comp"].add((dyn["dyncomp_resname"],dyn["dyncomp_id"]))
        dyn_dict[dyn_id]["software"]=dyn["mysoftware"] + " "+dyn["software_version"]
        dyn_dict[dyn_id]["forcefield"]=dyn["forcefield"]+" "+dyn["forcefield_version"]
        up=dyn["uniprot"]
        if not up:
            up=dyn["uniprot2"]
        if up:
            dyn_dict[dyn_id]["uniprot"].add(up)
        prot_name=dyn["protname"] or dyn["protname2"]
        prot_id=dyn["protid"] or dyn["protid2"]
        if prot_name:
            prot_name=prot_name.capitalize()
            dyn_dict[dyn_id]["prot_name"]=prot_name
            dyn_dict[dyn_id]["prot_id"]=prot_id
        uprot_entry=dyn["uprot_entry"] or dyn["uprot_entry2"]
        if uprot_entry:
            dyn_dict[dyn_id]["uprot_entry"].add(uprot_entry)
        species=dyn["species"]
        if not species:
            species=dyn["species2"]
        if species:
            dyn_dict[dyn_id]["species"]=species
        prot_slug=dyn["fam_slug"]
        if not prot_slug:
            prot_slug=dyn["fam_slug2"]
        if prot_slug:
            dyn_dict[dyn_id]["prot_slug"]=prot_slug
        else:#If it doesn't have a slug it's not a GPCR, it's a prot ligand
            dyn_dict[dyn_id]["lig_li"].add((prot_name,prot_id,True))
        dyn_dict[dyn_id]["fam_name"]=dyn["fam_name"] or dyn["fam_name2"]
        class_name=dyn["class_name"] or dyn["class_name2"]
        if class_name:
            dyn_dict[dyn_id]["class_name"]= class_name.split(" ")[1]
        dyn_dict[dyn_id]["modelname"]=dyn["modelname"]
        if dyn["modeltype"]==0:
            modeltype="Apoform"
        else:
            modeltype="Complex"
        dyn_dict[dyn_id]["modeltype"]=modeltype
        user_id=dyn["user_id"]
        if dyn['is_gpcrmd_community']:
            author="GPCRmd community"
        else:
            author ="%s %s, %s" % (dyn["user_fname"],dyn["user_lname"],dyn["user_institution"])
        dyn_dict[dyn_id]["author"]=author
    dynfiledata = dynobj.annotate(dyn_id=F('id'))
    dynfiledata = dynfiledata.annotate(file_id=F('dyndbfilesdynamics__id_files__id'))
    dynfiledata = dynfiledata.annotate(framenum=F('dyndbfilesdynamics__framenum'))
    dynfiledata = dynfiledata.annotate(file_is_traj=F('dyndbfilesdynamics__id_files__id_file_types__is_trajectory'))
    dynfiledata = dynfiledata.values("dyn_id","framenum","file_id","file_is_traj","delta")
    for dyn in dynfiledata:
        dyn_id=dyn["dyn_id"]
        if dyn["file_is_traj"]:
            dyn_dict[dyn_id]["simtime"]+=dyn["framenum"]*dyn["delta"]/1000
    for dyn_id,dyn_data in dyn_dict.items():
        dyn_data["simtime"]="%.2f" % dyn_data["simtime"]
    ########## non-GPCR
    dynNG_dict={}
    if nongpcr:
        dynNGobj=DyndbNonGPCRDynamics.objects.all()
        dynNGf = dynNGobj.annotate(lig_resname=F('id_nongpcr_ligand__resname'))
        dynNGf = dynNGf.annotate(lig_name=F('id_nongpcr_ligand__name'))
        dynNG_values=dynNGf.values("id",  "uniprotkbac", "pdbid", "software", "sversion", "prot_name", "model_type", "ff", "ffversion", "atom_num", "membrane", "species_scientific_name", "dyn_name", "accum_sim_time", "lig_resname", "lig_name","up_entry_name","author_name","author_institution")
        for dynNG in dynNG_values:
            dynNG_id=dynNG["id"]
            if dynNG_id not in dynNG_dict:
                dynNG_dict[dynNG_id]={}
                dynNG_dict[dynNG_id]["dyn_id"]=dynNG_id
                dynNG_dict[dynNG_id]["not_GPCR"]=True
            dynNG_dict[dynNG_id]["atom_num"]=dynNG.get("atom_num") if dynNG.get("atom_num") else ""
            author_name=dynNG.get("author_name") if dynNG.get("author_name") else ""
            author_inst=dynNG.get("author_institution") if dynNG.get("author_institution") else ""
            dynNG_dict[dynNG_id]["author"]=", ".join([author_name,author_inst])
            dynNG_dict[dynNG_id]["uniprot"]={dynNG.get("uniprotkbac","")}
            pdbid=dynNG.get("pdbid","")
            dynNG_dict[dynNG_id]["pdb_namechain"]=pdbid
            dynNG_dict[dynNG_id]["pdbid"]=pdbid
            dynNG_dict[dynNG_id]["software"]="%s %s" % (dynNG.get("software",""),dynNG.get("sversion",""))
            dynNG_dict[dynNG_id]["forcefield"]="%s %s" % (dynNG.get("ff",""),dynNG.get("ffversion",""))
            dynNG_dict[dynNG_id]["prot_name"]=dynNG.get("prot_name","")
            dynNG_dict[dynNG_id]["uprot_entry"]={dynNG.get("up_entry_name","")}
            model_type_val=dynNG.get("model_type")
            if model_type_val==0:
                model_type="Apoform"
            else:
                model_type="Complex"
            dynNG_dict[dynNG_id]["modeltype"]=model_type
            dynNG_dict[dynNG_id]["memb_comp"]=dynNG.get("membrane") if dynNG.get("membrane") else ""
            dynNG_dict[dynNG_id]["species"]=dynNG.get("species_scientific_name","").split(" (")[0].strip()
            dynNG_dict[dynNG_id]["lig_li"]={dynNG.get("lig_name","")}
            dynNG_dict[dynNG_id]["simtime"]=dynNG.get("accum_sim_time","")
            dynNG_dict[dynNG_id]["modelname"]=dynNG.get("dyn_name","")
    tabledata=sorted(dyn_dict.values(),key=lambda x:x.get("prot_slug","zzz"))
    if nongpcr:
        tabledata+=sorted(dynNG_dict.values(),key=lambda x:x.get("prot_name","zzz"))
    return tabledata

def table(request):
    dynobj=DyndbDynamics.objects.filter(is_published=True)
    context={}
    context["tabledata"]=searchtable_data(dynobj)
    return render(request, 'dynadb/table.html', context)

def table_reduced(request):
    dynobj=DyndbDynamics.objects.filter(is_published=True)
    context={}
    context["tabledata"]=searchtable_data(dynobj)
    return render(request, 'dynadb/table_reduced.html', context)

#Link to report page
#Description (?)
#Sodium (?)
def dyns_in_ref(request, ref_id):
    dynobj=DyndbDynamics.objects.filter(dyndbreferencesdynamics__id_references=ref_id)
    context={}
    context["tabledata"]=searchtable_data(dynobj,None)
    refobj=DyndbReferences.objects.get(id=ref_id)
    context["reference"]={'doi':refobj.doi,'title':refobj.title,'authors':refobj.authors,'url':refobj.url,'journal':refobj.journal_press,'issue':refobj.issue,'pub_year':refobj.pub_year,'volume':refobj.volume}
    return render(request, 'dynadb/dyns_in_ref.html', context)

def close__submission(request, submission_id):
    DS = DyndbSubmission.objects.filter(pk=submission_id)
    DS.update(is_closed = True)
    return HttpResponse('')

###################
## David's new form
###################

@login_required
def delete_submission(request, submission_id):
    """
    Delete submission entry
    """
    # Return if the to-delete submission id was not created by this user
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    DS = DyndbSubmission.objects.filter(id=submission_id, user_id=def_user)
    # Take all of the tables that we plan to eliminate
    # If this submission actually exists, start taking tables
    if len(DS):
        ds = DS[0]
        DSM = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
        DSP = DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
        DSMod = DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        DSDF = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id)
        DD = DyndbDynamics.objects.filter(submission_id=submission_id)
        DDC = DyndbDynamicsComponents.objects.filter(id_dynamics__submission_id=submission_id)
        DFM = DyndbFilesModel.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id)
        DFD = DyndbFilesDynamics.objects.filter(id_dynamics__submission_id=submission_id)
        DF = DyndbFiles.objects.filter(dyndbsubmissiondynamicsfiles__submission_id=submission_id)
        # What do we do with DyndbModel, DyndbProtein and DyndbMolecule, and their creation_submission_id
        # First delete all files of this dynamic
        for df in DF:
            filepath = df.filepath
            if os.path.exists(settings.MEDIA_ROOT + filepath):
                os.remove(settings.MEDIA_ROOT + filepath)
        # Now change any creation_submission_id pointing to the submission_id we want to delete
        DP = DyndbProtein.objects.filter(protein_creation_submission_id=submission_id)
        DP.update(protein_creation_submission_id=None)
        DM = DyndbModel.objects.filter(model_creation_submission_id=submission_id)
        DM.update(model_creation_submission_id=None)
        DMol = DyndbMolecule.objects.filter(molecule_creation_submission_id=submission_id)
        DMol.update(molecule_creation_submission_id=None)
        # Finally, it is time to remove tables
        for table in list(itertools.chain(DSDF, DFD, DFM, DF, DDC, DSMod, DSP, DSM, DD, DS)):
            table.delete()
    return HttpResponse('')

@login_required
def step0(request):
    """
    Create a new submission entry
    """
    submission_dict = {
        'user_id' : request.user.id
    }
    ds = dyndb_Submission(submission_dict)
    print(ds.errors, submission_dict)
    Ds = ds.save()
    submission_id = Ds.id
    # Redirect to step 1
    return step1(request, submission_id)

def check_submission_status(submission_id):
    """
    For this submission_id, check how many of the submission form steps have been performed
    """
    last_step_done = '1'
    DD=DyndbDynamics.objects.filter(submission_id=submission_id)
    if len(DD):
        last_step_done = '2'
    DSMol=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    if len(DSMol):
        last_step_done = '3'
    DSP=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    if len(DSP):
        last_step_done = '4'
    DFD = DyndbFilesDynamics.objects.filter(type=2, dyndbsubmissiondynamicsfiles__submission_id=submission_id)
    if len(DFD):
        last_step_done = '5'
    return last_step_done


###### STEP 1: System general information
def model_file_table (dname, MFpk, initFiles, submission_id): #d_fmolec_t, dictext_id
    """
    Add model PDB files into the database
    """
    fdbF={}
    fdbFobj={}
    #####  
    ft=DyndbFileTypes.objects.all()
    dict_ext_id={}
    for l in ft:
        dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
    ##############
    for key,val  in dname.items():
        fext="".join(val['path'].split(".")[1:])
        initFiles['id_file_types']=dict_ext_id[fext]
        initFiles['url']=val['url']
        initFiles['filename']="".join(val['path'].split("/")[-1])
        initFiles['filepath']=val['path']
        initFiles['description']="pdb crystal-derived assembly coordinates"
        fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
        dicfmod={}
        fdbFM={}
        if fdbF[key].is_valid():
            fdbFobj[key]=fdbF[key].save()
            dicfmod['id_model']=MFpk
            dicfmod['id_files']=fdbFobj[key].pk
        else:
            prev_entryFile=DyndbFiles.objects.filter(dyndbfilesmodel__id_model__dyndbsubmissionmodel__submission_id=submission_id)
            dicfmod['id_files']=prev_entryFile.values_list('id',flat=True)[0]
            dicfmod['id_model']=MFpk
            prev_entryFile.update(update_timestamp=timezone.now(),last_update_by_dbengine=initFiles['created_by_dbengine'],filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])        
        fdbFM[key]=dyndb_Files_Model(dicfmod)
        if fdbFM[key].is_valid():
            fdbFM[key].save()
        else:
            prev_entryFileM=DyndbFilesModel.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id)
            prev_entryFileM.update(id_model=dicfmod['id_model'],id_files=dicfmod['id_files'])               

def save_pdbfile(pdbfilekey, submission_id, uploadedfile, pdbfilepath=False, pdbfileurl=False, pdbname=False):
    """
    Save a "model" or "Dynamics" (the two possible values for pdbfilekey) PDB file into our server. Return URL and internal path to saved file
    """
    # Create pahts and url inside the server for our newly created PDB file
    submission_path = get_file_paths(pdbfilekey, url=False,submission_id=submission_id)
    os.makedirs(submission_path,exist_ok=True)
    submission_url = get_file_paths(pdbfilekey, url=True,submission_id=submission_id)
    # Create new on-redundant filename and fileurl, if none submitted to function
    if not (pdbfilepath and pdbfileurl and pdbname):
        pdbname = get_file_name_submission(pdbfilekey,submission_id,0,ext="pdb",forceext=False,subtype="pdb")
        pdbfilepath =  os.path.join(submission_path,pdbname)
        pdbfileurl = os.path.join(submission_url,pdbname)
    # Otherwise remove existing file so as to save new one:
    else:
        if os.path.isfile(settings.MEDIA_ROOT[:-1] + pdbfilepath):
            os.remove(settings.MEDIA_ROOT[:-1] + pdbfilepath)
    # Try to save the file inside the server
    try:
        # pdbfilepath =  os.path.join(submission_path,pdbname)
        save_uploadedfile(pdbfilepath,uploadedfile)
    except Exception as e:
        print("ERROR!!!")
        print(e)
        if os.path.isfile(settings.MEDIA_ROOT[:-1] + pdbfilepath):
            os.remove(settings.MEDIA_ROOT[:-1] + pdbfilepath)
        response = HttpResponseServerError('Cannot save uploaded file.',content_type='text/plain; charset=UTF-8')
    finally:
        uploadedfile.close()
    return (pdbfilepath, pdbfileurl, pdbname)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed    
def step1(request, submission_id):
    """
    Step1 of the new form: introduce General data of the system, including technical aspects of the simulation and of PDBids and name of the simulated system 
    Britta Zetterström
    """
    fdbMF = dyndb_Model()
    context = { 
        'fdbMF' : fdbMF,
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
     }
    # Check if this form page has previously been filled. If so, take its values and put them in the form 
    ds = DyndbSubmission.objects.get(pk=submission_id)
    context['is_gpcrcom'] = ds.is_gpcrmd_community
    DSM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    if len(DSM)>0: 
        model_id=DSM.values_list('model_id',flat=True)[0]
        DD=DyndbDynamics.objects.filter(submission_id=submission_id)[0]
        DM=DyndbModel.objects.filter(id=model_id)[0]
        context['model_id'] = model_id
        # Model information from previous submission (if any)
        if DM:
            context['name'] = DM.name
            context['type'] = DM.MODEL_TYPE[DM.type]
            context['pdbid'] = DM.pdbid
            context['description'] = DM.description
            context['source'] = DM.SOURCE_TYPE[DM.source_type]
        # Dynamics information from previous submission (if any)
        if DD:
            context['method'] = (DD.id_dynamics_methods.id, DD.id_dynamics_methods.type_name)
            context['software'] = DD.software
            context['sversion'] = DD.sversion
            context['ff'] = DD.ff
            context['ffversion'] = DD.ffversion
            context['additional'] = DD.description
            context['assay'] = (DD.id_assay_types.id, DD.id_assay_types.type_name)
            context['membrane'] = (DD.id_dynamics_membrane_types.id, DD.id_dynamics_membrane_types.type_name)
            context['solvent'] = (DD.id_dynamics_solvent_types.id, DD.id_dynamics_solvent_types.type_name)
            context['timestep'] = DD.timestep
            context['delta'] = DD.delta
    # Get list of method, membrane, solvent and assay types
    context['qDMT'] =DyndbDynamicsMembraneTypes.objects.all().order_by('id')
    context['qDST'] =DyndbDynamicsSolventTypes.objects.all().order_by('id')
    context['qDMeth'] =DyndbDynamicsMethods.objects.all().order_by('id')
    context['qAT'] =DyndbAssayTypes.objects.all().order_by('id')
    context['step'] = '1'
    # Check which of the form's step has this submission undergo
    context['max_step'] = check_submission_status(submission_id)
    
    #Repeated step?
    context['repeated_step'] = False

    return render(request, 'dynadb/step1.html', context)

def count_and_save_atoms(dyn_id, submission_id):
    """
    Count numer of atoms in the coordinates associated with this dynamics
    """        
    dd = DyndbDynamics.objects.get(pk=dyn_id)
    dsdf = DyndbSubmissionDynamicsFiles.objects.get(submission_id=submission_id,type=0,is_deleted=False)    
    pdbpath = dsdf.filepath
    if not settings.MEDIA_ROOT[:-1] in pdbpath: 
        pdbpath = settings.MEDIA_ROOT[:-1] + pdbpath
    pdbdyn = md.load_pdb(pdbpath, standard_names=False).top
    natoms = pdbdyn.n_atoms
    dd.atom_num = natoms
    dd.save()

def save_dyndbfile(filename, filextension, filepath, url, creation_fields, update_fields):
    # Create or update a DyndbFile entry
    dft = DyndbFileTypes.objects.get(extension=filextension)
    data = {
        'filename' : filename,
        'id_file_types' : dft.id,
        'filepath' : filepath.replace(settings.MEDIA_ROOT[:-1],""),
        'url' : url
    }
    #Update or create depnding on the files existance
    DF = DyndbFiles.objects.filter(filename=filename)
    if len(DF):
        data.update(update_fields)
        DF.update(**data)
        dfd = DF[0]
    else:
        data.update(creation_fields)
        Dfd = dyndb_Files(data)
        dfd = Dfd.save()
    return(dfd.id)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def step1_submit(request, submission_id):
    """
    Introduce in the database the data obtained from the form
    """
    # Some initial variables, including users and timestamps
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    creation_fields={
               'creation_timestamp':timezone.now(),
               'created_by_dbengine':def_user_dbengine, 
               'created_by':def_user,
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    update_fields = {
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    initFiles={'update_timestamp':timezone.now(),
        'creation_timestamp':timezone.now() ,
        'submission_id':None ,
        'created_by_dbengine':def_user_dbengine,
        'last_update_by_dbengine':def_user_dbengine,
        'created_by':def_user,
        'last_update_by':def_user  
    }
    # Get Post info            
    dictpost=request.POST
    dictfiles=request.FILES
    # Dynamics and model dictionaries to convert in database tables
    dynamics_dict = {
        'id_model' : None,
        'id_dynamics_methods' : dictpost['id_dynamics_methods'],
        'software' : dictpost['software'],
        'sversion' : dictpost['sversion'],
        'ff' : dictpost['ff'],
        'ffversion' : dictpost['ffversion'],
        'id_assay_types' : dictpost['id_assay_types'],
        'description' : dictpost['add_info'],
        'id_dynamics_membrane_types' : dictpost['id_dynamics_membrane_types'],
        'id_dynamics_solvent_types' : dictpost['id_dynamics_solvent_types'],
        'timestep' : dictpost['timestep'],
        'delta' : dictpost['delta'],
        'submission_id' : submission_id,
    }
    models_dict = {
            'name' : dictpost['name'],
            'type' : dictpost['type'],
            'source_type' : dictpost['source_type'],
            'pdbid' : dictpost['pdbid'],
            'description' : dictpost['description'],
            'template_id_model' : None,
            'model_creation_submission_id':submission_id,
    }
    submodels_dict = {
            'model_id': None,
            'submission_id':submission_id
    }
    ##### Check if this submission already exists
    ds = DyndbSubmission.objects.get(pk=submission_id)
    DM=DyndbModel.objects.filter(model_creation_submission_id=submission_id)
    DD = DyndbDynamics.objects.filter(submission_id=submission_id)
    DSM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    # Tag submission as from GPCRmd community if it is so
    if ('gpcrcom' in dictpost) and (dictpost['passcode']=='weareGPCRs'):
        ds.is_gpcrmd_community = True
        ds.save()
    # Create or modify existing DyndbModel object
    if len(DM):
        models_dict.update(update_fields)
        DM.update(**models_dict)
        model_id = DM[0].id
    else:
        models_dict.update(creation_fields)
        dm = dyndb_Model(models_dict)
        Dm = dm.save()
        model_id= Dm.id
    # Update model ids in to-submit dictionaries
    submodels_dict['model_id'] = model_id
    dynamics_dict['id_model'] = model_id
    # Create (if required) DyndbSubmissionModel object
    if len(DSM):
        pass
    else:
        submodels_dict.update(creation_fields)
        dsm=dyndb_Submission_Model(submodels_dict)
        dsm.save()
    # Create or update DYndbDynamics object
    if len(DD):
        dynamics_dict.update(update_fields)
        DD.update(**dynamics_dict) 
        dyn_id = DD[0].id
    else:
        dynamics_dict.update(creation_fields)
        dd = dyndb_Dynamics(dynamics_dict)
        Dd = dd.save()
        dyn_id = Dd.id
    ##### Submit crystal and simulated PDB structures, uploaded in this step
    DFD = DyndbFilesDynamics.objects.filter(id_dynamics=dyn_id, type=0)
    DSDF = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=0,is_deleted=False)    
    # Retreat PDB file from request
    uploadedfile = request.FILES['dynamics']
    # If a copy of this file is already avalible for this submission
    pdbfilepath = DSDF[0].filepath if len(DSDF) else False
    pdbfileurl = DSDF[0].url if len(DSDF) else False
    pdbname = DSDF[0].filename if len(DSDF) else False
    # Save uploaded PDB files in server
    (pdbfilepath, pdbfileurl, pdbname) = save_pdbfile('dynamics', submission_id, uploadedfile, pdbfilepath, pdbfileurl, pdbname)
    # Create DyndbFile entry for this file
    (up_filename, ext) = pdbname.split('.', 1)
    file_id = save_dyndbfile(pdbname, ext, pdbfilepath, pdbfileurl, creation_fields, update_fields)
    # Save DyndbFilesDynamics table
    def save_dyndbfiles_intertables(dyn_id, submission_id, file_id, pdbname, pdbfileurl, pdbfilepath, file_type=0):
        """
        Save intermediate tables between DyndbFiles and DyndbDynamics/DynbdbModel/DyndbSubmission
        """
        # Save DyndbFilesDynamics
        filesdyn_data = {
            'id_dynamics':dyn_id,
            'id_files':file_id,
            'type':0,  #Coordinates file
            'framenum':1# Lets hope nobody decides to send a PDB with more than one frame
        }
        DFD = DyndbFilesDynamics.objects.filter(type=0, id_dynamics=dyn_id)
        if len(DFD):
            DFD.update(**filesdyn_data)
            filesdyn_id = DFD[0].id
        else:
            Dfd = dyndb_Files_Dynamics(filesdyn_data)
            dfd = Dfd.save()
            filesdyn_id = dfd.id
        # Save DyndbSubmissionDynamicsFiles information table, or update if already existing
        subdynfil_data = {
            'submission_id' : submission_id,
            'type' : 0,
            'filenum' : 0,
            'files_dynamics_id' : dyn_id,
            'filename' : pdbname,
            'url' : pdbfileurl,
            'filepath' : pdbfilepath.replace(settings.MEDIA_ROOT[:-1],""), #Absolute path with relative one
            'framenum' : 1,
            'id_files' : file_id,
            'files_dynamics_id' : filesdyn_id
        }
        DSDF=DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=0,is_deleted=False)
        if len(DSDF): 
            DSDF.update(**subdynfil_data)
        else:
            Dsdf = dyndb_submission_dynamics_files(subdynfil_data)
            Dsdf.save()
        # Save DyndbFilesModel
        filemod_data = {
            'id_model' : model_id,
            'id_files' : file_id
        }
        DFM = DyndbFilesModel.objects.filter(id_model=model_id)
        if len(DFM):
            DFM.update(**filemod_data)
        else:
            Dfm = dyndb_Files_Model(filemod_data)
            Dfm.save()
    # Save DyndbFile intermediate tables
    save_dyndbfiles_intertables(dyn_id, submission_id, file_id, pdbname, pdbfileurl, pdbfilepath, file_type=0)
    # Count and save number of atoms in DyndbDynamics table using MDtraj
    count_and_save_atoms(dyn_id, submission_id)
    # If everyting was correct, go to step2
    context = { 
        'step' : '2',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
        'repeated_step' : False, #Repeated step?
     }
    return render(request,'dynadb/step2.html', context, status=200)

###### STEP 2: small molecules
def smalmol_info(inchikey):
    """
    Retrieve information about a small molecule from online databases using its inchikey
    """
    # If the submitted inchikey matches a standard compound sinchikey, use its standard molecule reference
    # Else try to find any molecule object with this inchikey
    DCom = DyndbCompound.objects.filter(sinchikey=inchikey)
    DMol = DyndbMolecule.objects.filter(inchikey=inchikey)
    # Check if the molecule already exists in our database. If so, extract everything from there
    blocked = 'readonly'
    if len(DMol):
        dmol = DMol[0]
        dcom = dmol.id_compound
        net_charge = dmol.net_charge
        inchi = dmol.inchi
        sinchi = dcom.sinchi
        sinchikey = dcom.sinchikey
        smiles = dmol.smiles
        iupacname = dcom.iupac_name
        cid = dcom.pubchem_cid
        synonyms = ', '.join(DyndbOtherCompoundNames.objects.filter(id_compound=dcom.id).values_list('other_names', flat=True))
        smalmol_name = dcom.name
        chemblid = dcom.chemblid
        description = dmol.description
        # Ensure that we actually have files for this molecule
        DFM_sdf = DyndbFilesMolecule.objects.filter(id_molecule=dmol.id, type=0)
        inGPCRmd = bool(len(DFM_sdf) and os.path.exists(DFM_sdf[0].id_files.filepath))
        DFM_image = DyndbFilesMolecule.objects.filter(id_molecule=dmol.id, type=2)
        if (len(DFM_image) and os.path.exists(DFM_image[0].id_files.filepath)):
            imagepath = DFM_image[0].id_files.url  
        else:
            imagepath = ''
    # If molecule not in the database
    else:       
        sinchikey = inchikey
        # Get pubchem info of compound. If request doesn't work, send empty strings and enable editing of molecules input fields
        resp = requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/'+inchikey+'/property/CanonicalSMILES,Charge,InChI,IUPACName,/JSON')
        if resp.ok:
            pub_dict = eval(resp.content.decode('UTF-8').replace('null', 'None'))['PropertyTable']['Properties'][0]
            net_charge = str(pub_dict['Charge'])
            inchi = pub_dict['InChI']
            smiles = pub_dict['CanonicalSMILES']
            iupacname = pub_dict['IUPACName']
            cid = str(pub_dict['CID'])
        else:
            net_charge = ""
            inchi = ""
            smiles = ""
            iupacname = ""
            cid = ""
            blocked = ''
            smalmol_name = ""
        sinchi=inchi
        # Get official name of compound. If you cannot get it leave it empty
        if cid:
            resp = requests.get('https://pubchem.ncbi.nlm.nih.gov/compound/'+str(pub_dict['CID']))
            if resp.ok:
                soup = BeautifulSoup(resp.text,'html')
                smalmol_name = soup.find('meta',attrs={'property' : 'og:title'}).get('content')
            else:
                smalmol_name = ""
                blocked = ''
        # Get synonims of compound, if possible
        resp = requests.get('https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/'+inchikey+'/synonyms/TXT')
        if resp.ok:
            synonyms = resp.text.replace("\n", '; ')
        else:
            synonyms = ""
            blocked = ''
        # Get chemblid
        try:
            resp = requests.get('https://www.ebi.ac.uk/chembl/api/data/molecule/'+inchikey)
            tree = ET.fromstring(resp.text)
            chemblid = tree.find('molecule_chembl_id').text.replace('CHEMBL','')
        except Exception as e:
            chemblid = ""
            blocked = ''
        # No description or image by default
        description = ''
        imagepath = ''
        inGPCRmd = False
    # Organize and send the retrieved information
    data = {
        'inchikey' : inchikey,
        'sinchikey': inchikey,
        'name': smalmol_name,
        'iupac': iupacname,
        'chemblid': chemblid,
        'cid': cid,
        'inchi': inchi,
        'sinchi':sinchi,
        'smiles': smiles,
        'net_charge': net_charge,
        'description': description, 
        'other_names': synonyms,
        'imagepath' : imagepath,
        'inGPCRmd' : inGPCRmd,
        'blocked' : blocked
    }
    return data

@login_required
def smalmol_info_url(request):
    """
    Same as smalmol_info(), but to send info as a JSON HttpResponse
    """
    inchikey = request.GET['inchikey'].replace(' ','')
    submission_id = request.GET['submission_id']
    data_mol = smalmol_info(inchikey)
    data_mol['submission_id'] = submission_id
    return HttpResponse(json.dumps(data_mol),content_type='step2/'+submission_id)    

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def find_smalmols(request, submission_id):
    """
    Find the small molecules present in the PDB file of this submission entry. THen process them, and try to find stuff like their ChemblID and such
    """
    def smalmol_dict(submission_id):
        """
        Base smalmol dictionary for submissions
        """
        mydict = {
                'inchi': '',
                'sinchikey': '',
                'net_charge': '',
                'inchikey': '',
                'resname' : '',
                'smiles': '',
                'description': '', 
                'name': '',
                'iupac': '',
                'cid': '',
                'chemblid': '',
                'other_names': '',
                'mol_type': '',
                'submission_id':submission_id,
                'inGPCRmd' : True,
                'creation_submission' : False
            }
        return(mydict)

    # Initial dictionaries
    smalmols_data = {}
    # Some very common molecules's inchikeys and molecule type
    common_mols = {
        'HOH' : ('XLYOFNOQVPJJNP-UHFFFAOYSA-N',6),
        'TIP3' : ('XLYOFNOQVPJJNP-UHFFFAOYSA-N',6),
        'POPC' : ('WTJKGGKOPKCXLL-VYOBOKEXSA-N',7),
        'SOD' : ('FKNQFGJONOIPTF-UHFFFAOYSA-N',8),
        'CLA' : ('VEXZGXHMUGYJMC-UHFFFAOYSA-M',8)
    }
    # Check if this entry already has small molecules assigned 
    #(AKA this is not the first time step2 is being done for this submission_id)
    dyn_id = DyndbDynamics.objects.get(submission_id=submission_id).pk 
    DSM = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    if len(DSM)>0:
        # For each small molecule found for this submission entry
        for dsm in DSM:
            # Get residue name as small mol name
            resname = DyndbDynamicsComponents.objects.get(id_molecule=dsm.molecule_id.id, id_dynamics=dyn_id).resname
            # Base dictionary
            mol_num = dsm.int_id
            smalmols_data[mol_num] = smalmol_dict(submission_id)
            # Fill dictionary
            mol_type = dsm.type 
            inchikey = dsm.molecule_id.inchikey
            smalmol_data = smalmol_info(inchikey)
            smalmols_data[mol_num].update(smalmol_data)
            smalmols_data[mol_num]['mol_type'] = mol_type
            smalmols_data[mol_num]['resname'] = resname
            # If this molecule entry was created in this submission, offer the option to modifiy its values
            creation_submid = dsm.molecule_id.molecule_creation_submission_id.id if dsm.molecule_id.molecule_creation_submission_id else None 
            if creation_submid == submission_id:
                smalmols_data[mol_num]['creation_submission'] = True
    else:    
        # Load PDB system file of this submission entry
        pdbpath = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id, type=0)[0].id_files.filepath
        pdbfile = md.load_pdb(settings.MEDIA_ROOT[:-1] + pdbpath, standard_names=False)
        top = pdbfile.top
        # Select small molecules (anything not protein) from the loaded PDB
        smalmol_names = { top.atom(i).residue.name for i in pdbfile.top.select('not protein')}
        # For each small molecule found in the system
        mol_num = 0
        for resname in smalmol_names:
            # SKip modified forms of Histidine (for some reason MDtraj takes them as non-protein)
            if resname in ['HSD','HSP','HSE']:
                continue
            # Base dictionary
            mymol_num = str(mol_num)
            smalmols_data[mymol_num] = smalmol_dict(submission_id)
            smalmols_data[mymol_num]['resname'] = resname
            # If there are any, obtain smalmol info of common molecules (POPC, TIP3, CLA and SOD) 
            if resname in common_mols:
                inchikey = common_mols[resname][0]
                smalmol_data = smalmol_info(inchikey)
                smalmols_data[mymol_num].update(smalmol_data)
                smalmols_data[mymol_num]['mol_type'] = common_mols[resname][1]
            mol_num+=1
    return HttpResponse(json.dumps(smalmols_data), content_type='step2/'+submission_id)

def save_compound(dictpost, initfiles, molnum, DCom=None, mode='create'):
    """
    Create or update a new DyndbCompound object, and save to the database
    In case a new one is needed
    """
    # ORganize information in dictionary
    comp_dict = {
            "name" : dictpost['smalmol_name'+molnum],
            "iupac_name" : dictpost['smalmol_iupac'+molnum],
            "std_id_molecule" : None,
            "sinchi" : dictpost['smalmol_sinchi'+molnum],
            "sinchikey" : dictpost['smalmol_sinchikey'+molnum],
            }
    # Do not give for granted pubchem cid and chemblid
    if dictpost['smalmol_cid'+molnum]:
        comp_dict['pubchem_cid'] = dictpost['smalmol_cid'+molnum]
    if dictpost['smalmol_chemblid'+molnum]:     
        comp_dict['chemblid'] = dictpost['smalmol_chemblid'+molnum]
    comp_dict.update(initfiles)
    # If there is no compound entry for this sinchikey, create a new one
    if mode == 'create':
        comp_dict.update(initfiles)
        dcf = dyndb_CompoundForm(comp_dict)
        dcom = dcf.save()
        id_comp = dcom.id
    else:
        # If there is, and its standard molecule is the current molecule, update it
        creation_submission_id = DCom[0].std_id_molecule.molecule_creation_submission_id.id if DCom[0].std_id_molecule.molecule_creation_submission_id else None
        if (DCom[0].std_id_molecule.molecule_creation_submission_id == dictpost['submission_id']) and (mode=='update'):
            DCom.update(**comp_dict)
        id_comp = DCom[0].id
    # Return compound id for future uses
    return(id_comp)

def save_molecule(dictpost, initfiles, molnum, id_comp, mode='create'):
    """
    Create or update a new DyndbMolecule object, or update the current one
    """
    # ORganize information in dictionary
    mol_dict = {
        "molecule_creation_submission_id" : dictpost['submission_id'],
        "id_compound" : id_comp,#Temporal placeholder
        "description" : dictpost['smalmol_description'+molnum],
        "net_charge" : dictpost['smalmol_netcharge'+molnum],
        "inchi" : dictpost['smalmol_inchi'+molnum],
        "inchikey" : dictpost['smalmol_inchikey'+molnum],
        "inchicol" : 1, # I dont know what this is, but apparently is always 1
        "smiles" : dictpost['smalmol_smiles'+molnum],
    }
    mol_dict.update(initfiles)
    # If there's a molecule entry already with this inchikey and smiles, dont create a new one
    DMol = DyndbMolecule.objects.filter(inchikey=dictpost['smalmol_inchikey'+molnum])
    if not len(DMol):
        dm = dyndb_Molecule(mol_dict)
        print(dm.errors)
        dmol = dm.save()
        id_mol = dmol.id
        # If we created a new molecule, check if compound has an std_id_molecule assigned yet.
        # If not, assign this one
        DC = DyndbCompound.objects.filter(id=id_comp)
        if not DC[0].std_id_molecule:
            DC.update(std_id_molecule=id_mol)
    else:
        # If there is a molecule entry and it was created in this submission, update its information
        creation_submid = DMol[0].molecule_creation_submission_id.id if DMol[0].molecule_creation_submission_id else None
        if len(DMol) and (mode=='update') and (DMol[0].molecule_creation_submission_id == dictpost['submission_id']):
            DMol.update(**mol_dict)
        id_mol = DMol[0].id
    return(id_mol)

def save_intermoltables(dictpost, molnum, id_mol, id_model, id_dyn, pdb_model, pdb_dyn, mol_counter):
    """
    Create or update tables relating Molecule with Dynamics, Model and Submission tables
    """
    # Equivalences between molecule types in DyndbSubmissionMolecules and the ones in Component tables
    types_dict = {'0' : '1', '1' : '1', '2' : '0', '3' : '2', '4' : '3', '5' : '4', '6' : '3', '7' : '2', '8' : '0', '9' : '4'}
    def count_mols(pdb, resname):
        nummol = len({pdb.atom(a).residue for a in pdb.select('resname '+resname) })
        # MDtraj has problems counting residues whose name starts with an integer
        if not nummol:
            for resname_i in {pdb.atom(a).residue for a in pdb.select('not protein') }:
                if resname in resname_i.name:
                    nummol+=1
        return nummol
    # Count molecules in the files
    nummol_model = count_mols(pdb_model, dictpost['smalmol_resname'+molnum])
    nummol_dyn = count_mols(pdb_dyn, dictpost['smalmol_resname'+molnum])
    # INitial dictionaries to serve as template for the three tables
    submol_dict = {
        'type' : dictpost['smalmol_type'+molnum],
        'submission_id' : dictpost['submission_id'],
        'molecule_id' : id_mol,
        'int_id' : mol_counter,
        'not_in_model' : (not bool(nummol_model))
    }
    dyncomp_dict = {
        'type' : types_dict[dictpost['smalmol_type'+molnum]],
        'id_molecule' : id_mol,
        'id_dynamics' : id_dyn,
        'resname' : dictpost['smalmol_resname'+molnum],
        'numberofmol' : nummol_dyn,
    } 
    modcomp_dict = {
        'type' : types_dict[dictpost['smalmol_type'+molnum]],
        'id_molecule' : id_mol,
        'id_model' : id_model,
        'resname' : dictpost['smalmol_resname'+molnum],
        'numberofmol' : nummol_model,
    }
    # Create or update SUbmissionMolecule object
    DSM = DyndbSubmissionMolecule.objects.filter(submission_id=dictpost['submission_id'], molecule_id=id_mol)
    if len(DSM):
        # If molecule already exists, use its molecule counter (int_id)
        dsm = DSM[0]
        submol_dict['int_id'] = dsm.int_id
        DSM.update(**submol_dict)
    else:
        dsm = dyndb_Submission_Molecule(submol_dict)
        print(dsm.errors)
        dsm.save()
    # Create or update DynamicsComponents object
    DDC = DyndbDynamicsComponents.objects.filter(id_molecule=id_mol, id_dynamics=id_dyn)
    if len(DDC):
        DDC.update(**dyncomp_dict)
    else:
        ddc = dyndb_Dynamics_Components(dyncomp_dict)
        ddc.save()
    # Create or update ModelComponents object
    DMC = DyndbModelComponents.objects.filter(id_molecule=id_mol, id_model=id_model)
    if len(DMC):
        DMC.update(**modcomp_dict)
    else:
        dmc = dyndb_Model_Components(modcomp_dict)
        dmc.save()

def sent_error(logfile, error_msg):
    logfile.close()
    data = {'msg' : error_msg}
    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')

def save_sdf(uploadfile, sdfname, submission_path, logfile):
    # (try to) load the SDF file, and check if it presents any mistakes
    # If it does, save them in a log file to check later
    try:
        # if not settings.MEDIA_ROOT[:-1] in uploadfile: 
        #     uploadfile = settings.MEDIA_ROOT[:-1] + uploadfile
        mol = open_molecule_file(uploadfile,logfile=logfile)
    except (ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension) as e:
        sent_error(logfile, e.args[0])
    except Exception as e:
        sent_error(logfile, 'Cannot load molecule from uploaded file.')
    # Check as well if the sdf file is in the format that we want
    if check_implicit_hydrogens(mol):
        sent_error(logfile, 'Molecule contains implicit hydrogens. Please, provide a molecule with explicit hydrogens.')
    if check_non_accepted_bond_orders(mol):
        sent_error(logfile, 'Molecule contains non-accepted bond orders. Please, provide a molecule with single, aromatic, double or triple bonds only.')
    # Try to write the SDF file. If not possible sent an error and delete the loaded molecule
    try:
        mol.SetProp("_Name",sdfname)
        write_sdf(mol,os.path.join(submission_path,sdfname))
    except:
        try:
            os.remove(os.path.join(submission_path,sdfname))
        except:
            pass
        sent_error(logfile, 'Error while storing SDF file.')
    del mol

def save_png(inchikey, pngname, submission_path, logfile):
    # Try to create an image for this molecule
    try:
        datapubchem,errdata = retreive_compound_png_pubchem('inchikey',inchikey,outputfile=os.path.join(submission_path,pngname),width=300,height=300)
        print(errdata)
    except:
        try:
            os.remove(os.path.join(submission_path,pngname))
        except:
            pass
        sent_error(logfile, 'Error while drawing molecule.')

def save_dyndbfile_molecule(filename, filetype, filemoltype, submission_path, submission_url, initfiles, id_mol):
    # And the wiiild mountaain thyme, grows around the blooming heather
    file_dict = {
        'filename' : filename,
        'id_file_types' : filetype,
        'description' : '',
        'filepath' : join_path(submission_path.replace(settings.MEDIA_ROOT[:-1], ""),filename,url=False),
        'url' : join_path(submission_url,filename,url=True),
    }
    file_dict.update(initfiles)
    # Create or update depending on the needs (and delete old files if required)
    DF = DyndbFiles.objects.filter(dyndbfilesmolecule__id_molecule=id_mol, dyndbfilesmolecule__type=filemoltype)
    if not len(DF):
        df = dyndb_Files(file_dict).save()
    else:
        try:
            os.remove(DF[0].filepath)
        except OSError:
            pass
        DF.update(**file_dict)
        df = DF[0]
    # Save intermediate table comunicating "DyndbFiles" and "DyndbMolecule" tables
    filemol_dict = {
        'id_molecule' : id_mol,
        'id_files' : df.id,
        'type' : filemoltype,
    }
    DFM = DyndbFilesMolecule.objects.filter(id_molecule=id_mol, type=filemoltype)
    if not len(DFM):
        dyndb_Files_Molecule(filemol_dict).save()
    else:
        DFM.update(**filemol_dict)

# This whole function is fucking ugly, an actual disgrace that should be mended at some point
def save_molfile(dictfiles, inchikey, molnum, id_mol, creation_fields, update_fields):
    """
    Save uploaded SDF file into our server (if any was uploaded) and make PNG images of it 
    Save the uploaded files into our database as DyndbFileMOlecule and DyndbFIle objects
    Come over the hills, my bonnie irish lass. Come over the hills to your daaaarliiing...
    """
    # Get some objects from database
    submission_id = dictfiles['submission_id']
    dm = DyndbMolecule.objects.get(id=id_mol)
    creation_submid = dm.molecule_creation_submission_id.id if dm.molecule_creation_submission_id else None
    DFM_sdf = DyndbFilesMolecule.objects.filter(id_molecule=id_mol, type=0)
    DFM_image = DyndbFilesMolecule.objects.filter(id_molecule=id_mol, type=2)
    # Paths
    submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
    submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
    # Ensure there is an SDF file to work with before advancing
    # If there isn't and we need it, send an error message
    if ('sdfmol'+molnum in dictfiles.keys()) and (not len(DFM_sdf) or (submission_id == creation_submid) or (len(DFM_sdf) and not os.path.exists(DFM_sdf[0].id_files.filepath))):
        # Base path and URL for our files to be in
        uploadfile = dictfiles['sdfmol'+molnum] 
        os.makedirs(submission_path,exist_ok=True)
        # Get some filenames
        logname = get_file_name_submission("molecule",submission_id,molnum,ref=False,ext="log",forceext=False,subtype="log")
        sdfname = get_file_name_submission("molecule",submission_id,molnum,ref=False,ext="sdf",forceext=False,subtype="molecule")
        logfile = open(os.path.join(submission_path,logname),'w')
        # IF there are no files OR we are updating previously submited molecule OR the current entry's associated file does not exist
        if not len(DFM_sdf) or (submission_id == creation_submid) or (len(DFM_sdf) and not os.path.exists(DFM_sdf[0].id_files.filepath)):
            # Save file
            save_sdf(uploadfile, sdfname, submission_path, logfile)
            # Save tables
            initfiles = update_fields if len(DFM_sdf) else creation_fields
            save_dyndbfile_molecule(sdfname, 20, 0, submission_path, submission_url, initfiles, id_mol)
        # Delete mol object and close logfile once we are done
        logfile.close()
    # Save for images
    # Do you love a laddie with curyly, brown haair...?? Still, I love him, I can't deny it
    if not len(DFM_image) or (submission_id == creation_submid) or (len(DFM_image) and not os.path.exists(DFM_image[0].id_files.filepath)):
        # Base path and URL for our files to be in
        os.makedirs(submission_path,exist_ok=True)
        # Get some filenames
        logname = get_file_name_submission("molecule",submission_id,molnum,ref=False,ext="log",forceext=False,subtype="log")
        pngname = get_file_name_submission("molecule",submission_id,molnum,ref=False,ext="png",forceext=False,subtype="image",imgsize=300)
        logfile = open(os.path.join(submission_path,logname),'w')
        # Save file
        save_png(inchikey, pngname, submission_path, logfile)
        # Save tables
        initfiles = update_fields if len(DFM_sdf) else creation_fields        
        save_dyndbfile_molecule(pngname, 19, 2, submission_path, submission_url, initfiles, id_mol)
        # Delete mol object and close logfile once we are done
        logfile.close()

def delete_molentry(dm, id_dyn, id_model, submission_id, creation_fields):
    """
    Delete molecule entry from submission. We don't actually delete the molecule table, but its adjacent tables
    """
    mol_id = dm.pk
    ddc = DyndbDynamicsComponents.objects.get(id_molecule=mol_id, id_dynamics=id_dyn)
    dsm = DyndbSubmissionMolecule.objects.get(molecule_id=mol_id, submission_id=submission_id)
    dmm = DyndbModelComponents.objects.get(id_molecule=mol_id,id_model=id_model)
    DCMM = DyndbComplexMoleculeMolecule.objects.filter(id_molecule=mol_id)
    moltype = dsm.type
    ddc.delete()
    dsm.delete()
    dmm.delete()
    # if it is a ligand molecule what was deleted, we might have to set a new complexExp for this
    if (moltype in  [0,1]) and len(DCMM):
        DCMM[0].delete()
        prots = [ a[0] for a in DyndbSubmissionProtein.objects.filter(submission_id=submission_id).values_list('protein_id') ] 
        prot_id_receptor = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id=submission_id).exclude(receptor_id_protein=None).id
        save_complex_related(submission_id, id_model, prots, creation_fields, prot_id_receptor)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed    
def step2(request, submission_id,):
    """
    Go to step2. Once there, javascript will send several requests to find small molecules for this entry
    """
    context = { 
        'step' : '2',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
     }
    return render(request,'dynadb/step2.html', context, status=200)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def step2_submit(request, submission_id,):
    """
    Submit into the database the data obtained from the step2 submission form
    Czemús Jasiénku
    """
    # Some initial variables, including users and timestamps
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    dictfiles = { key : request.FILES[key] for key in request.FILES } 
    dictfiles['submission_id'] = submission_id
    dictpost = { key : request.POST[key] for key in request.POST }
    dictpost['submission_id'] = submission_id
    inchikeys = []
    creation_fields={
               'creation_timestamp':timezone.now(),
               'created_by_dbengine':def_user_dbengine, 
               'created_by':def_user,
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    update_fields = {
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    # Get Model object of this submission object and load its pdb file with MDtraj
    dm = DyndbModel.objects.get(dyndbsubmissionmodel__submission_id=submission_id)
    id_model = dm.id
    modelfile_path = DyndbFilesModel.objects.get(id_model=id_model).id_files.filepath
    pdbmodel = md.load_pdb(settings.MEDIA_ROOT + modelfile_path, standard_names=False).top
    # Get Dynamics object of this submission object and load its pdb file with MDtraj
    dd = DyndbDynamics.objects.get(submission_id=submission_id)
    id_dyn = dd.id
    dynfile_path = DyndbFilesDynamics.objects.get(id_dynamics=id_dyn, type=0).id_files.filepath
    pdbdyn = md.load_pdb(settings.MEDIA_ROOT + dynfile_path, standard_names=False).top
    # If there are small molecules in this system
    num_entries = request.POST['num_entries']
    if num_entries:
        # Get an array with the form numbers of the submitted molecules
        entries_ids = num_entries.split(',')
        # Iterate over the molecules we have
        mol_counter = 0
        for molnum in dictpost['num_entries'].split(','):
            inchikey = dictpost['smalmol_inchikey'+molnum]
            sinchikey = dictpost['smalmol_sinchikey'+molnum]
            chemblid = dictpost['smalmol_chemblid'+molnum]
            pubcid =dictpost['smalmol_cid'+molnum]
            # Search if this compound already exists in database
            qobjs = []
            search = False
            inchikeys.append(inchikey)
            if inchikey:
                qobjs.append(Q(sinchikey=sinchikey))
            if chemblid:
                qobjs.append(Q(chemblid=chemblid))
            if pubcid:
                qobjs.append(Q(pubchem_cid=pubcid))
            for qobj in qobjs:
                if search:
                    search = search | qobj
                else:
                    search = qobj
            DC = DyndbCompound.objects.filter(search)
            # Create and save a new compound object in the database, if required
            if len(DC):
                id_comp = save_compound(dictpost, update_fields, molnum, DC, mode="update")
            else:
                id_comp = save_compound(dictpost, creation_fields, molnum, mode="create")
            # Check if molecule objects for the mol already exists. If so update it. If not create a new one
            DM = DyndbMolecule.objects.filter(dyndbsubmissionmolecule__submission_id=submission_id,inchikey=inchikey)
            if len(DM):
                id_mol = save_molecule(dictpost, update_fields, molnum, id_comp, mode='update')
            else:
                id_mol = save_molecule(dictpost, creation_fields, molnum, id_comp, mode='create')
            # Save intermediary tables between the "Molecule" object and the "Dynamics", "Model" and "Submission" ones 
            save_intermoltables(dictpost, molnum, id_mol, id_model, id_dyn, pdbmodel, pdbdyn, molnum)
            # Save any submitted files into database
            save_molfile(dictfiles, inchikey, molnum, id_mol, creation_fields, update_fields)
            mol_counter += 1
        # If a molecule previously associated to this with this submission has not been resubmitted, delete the table associating them
        for dm in DyndbMolecule.objects.filter(dyndbsubmissionmolecule__submission_id=submission_id):
            if not (dm.inchikey in inchikeys):
                delete_molentry(dm, id_dyn, id_model, submission_id, creation_fields)
    # Context variables
    context = { 
        'step' : '3',
        'submission_id' : submission_id,
        'max_step': check_submission_status(submission_id),
        'repeated_step' : False, #Repeated step?,
     }
    # Once everything is done, go to step 3
    return render(request,'dynadb/step3.html', context, status=200)

###### STEP 3: protein chains
def get_uniprot_seq(uniprotkbac):
    """
    Get the fasta sequence corresponding to a certain uniprot code
    """
    URL = 'http://www.uniprot.org/uniprot/'
    response = requests.get(URL+str(uniprotkbac)+'.fasta',stream=True)
    if response.ok:
        fasta = response.text
        fasta_split = fasta.split('\n')
        seq=""
        for line in fasta_split:
            if line.startswith('>'):
                header = line
            else:
                seq += line
        return(seq) 
    else:
        print('Could not obtain sequence for uniprotkbac '+uniprotkbac)
        return ''

def get_mutseq(pdb_path, segdict):
    """
    Terrible way of obtaining the sequence from a pdb file in the specified segments
    """
    mutseq = ''
    prev_resid = 0
    prev_resname = ''
    with open(settings.MEDIA_ROOT + pdb_path,'r') as myfile:
        for line in myfile:
            if line.startswith(('ATOM','HETATM')):
                resname = line[17:20].replace(' ','')
                chain = line[21]
                resid = line[22:26].replace(' ','')
                seg = line[72:76].replace(' ','')
                # Obtain sequence from proteins
                if (prev_resid != resid) or (prev_resname != resname):
                    # Check if protein is in segments
                    insegment = False
                    for i in segdict:
                        segdict_i = segdict[i]
                        insegment = (insegment) or (
                            (segdict_i['chain'] == chain) and
                            (segdict_i['segid'] == seg) and 
                            (segdict_i['to'] >= int(resid)) and 
                            (segdict_i['from'] <= int(resid))) 
                    # If it is, add it to our sequence
                    if insegment:
                        if resname in d:
                            mutseq += d[resname]
                        else:
                            mutseq += 'X'
                    prev_resid = resid
                    prev_resname = resname
    return(mutseq)

@login_required
def get_alignment_URL(request):
    """
    Align submitted uniprot sequence with submitted segments of this system
    """
    dictpost = { key : request.POST[key] for key in request.POST }
    uniseq = dictpost['unisequence']
    # Get segments
    segdict = {}
    for i in dictpost['segnums'].split(','):
        segdict['seg'+i] = {
            'chain' : dictpost['chain'+i],
            'segid' : dictpost['segid'+i],
            'from' : int(dictpost['from'+i]),
            'to' : int(dictpost['to'+i]),
        }
    # Load dynamics PDB file of this submission
    pdb_path = DyndbFilesDynamics.objects.get(id_dynamics__submission_id=dictpost['submission_id'], type=0).id_files.filepath
    # Get mutant sequence in the specified segemnts
    mutseq = get_mutseq(pdb_path, segdict)
    # Check if uniseq and mutseq were properly extracted, and send error otherwise
    if not mutseq:
        error_msg = "<b>Alignment error: </b><p>Protein sequence with specified segment coordinates was not found in previoulsy submitted PDB file. Please ensure your segment coordinates are correct.</p>"
        return HttpResponse(error_msg, status=500)
    elif not uniseq:
        error_msg = "<b>Alignment error: </b><p>No reference sequence for this protein was found. Please introduce one in the field above</p>"
        return HttpResponse(error_msg, status=500)
    # Align sequences
    result=align_wt_mut_global(uniseq,mutseq)
    alignment='>uniprot:\n'+result[0]+'\n>system_seq:\n'+result[1]
    # Convert alignment from fasta to phylip
    p_alignment = fasta_to_phylip(alignment)
    rep_dict = {'alig_phy': p_alignment, 'alig_fa' : alignment}
    return HttpResponse(json.dumps(rep_dict))

@login_required
def prot_info(request):
    """
    Obtain data of this protein from uniprot, and send it back
    """
    uniprotkbac = request.GET['uniprotkbac'].replace(' ','')
    isoform = request.GET['isoform']
    submission_id = request.GET['submission_id']
    (data,errdata) = retreive_data_uniprot(uniprotkbac,isoform=isoform, columns="id,accession,organism_id,protein_name,organism_name,sequence,protein_families")
    return HttpResponse(json.dumps(data),content_type='step3/'+submission_id)    

def find_prots(request,submission_id):
    """
    Find the small molecules present in the PDB file of this submission entry. THen process them, and try to find stuff like their ChemblID and such
    """
    # Check if this entry already has segments assigned
    #(AKA this is not the first time step3 is being done for this submission_id)
    dyn_id = DyndbDynamics.objects.get(submission_id=submission_id).pk 
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id=submission_id)
    prottoseg_types = ['0','1','6','5','7','6']
    prots_data = []
    if len(DP)>0:
        # Add an empty element for every DP instance found
        prots_data = [''  for dp in DP]
        # For each protein segment found for this submission entry
        for dp in DP:
            dus = dp.id_uniprot_species
            # Check if protein has synonims
            DOPN = DyndbOtherProteinNames.objects.filter(id_protein=dp.id)
            dps = DyndbProteinSequence.objects.get(id_protein=dp.id)
            prot_synonims = ';'.join(DOPN.values_list('other_names', flat=True)) if len(DOPN) else ''
            # Get Uniprot sequence (if any). Otherwise just take itself as model
            uniseq = get_uniprot_seq(dp.uniprotkbac) if dp.uniprotkbac else dps.sequence
            # Extract data to send into form
            mydict = {
                'uniprot': dp.uniprotkbac,
                'notuniprot' : (not bool(dp.uniprotkbac)),
                'isoform': dp.isoform,
                'isIsoform' : (dp.isoform != 1),
                'name': dp.name,
                'aliases': prot_synonims,
                'species_code': dus.taxon_node,
                'species_name': dus.scientific_name,
                'unisequence': uniseq,
                'segments' : [],
                'mutations' : [],
                'submission_id':submission_id,
                'noGPCR' : (not bool(dp.receptor_id_protein)),# We asume all receptors in the database are GPCRs
            }
            # Extract segemnts of this protein, and the information on each one
            DMR = DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id, id_protein=dp.id)
            for dmr in DMR:
                segdict = {
                    'pdbid' : dmr.pdbid,
                    'source_type' : dmr.source_type,
                    'chain' : dmr.chain,
                    'segid' : dmr.segid,
                    'resid_from' : dmr.resid_from,
                    'resid_to' : dmr.resid_to,
                    'bond' : bool(dmr.bonded_to_id_modeled_residues)
                }
                mydict['segments'].append(segdict)
            # Extract mutations
            DPM = DyndbProteinMutations.objects.filter(id_protein=dp.id)
            for dpm in DPM:
                mutdict = {
                    'resid' : dpm.resid,
                    'from' : dpm.resletter_from,
                    'to' : dpm.resletter_to,
                }
                mydict['mutations'].append(mutdict)
            # Extract ID of protein
            DSP = DyndbSubmissionProtein.objects.filter(submission_id=submission_id, protein_id=dp.id)
            if len(DSP):
                entry_id = DSP[0].int_id
                # Store this protein's data
                prots_data[entry_id] = mydict
            else:
                prots_data.append(mydict)
    #If this is a new submission, create some default placeholders for segment and protein entries
    else: 
        # use MDtraj to load the model PDB structure file submitted in step1
        dm = DyndbModel.objects.get(dyndbsubmissionmodel__submission_id=submission_id)
        dd = DyndbDynamics.objects.get(submission_id=submission_id)
        df = DyndbFiles.objects.get(dyndbfilesdynamics__id_dynamics=dd.id, dyndbsubmissiondynamicsfiles__type=0)
        pdb_path = df.filepath 
        pdbtop = md.load_pdb(settings.MEDIA_ROOT + pdb_path, standard_names=False).topology
        # Take chain and segment ids in the system
        chainseg = {}
        segresids = {}
        chainresids = {}
        mutseqs = {}
        prev_resid = ''
        prev_seg = ''
        with open(settings.MEDIA_ROOT + pdb_path, 'r') as myfile:
            for line in myfile:
                if line.startswith(('ATOM','HETATM')):
                    resname = line[17:20].replace(' ','')
                    chain = line[21]
                    resid = line[22:26].replace(' ','')
                    seg = line[72:76].replace(' ','')
                    # Don't repeat yourself
                    if prev_seg != seg:
                        chainseg.setdefault(chain,set()).add(seg)
                    # Don't repeat yourself
                    if prev_resid != resid: 
                        segresids.setdefault(seg,list()).append(resid)
                        chainresids.setdefault(chain,list()).append(resid)
                    prev_resid = resid
                    prev_seg = seg
        # Filter protein chain and segments
        protsegs = { pdbtop.atom(i).segment_id for i in pdbtop.select('protein')}
        chainseg_prot = {}
        for chain,segs in chainseg.items():
            mysegs = set()
            for seg in segs:
                if seg in protsegs:
                    mysegs.add(seg)
            if len(mysegs):
                chainseg_prot[chain] = mysegs
        # Iterate over protein chains
        for chain,segids in chainseg_prot.items():
            # Base dictionary for protein data
            mydict = {
                    'uniprot': '',
                    'notuniprot' : False,
                    'isoform': '1',
                    'isIsoform' : '',
                    'name': '',
                    'aliases': '',
                    'species_code': '',
                    'species_name': '',
                    'unisequence': '',
                    'segments' : [],
                    'mutations' : [],
                    'submission_id': submission_id,
                    'noGPCR' : False,
            }
            # If there are segments in this chain, create a segment entry for every one
            if len(segids):
                bond = False
                for segid in segids:
                    segdict = {
                        'pdbid' : dm.pdbid,
                        'source_type' : prottoseg_types[dm.source_type],
                        'chain' : chain,
                        'segid' : segid,
                        'resid_from' : segresids[segid][0],
                        'resid_to' : segresids[segid][-1],
                        'bond' : bond
                    }
                    bond = True # All segments in a chain that are not the first will be marked as "bonded with previous segment"
                    mydict['segments'].append(segdict)
            # If the chain has no segments, create only one for the whole chain
            else:
                chain_resids = set(chain_sel.get('resid'))
                segdict = {
                    'pdbid' : dm.pdbid,
                    'source_type' : prottoseg_types[dm.source_type],
                    'chain' : chain,
                    'segid' : '',
                    'resid_from' : chainresids[chain][0],
                    'resid_to' : chainresids[chain][-1],
                    'bond' : False
                }
            # Make a protein entry for every chain in the system
            prots_data.append(mydict)
    # Send data and template back to client
    return HttpResponse(json.dumps(prots_data), content_type='step3/'+submission_id)

def save_mutations(dictpost, mut_id, entry_id, prot_id, submission_id):
    """
    Save mutation entries for this protein
    """
    protmuts_dict = {
        'id_protein' : prot_id,
        'resid' : dictpost[mut_id+"resid"+entry_id],
        'resletter_from' : dictpost[mut_id+"from"+entry_id],
        'resletter_to' : dictpost[mut_id+"to"+entry_id]
    }
    # if entry already exists, update. Otherwise create new entry
    DPM=DyndbProteinMutations.objects.filter(id_protein=prot_id, resid=protmuts_dict['resid'], resletter_to=protmuts_dict['resletter_to'], )
    if len(DPM):
        DPM.update(**protmuts_dict)
    else:
        dpm = dyndb_Protein_MutationsForm(protmuts_dict)
        dpm.save()

def get_seq_coordinates(id_model, prot_id, resid_from, resid_to, chain, segid):
    """
    Obtain starting and ending positions of this segment in the reference Uniprot sequence (if any is avalible)
    """
    dp = DyndbProtein.objects.get(pk=prot_id)
    if dp.uniprotkbac:
        uniseq = get_uniprot_seq(dp.uniprotkbac) 
        dm = DyndbModel.objects.get(pk=id_model)
        pdb_path = DyndbFilesDynamics.objects.get(id_dynamics__id_model=id_model, type=0).id_files.filepath
        # Obtain segment sequence of this dynamic
        segdict = {'seg1':{
            'chain' : chain,
            'segid' : segid,
            'from' : int(resid_from),
            'to' : int(resid_to),
        }}
        dynseq = get_mutseq(pdb_path,segdict)
        # Perform alignment
        alig=align_wt_mut_global(uniseq,dynseq)
        print("Alineame")
        alig_uniseq = alig[0]
        alig_mutseq = alig[1]
        seg_alig = alig.aligned # Returns segments aligned (((0, 1), (2, 3), (4, 5)), ((0, 1), (1, 2), (2, 3)))
        # Find start of uniprot sequence in alginment
        starting = seg_alig[0][0][-1]
        # if alig_uniseq.startswith('-'):
        #     starting = 1
        # else:
        #     starting = alig[3]
        # Find ending of uniprot sequence in alginment            
        ending = seg_alig[0][-1][-1]
        # if alig_uniseq.endswith('-'):            
        #     ending = len(uniseq)
        # else:
        #     ending = alig[4]
        print(starting, ending)
        return(starting, ending)
    # If no uniprot for this protein, return start and end positions of original protein
    else:
        return(resid_from, resid_to)

def save_modeled_residues(dictpost, seg_id, entry_id, prot_id, id_model, submission_id, prev_modelres_id=None):
    """
    Save segments of modeled residues belonging to this protein
    """
    # Get segment positions in uniprot sequence
    resid_from = dictpost[seg_id+"from_resid"+entry_id]
    resid_to = dictpost[seg_id+"to_resid"+entry_id]
    chain = dictpost[seg_id+"chain"+entry_id]
    segid = dictpost[seg_id+"segid"+entry_id]
    (unistart, uniend) = get_seq_coordinates(id_model, prot_id, resid_from, resid_to, chain, segid)
    modelres_dict = {
        'id_protein' : prot_id,
        'id_model' : id_model,
        'chain' : chain,
        'segid' : segid,
        'resid_from' : resid_from,
        'resid_to' : resid_to,
        'seq_resid_from' : unistart,
        'seq_resid_to' : uniend,
        'bonded_to_id_modeled_residues' : prev_modelres_id if seg_id+"bound_previous"+entry_id in dictpost else None,
        'pdbid' : dictpost[seg_id+"pdbid"+entry_id],
        'source_type' : dictpost[seg_id+"sourcetype"+entry_id],
        'template_id_model' : None, # No idea what this is, but in vagrant is always None
    }
    # if entry already exists, update. Elsewhere create new entry
    DMR=DyndbModeledResidues.objects.filter(id_protein=prot_id, id_model=id_model, resid_from=dictpost[seg_id+"from_resid"+entry_id])
    if len(DMR):
        DMR.update(**modelres_dict)
        modelres_id = DMR[0].id
    else:
        dmr = dyndb_Modeled_Residues(modelres_dict)
        Dmr = dmr.save()
        modelres_id = Dmr.id
    return modelres_id

def apply_mutations(dictpost, mutation_ids, entry_id, tomutseq):
    """
    Apply mutations from post dictionary into this sequence
    """
    seq_ary = list(tomutseq)
    gapcounter = 1
    for mut_id in mutation_ids[entry_id]:
        resid = int(dictpost[mut_id+"resid"+entry_id])
        resletter_from = dictpost[mut_id+"from"+entry_id]
        resletter_to = dictpost[mut_id+"to"+entry_id]
        # if deletion
        if resletter_to=='-':
            seq_ary[resid-gapcounter] = ''
        # If insertion
        elif resletter_from=='-':
            seq_ary[resid-gapcounter] += resletter_to
        # If mismatch
        else:
            seq_ary[resid-gapcounter] = resletter_to
    return(''.join(seq_ary))

def save_protein_table(dictpost, entry_id, submission_id, mutation_ids, update_fields, creation_fields):
    """
    Save protein table and realted objects
    """
    # Identify DyndbUniprotSpecies corresponding to the species of this protein
    try:
        dus = DyndbUniprotSpecies.objects.get(taxon_node=dictpost['species_code'+entry_id])
    # GPCRmd has already all uniprot species in its database. We do not expect the user to submit a new one. 
    # If this species code is not found in the database, we asume is a typo
    except Exception as e:
        error = 'Species with taxon node %s not found in database'%dictpost['species_code'+entry_id]
        return HttpResponse(error,status=500,reason='Species with taxon node %s not found in database'%dictpost['species_code'+entry_id],content_type='text/plain; charset=UTF-8')
    """
    segdict = {}
    for i in dictpost['num_segs'+entry_id].split(','):
        segdict['seg'+i] = {
            'chain' : dictpost[i+'chain'+entry_id],
            'segid' : dictpost[i+'segid'+entry_id],
            'from' : int(dictpost[i+'from_resid'+entry_id]),
            'to' : int(dictpost[i+'to_resid'+entry_id]),
        }
    pdb_path = DyndbFilesDynamics.objects.get(id_dynamics__submission_id=dictpost['submission_id'], type=0).id_files.filepath
    mutseq = get_mutseq(pdb_path, segdict)
    """
    # Extract receptor name (in case this protein is actually a receptor)
    receptor_id = None
    P = Protein.objects.filter(accession=dictpost['prot_uniprot'+entry_id])
    if len(P):
        receptor_id = P[0].id
    # Find if there is already a protein entry for this protein in GPCRmd database, return its prot_id
    uniprotkbac = dictpost['prot_uniprot'+entry_id]
    isoform = dictpost['isoform'+entry_id]
    if not dictpost['num_muts'+entry_id]:
        DP = DyndbProtein.objects.filter(uniprotkbac=uniprotkbac, isoform=isoform)
        if len(DP):
            return(DP[0].pk)
    # Get mutant sequences by applying our mutations into the GPCRdb sequence of the receptor (or the uniprot one, in case there is none in GPCRdb)
    tomutseq = P[0].sequence if len(P) else dictpost['unisequence'+entry_id] 
    mutseq = apply_mutations(dictpost, mutation_ids, entry_id, tomutseq)
    # Save DyndbProtein entry 
    prot_dict = {
        'uniprotkbac' : uniprotkbac,
        'isoform' : isoform,
        'is_mutated' : bool(dictpost['num_muts'+entry_id]),
        'name' : dictpost['name'+entry_id],
        'receptor_id_protein' : receptor_id,
        'id_uniprot_species' : dus.id,
    }
    # Check if this protein already exists for this submission. If so, update current entry
    DP = DyndbProtein.objects.filter(dyndbsubmissionprotein__submission_id=submission_id, dyndbsubmissionprotein__int_id=entry_id)
    if len(DP):
        prot_dict.update(update_fields)
        DP.update(**prot_dict) 
        prot_id = DP[0].id
    else:
        prot_dict.update(creation_fields)
        prot_dict['protein_creation_submission_id'] = submission_id
        dp = dyndb_ProteinForm(prot_dict)
        Dp = dp.save()
        prot_id = Dp.id
    # Save DyndbProteinSequence entry
    protseq_dict = {
        'id_protein' : prot_id,
        'sequence' : mutseq,
        'length' : len(mutseq),
    }
    # Check if this protein entry already has a sequence. If so, update current entry
    DPS = DyndbProteinSequence.objects.filter(id_protein=prot_id)
    if len(DPS):
        DPS.update(**protseq_dict) 
    else:
        dps = dyndb_Protein_SequenceForm(protseq_dict)
        Dps = dp.save()
        dps.save()
    # Save "other names" entry for this protein
    for othername in dictpost['aliases'+entry_id].split(';'):
        #Skip empty entries
        othername = othername.lstrip()
        if not othername:
            continue
        otherprot_dict = {
            'other_names' : othername,
            'id_protein' : prot_id
        }
        DOPN = DyndbOtherProteinNames.objects.filter(id_protein = prot_id, other_names=othername)
        if not len(DOPN):
            dopn = dyndb_Other_Protein_NamesForm(otherprot_dict)
            dopn.save()
    return prot_id

def interprot_tables(dictpost, entry_id, prot_id, submission_id):
    """
    Save (if necessary) new many-to-many relational tables
    """
    # Save DyndbSubmissionProtein table (if entry does not exist yet)
    subprot_dict = {
        'submission_id' : submission_id,
        'protein_id' : prot_id,
        'int_id' : int(entry_id), 
    }
    DSP = DyndbSubmissionProtein.objects.filter(protein_id=prot_id, submission_id=submission_id)
    if not len(DSP):
        dsp = dyndb_Submission_Protein(subprot_dict)
        print(dsp.errors)
        dsp.save()

def save_cannonical_proteins(dictpost, entry_id, submission_id, prot_id, update_fields, creation_fields):
    """
    Find DyndbCannonicalProtein entry with this uniprot, or create new entry if there is none
    Also, create a DyndbProteinCannonicalProtein entry to associate our protein entry with a cannonical protein entry 
    """
    def save_cannonicprotein_table(id_protein, cannonprot_id):
        """
        Save DyndbProteinCannonicalProtein relational table
        """
        DPCP = DyndbProteinCannonicalProtein.objects.filter(id_protein=id_protein, id_cannonical_proteins=cannonprot_id)
        if not len(DPCP):
            protcanprot = {
                'id_protein' : id_protein,
                'id_cannonical_proteins' : cannonprot_id,
            }
            dpcp = dyndb_Protein_Cannonical_Protein(protcanprot)
            dpcp.save()
    # If no cannonical protein exists yet for this uniprotkb, create a new one
    DCP = DyndbCannonicalProteins.objects.filter(id_protein__uniprotkbac=dictpost['prot_uniprot'+entry_id])
    if not len(DCP):
        # If our current submitted protein is mutated or is not isoform 1 and has an actual uniprot, we
        # will create a new DyndbProtein entry (without mutations)
        if ((bool(dictpost['num_muts'+entry_id])) or (dictpost['isoform'+entry_id]!=1)) and (dictpost['prot_uniprot'+entry_id]):
            canonprot_dict = dict(dictpost)
            canonprot_dict['num_muts'+entry_id] = 0
            mutation_ids = { entry_id : []}
            canonprot_dict['isoform'+entry_id] = 1
            prot_id_cannon = save_protein_table(canonprot_dict, entry_id, submission_id, mutation_ids, update_fields, creation_fields)
        # Otherwise, we can use our current protein entry as cannonical 
        else: 
            prot_id_cannon = prot_id
        # Save DyndbCannonicalProtein entry for our cannonical protein
        protcan_dict = {
            'id_protein' : prot_id_cannon
        }
        dcp = dyndb_Cannonical_ProteinsForm(protcan_dict)
        Dcp = dcp.save()
        cannonprot_id = Dcp.pk
    # Otherwise just take first match (not the best method maybe)
    else:
        cannonprot_id = DCP[0].pk
        prot_id_cannon = DCP[0].id_protein.pk
    # For the relational table between DYndbCannonicalPRotein and DyndbProtein, we'll have to save two of them if a new protein entry was created
    if prot_id_cannon == prot_id:
        save_cannonicprotein_table(prot_id_cannon, cannonprot_id)
    else:
        save_cannonicprotein_table(prot_id_cannon, cannonprot_id)
        save_cannonicprotein_table(prot_id, cannonprot_id)

def save_complex_related(submission_id, id_model, prots, creation_fields, prot_id_receptor = False):
    """
    Create or update complex-related models for this entry 
    Namely DyndbComplexMolecule,DyndbComplexExp, DyndbComplexMoleculeMolecule, DyndbComplexCompound) and DyndbComplexProtein
    """
    # Get ligand compounds of this submission
    DM = DyndbMolecule.objects.filter(dyndbsubmissionmolecule__type__in=[0,1], dyndbsubmissionmolecule__submission_id=submission_id)
    comps = DM.values_list('id_compound',flat=True)
    mols =  DM.values_list('id',flat=True)
    # If there are no ligand compounds in the submission or there is only one protein(apoform), assign a prot_id to the model
    dm = DyndbModel.objects.get(id=id_model)
    if not len(comps) and (len(prots) == 1):
        dm.id_protein_id = prot_id_receptor
        dm.save()
        return
    # Otherwise assign none
    else:
        dm.id_protein_id = None
        dm.save()
    # Check if a complex with this exact proteins and compounds already exists. If so, we won't update the existing one
    DCE = DyndbComplexExp.objects.filter(compounds__in=comps, proteins__in=prots)
    # Check if the complexes found have the exact same proteins and compounds as our complex
    valid_DCE = []
    for dce in DCE:
        absent_element = False
        for comp_id in dce.compounds.values_list('id', flat=True):
            if comp_id not in comps:
                absent_element = True
        for prot_id in dce.proteins.values_list('id', flat=True):
            if prot_id not in prots:
                absent_element = True
        if not absent_element:
            valid_DCE.append(dce)
    # Save complex-experiment object and get its id
    if not len(valid_DCE):
        complexexp_dict = {}
        complexexp_dict.update(creation_fields)
        dce = dyndb_Complex_Exp(complexexp_dict).save()
        id_complexp = dce.pk
    # IF already exists, take that complex-experiment object
    else:
        id_complexp = valid_DCE[0].pk
    # With this id, now we can create and save tha many-to-many tables betwen complexp and compound and molecule 
    # And it didn't always rain, every single day, since you and I were true
    # complexcompound table (one for each compound in system)
    for id_comp in comps: 
        comp_type = DyndbSubmissionMolecule.objects.get(molecule_id__id_compound=id_comp, submission_id=submission_id).type
        DCC = DyndbComplexCompound.objects.filter(id_complex_exp=id_complexp, id_compound=id_comp, type=comp_type)    
        if not len(DCC):
            complexcomp_dict = {'id_complex_exp': id_complexp,
                                'id_compound' : id_comp,
                                'type' : comp_type }
            dyndb_Complex_Compound(complexcomp_dict).save()
    # ComplexProtein tables (one for each protein in the system)
    # Wir sind verloren, wir sind verloren, wir sind verloren
    for id_prot in prots:
        DCP = DyndbComplexProtein.objects.filter(id_complex_exp=id_complexp, id_protein=id_prot)    
        if not len(DCP):
            complexprot_dict = {'id_complex_exp': id_complexp,
                                'id_protein' : id_prot}
            dyndb_Complex_Protein(complexprot_dict).save()
    # Create ComplexMolecule table regardless of this system actually having any non-protein molecules
    DCM = DyndbComplexMolecule.objects.filter(id_complex_exp=id_complexp)
    if not len(DCM):
        complexmol_dict = {'id_complex_exp': id_complexp }
        complexmol_dict.update(creation_fields)
        dcm = dyndb_Complex_Molecule(complexmol_dict).save()
        id_complmol = dcm.pk
    else:
        id_complmol = DCM[0].pk
    # Add a complexmoleculemolecule for every entry in the system
    for id_mol in mols:
        DCMM = DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complmol, id_molecule=id_mol)
        if not len(DCMM):
            mol_type = DyndbSubmissionMolecule.objects.get(molecule_id__id_compound=id_comp, submission_id=submission_id).type        
            # complexmoleculemolecule table
            complex_mol_mol = {'id_complex_molecule': id_complmol,
                               'id_molecule' : id_mol,
                               'type' : mol_type}
            dcmm = dyndb_Complex_Molecule_Molecule(complex_mol_mol).save()
    # Finally, update model table with our newly obtained dyndbcomplexmolecule id
    dm = DyndbModel.objects.get(id=id_model)
    dm.id_complex_molecule_id = id_complmol
    dm.save()

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed        
def step3(request, submission_id):
    """
    Go to step3 of the submission form (the one about protein chains and mutations)
    As in the previous step, once the template is loaded a javascript AJAx request will be triggered to 
    analyze the protein chains in our dynamics PDB file
    For you are my land, and you always will be; the voice ever calling me to you...
    """
    context = { 
        'step' : '3',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
     }
    return render(request,'dynadb/step3.html', context, status=200)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def step3_submit(request, submission_id,):
    """
    Submit into the database the data obtained from the step3 submission form
    """
    # Some initial variables, including users and timestamps
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    dictpost = { key : request.POST[key].lstrip() for key in request.POST }
    dictpost['submission_id'] = submission_id
    creation_fields={
               'creation_timestamp':timezone.now(),
               'created_by_dbengine':def_user_dbengine, 
               'created_by':def_user,
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    update_fields = {
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    # Get Model object of this submission object and load its pdb file with MDtraj
    dm = DyndbModel.objects.get(dyndbsubmissionmodel__submission_id=submission_id)
    id_model = dm.id
    modelfile_path = DyndbFilesModel.objects.get(id_model=id_model).id_files.filepath
    pdbmodel = md.load_pdb(settings.MEDIA_ROOT + modelfile_path, standard_names=False).top
    # Get Dynamics object of this submission object and load its pdb file with MDtraj
    dd = DyndbDynamics.objects.get(submission_id=submission_id)
    id_dyn = dd.id
    # Get arrays with the form numbers of the submitted proteins 
    entries_ids = request.POST['num_entries'].split(',')
    # Get arrays with the form numbers of segments and mutations
    mutations_ids = {}
    segments_ids = {}
    for entry_id in entries_ids:
        segments_ids[entry_id] = request.POST['num_segs'+entry_id].split(',')
        mutations_ids[entry_id] = request.POST['num_muts'+entry_id].split(',') if request.POST['num_muts'+entry_id] else [] 
    # For every protein entry
    prots = set()
    for entry_id in entries_ids:
        # IF this entry has no uniprotkbac, assign an empty string as token
        if 'prot_uniprot'+entry_id not in dictpost:
            dictpost['prot_uniprot'+entry_id] = ''
        # Protein entry 
        prot_id = save_protein_table(dictpost, entry_id, submission_id, mutations_ids, update_fields, creation_fields)
        # Relational tables for DyndbProtein
        # Carry the lad, that's born to be king, over the sea to Skye
        interprot_tables(dictpost, entry_id, prot_id, submission_id)
        # Stablish cannonical protein for our entry
        save_cannonical_proteins(dictpost, entry_id, submission_id, prot_id, update_fields, creation_fields)
        # Save receptor prot_id for later
        if not 'notaGPCR'+entry_id in dictpost:
            prot_id_receptor = prot_id
        else:
            prot_id_receptor = False
        # Delete any previous mutations before saving new ones
        DyndbModeledResidues.objects.filter(id_protein=prot_id).delete()
        # Save modeled residues (segments, as I call them) entries
        modelres_id = None
        for seg_id in segments_ids[entry_id]:
            modelres_id = save_modeled_residues(dictpost, seg_id, entry_id, prot_id, id_model, submission_id, modelres_id)   
        # Delete any previous mutations before saving new ones
        DyndbProteinMutations.objects.filter(id_protein=prot_id).delete()
        # Save mutations
        for mut_id in  mutations_ids[entry_id]:
            save_mutations(dictpost, mut_id, entry_id, prot_id, submission_id)        
        # set of prot ids for later
        prots.add(prot_id)
    # If there is no receptor in the system just take the latest protein and get over it
    prot_id_receptor = prot_id
    # Save complex if required
    save_complex_related(submission_id, id_model, prots, creation_fields, prot_id_receptor)
    # Once everything is done, go to step 4
    context = { 
        'step' : '4',
        'submission_id' : submission_id,
        'max_step': check_submission_status(submission_id),
        'repeated_step' : False, #Repeated step?,
    }
    return render(request,'dynadb/step4.html', context, status=200)

###### STEP 4: SImulation files
def get_fdbREFF(submission_id):
    """
    Get References form for step5
    """
    # Find if there are already references for this submission
    DR_values = DyndbReferences.objects.filter(dyndbreferencesdynamics__id_dynamics__submission_id=submission_id).values(
        'doi',
        'authors',
        'title', 
        'pmid', 
        'journal_press', 
        'issue', 
        'volume', 
        'pages', 
        'pub_year', 
        'dbname', 
        'url'
        )
    if len(DR_values):
        fdbREFF = dyndb_ReferenceForm(initial=DR_values[0]) 
    else:
        fdbREFF = dyndb_ReferenceForm()
    return(fdbREFF)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed        
def step4(request, submission_id):
    """
    Go to step4 of the submission form (the one about submittion files)
    """
    context = { 
        'step' : '4',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
    }
    return render(request,'dynadb/step4.html', context, status=200)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def step4_submit(request, submission_id):
    """
    Save files from step4 into database
    """
    for uh in request.upload_handlers:
        uh = TemporaryFileUploadHandlerMaxSize(request,8589934592 ) #Increase size limit to 8Gb by file
    # Some initial variables
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    dictpost = { key : request.POST[key] for key in request.POST }
    dictpost['submission_id'] = submission_id
    dictfiles = { key : request.FILES[key] for key in request.FILES }
    creation_fields={
               'creation_timestamp':timezone.now(),
               'created_by_dbengine':def_user_dbengine, 
               'created_by':def_user,
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    update_fields = {
               'update_timestamp':timezone.now(),
               'last_update_by_dbengine':def_user_dbengine,
               'last_update_by':def_user
               }
    numtypes = {
                'dyn' : 1,
                'trj' : 2,
                'prm' : 3,
                'oth' : 4,
                'prt' : 5
    }
    # Get Dynamics object of this submission object and get its pdbfile path
    dd = DyndbDynamics.objects.get(submission_id=submission_id)
    id_dyn = dd.id
    pdbpath = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id, type=0)[0].id_files.filepath
    # First of all, lets save what has been uploaded
    for filekey in dictfiles:
        numtype = numtypes[filekey]
        # Check if at least a file of this type exists already in our server for this submission_id
        DSDF = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id, type=numtype)
        # Get list of all files submitted in this input thing, and iterate over them
        files_list = request.FILES.getlist(filekey)
        i=0
        for filecontent in files_list:
            # Get file extension
            (up_filename, ext) = filecontent.name.split('.', 1)
            # Check if file already exists in database. If so, overwrite
            if len(DSDF)>i:
                # Save file
                dsdf = DSDF[i]
                df = dsdf.id_files
                dfd = dsdf.files_dynamics_id
                filepath = dsdf.filepath
                # Update timestamps in DyndbFiles
                DyndbFiles.objects.filter(pk=df.id).update(**update_fields)
            # In other case, new tables must be created
            else:
                basepath = '/Dynamics'
                baseurl = "/dynadb/files/Dynamics"
                # Get file DyndbFileTypes id. The first one, because whatever
                dft = DyndbFileTypes.objects.filter(extension=ext)[0]
                # Save new DyndbFiles entry. The url, filepath and filename will be stablished once we have created the entry
                placeholder = '%s_%s_%d'%('placeholder',id_dyn,i)
                files_dict = {
                    'filename': placeholder,
                    'id_file_types' : dft.id, 
                    'description' : filekey,
                    'filepath' : placeholder,
                    'url' : placeholder,
                }
                files_dict.update(creation_fields)
                Df = dyndb_Files(files_dict)
                print(Df.errors, placeholder)
                df = Df.save()
                file_id = df.id
                # Now that we have the file_id, create filenames, paths and urls accordingly
                fileurl = "%s/dyn%s/%d_%s_%s.%s" %(baseurl,submission_id,file_id,filekey,id_dyn,ext)
                filepath = "%s/dyn%s/%d_%s_%s.%s" %(basepath,submission_id,file_id,filekey,id_dyn,ext)
                filename = "%d_%s_%s.%s" % (file_id,filekey,id_dyn,ext)
                df.url = fileurl
                df.filepath = filepath
                df.filename = filename
                df.save()
                # Save DyndbFilesDynamics table
                filesdyn_dict = {
                    'id_dynamics' : id_dyn, 
                    'id_files' : file_id,
                    'type' : numtype,
                    'framenum' : 1 # Provisional. Changed bellow
                }
                Dfd = dyndb_Files_Dynamics(filesdyn_dict)
                if Dfd.is_valid():
                    dfd = Dfd.save()
                else:
                    error=Dfd.errors.as_text()
                    response = HttpResponse(error,status=422,sreason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                filedyn_id = dfd.id
                # Save DyndbSubmissionDynamicsFiles
                filesdynsub_dict = {
                    'submission_id' : submission_id,
                    'type' : numtype,
                    'filename' : filename,
                    'filepath' : filepath,
                    'url' : fileurl,
                    'filenum' : i,
                    'framenum' : 1, # Provisional again
                    'id_files' : file_id,
                    'files_dynamics_id' : filedyn_id
                } 
                Dsdf = dyndb_submission_dynamics_files(filesdynsub_dict)
                if Dsdf.is_valid():
                    dsdf = Dsdf.save()
                else:
                    error=Dfd.errors.as_text()
                    response = HttpResponse(error,status=422,sreason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response

            # Numfile
            i+=1
            # Save file in server
            # Rain comes over the gray hills, and on the air a soft goodbye
            save_uploadedfile(filepath,filecontent)
            # If file is trajectory, get number of frames and save it 
            if filekey=='trj':
                framenum = get_frames_num(settings.MEDIA_ROOT + filepath,'traj',ext)
                dsdf.framenum = framenum
                dfd.framenum = framenum
                dsdf.save()
                dfd.save()
    # Once everything is done, go to step 5
    context = { 
        'step' : '5',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
        "fdbREFF" : get_fdbREFF(submission_id),
        'repeated_step' : False, #Repeated step?,
    }
    return render(request,'dynadb/step5.html', context, status=200)

##### STEP 5: References

# DOI RETRIEVER
def doitopmid(doi):
    """
    Return the PMID for a given DOI.
    """

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + doi + "&format=json"
    r = requests.get(url)
    info_pubmed_dict = json.loads(r.text)
    pmid = info_pubmed_dict["esearchresult"]["idlist"][0]# PMID:
    return int(pmid)

def doitobib(doi):
    """
    Return a bibTeX string of metadata for a given DOI.
    """
    #IMPORTS
    from requests.exceptions import HTTPError,ConnectionError,Timeout,TooManyRedirects

    #OUTDATA
    data = dict()
    errdata = dict()

    #URL
    url = "https://doi.org/" + doi
    headers = {"accept": "application/x-bibtex"}
    try: 
        r = requests.get(url, headers = headers)
        info_r = r.text

        # Clean the data
        info = info_r.replace("\n", "").replace("\t", "").split(",") 
        # Extract info and store it on different variables
        for dt in info: 
            if "doi =" in dt: #DOI
                l_doi = dt.split("{")
                doi_in = l_doi[-1].replace("}","")
                data["doi"] = doi_in
            elif "author =" in dt: #Author
                l_auth = dt.split("=")
                auth = l_auth[-1].replace("{","").replace("\\", "").replace("'","").replace("}","")
                auth = re.sub("[^A-Z0-9_\s-]", "", auth,0,re.IGNORECASE).replace("and", ",").replace(" ,",",")[1:]
                data["auth"] = auth
            elif "title =" in dt: #Title
                l_title = dt.split("=")
                title = l_title[-1].replace("{","").replace("}","")[1:]
                data["title"] = title
            elif "journal =" in dt: #Journal or Press
                l_journal = dt.split("=")
                journal = l_journal[-1].replace("{","").replace("}","")[1:]
                data["journal"] = journal
            elif "year =" in dt: #Publication year::
                l_year = dt.split("=")
                year = l_year[-1][1:]
                data["year"] = int(year)
            elif "number =" in dt: #Issue:
                l_number= dt.split("=")
                number = l_number[-1].replace("{","").replace("}","")[1:]
                data["issue"] = int(number)
            elif "volume =" in dt: #Volume:
                l_volume = dt.split("=")
                volume = l_volume[-1].replace("{","").replace("}","")[1:]
                data["volume"] = int(volume)
            elif "pages =" in dt: #Pages:
                l_pages = dt.split("=")
                pages = l_pages[-1].replace("{","").replace("}","")[1:]
                if "--" in pages:
                    data["pages"] = pages.replace("--","-")
                else:
                    data["pages"] = pages
            elif "url =" in dt: #URL:
                l_url = dt.split("=")
                url = l_url[-1].replace("{","").replace("}","")[1:]
                data["url"] = url
        
        # Extract PMID
        try: 
            data["pmid"] = doitopmid(doi)
        except Exception as e: 
            print(e)
            data["pmid"] = doitopmid(doi_in)
    except HTTPError:
        errdata['Error'] = True
        errdata['ErrorType'] = 'HTTPError'
        errdata['status_code'] = r.status_code
        errdata['reason'] = r.reason
    except ConnectionError as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'ConnectionError'
        errdata['reason'] = 'Cannot connect.'
    except Timeout as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'Timeout'
        errdata['reason'] = 'Timeout exceeded.'
    except TooManyRedirects as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'TooManyRedirects'
        errdata['reason'] = 'Too many redirects.'
    except StreamSizeLimitError as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'StreamSizeLimitError'
        errdata['reason'] = str(e)
    except StreamTimeoutError as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'StreamTimeoutError'
        errdata['reason'] = str(e)
    except ParsingError as e:
        errdata['Error'] = True
        errdata['ErrorType'] = 'ParsingError'
        errdata['reason'] = str(e)
    except:
        errdata['Error'] = True
        errdata['ErrorType'] = 'Internal'
        do_not_skip_on_debug = True
        raise
    finally:
        try:
            r.close()
        except:
            pass
        return (data,errdata)

@login_required
def doi_info(request):
    """
    Obtain data from doi, and send it back
    """
    # doi = "10.1093/bioinformatics/btaa117"
    doi = request.GET['doi_in'].replace(' ','')
    submission_id = request.GET['submission_id']
    (data,errdata) = doitobib(doi)
    return HttpResponse(json.dumps(data),content_type='step5/'+submission_id)   

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
@test_if_closed        
def step5(request, submission_id):
    """
    Go to step5 of the submission form (the one about references and publications)
    """
    context = { 
        'step' : '5',
        'submission_id' : submission_id,
        'max_step' : check_submission_status(submission_id),
        "fdbREFF" : get_fdbREFF(submission_id)
     }
    
    #Repeated step?
    context['repeated_step'] = False

    return render(request,'dynadb/step5.html', context, status=200)

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def step5_submit(request, submission_id):
    """
    Save references for this submission
    Juanma's code. No idea what's going on here
    """
    sub = submission_id
    action="/".join(["/dynadb/REFERENCEfilled",sub])
    now=timezone.now()
    dynamics_id = DyndbDynamics.objects.get(submission_id=submission_id).pk
    user=User.objects.get(dyndbsubmission__dyndbdynamics=dynamics_id) 
    author=user.first_name + " "+ user.last_name+", "+user.institution     
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    initREFF={'dbname':None, 'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    fdbREFF = dyndb_ReferenceForm(request.POST)
    SubmitRef=True
    if (request.POST['doi']):
        qRFdoi=DyndbReferences.objects.filter(doi=request.POST['doi'])
        if qRFdoi.exists():
            iii1="Please, Note that the reference you are trying to submit has a DOI previously stored in the GPCRmd. Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCRmd administrator"
            response = HttpResponse(iii1,content_type='text/plain; charset=UTF-8')
            FRpk = qRFdoi.values_list('id',flat=True)
            SubmitRef=False
           # return response
    if (request.POST['pmid']):
        qRFpmid=DyndbReferences.objects.filter(pmid=request.POST['pmid'])
        if qRFpmid.exists():
            iii1="Please, Note that the reference you are trying to submit has a PMID previously stored in the GPCRmd.  Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCRmd administrator"
            response = HttpResponse(iii1,content_type='text/plain; charset=UTF-8')
            SubmitRef=False
            FRpk = qRFpmid.values_list('id',flat=True)
           # return response
    if SubmitRef:
        if fdbREFF.is_valid(): 
            # process the data in form.cleaned_data as required
            formREFF=fdbREFF.save(commit=False)
            for (key,value) in initREFF.items():
                setattr(formREFF, key, value)
            formREFF.save()
            FRpk = formREFF.pk
        else:
            iii=fdbREFF.errors.as_text()
            response = HttpResponse(iii,status=422,sreason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
    # Check whether the fdbREFF instance of dyndb_ReferenceForm is valid:
    SubmitRef=True
    qRFdoi=DyndbReferences.objects.filter(doi=request.POST['doi'])
    FRpk = FRpk[0]
    qSubmission=DyndbSubmission.objects.filter(id=submission_id)
    qT=list(qSubmission.filter(dyndbsubmissionprotein__submission_id=submission_id,dyndbsubmissionmolecule__submission_id=submission_id,dyndbsubmissionmodel__submission_id=submission_id,dyndbdynamics__submission_id=submission_id).values('dyndbsubmissionprotein__protein_id','dyndbsubmissionmolecule__molecule_id','dyndbsubmissionmolecule__molecule_id__id_compound','dyndbsubmissionmodel__model_id','dyndbdynamics__id'))
    dictprot={'id_protein':qT[0]['dyndbsubmissionprotein__protein_id'], 'id_references':FRpk}
    dictmod={'id_model':qT[0]['dyndbsubmissionmodel__model_id'], 'id_references':FRpk }
    dictdyn={'id_dynamics':qT[0]['dyndbdynamics__id'], 'id_references':FRpk }
    refprot=dyndb_References_Protein(dictprot)
    if SubmitRef:
        if not qRFdoi.filter(dyndbreferencesprotein__id_protein=qT[0]['dyndbsubmissionprotein__protein_id'],dyndbreferencesprotein__id_references=FRpk).exists():
            if refprot.is_valid():
                refprot.save()
            else:
                print("refprot is not valid",refprot.errors.as_text())
    refmod=dyndb_References_Model(dictmod)
    if  SubmitRef:
        if not qRFdoi.filter(dyndbreferencesmodel__id_model=qT[0]['dyndbsubmissionmodel__model_id'],dyndbreferencesmodel__id_references=FRpk).exists():
            if refmod.is_valid():
                refmod.save()
            else:
                print("refmod is not valid",refmod.errors.as_text())
    refdyn=dyndb_References_Dynamics(dictdyn)
    if SubmitRef:
        if not qRFdoi.filter(dyndbreferencesdynamics__id_dynamics=qT[0]['dyndbdynamics__id'],dyndbreferencesdynamics__id_references=FRpk).exists():
            if refdyn.is_valid():
                refdyn.save()
                print("refdyn may  be saved ",refdyn.errors.as_text())
            else:
                print("refdyn is not valid",refdyn.errors.as_text())
    dictmol={}
    dictcomp={}
    i=0
    for l in qT:
        dictmol[i]={'id_molecule':qT[i]['dyndbsubmissionmolecule__molecule_id'],  'id_references':FRpk}
        refmol=dyndb_References_Molecule(dictmol[i])                                     
        if SubmitRef:
            if not qRFdoi.filter(dyndbreferencesmolecule__id_molecule=qT[i]['dyndbsubmissionmolecule__molecule_id'],dyndbreferencesmolecule__id_references=FRpk).exists():
                if refmol.is_valid():                                                         
                    refmol.save()                                                             
                else:                                                                         
                    print("refmol is not valid",refmol.errors.as_text())                      
        dictcomp[i]={'id_compound':qT[i]['dyndbsubmissionmolecule__molecule_id__id_compound'],  'id_references':FRpk}
        refcomp=dyndb_References_Compound(dictcomp[i])
        if not SubmitRef:
            if not qRFdoi.filter(dyndbreferencescompound__id_compound=qT[i]['dyndbsubmissionmolecule__molecule_id__id_compound'],dyndbreferencescompound__id_references=FRpk).exists():
                if refcomp.is_valid():
                    refcomp.save()
                else:
                    print("refcomp is not valid",refcomp.errors.as_text())
        i=i+1
    # Set submissions as publshed
    DS = DyndbSubmission.objects.filter(pk=submission_id)
    DD = DyndbDynamics.objects.filter(submission_id=submission_id)
    # End of submission    
    return submission_summaryiew(request,submission_id)
