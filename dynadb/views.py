# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import Count
from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone
from django.template import loader
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth.decorators import login_required
from accounts.user_functions import user_passes_test_args, is_submission_owner, is_published_or_submission_owner
from collections import OrderedDict
from sendfile import sendfile
from pathlib import Path
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
import tarfile
from operator import itemgetter
from os import listdir
from os.path import isfile, normpath
from django.db.models.functions import Concat
from django.db.models import CharField,TextField, Case, When, Value as V, F
from .customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension, DownloadGenericError, RequestBodyTooLarge, FileTooLarge, TooManyFiles
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from .sequence_tools import get_mutations, check_fasta
from .csv_in_memory_writer import CsvDictWriterNoFile, CsvDictWriterRowQuerySetIterator
from .uploadhandlers import TemporaryFileUploadHandlerMaxSize,TemporaryMoleculeFileUploadHandlerMaxSize
from .molecule_properties_tools import open_molecule_file, check_implicit_hydrogens, check_non_accepted_bond_orders, generate_inchi, generate_inchikey, generate_smiles, get_net_charge, write_sdf, generate_png, stdout_redirected, neutralize_inchikey, standarize_mol_by_inchi,validate_inchikey,remove_isotopes
from rdkit.Chem import MolFromInchi,MolFromSmiles
from .molecule_download import retreive_compound_data_pubchem_post_json, retreive_compound_sdf_pubchem, retreive_compound_png_pubchem, CIDS_TYPES, pubchem_errdata_2_response, retreive_molecule_chembl_similarity_json, chembl_get_compound_id_query_result_url,get_chembl_molecule_ids, get_chembl_prefname_synonyms, retreive_molecule_chembl_id_json, retreive_compound_png_chembl, chembl_get_molregno_from_html, retreive_compound_sdf_chembl, chembl_errdata_2_response
#from .models import Question,Formup
#from .forms import PostForm
from structure.models import StructureType, StructureModelLoopTemplates
from protein.models import Protein
from common.models import  WebResource
from .models import DyndbBinding,DyndbEfficacy,DyndbReferencesExpInteractionData,DyndbExpInteractionData,DyndbReferences, DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel,  DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbCannonicalProteins,  DyndbSubmissionMolecule, DyndbSubmissionProtein,DyndbComplexProtein,DyndbReferencesProtein,DyndbComplexMoleculeMolecule,DyndbComplexMolecule,DyndbComplexCompound,DyndbReferencesMolecule,DyndbReferencesCompound,DyndbComplexExp
from .models import DyndbSubmissionProtein, DyndbFilesDynamics, DyndbReferencesModel, DyndbModelComponents,DyndbProteinMutations,DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbModeledResidues, DyndbDynamicsMembraneTypes, DyndbDynamicsSolventTypes, DyndbDynamicsMethods, DyndbAssayTypes, DyndbSubmissionModel, DyndbFilesModel,DyndbSubmissionDynamicsFiles,DyndbSubmission, DyndbReferences
from .pdbchecker import split_protein_pdb, split_resnames_pdb, molecule_atoms_unique_pdb, diff_mol_pdb, residue_atoms_dict_pdb, residue_dict_diff, get_atoms_num

#from django.views.generic.edit import FormView
from .forms import dyndb_ProteinForm, dyndb_Model, dyndb_Files,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List,  dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model
from .forms import  dyndb_ProteinForm, dyndb_Model, dyndb_Files,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List,  dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model, dyndb_Protein_Cannonical_Protein, dyndb_Complex_Compound, dyndb_References_Protein, dyndb_References_Model, dyndb_References_Molecule, dyndb_References_Dynamics, dyndb_References_Compound 
#from .forms import NameForm, TableForm
from .pipe4_6_0 import *
from time import sleep
from random import randint
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from .models import Model2DynamicsMoleculeType, smol_to_dyncomp_type
from django.conf import settings
from django.views.defaults import server_error
from revproxy.views import ProxyView

model_2_dynamics_molecule_type = Model2DynamicsMoleculeType()

# Custom view function wrappers
from functools import wraps
from django.utils.decorators import available_attrs
def default_500_handler(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
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
    @wraps(view_func, assigned=available_attrs(view_func))
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
    @wraps(view_func, assigned=available_attrs(view_func))
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
            iii1="Please, Note that the reference you are trying to submit has a DOI previously stored in the GPCRdb. Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCR DB administrator"
            print(iii1)
            response = HttpResponse(iii1,content_type='text/plain; charset=UTF-8')
            FRpk = qRFdoi.values_list('id',flat=True)
            SubmitRef=False
           # return response
        if qRFpmid.exists():
            iii1="Please, Note that the reference you are trying to submit has a PMID previously stored in the GPCRdb.  Check if the stored entry corresponds to the one you are submitting. Click 'ok' to continue to the stored reference. In case of error in the stored data, contact the GPCR DB administrator"
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
        result='>uniprot:\n'+result[0]+'\n>mutant:\n'+result[1]
        request.session[alignment_key]=result
        tojson={'alignment':result, 'message':'' , 'userkey':alignment_key}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')
    else:
        alignment=request.session[alignment_key]
        return render(request,'dynadb/show_alignment.html', {'alig':alignment})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
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



#   _____________________________________________________________ 
#   _____________________________________________________________ 
#   _____________________________________________________________ 
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
                 print(qcompo_mol,"ANTES UPDATE")
                 qcompo_mol.update(std_id_molecule=None)
                 print(qcompo_mol,"DESPUES UPDATE")
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
def PROTEINview(request, submission_id):
    
    p= submission_id
    print ("submission_id ==",submission_id)
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    print("HOLA  ", def_user)
    
    if request.method == 'POST':
        
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
         # if dictprot[ii]['name'] == '' and dictprot[ii]['uniprotkbac'] == '':
         #     dictprot[ii]['name'] = 'Unnamed Protein'
         #     dictprot[ii]['uniprotkbac'] = 'None'
         #     dictprot[ii]['isoform'] = 10000
         #     dictprot[ii]['isoform'] = 10000
                
             
           #print("\n\nNOOOOOOOOOOOOOOOO\n")
           #if 'isoform' not in dictprot[ii].keys() or dictprot[ii]['isoform']=='':
           #    dictprot[ii]['isoform']=''

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

#### Complex protein should be filled in the Model form

#           if 'receptor' in dictprot[ii].keys():
#               dictCP[ii]={'is_receptor':dictprot[ii]['receptor'],'id_protein':formPF[ii].pk,'id_complex_exp':1} #id_complex_exp should be Corrected!!!!
#               fdbCP[ii]=dyndb_Complex_Protein(dictCP[ii])
#               if fdbCP[ii].is_valid():
#                   fdbCP[ii].save()
#               else:
#                   iii1=fdbCP[ii].errors.as_text()
#                   print("fdbCP[",ii,"] no es valido")
#                   print("!!!!!!Errores despues del fdbCP[",ii,"]\n",iii1,"\n")
#             

##### Create a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
##### 
############# OTHER NAMES SOLO SE RELLENA EN LA PROTEINA CANONICA!!!!! 

#           if len(dictprot[ii]['other_names'])> 0:
#               listON[ii]=dictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
#               listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
#               dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
#               fdbOPN[ii]={}
#               numON=0
#           
#               for on in listON[ii]:

#                   numON=numON+1
#                   dictOPN[ii][numON]={}
#                   fdbOPN[ii][numON]={}
#                   dictOPN[ii][numON]['other_names']=on
#                   dictOPN[ii][numON]['id_protein']=formPF[ii].pk
#                   fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
#                   if fdbOPN[ii][numON].is_valid():
#                       fdbOPN[ii][numON].save()
#                   else:
#                       iii1=fdbOPN[ii][numON].errors.as_text()
#                       print("fdbOPN[",ii,"] no es valido")
#                       print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
#           else:
#               print("NO OTHER NAMES have been found\n")

#####  Fill dyndb_Protein_SequenceForm fields depending on whether the protein is mutated   
#####  'msequence' does not appear in models but it does in the html so the information in 
#####  this html field should be tranfered into the 'sequence' field in the form instance      

            if 'sequence' not in dictprot[ii].keys():
                dictprot[ii]['sequence']="TOTO"
                print("No Sequence found (NORMAL)")
                if seq is None:
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    DyndbProtein.objects.filter(id=formPF[ii].pk).delete()
                    DyndbSubmissionProtein.objects.filter(protein_id=formPF[ii].pk).delete()
                    return response

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
                if len(nummutl[ii])==0:
                    response = HttpResponse('Protein mutations have not been obtained. Please follow these steps: 1) After having obtained the retrieved data about the current protein from the UniprotKB DB ("Wild-type" sequence can be manually entered if no data about the protein exist in UniprotKB) and having provided the "Mutant sequence" in the corresponding field in the form, remember to align the "Mutant sequence" to the Wild type one by clicking the "Align to the wild type" button. Then, click the "Get mutations" button and the check if the mutations in the "Protein Mutations" table are correct. If no results are obtained, please make the database administrator know.' ,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response

##### Let's create the field 'id_protein' in dyndb_Protein_MutationsForm so that an entry could be registered in the version not supporting Mutations scripts

    #           if len(nummutl[ii])==0:
    #               nummutl[ii].append(0)
    #               dictPM[ii][0]={}
    #               dictPM[ii][0]['id_protein']=formPF[ii].pk 
    #               print("NO info about mutations has been provided but an entry should be registered")

                mseq=dictprot[ii]['msequence']
                seq=dictprot[ii]['sequence']
                lmseq=len(mseq)
                initPS[ii]={'id_protein':formPF[ii].pk,'sequence':mseq,'length':lmseq} 
                print ("PIPOLLLLLLLLLLLLLLLLLLL\n",seq,"\n",mseq)
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
                        print ("AAAAAAA ",el)
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
                            print("mutation #",nm," ",dictPM[ii][nm])
                 
                            if fdbPM[ii][nm].is_valid():
                                print("PM is valid")
                                fdbPM[ii][nm].save()
                            else:
                                iii1=fdbPM[ii][nm].errors.as_text()
                                print("fdbPM[",ii,"][",nm,"] no es valido")
                                print("!!!!!!Errores despues del fdbPM[",ii,"][",nm,"]\n",iii1,"\n")
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
            print("\n\nSEQUENCE INSTANCE\n\n")
            if fdbPS[ii].is_valid():
                fdbPS[ii].save()
                print ("hasta aqui")
            else:
                iii1=fdbPS[ii].errors.as_text()
                print("fdbPS[",ii,"] no es valido")
                print("!!!!!!Errores despues del fdbPS[",ii,"] \n",iii1,"\n")
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
                print("PPPPPPP dunikb",dunikb)
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
                        print("\n primary  key aux: ", formPFaux[ii].pk )
                    else:
                        iii1=fdbPFaux[ii].errors.as_text()
                        print("fdbPFaux",ii," no es valido")
                        print("!!!!!!Errores despues del fdbPFaux[",ii,"]\n",iii1,"\n")
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
                            print("fdbSPaux[",ii,"] no es valido")
                            print("!!!!!!Errores despues del fdbSPaux[",ii,"]\n",iii1,"\n")
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
        #return HttpResponseRedirect("/".join(["/dynadb/PROTEINfilled",submission_id]), {'submission_id':submission_id, 'dictprotinit':dictprotinit, 'dictprot':dictprot })
 #       return HttpResponseRedirect(request, '/dynadb/PROTEINfilled.html', {'submission_id':submission_id, 'dictprotinit':dictprotinit, 'dictprot':dictprot })

        
    # if a GET (or any other method) we'll create a blank form
    else:
#        qSub=DyndbSubmissionProtein.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).values_list('submission_id',flat=True)[0]).order_by('int_id')
 #       print(qSub)
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
         
            return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id})

        else:
            print(len(qSub),"len")
            print("SEGUROi")
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
  

        return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id})
#       return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS,'fdbPM':fdbPM,'fdbOPN':fdbOPN,'submission_id':submission_id})
#       return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS, 'fdbOPN':fdbOPN})
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
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
    data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(data, content_type='application/json')


def count_dynamics(result_id,result_type):
    '''Counts how many times a given result_id appears in a simulation and saves its id. Returns the names list and the number of times it appeas.'''
    dynset=set()
    if result_type=='compound': #we need to count complexcompound too!!!!
        for molecule in DyndbMolecule.objects.filter(id_compound=result_id):
            somenumber,dynsets=count_dynamics(molecule.id,'molecule')
            dynset=dynset.union(dynsets)

    for simu in DyndbDynamics.objects.select_related('id_model__id_complex_molecule__id_complex_exp').all():
        if result_type=='protein':
            modelobj=DyndbModel.objects.select_related('id_protein').get(pk=simu.id_model.id).id_protein
            if modelobj is not None:
                if modelobj.id==result_id:
                    dynset.add(simu.id)
                    continue
            else:
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
            imagepath=imagepath.replace("/protwis/sites/","/dynadb/") #this makes it work
        except:
            imagepath=''
    else:
        try:
            imagepath=DyndbFilesMolecule.objects.select_related('id_files').filter(id_molecule=id).filter(type=2)[0].id_files.filepath
            imagepath=imagepath.replace("/protwis/sites/","/dynadb/") #this makes it work
        except:
            imagepath=''

    return imagepath

@textonly_500_handler
def ajaxsearcher(request):
    '''Searches user input among indexed data. If "search by id" option is allowed, a simple database query is used using that ID.'''
    if request.method == 'POST':
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
            tojson={'compound':compoundlist, 'protein':proteinlist,'molecule':moleculelist, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        if request.POST.get("id_search",False)=='true': #uses user_input as an ID to search the database.
            if return_type=='gpcr' or return_type=='All':
                try:
                    protein=DyndbProtein.objects.filter(is_published=True).get(pk=user_input)
                    isrec=protein.receptor_id_protein
                    if isrec is not None:
                        gpcrlist.append([str(protein.id),str(protein.name)])
                except:
                    gpcrlist=[]

            if return_type=='protein' or return_type=='All':
                try:
                    protein=DyndbProtein.objects.filter(is_published=True).get(pk=user_input)
                    isrec=protein.receptor_id_protein
                    if isrec is None:
                        proteinlist.append([str(protein.id),str(protein.name)])
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
                    moleculelist.append([str(molecule.id),str(molecule.inchikey),imagepath,compname,netcharge])
                except:
                    moleculelist=[]


            if return_type=='compound' or return_type=='All': #call the corresponding view??????
                try:
                    compound=DyndbCompound.objects.select_related('std_id_molecule').filter(is_published=True).get(pk=user_input)
                    imagepath=get_imagepath(user_input, 'compound')
                    compoundlist.append([ str(compound.id),str(compound.name),'',imagepath ])
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
                            if str(mol.id) not in [i[0] for i in moleculelist]: #molecule
                                mol_id=mol.id
                                netcharge=mol.net_charge
                                if netcharge>0:
                                    netcharge='+'+str(netcharge)
                                comp=res.id_compound #DyndbMolecule.objects.get(pk=mol_id).id_compound.id
                                compname=mol.id_compound.name # DyndbMolecule.objects.get(pk=mol_id).id_compound.name
                                imagepath=get_imagepath(mol.id, 'molecule')
                                moleculelist.append([str(mol_id),str(res.inchikey),imagepath,compname,netcharge]) 

                            imagepath=get_imagepath(res.id_compound, 'compound')
                        compoundlist.append([ str(res.id_compound),str(res.name),str(res.iupac_name),imagepath ])

                    elif 'protein' in str(res.id):
                        published=len(DyndbProtein.objects.filter(id=res.id_protein,is_published=True))>0
                        if ([str(res.id_protein),str(res.name)] not in gpcrlist) and ([str(res.id_protein),str(res.name)] not in proteinlist) and published:
                            protein=DyndbProtein.objects.get(pk=res.id_protein)
                            isrec=protein.receptor_id_protein
                            if isrec is None:
                                proteinlist.append([str(protein.id),str(protein.name)])
                            else:
                                gpcrlist.append([str(protein.id),str(protein.name)])
                                
                            #include all mutants of the found protein:    
                            for mutants in DyndbProtein.objects.filter(uniprotkbac=protein.uniprotkbac):
                                isrecm=mutants.receptor_id_protein
                                if isrecm is None and [str(mutants.id),str(mutants.name)] not in proteinlist:
                                    proteinlist.append([str(mutants.id),str(mutants.name)])
                                if isrecm is not None and [str(mutants.id),str(mutants.name)] not in gpcrlist:
                                    gpcrlist.append([str(mutants.id),str(mutants.name)])


                    elif 'molecule' in str(res.id):
                        mol_id=res.id.split('.')[2]
                        published=len(DyndbMolecule.objects.filter(id=mol_id,is_published=True))>0
                        if str(mol_id) not in [i[0] for i in moleculelist] and published: #molecule
                            molobj=DyndbMolecule.objects.select_related('id_compound').get(pk=mol_id)
                            netcharge=molobj.net_charge
                            if netcharge>0:
                                netcharge='+'+str(netcharge)
                            comp=molobj.id_compound.id
                            compname=molobj.id_compound.name
                            imagepath=get_imagepath(mol_id,'molecule')
                            moleculelist.append([str(mol_id),str(res.inchikey),imagepath,compname,netcharge]) #define inchikey in searchindex

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
            tojson={'compound':[], 'protein':proteinlist,'gpcr':[],'molecule':[],'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        if return_type=='gpcr':
            tojson={'compound':[], 'protein':[],'gpcr':gpcrlist,'molecule':[],'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        elif return_type=='molecule':
            tojson={'compound':[], 'protein':[],'gpcr':[],'molecule':moleculelist,'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        elif return_type=='compound':
            tojson={'compound':compoundlist, 'protein':[],'gpcr':[],'molecule':[],'names':[], 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        elif return_type=='complex' or return_type=='model' or return_type=='dynamics':
            tojson={'compound':[], 'protein':[],'gpcr':[],'molecule':[], 'names':names, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

        elif return_type=='All': #no filter
            tojson={'compound':compoundlist, 'protein':proteinlist,'gpcr':gpcrlist,'molecule':moleculelist,'names':names, 'message':''}
            data = json.dumps(tojson)
            return HttpResponse(data, content_type='application/json')

###################################################################################################################################
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
                for dyn in DyndbDynamics.objects.filter(timestep__lte=request.POST.get('tstep') ):
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
        for cmolid in idlist:
            exp_id=DyndbComplexMolecule.objects.select_related('id_complex_exp').get(pk=cmolid).id_complex_exp.id
            liglist=[]
            receptorlist=[]

            for match in DyndbComplexCompound.objects.select_related('id_compound').filter(id_complex_exp=exp_id):
                if match.type==0 or match.type==1:
                    liglist.append(match.id_compound.name.rstrip())

            for rmatch in DyndbComplexProtein.objects.select_related('id_protein__receptor_id_protein','id_protein').filter(id_complex_exp=exp_id):
                if type(rmatch.id_protein.receptor_id_protein.id)==int:
                    receptorlist.append(rmatch.id_protein.name.rstrip())

            complex_list_names.append([exp_id, receptorlist, liglist])
        return complex_list_names

    elif return_type=='model':
        modelshowresult=[]
        for modid in idlist:
            print(modid)
            try:
                cmol_id=DyndbModel.objects.select_related('id_complex_molecule').get(pk=modid).id_complex_molecule.id
                getligrec([cmol_id],'complex')[1:]
                modelshowresult.append( [modid] + getligrec([cmol_id],'complex')[0][1:] )
                print('heeeeere', [modid] + getligrec([cmol_id],'complex')[0][1:] )
            except AttributeError: #model is an apoform
                modelshowresult.append([modid]+ [DyndbModel.objects.get(pk=modid).id_protein.name.rstrip()] )
                print('here',[modid]+ [DyndbModel.objects.get(pk=modid).id_protein.name.rstrip()])
        return modelshowresult

    else:
        dynresult=[]
        for dyn_id in idlist:
            cmol_id=DyndbDynamics.objects.select_related('id_model').get(pk=dyn_id).id_model.id
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
            if array[4]=='false':
                array[4]=False
            arrays_def.append(array)

    #{(1, 'AND'): ['protein', '1', 'true'], (0, ' '): ['molecule', '1', 'orto']}
    #{(0, ' '): ['molecule', '1', 'orto'], (1, 'AND'): [['protein', '1', 'true'], ['OR', 'protein', '2', 'true']]}

        resultlist=mainsearcher(arrays_def,return_type)
        print(resultlist,'these are the resullts')
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
            print(resultlist,'RESULTS')
            complex_list_names=getligrec(resultlist,'complex')
            print(complex_list_names)
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
                print(dyn_id,'is it NONE')
                if DyndbDynamics.objects.select_related('id_model__id_protein').get(pk=dyn_id).id_model.id_protein is not None:
                    tmplist.append(dyn_id)

        if request.POST.get('is_apo')=='com' or request.POST.get('is_apo')=='both':
            for dyn_id in resultlist:
                if DyndbDynamics.objects.select_related('id_model__id_protein').get(pk=dyn_id).id_model.id_protein is None:
                    tmplist.append(dyn_id)

        resultlist=tmplist

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
            for dyn in DyndbDynamics.objects.filter(timestep__lte=request.POST.get('tstep') ):
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

        resultlist=list(filter(lambda x: len(DyndbDynamics.objects.filter(id=x,is_published=True))>0,resultlist))
        dynresult=getligrec(dynlist,'dynamics')

        tojson={'result':resultlist ,'model':model_list,'dynlist':dynresult,'message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

###################################################################################
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
###################################################################################
###################################################################################
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
     #   return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')

    data['smiles'] = generate_smiles(mol)

    data['charge'] = get_net_charge(mol)
        
    try:    
        data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])

        data['inchikey'] = generate_inchikey(data['inchi']['inchi'])

        data['inchicol'] = 1
        data['inchicol'] = 1
    except:
        data['msg'] ='Error while computing InChIKey.'
        #print(data['msg'],file=logfile)
        #logfile.close()
       # data['msg'] = msg+' Please, see log file.'
     #   return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')

    SDFhandler.close()
    
    return data


@user_passes_test_args(is_published_or_submission_owner)
def query_protein(request, protein_id,incall=False):
    '''Returns database information about the given protein_id. If incall is True, it will return a dictionary, otherwise, it will retun an Http response.'''
    fiva=dict()
    actlist=list()
    fiva['mutations']=list()
    fiva['models']=list()
    fiva['other_names']=list()
    fiva['activity']=list()
    fiva['references']=list()
    protein_record = DyndbProtein.objects.select_related(None).get(pk=protein_id)
    fiva['Uniprot_id']=protein_record.uniprotkbac    
    fiva['Protein_name']=protein_record.name
    fiva['is_mutated']=protein_record.is_mutated
    #fiva['cannonical']=protein_record.id_cannonical_proteins.id_protein.id #3 hits
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
        ref=[match.id_references.doi,match.id_references.title,match.id_references.authors,match.id_references.url]
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        fiva['references'].append(ref)  

    for match in DyndbExpProteinData.objects.filter(id_protein=protein_id): #not working, but table incomplete so dont know if my fault.
        for match2 in DyndbProteinActivity.objects.filter(pk=match.id):
            fiva['activity'].append((match2.rvalue,match2.units,match2.description))
    if incall==True:
        return fiva
    #print('MODELS',fiva['models'])
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
@user_passes_test_args(is_published_or_submission_owner)
def query_molecule(request, molecule_id,incall=False):
    '''Returns information about the given molecule_id. If incall is True, it returns a simple dictionary, otherwise, an http response is returned. '''
    molec_dic=dict()
    molec_dic['inmodels']=list()
    molec_dic['references']=list()
    molobj=DyndbMolecule.objects.select_related('id_compound').get(pk=molecule_id)
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
    #print('path to image',molec_dic['imagelink'])
    for match in DyndbModelComponents.objects.filter(id_molecule=molecule_id):
        molec_dic['inmodels'].append(match.id_model.id)

    for molfile in DyndbFilesMolecule.objects.select_related('id_files').filter(id_molecule=molecule_id).filter(type=0):
        intext=open(molfile.id_files.filepath,'r')
        string=intext.read()
        molec_dic['sdf']=string

    for match in DyndbReferencesMolecule.objects.select_related('id_references').filter(id_molecule=molecule_id):
        ref=[match.id_references.doi,match.id_references.title,match.id_references.authors,match.id_references.url]
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        molec_dic['references'].append(ref)  
    if incall==True:
        return molec_dic
    return render(request, 'dynadb/molecule_query_result.html',{'answer':molec_dic})
    
@user_passes_test_args(is_published_or_submission_owner)
def query_molecule_sdf(request, molecule_id):
    '''Gets the sdf file of the given molecule_id '''
    for molfile in DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).filter(type=0): #MAKE SURE ONLY ONE FILE IS POSSIBLE
        intext=open(molfile.id_files.filepath,'r')
        string=intext.read()
    with open('/tmp/'+str(molecule_id)+'_gpcrmd.sdf','w') as fh:
        fh.write(string)
    with open('/tmp/'+str(molecule_id)+'_gpcrmd.sdf','r') as f:
        data=f.read()
        response=HttpResponse(data, content_type=mimetypes.guess_type('/tmp/'+str(molecule_id)+'_gpcrmd.sdf')[0])
        response['Content-Disposition']="attachment;filename=%s" % (str(molecule_id)+'_gpcrmd.sdf') #"attachment;'/tmp/'+protein_id+'_gpcrmd.fasta'"
        response['Content-Length']=os.path.getsize('/tmp/'+str(molecule_id)+'_gpcrmd.sdf')
    return response
            
@user_passes_test_args(is_published_or_submission_owner)
def query_compound(request,compound_id,incall=False):
    '''Returns information about the given compound_id. If incall is True, it will return a dictionary, otherwise, it returns an Http REsponse '''
    comp_dic=dict()
    comp_dic['link_2_molecule']=list()
    #comp_dic['imagelink']=list()
    comp_dic['references']=list()
    comp_dic['othernames']=list()
    for oname in DyndbOtherCompoundNames.objects.filter(id_compound=compound_id):
        comp_dic['othernames'].append(oname.other_names)
    comp_obj=DyndbCompound.objects.select_related('std_id_molecule').get(pk=compound_id)
    comp_dic['name']=comp_obj.name
    comp_dic['iupac_name']=comp_obj.iupac_name
    comp_dic['pubchem_cid']=comp_obj.pubchem_cid
    comp_dic['chemblid']=comp_obj.chemblid
    comp_dic['sinchi']=comp_obj.sinchi
    comp_dic['sinchikey']=comp_obj.sinchikey
    comp_dic['imagelink']=get_imagepath(compound_id,'compound')
    comp_dic['related_mol_images']=[]

    for molecule in DyndbMolecule.objects.filter(id_compound=compound_id):
        comp_dic['link_2_molecule'].append(molecule.id)
        comp_dic['related_mol_images'].append([molecule.id,get_imagepath(molecule.id,'molecule')])
        
    for match in DyndbReferencesCompound.objects.select_related('id_references').filter(id_compound=compound_id):
        ref=[match.id_references.doi,match.id_references.title,match.id_references.authors,match.id_references.url]
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        comp_dic['references'].append(ref)  
    if incall==True:
        return comp_dic
    return render(request, 'dynadb/compound_query_result.html',{'answer':comp_dic})

@user_passes_test_args(is_published_or_submission_owner)
def query_complex(request, complex_id,incall=False):
    '''Returns information about the given complex_id. If incall is True, it will return a dictionary, otherwise, it returns an Http REsponse '''
    plist=list()
    clistorto=list()
    clistalo=list()
    model_list=list()
    comdic=dict()

    for cprotein in DyndbComplexProtein.objects.select_related('id_protein').filter(id_complex_exp=complex_id).values('id_protein__id','id_protein__name'): 
        plist.append([cprotein['id_protein__id'], cprotein['id_protein__name']])

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
    q = q.values('ec_fifty_val','binding_val','references')
    efficacy=dict()
    binding=dict()
    reference_list=[]
    references=dict()
    for row in q:
        print (row['ec_fifty_val'],row['binding_val'],row['references'])
        if row['ec_fifty_val'] is not None:
            efficacyrow=DyndbEfficacy.objects.get(pk=row['ec_fifty_val'])
            efficacy['value']=efficacyrow.rvalue
            efficacy['units']=efficacyrow.units
            efficacy['description']=efficacyrow.description
   
        if row['binding_val'] is not None:
            bindrow=DyndbBinding.objects.get(pk=row['binding_val'])
            binding['value']=bindrow.rvalue
            binding['units']=bindrow.units
            binding['description']=bindrow.description

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
    comdic={'proteins':plist,'compoundsorto': clistorto,'compoundsalo': clistalo, 'models':model_list, 'reference':reference_list,'binding':binding,'efficacy':efficacy}
    print(comdic)
    if incall==True:
        return comdic
    return render(request, 'dynadb/complex_query_result.html',{'answer':comdic})

@user_passes_test_args(is_published_or_submission_owner)
def query_model(request,model_id,incall=False):
    '''Returns information about the given model_id. If incall is True, it will return a dictionary, otherwise, it returns an Http Response '''
    model_dic=dict()
    numbertostring={0:'Apomorfic (no ligands)',1:'Complex Structure (proteins and ligands)'}
    #model_dic['description']=DyndbModel.objects.get(pk=model_id).description #NOT WORKING BECAUSE OF MISSING INFOMRATION
    modelobj=DyndbModel.objects.select_related('id_protein','id_complex_molecule').get(pk=model_id)
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
        model_dic['link2protein'].append([modelobj.id_protein.id, query_protein(request,modelobj.id_protein.id,True)['Protein_name'] ])

    except:

        q = DyndbModel.objects.filter(pk=model_id)
        q = q.annotate(protein_id=F('id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__id'))
        q = q.values('id', 'protein_id')
        for row in q:
            if row['protein_id'] not in model_dic['link2protein']:
                model_dic['link2protein'].append([row['protein_id'],query_protein(request,row['protein_id'],True)['Protein_name'] ])

    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=model_id):
        model_dic['components'].append([match.id_molecule.id, query_molecule(request,match.id_molecule.id,True)['imagelink']])

    for match in DyndbDynamics.objects.filter(id_model=model_id):
        model_dic['dynamics'].append(match.id)

    if modelobj.id_complex_molecule is not None:
        cmol_id=modelobj.id_complex_molecule.id
        for match in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=cmol_id):
            if match.type==0:
                model_dic['ortoligands'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])
            else:
                model_dic['aloligands'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])

    for match in DyndbReferencesModel.objects.select_related('id_references').filter(id_model=model_id):
        ref=[match.id_references.doi,match.id_references.title,match.id_references.authors,match.id_references.url]
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        model_dic['references'].append(ref)  
    if incall==True:
        return model_dic

    return render(request, 'dynadb/model_query_result.html',{'answer':model_dic})
    
@user_passes_test_args(is_published_or_submission_owner)
def query_dynamics(request,dynamics_id):
    '''Returns information about the given dynamics_id.Returns an Http Response '''
    dyna_dic=dict()
    dynaobj=DyndbDynamics.objects.select_related('id_dynamics_solvent_types__type_name','id_dynamics_membrane_types__type_name').get(pk=dynamics_id)
    dyna_dic['nglviewer_id']=dynamics_id
    dyna_dic['link_2_molecules']=list()
    dyna_dic['files']=list()
    dyna_dic['references']=list()
    dyna_dic['related']=list()
    dyna_dic['soft']=dynaobj.software
    dyna_dic['softv']=dynaobj.sversion
    dyna_dic['forcefield']=dynaobj.ff
    dyna_dic['forcefieldv']=dynaobj.ffversion
    dyna_dic['link_2_model']=dynaobj.id_model.id
    dyna_dic['description']=dynaobj.description
    dyna_dic['timestep']=dynaobj.timestep
    dyna_dic['delta']=dynaobj.delta
    dyna_dic['solventtype']=dynaobj.id_dynamics_solvent_types.type_name
    dyna_dic['membranetype']=dynaobj.id_dynamics_membrane_types.type_name
    dyna_dic['ortoligands']=list()
    dyna_dic['aloligands']=list()
    dyna_dic['link2protein']=list()
    for match in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=dynamics_id):
        dyna_dic['link_2_molecules'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])

    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id):
        candidatecomp=[match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']]
        if candidatecomp not in dyna_dic['link_2_molecules'] : 
            #dyna_dic['link_2_molecules'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])
            dyna_dic['link_2_molecules'].append(candidatecomp)
    cmolid=dynaobj.id_model.id_complex_molecule
    if cmolid is not None:
        cmol_id=cmolid.id
        for match in DyndbComplexMoleculeMolecule.objects.select_related('id_molecule').filter(id_complex_molecule=cmol_id):
            if match.type==0:
                dyna_dic['ortoligands'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])
            else:
                dyna_dic['aloligands'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])

    for match in DyndbRelatedDynamicsDynamics.objects.select_related('id_related_dynamics__id_dynamics').filter(id_dynamics=dynamics_id):
        dyna_dic['related'].append(match.id_related_dynamics.id_dynamics.id)

    
    try: #if it is apomorfic
        dyn_model_id=dynaobj.id_model.id
        dyna_dic['link2protein'].append([DyndbModel.objects.get(pk=dyn_model_id).id_protein.id, query_protein(request,DyndbModel.objects.get(pk=dyn_model_id).id_protein.id,True)['Protein_name'] ]) #NOT WORKING BECAUSE OF MISSING INFORMATION

    except:
        q = DyndbModel.objects.filter(pk=dyn_model_id)
        q = q.annotate(protein_id=F('id_complex_molecule__id_complex_exp__dyndbcomplexprotein__id_protein__id'))
        q = q.values('id', 'protein_id')
        for row in q:
            if row['protein_id'] not in dyna_dic['link2protein']:
                dyna_dic['link2protein'].append([row['protein_id'],query_protein(request,row['protein_id'],True)['Protein_name'] ])

    for match in DyndbReferencesDynamics.objects.select_related('id_references').filter(id_dynamics=dynamics_id):
        ref=[match.id_references.doi,match.id_references.title,match.id_references.authors,match.id_references.url]
        counter=0
        for element in ref:
            if element is None:
                ref[counter]=''
            counter+=1            
        dyna_dic['references'].append(ref)

    for match in DyndbFilesDynamics.objects.select_related('id_files').filter(id_dynamics=dynamics_id):
        dyna_dic['files'].append( ( match.id_files.filepath.replace("/protwis/sites/","/dynadb/") , match.id_files.filename ) ) 
    
    return render(request, 'dynadb/dynamics_query_result.html',{'answer':dyna_dic})
    
    
def carousel_model_components(request,model_id):
    model_dic=dict()
    model_dic['components']=[]
    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=model_id):
        model_dic['components'].append([match.id_molecule.id, query_molecule(request,match.id_molecule.id,True)['imagelink']])    
    return render(request, 'dynadb/model_carousel.html',{'answer':model_dic})
    
    
    
def carousel_dynamics_components(request,dynamics_id):
    print('here')
    dyna_dic=dict()
    dyna_dic['link_2_molecules']=[]
    for match in DyndbDynamicsComponents.objects.select_related('id_molecule').filter(id_dynamics=dynamics_id):
        print('heereeeeee2')
        dyna_dic['link_2_molecules'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])

    for match in DyndbModelComponents.objects.select_related('id_molecule').filter(id_model=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id):
        candidatecomp=[match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']]
        if candidatecomp not in dyna_dic['link_2_molecules'] : 
            #dyna_dic['link_2_molecules'].append([match.id_molecule.id,query_molecule(request,match.id_molecule.id,True)['imagelink']])
            dyna_dic['link_2_molecules'].append(candidatecomp)
    print(dyna_dic)
    return render(request, 'dynadb/dynamics_carousel.html',{'answer':dyna_dic})
        
    
@textonly_500_handler
@login_required
def protein_get_data_upkb(request, uniprotkbac=None):
    print("HELLO")
    
    KEYS = set(('entry','entry name','organism','length','name','aliases','sequence','isoform','speciesid'))
    if request.method == 'POST' and 'uniprotkbac' in request.POST.keys():
      print("POST\n",request.POST)
      uniprotkbac = request.POST['uniprotkbac']
    if uniprotkbac is not None:
      if valid_uniprotkbac(uniprotkbac):
        if uniprotkbac.find('-') < 0:
          uniprotkbac_noiso = uniprotkbac
          isoform = None
        else:
          uniprotkbac_noiso,isoform = uniprotkbac.split('-')
        data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,entry name,organism,length,')
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
            response = JsonResponse(data) 
            #response={'dict':data,'json':JsonResponse(data)}
            #print (response) ###JUANMA
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
def submitpost_view(request,submission_id,model_id=1):
    if request.method == 'POST':
        print(request.POST.items())
        print(request.POST)

        indexl=[]
        print("Submitpost_view")
        print(request.POST)
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
        print("\n\n\n",indexl,"\n\n\n")
       
#        response=SMALL_MOLECULEfunction(request.POST, indexl, submission_id)
        response=SMALL_MOLECULEview(request.POST, submission_id)
        print(response)
    #   for index in indexl:
    #        SMALL_MOLECULEfunction(request.POST, index, submission_id)
    #   try:
    #       data = request.POST['inchi']
    #        print("\nINCHI\n",data)
    #   except:
    #       pass 
    #    print("PIPOL",request.POST.keys())
    #    for items in request.POST.items():
    #        print ("ITEM ", items)
    #    print(len(request.POST))
        return response
    else:
        print("PPP")
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
        ###return render(request,'dynadb/SMALL_MOLECULE.html', {'submission_id' : submission_id})
        #return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbSub':fdbSub,'fdbCF':fdbCF,'fdbON':fdbON, 'fdbF':fdbF, 'fdbFM':fdbFM, 'fdbMM':fdbMM, 'submission_id' : submission_id})

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
      response = HttpResponse('Parsing error: '+str(e),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
      return response
    except:
      raise

@textonly_500_handler
@login_required
def upload_pdb(request): #warning , i think this view can be deleted
    if request.method == 'POST':
        form = FileUploadForm(data=request.POST, files=request.FILES) #"upload_pdb"
        myfile = request.FILES["file_source"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        request.session['newfilename']=uploaded_file_url
        pdbname='/protwis/sites'+request.session['newfilename']
        tojson={'chain': 'A','message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')
        

def obtain_res_coords(pdb_path,res1,res2,pair, pair2): 
    '''res1 is last residue of previous segment, res2 is start of current segment. PAIR is [A,B], pair2 is [PROA,PROB]'''
    res1_coords=[]
    res2_coords=[]
    readpdb=open(pdb_path,'r')
    #print(res1,res2,pair,pair2)
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
                print('RESULTS SEARCH TOP', res)
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
            #~ number_segments,breaklines=get_number_segments(pdbname)
            #~ request.session[combination_id]['segments'] = number_segments,breaklines
            #~ if number_segments>len(arrays):
                #~ results={'type':'string_error','title':'Number of defined segments does not match number of segments found in the PDB. These are the lines that initiate a new segment:', 'errmess':breaklines}
                #~ request.session[combination_id] = results
                #~ tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                #~ data = json.dumps(tojson)
                #~ request.session[combination_id]['segments'] = results
                #~ return HttpResponse(data, content_type='application/json')  

            uniquetest=unique(pdbname, chain!='',segid!='')
            if uniquetest is True:
                checkresult=checkpdb(pdbname,segid,start,stop,chain)
                if isinstance(checkresult,tuple):
                    print('hell55')
                    tablepdb,simplified_sequence,hexflag=checkresult
                    guide=matchpdbfa(sequence,simplified_sequence,tablepdb,hexflag,seqstart)
                    if isinstance(guide, list):
                        path_to_repaired=repairpdb(pdbname,guide,segid,start,stop,chain,counter)
                        full_run_dict[(segment_def,path_to_repaired)]=guide
                    elif isinstance(guide, tuple):
                        print('heello5')
                        tuple_error_dict[segment_def]=guide
                        if guide[0].startswith('Error'):
                            errorflag=1
                        elif guide[0].startswith('Warning'):
                            errorflag=0
                    else: #PDB has insertions error
                        print('ERROR PDB INSERTION')
                        guide='Error in segment definition: Start:'+ str(start) +' Stop:'+ str(stop) +' Chain:'+ chain +' Segid:'+ segid+'\n'+guide
                        results={'type':'string_error', 'title':'Alignment error in segment definition' ,'errmess':guide,'message':''}
                        request.session[combination_id] = results
                        request.session.modified = True
                        tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                        data = json.dumps(tojson)
                        return HttpResponse(data, content_type='application/json')
                        print('hre3')
                else: #checkpdb has an error
                    results={'type':'string_error','title':'Corrupted resid numbering or missing field in PDB', 'errmess':checkresult} #prints the error resid.
                    request.session[combination_id] = results
                    request.session.modified = True
                    tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                    data = json.dumps(tojson)
                    return HttpResponse(data, content_type='application/json')
                    print('here2')
            else: #unique test failed
                results={'type':'string_error','title':'Lack of uniqueness','errmess':uniquetest} #says which combination causes the problem
                request.session[combination_id] = results
                request.session.modified = True
                tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                data = json.dumps(tojson)
                return HttpResponse(data, content_type='application/json')

            counter+=1

        if len(full_run_dict)>0 or len(tuple_error_dict)>0:
            print('full RUN')
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
def servecorrectedpdb(request,pdbname):
    ''' Allows the download of a PDB file with the correct resids, according to the aligment performed by pdbcheck function. '''
    with open('/'+pdbname,'r') as f:
        data=f.read()
        response=HttpResponse(data, content_type=mimetypes.guess_type(pdbname)[0])
        response['Content-Disposition']="attachment;filename=%s" % (pdbname[pdbname.rfind('/')+1:])
        response['Content-Length']=os.path.getsize('/'+pdbname)
    return response

@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
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
def upload_model_pdb(request,submission_id):

    request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,50*1024**2)
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
    
    #q = DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id__in=molintdict.keys(),molecule_id__dyndbfilesmolecule__type=sdf_mol_file_type)
    #q = q.annotate(filepath=F('molecule_id__dyndbfilesmolecule__id_files__filepath'))
    #q = q.values('int_id','molecule_id','filepath')
    
    
    
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
def pdbcheck_molecule(request,submission_id,form_type):
    if form_type=="dynamicsreuse":
        form_type="dynamics"
    post_mc_dict = {'resname':'residue name','molecule':'molecule form number','id_molecule':'molecule ID'}
    #post_mc_dict = {'resname':'residue name','molecule':'molecule form number','id_molecule':'molecule ID','numberofmol':'number of molecules'}
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
                return JsonResponse({'msg':'Cannot find uploaded PDB file. Try to upload the file again.'},status=422,reason='Unprocessable Entity')

            data = dict()
            data['download_url_log'] = None
 
            fieldset_mc = dict()
            fieldset_ps = dict()
            print("POST ",request.POST)
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
                diff_form_pdb = form_resnames.difference(pdb_resnames)
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
                            failc, pdbmol = diff_mol_pdb(mol,pdbdict[resname],logfile=logfile)
                            fail += failc
                            try:
                                generate_png(pdbmol,pdbdict[resname]+'.png',logfile=os.devnull,size=300)
                            except:
                                pass
                            finally:
                                del pdbmol
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
    print ("MODELreuseREQUESTview")
    try:
        print(submission_id)
    except NameError:
        submission_id==None
    if not submission_id==None:
        qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
        qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
        qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
            enabled=True
    if model_id == 0: #model_id is 0 when the view is accesed from the memberpage view!!! then the model_id selected by the user is passed to other reuse views
        return render(request,'dynadb/MODELreuseREQUEST.html', {})
    print ("\n\nooo ", print (model_id) )
    # Dealing with POST data
    if request.method == 'POST':
        dictsubid={}#dictionary for instatiating dyndbSubmission and obtaining a new submission_id for our new submission
        dictsubid['user_id']=str(request.user.pk)
        dictsubid['is_reuse_model']=str(1)
        fdbsub=dyndb_Submission(dictsubid)
        fdbsubobj=fdbsub.save()
        print("submission_id",fdbsubobj.pk)
        if request.POST['Choose_reused_model']== '':
            print("NO MODEL", request.POST.dict()['Choose_reused_model'])
            if request.POST['Choose_submission_id']== '':
                print("NO Submission_id ", request.POST.dict()['Choose_submission_id'])
                request.POST['Choose_submission_id']='0'
                request.POST['Choose_reused_model']='0'
                print("NO Submission_id ", request.POST.dict()['Choose_submission_id'])
            else:
                request.POST['Choose_reused_model']=DyndbSubmissionModel.objects.filter(submission_id=request.POST.dict()['Choose_submission_id']).values_list('model_id',flat=True)[0]
            print(request.POST['Choose_reused_model'])
        else:
            if request.POST['Choose_submission_id']== '':
                print("reuse model != '' ")
                qS=DyndbSubmissionModel.objects.filter(model_id=request.POST['Choose_reused_model']).values_list('submission_id',flat=True)[0]
                request.POST['Choose_submission_id']=qS
                # choose_submission_id is not passed as a parameter to the other views. The Submission_id parameter stands for the ID of the current submission, not the submission made the first time model was submitted
                submission_id = str(fdbsubobj.pk)
                print("\n MIRA LA SUBMISSION ID:",submission_id)
      #          submission_id=str(request.POST['Choose_submission_id'])
                model_id=str(request.POST['Choose_reused_model'])
                submission_model=dyndb_Submission_Model({'model_id':model_id, 'submission_id':submission_id})
                print("submission model",submission_model.__dict__['data'])
                if submission_model.is_valid():
                    submission_model.save()
                else:
                    print("ERROR",submission_model.errors.as_text())
                    response = HttpResponse("Submission Model has not been registered",content_type='text/plain; charset=UTF-8')
                    return response   

                return HttpResponseRedirect("/".join(["/dynadb/modelreuse",str(submission_id),str(model_id),""]), {'submission_id':str(submission_id),'model_id':str(model_id)} )
           
            else:
                a=DyndbSubmissionModel.objects.filter(submission_id=request.POST.dict()['Choose_submission_id']).values_list('model_id',flat=True)[0]
                print(a, type(a))
                if request.POST['Choose_reused_model'] != a:
                    print("MIRA",a, request.POST['Choose_reused_model'])
                    request.POST['Choose_reused_model']=a
                submission_id = fdbsubobj.pk
                model_id=str(request.POST['Choose_reused_model'])
                #return HttpResponseRedirect("/".join(["/dynadb/modelreuse",submission_id,model_id,""]), {'submission_id':submission_id,'model_id':model_id,'message':"The Complex ID you provided does not match the actual complex contained in the Submission ID. The correct Complex ID is shown here "} )
                return HttpResponseRedirect("/".join(["/dynadb/modelreuse",str(submission_id),model_id,""]), {'submission_id':submission_id,'model_id':model_id,'message':"The Complex ID you provided does not match the actual complex contained in the Submission ID. The correct Complex ID is shown here "} )
        if request.POST['Choose_submission_id']=='0' and request.POST['Choose_reused_model']=='0':
            message="Please provide either a Complex ID or a Submission ID corresponding to the system to be reused"
            Context={'value':0,'CHoose_submission_id':message,'CHoose_reused_model':message}
            print(Context)
            return render(request,'dynadb/MODELreuseREQUEST.html', Context)
        if request.POST['Choose_submission_id']=='':
            request.POST['Choose_submission_id']=DyndbSubmissionModel.objects.filter(model_id=request.POST.dict()['Choose_reused_model']).values_list('submission_id',flat=True)[0]
            print("NO Submission_id")
        print(request.POST.dict())
        submission_id =str( fdbsubobj.pk)
#        submission_id=str(request.POST['Choose_submission_id'])
        model_id=str(request.POST['Choose_reused_model'])
        submission_model=dyndb_Submission_Model({'model_id':model_id, 'submmission_id':submission_id})
        print("submission model",submission_model.__dict__['data'])
        if submission_model.is_valid():
            submission_model.save()
            print("submission modeli is valid")
        else:
            response = HttpResponse("Submission Model has not been registered",content_type='text/plain; charset=UTF-8')
            return response   
        return HttpResponseRedirect("/".join(["/dynadb/modelreuse",submission_id,model_id,""]), {'submission_id':submission_id,'model_id':model_id,'message':""} )
    else:

        return render(request,'dynadb/MODELreuseREQUEST.html', {})
@login_required
def MODELrowview(request):
    form=[1,2,3]
    qMODEL=DyndbModeledResidues.objects.filter(id_model=1)
    rows=qMODEL.values('chain','segid','resid_from','resid_to','seq_resid_from','seq_resid_to','bonded_to_id_modeled_residues_id','source_type','pdbid')
    qMODCOMP=DyndbModelComponents.objects.filter(id_model=1)
    qMODCOMP=qMODCOMP.order_by('id_molecule')
    rowsMC=qMODCOMP.values('resname','id_molecule','numberofmol','type')
    for i in list(range(0,len(rows))):
        if rows[i]['segid']=='':
            rows[i]['segid']="-"
    return render(request,'dynadb/MODELreuseCOMMON.html', {'rows':rows})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def MODELreuseview(request, submission_id, model_id  ):
    enabled=False
    model_id=int(model_id)
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]).order_by('int_id')
    print(qSub,"  ", model_id, submission_id)
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
#    if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
    if qSubPNew.exists() and qSubMolNew.exists(): #el submit Model is submitted when clicking the " Continue to step 4: Dynamics Information " button 
        enabled=True
    print("reuseview")
    qModel=DyndbModel.objects.filter(id=model_id)
    INITsubmission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]
    p=qModel
    Typeval=p.values()[0]['type']
    Type=p.model.MODEL_TYPE[Typeval][1]
    STypeval=p.values()[0]['source_type']
    SType=p.model.SOURCE_TYPE[STypeval][1]
    print("QMODEL ",p)
    qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id,id_protein__dyndbsubmissionprotein__submission_id=INITsubmission_id).annotate(int_id=F('id_protein__dyndbsubmissionprotein__int_id')).order_by('resid_from')
#    qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id).order_by('resid_from')
    lformps=list(range(0,len(qMODRES)))
    q0MODRES=qMODRES[0]
    rowsMR=qMODRES
    lmrstype=[]
    for l in qMODRES:
        mrstype=l.SOURCE_TYPE[l.source_type]
        lmrstype.append(mrstype)
    print ("residues!!",lmrstype)
    qMODCOMP=DyndbModelComponents.objects.filter(id_model=model_id).exclude(type=None).exclude(numberofmol=None)
    qMODCOMP=qMODCOMP.order_by('id')
    lmtype=[]
    lformmc=list(range(0,len(qMODCOMP)))
    lcompname=[]
    l_ord_mol=[]
    d=0
    for l in qMODCOMP:
        d=d+1
        print("query list element",l.id," ",d)
        mtype=l.MOLECULE_TYPE[l.type]
        lmtype.append(mtype)
        qName=DyndbCompound.objects.filter(id=DyndbMolecule.objects.filter(id=l.id_molecule_id).values_list('id_compound',flat=True)).values_list('name',flat=True)[0]
        lcompname.append(qName)
        l_ord_mol.append(d)
    print(lmtype)
    print(l_ord_mol)
    rowsMC=qMODCOMP.values('resname','id_molecule_id','numberofmol','type')
    print("OOO\n",rowsMC)

    action="/".join(["/dynadb/modelreuse",submission_id,""])
    reuse_model=model_id
    print(rowsMR.values)
    print("aqui",lformps)
    if request.method == 'POST':
        print("POSTi aaaaaa")

        print(request.POST)
        if not qSubModNew.exists():
            dictsubmod={'submission_id':submission_id, 'model_id':request.POST['model_id']}
            fdbSM=dyndb_Submission_Model(dictsubmod)
            if fdbSM.is_valid():
                print ("TTTTTTTTTTTtt")
                print ("MODEL SUBMISSION ITEMS", fdbSM.fields.items())
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
def PROTEINreuseview(request, submission_id, model_id ):
    enabled=False
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id')
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0]).exclude(int_id=None).order_by('int_id')
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
        enabled=True

    print(qSub)
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
#        MUT=qPROT.values('id','is_mutated')
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
#            MUT.values('is_mutated').filter(id=tt)[0]['is_mutated']:
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

#   for tt in qPROT.values_list('id',flat=True):
#       qALIAS=DyndbOtherProteinNames.objects.filter(id_protein=tt)
#       llo=("; ").join(qALIAS.values_list('other_names',flat=True))
#       alias.append(llo) 
#       print("AQUI", tt,alias)
#       qSEQ=DyndbProteinSequence.objects.filter(id_protein=tt).values_list('sequence',flat=True)[0]
#       if MUT.values('is_mutated').filter(id=tt)[0]['is_mutated']:
#           llsm=qSEQ
#           mseq.append(llsm)
#           qpCp=DyndbProteinCannonicalProtein.objects.filter(id_protein=tt).values_list('id_cannonical_proteins',flat=True)[0]
#           llsw=DyndbProteinSequence.objects.filter(id_protein=qpCp).values_list('sequence',flat=True)[0]
#           qPMut=DyndbProteinMutations.objects.filter(id_protein=tt)
#           MUTations.append(qPMut)
#       else:
#           llsw=qSEQ
#           mseq.append('')
#           MUTations.append('')
#       wseq.append(llsw) 

    return render(request,'dynadb/PROTEIN.html', {'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id':submission_id,'model_id':model_id, 'enabled':enabled })
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def SMALL_MOLECULEreuseview(request, submission_id, model_id ):
#    qSub=DyndbSubmissionMolecule.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).values_list('submission_id',flat=True)[0]).exclude(int_id=None).exclude(not_in_model=True).order_by('int_id')
    enabled=False
    qSubPNew=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
    qSubMolNew=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(int_id=None)
    qSubModNew=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
    if qSubPNew.exists() and qSubMolNew.exists() and qSubModNew.exists():
    #if qSubPNew.exists() and qSubMolNew.exists():
        enabled=True
    qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=True).filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0],molecule_id__dyndbfilesmolecule__id_files__id_file_types=19,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url')).order_by('int_id')

#    qSuburl=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=True).filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0],molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url')).order_by('int_id')
#    qSuburlstd=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=True).filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0],molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url')).order_by('int_id')

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
    print(alias)
    print(qCOMP)
    print(qMOL)
    listExtraMolColapse=list(range(max(int_id),40))
    print(listExtraMolColapse)
    fdbSub = dyndb_Submission_Molecule()
    last=int_id0[-1]

    qSubNotMod=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=False).filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).order_by('int_id').annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url'))
    print("VALUES XXXXX",qSubNotMod.values(),"   qSubNotMod.exists ",qSubNotMod.exists())
    print("ENABLED???? ",enabled," ")
    if enabled and qSubNotMod.exists():
      #  qSubNotMod=DyndbSubmissionMolecule.objects.exclude(int_id=None).exclude(not_in_model=False).filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).order_by('id').values_list('submission_id',flat=True)[0],molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url')).order_by('int_id')
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
        print(aliasNotMod)
        print(qCOMPNotMod)
        print(qMOLNotMod)
        listExtraMolColapseNotMod=list(range(max(int_idNotMod+int_id),40))
        print(listExtraMolColapseNotMod)
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
        print(alias)
        print(qCOMP)
        print(qMOL)
        listExtraMolColapseNotMod=list(range(max(int_idNotMod),40))
        fdbSub = dyndb_Submission_Molecule()
        lastNotMod=int_id0[-1]
        last=int_id0[-1]

    return render(request,'dynadb/SMALL_MOLECULE.html', {'url':url,'urlstd':urlstd,'fdbSub':fdbSub,'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'last':last,'alias':alias,'submission_id':submission_id,'model_id':model_id,'list':listExtraMolColapse, 'enabled':enabled, 'urlNotMod':urlNotMod,'urlstdNotMod':urlstdNotMod,'qMOLNotMod':qMOLNotMod,'labtypelNotMod':labtypelNotMod,'TypeNotMod':TypeNotMod,'impNotMod':impNotMod,'qCOMPNotMod':qCOMPNotMod,'int_idNotMod':int_idNotMod,'int_id0NotMod':int_id0NotMod,'lastNotMod':lastNotMod,'aliasNotMod':aliasNotMod,'listNotMod':listExtraMolColapseNotMod, 'qSubNotModsaved':qSubNotMod.exists() })
 
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
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
                        print(key,val)
                        Pscompmod[ii][0][key]=val
            print("\nlista numero 0 \n",Pscompmod[ii][0].items() )
           # print("\nlista numero 0 entera \n",Pscompmod[ii] )
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
            direct='/protwis/sites/files/Dynamics/dyn'+str(submission_id)
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
                    #print("val ",val, " ;val split",fext," Tambien id")
                    if fext in dict_ext_id.keys():
                        initFiles['id_file_types']=dict_ext_id[fext]
                        initFiles['filename']=val.name
                        initFiles['filepath']=direct
                        #initFiles['filepath']='/protwis/sites/files/Dynamics/dyn'+dyn_obj[ii].pk#modificar
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
 
 
##       return HttpResponse(qDS.values_list()[0])
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
def MODELview(request, submission_id):
    
    def model_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        print("inside the function model_file_table")
        print(dname)
        fdbF={}
        fdbFobj={}
        
       #####  
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
       ##############
        for key,val  in dname.items():
            print("val\n", val)
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
                print("HOLA initFiles\n", initFiles)
                fdbFobj[key]=fdbF[key].save()
                dicfmod['id_model']=MFpk
                dicfmod['id_files']=fdbFobj[key].pk
            else:
                prev_entryFile=DyndbFiles.objects.filter(dyndbfilesmodel__id_model__dyndbsubmissionmodel__submission_id=submission_id)
                dicfmod['id_files']=prev_entryFile.values_list('id',flat=True)[0]
                dicfmod['id_model']=MFpk
                prev_entryFile.update(update_timestamp=timezone.now(),last_update_by_dbengine=user,filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])
                #prev_entryFile.update(filename=initFiles['filename'],filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])
            #   error=("- ").join(["Error when storing MODEL file info, dyndb_Files form"])
            #   print("Errores en el form dyndb_Files\n ", fdbFM[key].errors.as_text())
            #   response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            #   return response
            
            fdbFM[key]=dyndb_Files_Model(dicfmod)
            if fdbFM[key].is_valid():
                fdbFM[key].save()
            else:
                prev_entryFileM=DyndbFilesModel.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id)
                prev_entryFileM.update(id_model=dicfmod['id_model'],id_files=dicfmod['id_files'])

               # print("Errores en el form dyndb_Files_Model\n ", fdbFM[key].errors.as_text())
               # error=("- ").join(["Error when storing MODEL file info, dyndb_Files_Model form"])
               # response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
               # return response



    # Function for saving files
    print("REQUEST SESSIONS",request.session.items())
    request.session['info']="PASAR a SESSION"
    print("REQUEST SESSIONS",request.session.items())
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    print("HOLA  ", def_user)
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None,'id_structure_model':None, 'template_id_model':None,'model_creation_submission_id':submission_id,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user    }
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  }
    # Dealing with POST data
    if request.method == 'POST':
        #Defining variables and dictionaries with information not available in the html form. This is needed for form instances.
        action="/".join(["/dynadb/MODELfilled",submission_id,""])
     #   response = HttpResponse('PRUEBA MODEL',content_type='text/plain; charset=UTF-8')
     #   return response
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
        print ("REQUEST.POST",dictpost)
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
                print(response)
                return response
            if not (type(intervalA[0])==int  and type(intervalA[1])==int and type(intervalB[0])==int  and type(intervalB[1])==int):   
                response= "the elements in the tuples must be integers"
                print(response)
                return response
            if intervalA[0] > intervalA[1] or intervalB[0] > intervalB[1]:
                response= "the first element of the tuple must be the smallest value"
                print(response)
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
                            response = HttpResponse('Several complex_exp entries involving exactly the same set of proteins exist in the GPCRmd DB... Please Report that error to the GPCRdb administrator',status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
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
                            response = HttpResponse('Several complex_exp entries involving exactly the same set of proteins and compounds exist in the GPCRmd DB... Please Report that error to the GPCRdb administrator',status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                            return response
                            
##                      if(len(cec)<len(cep)):# Complexes with the same number of molecules than our submission is lower than complexes with the same number of proteins than our submission. There should be only one. Then complex_exp value is taken from the DyndbComplexCompound query "c"
##                          rowCompl=[cec[0]['id_complex_exp']]
##                      else:# Number of Complexes involving the same number of proteins than our submission is lower or equal than the number of complexes involving the same number of compounds considered in our submission. Only one Complex involving the same number of proteins must exist. if 'equal' just a single complex_exp and complex_molecule exist
##                          rowCompl=[cep[0]['id_complex_exp']]
            
          # for el in row:
          #     elok=DyndbComplexMolecule_Molecule.filter(
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
 
##                          b=DyndbComplexMolecule.objects.filter(id__in=a.values_list('id_complex_molecule',flat=True).filter(id_complex_exp=rowCompl[0]).values('id_complex_exp').annotate(num=Count('id_complex_molecule')).filter(num=len(lmol_in_model))
 
##                          lmce=b.values_list('complex_exp',flat=True)
##                          # id_complex_exp of complexes with the same number of protein than our submission
##                          p=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLp).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model))  
##                          lpce=p.values_list('complex_exp',flat=True)
##                          # There is one 
##                          l_compl_exp=list(lmce&lpce)
 
                         #  if(len(a)<len(p)):# Complexes with the same number of molecules than our submission is lower than complexes with the same number of proteins than our submission. 
                         ##  actually one single complex_molecule involving the same number of molecules exist
                         #      ce=DyndbComplexMolecule.objects.filter(id=a[0]['id_complex_molecule']).values()[0]['id_complex_exp_id']
                         #      cm=a[0]['id_complex_molecule']
                         #      rowl=[ce,cm]
                         #  else:# Number of Complexes involving the same number of proteins than our submission is lower or equal than the number of complexes involving the same number of molecules than our submission. Only one Complex involving the same number of proteins must exist. if 'equal' just a single complex_exp and complex_molecule exist
                         #      cm=DyndbComplexMolecule.objects.filter(id_complex_exp=p[0]['id_complex_exp']).values()[0]['id']  
                         #      ce=p[0]['id_complex_exp']
                         #      rowl=[ce,cm]
 
##______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________
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
 
            print ("DICGTMODEL",dictmodel)
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

#_______ bloque dynamics_____________________ BORRAR
      #     if dyn_ins[ii].is_valid():
      #         qDe=DyndbDynamics.objects.filter(submission_id=submission_id)
      #         if len(qDe) == 0:
      #             PREVIOUS_COMP=False
      #             dyn_obj[ii]=dyn_ins[ii].save()
      #             DFpk=dyn_obj[ii].pk
      #         else:
      #             PREVIOUS_COMP=True
      #             print("\n\n PREVIOUS COMPOUNDS updating dyn object")
      #             DFpk=qDe.values_list('id',flat=True)[0]
      #             qDe.update(update_timestamp=timezone.now(),delta=POSTimod[ii]['delta'], description=POSTimod[ii]['description'].strip() , ff=POSTimod[ii]['ff'].strip(), ffversion=POSTimod[ii]['ffversion'].strip() , id_dynamics_solvent_types =POSTimod[ii]['id_dynamics_solvent_types'], solvent_num =POSTimod[ii]['solvent_num'], sversion =POSTimod[ii]['sversion'].strip() , atom_num = POSTimod[ii]['atom_num'], timestep =POSTimod[ii]['timestep'], id_dynamics_methods =POSTimod[ii]['id_dynamics_methods'] , software=POSTimod[ii]['software'].strip() ,  id_dynamics_membrane_types =POSTimod[ii]['id_dynamics_membrane_types'], id_assay_types =POSTimod[ii]['id_assay_types'])
      #     else:
      #         iii1=dyn_ins[ii].errors.as_text()
      #         print("errors in the form Dynamics", ii," ", dyn_ins[ii].errors.as_text())
      #         response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
      #         return response
#________________

        # if the submission have been corrected by modifying any protein or molecule the model must be updated    
       #check_submission_model_exists=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
       #if check_submission_model_exists.exists():
       #    if check_submission_model_exists.filter(model_id__id_complex_molecule=None,model_id__id_protein=None,model_id__model_creation_submission_id=None).exists():
                
        fdbMF = dyndb_Model(dictmodel)
        for key,value in initMOD.items():
            fdbMF.data[key]=value

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
            if len(lprot_in_model)==1:
                print("\nAAAAAAAAAAAAAAAAAAAAA\n")
                qMe.update(update_timestamp=timezone.now(), description=fdbMF.data['description'].strip() ,name=fdbMF.data['name'] ,type =fdbMF.data['type'] ,id_protein =fdbMF.data['id_protein'] , id_complex_molecule=id_complex_molecule , source_type=fdbMF.data['source_type'] ,pdbid=fdbMF.data['pdbid'] ,template_id_model=fdbMF.data['template_id_model'] ,id_structure_model=fdbMF.data['id_structure_model']  )
            else:
                print("\n MAS de UNA PROT\n")
                qMe.update(update_timestamp=timezone.now(), description=fdbMF.data['description'].strip() ,name=fdbMF.data['name'] ,type =fdbMF.data['type'] ,id_protein =None ,id_complex_molecule=id_complex_molecule , source_type=fdbMF.data['source_type'] ,pdbid=fdbMF.data['pdbid'] ,template_id_model=fdbMF.data['template_id_model'] ,id_structure_model=fdbMF.data['id_structure_model']  )
        


       #if fdbMF.is_valid():
       #    qMe=DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id)
       #    print("LLLLLLLLLLLL    ",qMe.values())
       #    if len(qMe)==0:
       #        PREVIOUS_COMP=False
       #        PREVIOUS_PROT_FRAG=False
       #        fdbMFobj=fdbMF.save()
       #        MFpk=fdbMFobj.pk
       #    else:
       #        PREVIOUS_COMP=True
       #        PREVIOUS_PROT_FRAG=True
       #        MFpk=qMe.values_list('id',flat=True)[0]
       #        if len(lprot_in_model)==1:
       #            qMe.update(update_timestamp=timezone.now(), description=fdbMF.data['description'].strip() ,name=fdbMF.data['name'] ,type =fdbMF.data['type'] ,id_protein =fdbMF.data['id_protein'] , id_complex_molecule=id_complex_molecule , source_type=fdbMF.data['source_type'] ,pdbid=fdbMF.data['pdbid'] ,template_id_model=fdbMF.data['template_id_model'] ,id_structure_model=fdbMF.data['id_structure_model']  )
       #
       #else:
       #    iii1=fdbMF.errors.as_text() 
       #    print("Errores en el form dyndb_Models\n", iii1)
       #    response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
          # if CE_exists==False:#There wasn't any entry for the current complex before submitting the current data. We have to delete the registered info if the view raises an error 
          #     DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
          #     DyndbComplexProtein.objects.filter(id_protein=prot).filter(id_complex_exp=CEpk).delete()
          #     DyndbComplexExp.objects.filter(id=CEpk).delete()
          # else:
          #     for comp_type_t in Upd_Comp_Type_l:
          #         if comp_type_t[0]:
          #             DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
          # if CM_exists==False:#There wasn't any entry for the current complex molecule after submitting the current data. We have to delete the registered info if the view raises an error 
          #     DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
          #     DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_molecule).delete()
       #     return response

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
             
         #  if CE_exists==False:#There wasn't any entry for the current complex after submitting the current data. We have to delete the registered info if the view raises an error 
         #      DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
         #      DyndbComplexProtein.objects.filter(id_protein=prot).filter(id_complex_exp=CEpk).delete()
         #      DyndbComplexExp.objects.filter(id=CEpk).delete()
         #  else:
         #      for comp_type_t in Upd_Comp_Type_l:
         #          if comp_type_t[0]:
         #              DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
         #  if CM_exists==False:#There wasn't any entry for the current complex molecule after submitting the current data. We have to delete the registered info if the view raises an error 
         #      DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
         #      DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_molecule).delete()
         #  DyndbModel.objects.filter(id=MFpk).delete()
                return response

        print("HHHHHHHHHHHHH")
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


#        request.session['newfilename']=direct+'/'+newname #added on 27/9 to access the path of the uploaded PDB file from pdbcheck view. Alex.

        fdbPS={} 
        fdbPSobj={} 
        
        qMR=DyndbModeledResidues.objects.filter(id_model__dyndbsubmissionmodel__submission_id=submission_id,source_type__gte=0,id_protein__dyndbsubmissionprotein__submission_id=submission_id).order_by('resid_from')
        qMRl=list(qMR.values_list('id_model','id_protein','resid_from','resid_to','seq_resid_from','seq_resid_to','id_protein__dyndbsubmissionprotein__int_id','chain','segid','pdbid','bonded_to_id_modeled_residues','id').order_by('resid_from'))#the 11th element of the tuple is the id in model components
        print("indexpsl", indexpsl)
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
            print("indexpsl", ii)
            if ii == indexpsl[0]:
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
                      # if CE_exists==False:#There wasn't any entry for the current complex before submitting the current data. We have to delete the registered info if the view raises an error 
                      ##    DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
                      ##    DyndbComplexProtein.objects.filter(id_protein=prot).filter(id_complex_exp=CEpk).delete()
                      ##    DyndbComplexExp.objects.filter(id=CEpk).delete()
                      # else:
                      #     for comp_type_t in Upd_Comp_Type_l:
                      #         if comp_type_t[0]:
                      #             DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
                      # if CM_exists==False:#There wasn't any entry for the current complex molecule before submitting the current data. the block delete registered info if the view raises an error
                      ##    DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
                      ##    DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_molecule).delete()
                      ##DyndbFiles.objects.filter(id__in=DyndbFilesModel.objects.filter(id_model=MFpk).values_list('id_files',flat=True)).delete()
                      ##DyndbFilesMolecule.objects.filter(id_model=MFpk).delete()
                      ##DyndbSubmissionModel.objects.filter(model_id=MFpk).delete()
                      ##DyndbModel.objects.filter(id=MFpk).delete()
                        return response
            if len(indexpsl)<len(qMRl):
                id_list=[]
                for i in range(len(indexpsl),len(qMRl)):
                    id_list.append(qMRl[i][11])
                print ("\nMIRA ",id_list)
                print ("lista",qMR.values())
                qMR.filter(id__in=id_list).delete()
                print ("QUEDA",qMR.values())
                print ("lista",id_list)
            #update the 'bonded_to_id_modeled_residues' field in rows beyond the length of the data stored in the DB                                                                                                                                                                                     
        else:
            for ii in dictprotsourmod.keys():
                print ("deberia llegar aqui")
                print("\n sourmod",dictprotsourmod[ii])
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
#       _    OLD MODEL COMPONENTS BLOCK    _________________________________________________________ 
#       for ii in indexmcl:  
#           print("\nTYPEMC",dictmodcompmod[ii]['typemc'])
#           dictmodcompmod[ii]['id_model']=MFpk
#           dictmodcompmod[ii]['name']=dictmodcompmod[ii].pop('namemc')
#           dictmodcompmod[ii]['id_molecule']= qSMolecules.values().filter(int_id=int(dictmodcompmod[ii]['molecule'])-1)[0]['molecule_id_id']
#           dictmodcompmod[ii]['type']=dictmodcompmod[ii].pop('typemc')
#           print ("\ndictmodcompmod type  name y id_model",i,":\n", dictmodcompmod[ii]['type'], dictmodcompmod[ii]['name'],  dictmodcompmod[ii]['id_model'])
#           fdbMC[ii] = dyndb_Model_Components(dictmodcompmod[ii])
#           if fdbMC[ii].is_valid():
#               fdbMCobj[ii]=fdbMC[ii].save(commit=False)
#               fdbMCobj[ii]=fdbMC[ii].save()
#           else:
#               iii1=fdbMC[ii].errors.as_text()
#               print("Errores en el form dyndb_Model_Components\n ", iii1 )
#               response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
#               if CE_exists==False:#There wasn't any entry for the current complex after submitting the current data. We have to delete the registered info if the view raises an error 
#                   DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
#                   DyndbComplexProtein.objects.filter(id_protein=prot).filter(id_complex_exp=CEpk).delete()
#                   DyndbComplexExp.objects.filter(id=CEpk).delete()
#               else:
#                   for comp_type_t in Upd_Comp_Type_l:
#                       if comp_type_t[0]:
#                           DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
#               if CM_exists==False:#There wasn't any entry for the current complex molecule after submitting the current data. We have to delete the registered info if the view raises an erro 
#                   DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
#                   DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_molecule).delete()
#               DyndbFiles.objects.filter(id__in=DyndbFilesModel.objects.filter(id_model=MFpk).values_list('id_files',flat=True)).delete()
#               DyndbFilesMolecule.objects.filter(id_model=MFpk).delete()
#               DyndbSubmissionModel.objects.filter(model_id=MFpk).delete()
#               DyndbModeledResidues.objects.filter(id_model=MFpk).delete()
#               DyndbModel.objects.filter(id=MFpk).delete()
#               return response
#
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
            #          if CE_exists==False:#There wasn't any entry for the current complex after submitting the current data. We have to delete the registered info if the view raises an error 
            #              DyndbComplexCompound.objects.filter(id_complex_exp=CEpk).delete()
            #              DyndbComplexProtein.objects.filter(id_protein=prot).filter(id_complex_exp=CEpk).delete()
            #              DyndbComplexExp.objects.filter(id=CEpk).delete()
            #          else:
            #              for comp_type_t in Upd_Comp_Type_l:
            #                  if comp_type_t[0]:
            #                      DyndbComplexCompound.objects.filter(id_compound=comp_type_t[1]).filter(id_complex_exp=comp_type_t[2]).update(type=comp_type_t[3])
            #          if CM_exists==False:#There wasn't any entry for the current complex molecule after submitting the current data. We have to delete the registered info if the view raises an erro 
            #              DyndbComplexMolecule.objects.filter(id_complex_exp=CEpk).delete()
            #              DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule=id_complex_molecule).delete()
            #          DyndbFiles.objects.filter(id__in=DyndbFilesModel.objects.filter(id_model=MFpk).values_list('id_files',flat=True)).delete()
            #          DyndbFilesMolecule.objects.filter(id_model=MFpk).delete()
            #          DyndbSubmissionModel.objects.filter(model_id=MFpk).delete()
            #          DyndbModeledResidues.objects.filter(id_model=MFpk).delete()
            #          DyndbModel.objects.filter(id=MFpk).delete()
            #           return response
             
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

        response = HttpResponse("The model has been successfully registered" ,content_type='text/plain; charset=UTF-8')
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
            Typeval=p.values()[0]['type']
            Type=p.model.MODEL_TYPE[Typeval][1]
            STypeval=p.values()[0]['source_type']
            SType=p.model.SOURCE_TYPE[STypeval][1]
            print("QMODEL ",p)
            qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id,id_protein__dyndbsubmissionprotein__submission_id=INITsubmission_id).annotate(int_id=F('id_protein__dyndbsubmissionprotein__int_id')).order_by('resid_from')
##           qMODRES=DyndbModeledResidues.objects.filter(id_model=model_id).order_by('resid_from')
            lformps=list(range(0,len(qMODRES)))
            q0MODRES=qMODRES[0]
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

#            molinmodel_not_in_modelcompl=list(DyndbSubmissionMolecule.objects.filter(type__lt=6,submission_id=submission_id).exclude(id__in=molinmodel_in_modelcomp).annotate(name=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_molecule__id_compound'),resname=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__resname'),numberofmol=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__numberofmol'),typemc=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__type'),id_model=F('submission_id__dyndbsubmissionmodel__model_id__dyndbmodelcomponents__id_model')).values())
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

            #qMODCOMP=DyndbSubmissionMolecule.objects.filter(type__lt=6,submission_id=submission_id).exclude(submission_id__dyndbmodel__dyndbmodelcomponents__id_model__lt=model_id).exclude(submission_id__dyndbmodel__dyndbmodelcomponents__id_model__gt=model_id,).annotate(resname=F('submission_id__dyndbmodel__dyndbmodelcomponents__resname'),numberofmol=F('submission_id__dyndbmodel__dyndbmodelcomponents__numberofmol'),typemc=F('submission_id__dyndbmodel__dyndbmodelcomponents__type'),id_model=F('submission_id__dyndbmodel__dyndbmodelcomponents__id_model'))
            lmtype=[]
            lformmc=list(range(0,len(qMODCOMP)))
            lcompname=[]
            l_ord_mol=[]
            d=0
           #for l in qMODCOMP:
           #    d=d+1
           #    print("query list element",l.id," ",d)
           #    mtype=DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l.type]]
           #    lmtype.append(mtype)
           # #   qName=DyndbCompound.objects.filter(id=DyndbMolecule.objects.filter(id=l.molecule_id_id).values_list('id_compound',flat=True)).values_list('name',flat=True)[0]
             #   lcompname.append(qName)
             #   l_ord_mol.append(d)
          # print(lmtype)
          # print(l_ord_mol)
            rowsMC=qMODCOMP
           # print("OOO\n",rowsMC)
         
            reuse_model=model_id
            print(rowsMR.values)
            print("aqui",lformps)
         
            fdbMF = dyndb_Model()
            fdbPS = dyndb_Modeled_Residues()
            fdbMC = dyndb_Model_Components()
            #return render(request,'dynadb/MODEL.html', {'rowsMR':rowsMR,'lcompname':lcompname,'lformps':lformps,'lformmc':lformmc,'SType':SType,'Type':Type,'lmtype':lmtype,'lmrstype':lmrstype,'rowsMC':rowsMC, 'p':p ,'l_ord_mol':l_ord_mol,'fdbPS':fdbPS,'fdbMC':fdbMC,'submission_id':submission_id, 'saved':True,'protlist':protlist})
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
def SMALL_MOLECULEview2(request,submission_id):
    print("REQUEST SESSIONS",request.session.items())
    print("REQUEST SESSIONS",request.path)
#    print("REQUEST SESSION id",request.session.id)
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
#       fdbMF=dyndb_CompoundForm(request.POST)
#       fdbCN= dyndb_Other_Compound_Names(request.POST)
#       fdbMF = dyndb_Molecule(request.POST)
#       fdbMfl = dyndb_Files_Molecule(request.POST)
#       fdbMM = dyndb_Complex_Molecule_Molecule(request.POST)
#
#       # check whether it's valid:
#       if fdbMF.is_valid() and fdbMfl.is_valid() and fdbMM.is_valid() and fdbCF.is_valid() and fdbCN.is_valid(): 
#           # process the data in form.cleaned_data as required

#           formMF=fdbMF.save(commit=False)
#           formMfl=fdbMfl.save(commit=False)
#           formMM=fdbMM.save(commit=False)

#           form.user=request.user
#           form.save()
#           # redirect to a new URL:
#           return HttpResponseRedirect('/dynadb/PROTEIN/')

#   # if a GET (or any other method) we'll create a blank form
#   else:

#       fdbMF = dyndb_Molecule()
#       fdbMfl = dyndb_Files_Molecule()
#       fdbMM = dyndb_Complex_Molecule_Molecule()
#       fdbCF=dyndb_CompoundForm()
#       fdbCN=dyndb_Other_Compound_Names()

#       return render(request,'dynadb/SMALL_MOLECULE2.html', {'fdbMF':fdbMF,'fdbMfl':fdbMfl,'fdbMM':fdbMM, 'fdbCF':fdbCF, 'fdbCN':fdbCN })
        
@csrf_exempt
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def generate_molecule_properties(request,submission_id):

    request.upload_handlers[1] = TemporaryMoleculeFileUploadHandlerMaxSize(request,50*1024**2)
    
    try:
        return _generate_molecule_properties(request,submission_id)
    except (RequestBodyTooLarge, FileTooLarge, TooManyFiles) as e:
        return HttpResponse(e.args[0],status=413,reason='Payload Too Large',content_type='text/plain; charset=UTF-8')
    except:
        raise
    

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
                try:
                    generate_png(mol,os.path.join(submission_path,pngname),logfile,size=pngsize)
                except:
                    try:
                        os.remove(os.path.join(submission_path,sdfname))
                    except:
                        pass
                    try:
                        os.remove(os.path.join(submission_path,pngname))
                    except:
                        pass
                    raise
                    msg = 'Error while drawing molecule.'
                    print(msg,file=logfile)
                    logfile.close()
                    data['msg'] = msg+' Please, see log file.'
                    return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
                data['download_url_png'] = join_path(submission_url,pngname,url=True)
                print('Finished with molecule.',file=logfile)
                logfile.close()
                del mol
                
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
@user_passes_test_args(is_submission_owner,redirect_field_name=None)           
def open_pubchem(request,submission_id):
    if request.method == 'POST':
        if 'cids' in request.POST.keys():
            cids = request.POST['cids'].split(',')
            query = ''
            for cid in cids:
                query += str(cid)+'[CompoundID] OR '
            query = query[:query.rfind(' OR ')]
            return render(request,'dynadb/open_pubchem.html',{'query':query,'action':'https://www.ncbi.nlm.nih.gov/pccompound/'})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)            
def open_chembl(request,submission_id):
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
            
#   def SMALL_MOLECULEview(request, submission_id):
#   
#       def handle_uploaded_file(f,p,name):
#           print("file name = ", f.name , "path =", p)
#           f.name=name
#           print("NEW name = ", f.name , "path =", p)
#           path=p+"/"+f.name
#           with open(path, 'wb+') as destination:
#               for chunk in f.chunks():
#                   destination.write(chunk)
#   
#       print(request.POST.keys())
#       author="jmr"   #to be modified with author information. To initPF dict
#       action="/".join(["/dynadb/MOLECULEfilled",submission_id,""])
#       now=timezone.now()
#       onames="Pepito; Juanito; Herculito" #to be modified... scripted
#       initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
#       initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
#       initON={'other_names': onames,'id_compound':None} 
#       dicpost=request.POST
#       dicfiles=request.FILES
#       initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
#       ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
#       ft=DyndbFileTypes.objects.all()
#       dict_ext_id={}
#       for l in ft:
#           dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
#   
#       d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
#       if request.method == 'POST':
#           dictmol={}
#           fieldsmol=["id_compound","description","net_charge","inchi","inchikey","inchicol","smiles"]
#           dictON={}
#           fieldsON=["other_names"]
#           dictcomp={}
#           fieldscomp=["name","iupac_name","pubchem_cid","chemblid","sinchi","sinchikey","std_id_molecule","id_ligand"]
#           dictfmol={} 
#           fieldsPMod={"is_present","type"}
#           dictPMod={}
#           form=re.compile('form-')
#           indexl=[]
#          # print("!!!!!indexl== ",indexl)
#           nl=0 #counter of pairs in dicpost.items()
#           for key,val in dicpost.items():
#               nl=nl+1
#               if form.search(key):
#                   index=int(key.split("-")[1])
#                   if index not in indexl:
#                       indexl.append(index)
#                       dictmol[index]={}
#                       dictON[index]={}
#                       dictcomp[index]={}
#                       dictPMod[index]={}
#                   nkey="-".join(key.split("-")[2:])  
#                   #dictmol[index]["-".join(key.split("-")[2:])]=val
#               else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
#                   if len(indexl)==0:
#                       index=0
#                       indexl.append(0)
#                       dictmol[0]={}
#                       dictON[0]={}
#                       dictcomp[0]={}
#                       dictPMod[index]={}
#                   nkey=key
#              # print("indexl==V ",indexl)
#                   #dictmol[0][key]=val
#                   #dictON[0][key]=val
#                   #dictfmol[0][key]=val
#               #print("\nINICIO: key-val== ",key," ",val,"nkey ==", nkey,"\n")
#               dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
#               dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
#               for k,v in dfieldtype.items():
#                   if nkey in v:
#                       dfielddict[k][index][nkey]=val
#                     #  print("Index ", index, "Indexl", indexl, " key== ",key, " Lista== ", v, " nkey", nkey)
#                     #  print ("\n key ", nl, "dfielddict == ", dfielddict)
#                       break
#              #     else:
#              #         print("OJO!!! key== ",key, " no en Lista== ", v)
#               print ("\n key ", nl, "dfielddict == ", dfielddict)
#               continue 
#           indexl.sort()
#           print(indexl)
#           #print ("number of pairs in request.POST ===", nl, "\n ", dfielddict['0'],"\n",dfielddict['1'],"\n",dfielddict['2'])
#           indexfl=[]
#           if len(dicfiles) == 0:
#               response = HttpResponse('No file has been uploaded',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
#               return response
#           for key,val in dicfiles.items():
#               if form.search(key):
#                   indexf=int(key.split("-")[1])
#                   nkey="-".join(key.split("-")[2:])  
#                   if indexf not in indexfl:
#                       indexfl.append(indexf)
#                       dictfmol[indexf]={}
#                   #dictmol[index]["-".join(key.split("-")[2:])]=val
#               else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
#                   if len(indexfl)==0:
#                       indexf=0
#                       indexfl.append(0)
#                       dictfmol[0]={}
#                   nkey=key
#               dictfmol[indexf][nkey]=val
#         #  print("INDEXFL", indexfl)
#           fdbMF={}
#           fdbMFobj={}
#           fdbCF={}
#           fdbCFobj={}
#           fdbON={}
#           fdbONobj={}
#           dON={}
#           on=0
#        #   print("ANTES SORT",indexfl, indexl)
#           if len(indexl) > 1:
#               indexfli=list(map(int,indexfl))
#               indexli=list(map(int,indexl))
#               indexfl=sorted(indexfli)
#               indexl=sorted(indexli)
#           #print(indexfl, indexl)
#           dicfmole={}
#           fdbF={}
#           fdbFobj={}
#           fdbFM={}
#           fdbSM={}
#           fdbFMobj={}
#           Std_id_mol_update=[]
#   
#           for ii in indexl:
#               Std_id_mol_update.append(True)
#               print("len(Std_id_mol_update)= ",len(Std_id_mol_update), "ii", ii, "indexl ",indexl)
#               fdbCF[ii]={}
#               fdbCFobj[ii]={}
#               fdbMF[ii]={}
#               fdbSM[ii]={}
#               fdbMFobj[ii]={}
#               fdbON[ii]={}
#               fdbONobj[ii]={}
#               dON[ii]={}
#                
#               #### Check if the molecule is already in our Database. If so the standar molecule shoud be as well!!!!!
#   
#               qMF=DyndbMolecule.objects.filter(inchikey=dictmol[ii]['inchikey']).filter(inchi=dictmol[ii]['inchi'].split('=')[1])
#               print("\nQuery Molecule antes aux\n ",qMF.filter(id__gt=7).values())
#                                                   #generation of the sinchi
#               #dictcomp[ii]['sinchi']=    
#   
#               if dictcomp[ii]['pubchem_cid']!='':
#                   qCFStdFormExist=DyndbCompound.objects.filter(pubchem_cid=dictcomp[ii]['pubchem_cid']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
#               elif dictcomp[ii]['chemblid']!='':
#                   qCFStdFormExist=DyndbCompound.objects.filter(chemblid=dictcomp[ii]['chemblid']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
#               else: 
#                   qCFStdFormExist=DyndbCompound.objects.filter(sinchikey=dictcomp[ii]['sinchikey']).filter(sinchi=dictcomp[ii]['sinchi']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
#               if len(qMF.values())==1: #there is a entry matching this molecule
#                   if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
#                       dictPMod[ii]['not_in_model']=False
#                   else:
#                       dictPMod[ii]['not_in_model']=True
#   
#                   dictPMod[ii]['int_id']=ii
#                   dictPMod[ii]['submission_id']=submission_id
#                   MFpk=qMF.values_list('id',flat=True)[0]
#                   dictPMod[ii]['molecule_id']=MFpk
#                   fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
#   
#                   if fdbSM[ii].is_valid(): # only the submission molecule table should be filled!!!!
#                       fdbSM[ii].save()
#                   else:    
#                       iii1=fdbSM[ii].errors.as_data()
#                       print("fdbSM",ii," no es valido")
#                       print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#   
#                   if ii==indexl[-1]:#if ii is the last element of the list indexl
#                       print("Molecule #", ii, "has been found in our database")
#                       break
#                   else:
#                       print("Molecule #", ii, "has been found in our database")
#                       continue
#   
#               elif len(qMF.values())>1:
#                   response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain; charset=UTF-8')
#                   return response
#   
#   #########   Use of functions retrieving std_molecule info from external sources!!!! It is needed for updatingi
#               molid=ii 
#               submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
#               sdfnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
#   
#               path_namef=("").join([submission_path, sdfnameref])
#               INFOstdMOL=generate_molecule_properties2(submission_id,molid) #:INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
#               sinchi_fixed=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
#               INFOstdMOL['sinchi']['sinchi']=INFOstdMOL['sinchi']['sinchi'].split('=')[1]
#               INFOstdMOL['inchi']['inchi']=INFOstdMOL['inchi']['inchi'].split('=')[1]
#                   
#   #### check if the molecule is actually the standard form of the molecule. If this specific form of the molecule is not in the database (DyndbMolecule) but other molecules corresponding the same compound are, the one we are dealing with won`t be the standard as it is previously recorded when the first molecule corresponding the compound was registered. So, if there is no any entry in the DyndbCompound table matching the sinchikey of the molecule in the form, still will be possible that the current entry would be the standard form.
#               if len(qCFStdFormExist.values())==1: #The compound and the standard form of the current molecule is in the database (Only fill the current non standard molecule)
#                   print("Compound entry matching SInChIKey and SInChI has been found in GPCRmd database")
#                   CFpk=qCFStdFormExist.values_list('id',flat=True)[0]
#                   Std_id_mol_update[ii]=False
#               elif len(qCFStdFormExist.values())>1: #the compound is found more than once in the database
#                   response("Several Compound entries have been found in the DATABASE. Please, report this ERROR to the GPCRmd database administrator")
#                   return response
#               elif len(qCFStdFormExist.values())==0: #Neither the compound nor the standard form of the molecule are in the database
#                   Std_id_mol_update[ii]=True
#            #### No compound entry has been found in GPCRmd DB.Keep track of the Compound in the DyndbCompound table and the aliases in the DyndbOtherCompoundNames
#              
#                   #### DyndbCompound
#   
#                   for key,val in initCF.items():
#                       if key not in dictcomp[ii].keys():
#                           dictcomp[ii][key]=val
#                       if key == "sinchi":
#                           dictcomp[ii][key]=sinchi_fixed
#                   fdbCF[ii]=dyndb_CompoundForm(dictcomp[ii]) 
#                   if fdbCF[ii].is_valid():
#                       fdbCFobj[ii]=fdbCF[ii].save()
#                       CFpk=fdbCFobj[ii].pk
#                   else:
#                       print("Errores en el form dyndb_CompoundForm\n ", fdbCF[ii].errors.as_data())
#              
#                   #### DyndbOtherCompoundNames 
#                   ONlist=dictON[ii]["other_names"].split(";")
#              
#                   for el in ONlist:
#                       on=on+1
#                       dON[ii][on]={}
#                       dON[ii][on]["other_names"]=el
#                       dON[ii][on]["id_compound"]=CFpk
#                       fdbON[ii][on]=dyndb_Other_Compound_Names(dON[ii][on]) 
#                       if fdbON[ii][on].is_valid():
#                           fdbON[ii][on].save()
#                       else:
#                           print("Errores en el form dyndb_Other_Compound_Names\n ", fdbON[ii][on].errors.as_data())
#      #### Get the standard Molecule by providing the SInChIKey to the PubChem or CHEMBL databases if the molecule is actually the standard form of the molecule.
#   
#   #### DyndbCompound and DyndbOtherCompoundNames tables have been filled. Then entries for the std molecule should be registered in DyndbMolecule and DyndbSubmissionMolecule
#                   if 'msg' in INFOstdMOL.keys():
#                       HttpResponse(INFOstdMOL['msg']) 
#        #### Check if inchi of the standard molecule matches the inchi in the current entry (HTML form)         
#                   print("COMPROBAR ",INFOstdMOL)
#                   
#                   
#                   if INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'].split('=')[1]: #Both molecules are the standard molecule so one entry is saved
#                       print("The molecule ",ii, "is actually the standard molecule")
#                       dictmol[ii]['description']="Standard form"
#                   else:
#                       auxdictmol={}
#                       print("The molecule ",ii, "is not the standard molecule. The standard one will be saved right now!!!!")
#                       for key,val in INFOstdMOL.items():# HAY QUE INTRODUCIR LOS DATOS DEL SCRIPT PARA PODER CREAR UN DICCIONARIO PARA LA INSTANCIA!!!
#                           print("AQUI ",key,val)
#                           if type(val)==dict:
#                               auxdictmol[key]=val[key]
#                               print("auxdictmol inchi ", auxdictmol[key] )
#                                #   "Problem while generating inchi:\n"+ msg   
#                           
#                           if key in dfieldtype['0']:
#                               if key == 'inchikey':
#                                   auxdictmol[key]=val.split('=')[1]  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
#                                   nrep_inchikey=len(DyndbMolecule.objects.filter(inchikey=val))
#                                   if nrep_inchikey >= 1:
#                                       auxdictmol['inchicol']=nrep_inchikey+1
#                                   else:
#                                       auxdictmol['inchicol']=1
#                               elif key == 'inchi':
#                                   auxdictmol['inchi']=INFOstdMOL['inchi']['inchi']
#                               elif key == 'description':
#                                   auxdictmol['description']="Standard form"
#                               else:
#                                   auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
#                      
#                       for key,val in initMF.items():
#                           if key not in auxdictmol.keys():
#                               auxdictmol[key]=val  ##### completion of the dictionary
#                       auxdictmol['id_compound']=CFpk
#                       fdbMFaux=dyndb_Molecule(auxdictmol)
#                       if fdbMFaux.is_valid():
#                           fdbMFobj=fdbMFaux.save()
#                           MFauxpk=fdbMFobj.pk
#                       else:
#                           print("Errores en el form dyndb_Molecule\n ", fdbMFaux.errors.as_data())
#         
#                   #### Entry in DyndbSubmissionMolecule corresponding to the standard molecule 
#                       auxdictPMod={}
#                       auxdictPMod['not_in_model']=True
#                       auxdictPMod['int_id']=None
#                       auxdictPMod['submission_id']=submission_id
#                       auxdictPMod['molecule_id']=MFauxpk
#                       fdbSMaux=dyndb_Submission_Molecule(auxdictPMod)
#         
#                       if fdbSMaux.is_valid(): # only the submission molecule table should be filled!!!!
#                           fdbSMaux.save()
#                       else:    
#                           iii1=fdbSMaux.errors.as_data()
#                           print("fdbSMaux",ii," no es valido")
#                           print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#   
#              #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule 
#                       # In this block the condition INFOstdMOL['inchi']['inchi']==dictmol[ii]['inchi'] is false. Then the std molecule pk is MFauxpk and the flag Std_id_mol_update is set
#                       # to False in order to avoid subsequents updates when the molecule in the form (not standard) would be entried.
#                       DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFauxpk) 
#                       Std_id_mol_update[ii]=False
#   
#   #___________________________________________________________________________________
#   #           The code enclosed in this section is not dependent on whether the Compound has an entry in the database!!!  
#   
#               for key,val in initMF.items():
#                   if key not in dictmol[ii].keys():
#                       dictmol[ii][key]=val
#               dictmol[ii]['id_compound']=CFpk
#               dictmol[ii]['inchi']=dictmol[ii]['inchi'].split('=')[1]
#               fdbMF[ii]=dyndb_Molecule(dictmol[ii])
#               if fdbMF[ii].is_valid():
#                   fdbMFobj[ii]=fdbMF[ii].save()
#                   MFpk=fdbMFobj[ii].pk
#               else:
#                   print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_data())
#   
#              #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule
#              # if the Std_id_mol_update flag is set to True the molecule in the form is the standard one and the std_id_molecule field in DyndbCompound should be update with MFpk
#               if Std_id_mol_update[ii]:
#                   DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFpk) 
#                   Std_id_mol_update[ii]=False
#              
#               if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
#                   dictPMod[ii]['not_in_model']=False
#               else:
#                   dictPMod[ii]['not_in_model']=True
#               dictPMod[ii]['int_id']=ii
#               dictPMod[ii]['submission_id']=submission_id
#               dictPMod[ii]['molecule_id']=MFpk
#               fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
#               if fdbSM[ii].is_valid():
#                   fdbSM[ii].save()
#               else:    
#                   iii1=fdbSM[ii].errors.as_data()
#                   print("fdbSM",ii," no es valido")
#                   print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#   #________________________________________________________________________________
#   
#   
#               print("\nQuery Molecule antes de la evaluacion \n ",qMF.filter(id__gt=7).values())
#               if len(qMF.values())==1:
#                   print("Your molecule is already present in our database")               
#               elif len(qMF.values())>1:
#                   response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain; charset=UTF-8')
#                   return response
#               elif len(qMF.values())==0:
#                   direct='/protwis/sites/files/Molecule/mol'+str(submission_id)
#                   print("\nDirectorio a crear ", direct)
#                   if not os.path.exists(direct):
#                       os.makedirs(direct)
#                
#                   fdbF[ii]={}
#                   fdbFobj[ii]={}
#                   for key,val in dictfmol[ii].items():
#                       fext="".join(val.name.split(".")[1:])
#                       print("val ",val, " ;val split",fext," Tambien id", dict_ext_id[fext])
#                       #print("val ",val, " ;val split",fext," Tambien id")
#                       if fext in dict_ext_id.keys():
#                           initFiles['id_file_types']=dict_ext_id[fext]
#                           initFiles['filename']=val.name
#                           initFiles['filepath']=direct
#                           initFiles['description']="sdf/mol2 requested in the molecule form"
#                
#                           fdbF[ii][key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
#                           dicfmole[ii]={}
#                           fdbFM[ii]={}
#                           if fdbF[ii][key].is_valid():
#                               fdbFobj[ii][key]=fdbF[ii][key].save()
#                               newname=str(fdbFobj[ii][key].pk)+"_mol_"+str(submission_id)+"."+fext
#                               handle_uploaded_file(dictfmol[ii][key],direct,newname)
#                               completepath=direct+"/"+newname
#                               fdbFobj[ii][key].filename=newname   #rename filename in the database after saving the initial name
#                               fdbFobj[ii][key].filepath=completepath   #rename filename in the database after saving the initial name
#                               fdbFobj[ii][key].save() 
#                               dicfmole[ii]['type']=d_fmolec_t['Molecule'] #Molecule
#                               dicfmole[ii]['id_molecule']=MFpk
#                               dicfmole[ii]['id_files']=fdbFobj[ii][key].pk
#                               fdbFM[ii][key]=dyndb_Files_Molecule(dicfmole[ii])
#                               if fdbFM[ii][key].is_valid():
#                                   fdbFM[ii][key].save()
#                               else:
#                                   print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[ii][key].errors.as_data())
#                           else:
#                               print("Errores en el form dyndb_Files\n ", fdbF[ii][key].errors.as_data())
#                       else:
#                           print("This extension is not valid for submission")
#   
#           return HttpResponseRedirect("/".join(["/dynadb/MOLECULEfilled",submission_id,""]), {'submission_id':submission_id })
#                           
#                          
#   
#           # check whether it's valid:
#       else:
#   
#           fdbMF = dyndb_Molecule()
#           fdbSub = dyndb_Submission_Molecule()
#           fdbCF=dyndb_CompoundForm()
#           fdbON=dyndb_Other_Compound_Names()
#           fdbF = dyndb_Files()
#           fdbFM = dyndb_Files_Molecule()
#           fdbMM = dyndb_Complex_Molecule_Molecule()
#   
#           return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbSub':fdbSub,'fdbCF':fdbCF,'fdbON':fdbON, 'fdbF':fdbF, 'fdbFM':fdbFM, 'fdbMM':fdbMM, 'submission_id' : submission_id})
@textonly_500_handler
@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
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
    filetype_dbtypestext_dict = {'coor':'coor','top':'top','traj':'traj','parm':'param','other':'other'}
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
def upload_dynamics_files(request,submission_id,trajectory=None):
    trajectory_max_files = 200
    if trajectory is None:
        request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,50*1024**2)
    else:
        request.upload_handlers[1] = TemporaryFileUploadHandlerMaxSize(request,2*1024**3,max_files=trajectory_max_files)
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
    file_types['coor']['db'] = ["is_model"]
    file_types['top']['db'] = ["is_topology"]
    file_types['traj']['db'] = ["is_trajectory"]
    file_types['parm']['db'] = ["is_parameter","is_anytype"]
    file_types['other']['db'] = ["is_anytype"]
    
    file_types['coor']['long_name'] = "Coordinate file"
    file_types['top']['long_name'] = "Topology file"
    file_types['traj']['long_name'] = "Trajectory files"
    file_types['parm']['long_name'] = "Simulation parameters"
    file_types['other']['long_name'] = "Other files"
    file_types['coor']['description'] = "Upload the initial coordinates file of the system in PDB format (.pdb) max 50 MB."
    file_types['top']['description'] = "Upload the file describing the topology of your system. Top (.psf, .prmtop, .top, other) max 50 MB."
    file_types['traj']['description'] = "Upload the files containing the evolution of the system coordinates with time. Traj (.dcd, .xtc) max. 2 GB."
    file_types['parm']['description'] = "Upload the file containing the force field parameters. Param (.tar.gz,.tgz) max 50 MB."
    file_types['other']['description'] = "Additional files needed for rerunning the simulation. Include here individual topology files and parameters that are not published elsewhere (e.g. resulting from optimitzation). max 50 MB."
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

@csrf_protect
def _upload_dynamics_files(request,submission_id,trajectory=None,trajectory_max_files=200):
    
    file_types = get_dynamics_file_types()
    file_type = None
    new_window = '0'
    no_js = '1'
    download_url = ''
    error = ''
    filetype_complete_names = {'coor':'coordinate','top':'topology','traj':'trajectory','parm':'parameter','other':'other'}
    filetype_subtypes_dict = {'coor':'pdb','top':'topology','traj':'trajectory','parm':'parameters','other':'other'}
    filetype_dbtypestext_dict = {'coor':'coor','top':'top','traj':'traj','parm':'param','other':'other'}
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
    
    accept_string = ',.'.join(file_types[file_type]['extension'])
    accept_string = '.' + accept_string
    action ='./?file_type='+file_type+'&new_window='+str(new_window)+'&no_js='+str(no_js)+'&timestamp='+str(round(time.time()*1000))
    
    if request.method == "POST":
        exceptions = False
        data = dict()
        data['download_url_file'] = []
        if file_type in filetype_subtypes_dict:
            subtype = filetype_subtypes_dict[file_type]
        else:
            response = HttpResponse('Unknown file type: '+str(file_type),status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
            return response
            
        if file_type in atomnum_check_file_types:    
            reffilepath, reffilename, ref_file_type, ref_numatoms = get_dynamics_files_reference_atomnum(submission_id,file_type)
            prev_numatoms = ref_numatoms
        
        
        dbtype = type_inverse_search(DyndbSubmissionDynamicsFiles.file_types,searchkey=filetype_dbtypestext_dict[file_type],case_sensitive=False,first_match=True)
        submission_path = get_file_paths("dynamics",url=False,submission_id=submission_id)
        submission_url = get_file_paths("dynamics",url=True,submission_id=submission_id)    
        try:
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
                        dyndb_submission_dynamics_files = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype)
                        dyndb_submission_dynamics_files = dyndb_submission_dynamics_files.values('filepath')
                        
                        for row in dyndb_submission_dynamics_files:
                            filepath2 = row['filepath']
                            if os.path.exists(filepath2):
                                os.remove(filepath2)
                                
                        dyndb_submission_dynamics_files = DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id,type=dbtype)
                        dyndb_submission_dynamics_files.delete()
                    elif prev_numatoms != numatoms:
                        response = HttpResponse('Uploaded trajectory file "'+uploadedfile.name+'" number of atoms ('+str(numatoms)+') differs from "'+prev_name+'".',status=432,reason='Partial Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                        return response
                    prev_name = uploadedfile.name
                    prev_numatoms = numatoms

                    
                
                (file_entry,created) = DyndbSubmissionDynamicsFiles.objects.update_or_create(submission_id=DyndbSubmission.objects.get(pk=submission_id),type=dbtype,filenum=filenum,defaults={'filename':filename,'filepath':filepath,'url':download_url})
                
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

        return render(request,'dynadb/DYNAMICS_file_upload.html',{'action':action,'file_type':file_type,
        'long_name':file_types[file_type]['long_name'],'description':file_types[file_type]['description'],
        'new_window':new_window,'download_url':download_url,'success':None,'error':'','accept_ext':accept_string,'no_js':no_js,'get':True})





@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def DYNAMICSview(request, submission_id, model_id=None):
    def_user_dbengine=settings.DATABASES['default']['USER']
    def_user=request.user.id
    initDyn={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() , 'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user ,  'id_model':model_id,'submission_id':submission_id }
    initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }
    initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None,'id_structure_model':None, 'template_id_model':None,'model_creation_submission_id':submission_id,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user    }
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'submission_id':None ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  }
                   
    def dynamics_file_table (dname, DFpk): #d_fmolec_t, dictext_id 
        print(dname)
        fdbF={}
        fdbFobj={}
        qft=DyndbFileTypes.objects.all().values()
        ext_to_descr={'pdb': "pdb simulation coordinates file", 'psf':'psf simulation topology file', 'prm':"prm simulation parameters file", 'dcd':"dcd simulation trajectory file", 'xtc':"xtc simulation trajectory file", 'tar.gz':'parameters or other simulation files' }  
       #####  
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            if l.__dict__['extension'].rstrip() == "psf":
                dict_ext_id[l.__dict__['extension'].rstrip()]=5

            elif l.__dict__['extension'].rstrip() == "prm":
                dict_ext_id[l.__dict__['extension'].rstrip()]=5
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
             initFiles['description']=ext_to_descr[fext]
             print("HOLA initFiles", initFiles)
    
             fdbF[key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
             dicfdyn={}
             dicfdyn['type']=val['type']
             fdbFM={}
             if fdbF[key].is_valid():
                 fdbFobj[key]=fdbF[key].save()
                 dicfdyn['id_dynamics']=DFpk
                 dicfdyn['id_files']=fdbFobj[key].pk
             else:
                 prev_entryFile=DyndbFiles.objects.filter(dyndbfilesdynamics__id_dynamics__submission_id=submission_id,id_file_types=initFiles['id_file_types'])
                 dicfdyn['id_files']=prev_entryFile.values_list('id',flat=True)[0]
                 dicfdyn['id_dynamics']=DFpk
                 prev_entryFile.update(update_timestamp=timezone.now(), filepath=initFiles['filepath'],url=initFiles['url'],id_file_types=initFiles['id_file_types'],description=initFiles['description'])
          #  else:
          #      print("Errores en el form dyndb_Files\n ", fdbF[key].errors.as_text())
          #      error=("- ").join(["Error when storing File info",ext_to_descr[fext]])
          #      response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
          #      return response
             fdbFM[key]=dyndb_Files_Dynamics(dicfdyn)
             if fdbFM[key].is_valid():
                 fdbFM[key].save()
             else:
                 prev_entryFileM=DyndbFilesDynamics.objects.filter(id_dynamics__submission_id=submission_id,id_files__id_file_types=initFiles['id_file_types'])
                 prev_entryFileM.update(id_dynamics=dicfdyn['id_dynamics'],id_files=dicfdyn['id_files'])

          #  else:
          #      error=("- ").join(["Error when storing Dynamics file info",ext_to_descr[fext]])
          #      print("Errores en el form dyndb_Files\n ", fdbFM[key].errors.as_text())
          #      response = HttpResponse(error,status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
          #      return response

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

#        with open('/protwis/sites/protwis/dynadb/dict_ext_id.txt', 'wb') as handle:
 #           pickle.dump(dict_ext_id, handle)
          
        print("JJJJJJJJ")
        # Defining a dictionary "d_fdyn_t" containing choices in the table dyndb_files_dynamics (field 'type')

        d_fdyn_t={'coor':'0','top':'1','traj':'2','parm':'3','other':'3'}

        dicpost=request.POST
        #dicfiles=request.FILES
        #print(dicfiles)
        #print("CLASS traj",type(request.FILES['traj'])," ",request.FILES['traj'] )
        #print("CLASS traj",type(request.FILES['traj'])," ",request.FILES.getlist('traj') )
        #print(len(request.FILES.getlist('traj')))
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

            if dyn_ins[ii].is_valid():
                qDe=DyndbDynamics.objects.filter(submission_id=submission_id)
                if len(qDe) == 0:
                    PREVIOUS_COMP=False
                    dyn_obj[ii]=dyn_ins[ii].save()
                    DFpk=dyn_obj[ii].pk
                else:
                    PREVIOUS_COMP=True
                    print("\n\n PREVIOUS COMPOUNDS updating dyn object")
                    DFpk=qDe.values_list('id',flat=True)[0]
                    qDe.update(update_timestamp=timezone.now(),delta=POSTimod[ii]['delta'], description=POSTimod[ii]['description'].strip() , ff=POSTimod[ii]['ff'].strip(), ffversion=POSTimod[ii]['ffversion'].strip() , id_dynamics_solvent_types =POSTimod[ii]['id_dynamics_solvent_types'], solvent_num =POSTimod[ii]['solvent_num'], sversion =POSTimod[ii]['sversion'].strip() , atom_num = POSTimod[ii]['atom_num'], timestep =POSTimod[ii]['timestep'], id_dynamics_methods =POSTimod[ii]['id_dynamics_methods'] , software=POSTimod[ii]['software'].strip() ,  id_dynamics_membrane_types =POSTimod[ii]['id_dynamics_membrane_types'], id_assay_types =POSTimod[ii]['id_assay_types'])
            else:
                iii1=dyn_ins[ii].errors.as_text()
                print("errors in the form Dynamics", ii," ", dyn_ins[ii].errors.as_text())
                response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                return response

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
            #print("\nlista numero 0 \n",Pscompmod[ii][0].items() )
           # print("\nlista numero 0 entera \n",Pscompmod[ii] )
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








































#               elif  lenCompDB < lenform:
#                   print("\n HIGHER number of form rows")
#                   for val in new_val:
#                       if BREAK2:
#                           break
#                       if len(del_el)>0:
#                           for el in del_el: 
#                               if val in used_new_val:
#                                  continue
#                               qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
#                               used_new_val.append(val)
#                               used_del_el.qppend(el)
#                               if el == used_del_el[-1]:
#                                   if len(lempty_rows) > 0:
#                                       for i in lempty_rows:
#                                           for val in new_val:
#                                               if val not in used_new_val:
#                                                   if not i == lempty_rows[-1]:
#                                                       qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
#                                                       used_new_val.append(val)
#                                                       break 
#                                                   else:
#                                                       Scom_inst=dyndb_Dynamics_Components(val)
#                                                       if Scom_inst.is_valid():
#                                                           Scom_obj=Scom_inst.save()
#                                                           continue
#                                                       else:
#                                                           iii1=Scom_inst.errors.as_text()
#                                                           print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
#                                                           response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
#                                                           return response                                                                                                         
#                       elif len(lempty_rows) > 0:
#                           print("\n LENGHT EMPTY ROWS", len(lempty_rows))
#                           for i in lempty_rows:
#                               for val in new_val:
#                                   if val not in used_new_val:
#                                       if not i == lempty_rows[-1]:
#                                           print("\n LENGHT EMPTY ROWS", lempty_rows, val)
#                                           qDC_empty_rows.filter(id=i).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
#                                           used_new_val.append(val)
#                                           print("\n LENGHT EMPTY ROWS", lempty_rows, qDC_match_form.values())
#                                           break 
#                                       else:
#                                           Scom_inst=dyndb_Dynamics_Components(val)
#                                           if Scom_inst.is_valid():
#                                               Scom_obj=Scom_inst.save()
#                                               continue
#                                           else:
#                                               iii1=Scom_inst.errors.as_text()
#                                               print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
#                                               response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
#                                               return response                                                                                                         
#                       else: 
#                           Scom_inst=dyndb_Dynamics_Components(val)
#                           if Scom_inst.is_valid():
#                               Scom_obj=Scom_inst.save()
#                               continue
#                           else:
#                               iii1=Scom_inst.errors.as_text()
#                               print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
#                               response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
#                               return response                                                                                                         







   #            if counterf == len(Pscompmod[ii]): # the number of components in the form have been parsed in the previous for loop. That implies at 
   #                ldel_el=len(del_el)
   #                lnew_val=len(new_val)
   #                print ("\n PIPOL!!!!!")
   #                if ldel_el >0 and lnew_val>0:
   #                    ldel_used=[]#old entries of components not used in the last version of the model updated to new components 
   #                    lnval_used=[] #new form components already updated
   #                    for el in ldel_el:
   #                        print ("\nLOOP c counterf == len(Pscompmod[ii]):")
   #                        if BREAK2:
   #                            if ldel_el>lnew_val:
   #                                for el in ldel_el:
   #                                    if el not in ldel_used:
   #                                        qDC_match_form.filter(id=el['id']).update(numberofmol=1,resname="___")  
   #                            elif ldel_el<lnew_val:
   #                                for val in lnew_val:
   #                                    if val not in lnval_used:
   #                                        Scom_inst=dyndb_Dynamics_Components(val)
   #                                        if Scom_inst.is_valid():
   #                                            Scom_obj=Scom_inst.save()
   #                                        else:
   #                                            iii1=Scom_inst.errors.as_text()
   #                                            print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
   #                                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
   #                                            return response                                                                                                         
   #                            break

   #                        if el in ldel_used:
   #                            continue
   #                        for val in newval:
   #                            if val in lnval_used:
   #                                continue 
   #                            qDC_match_form.filter(id=el['id']).update(numberofmol=val['numberofmol'], id_molecule=val['id_molecule'],id_dynamics=val['id_dynamics'],resname=val['resname'],type=val['type'])
   #                            lnval_used.append(val)
   #                            ldel_used.append(el)
   #                            if len(lnval_used)==lnew_val or len(ldel_used) ==ldel_el:
   #                                BREAK2=True 
   #                                break

   #                elif ldel_el >0:
   #                    for el in ldel_el:
   #                        qDC_match_form.filter(id=el['id']).update(numberofmol=1,resname="___",type=None)  
   #                elif lnew_val >0:
   #                    for val in lnew_val:
   #                        Scom_inst=dyndb_Dynamics_Components(val)
   #                        if Scom_inst.is_valid():
   #                            Scom_obj=Scom_inst.save()
   #                        else:
   #                            iii1=Scom_inst.errors.as_text()
   #                            print("errors in the form Dynamics Components", Scom_inst.errors.as_text())                                   
   #                            response = HttpResponse(iii1,status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')                         
   #                            return response                                                                                                         

            #Create storage directory: Every Simulation # has its own directory labeled as "dyn"+dyn_obj[ii].pk
            #Maybe we have to label the directory with submissionID?????
            direct='/protwis/sites/files/Dynamics/dyn'+str(submission_id)
            print("\nDirectorio a crear ", direct)
            if not os.path.exists(direct):
                os.makedirs(direct)
            
            qSDF=DyndbSubmissionDynamicsFiles.objects.filter(submission_id=submission_id)
            lfiles=list(qSDF.values('filepath','url','type'))
            for f in lfiles:
                if not isfile(f['filepath']):
                    response = HttpResponse((" ").join(["There is a simulation file which has not been succesfully saved (",f[filename],") Make the GPCRmd administrator know"]),status=500,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
                    return response
                else:
                    dname={'file':{'path':f['filepath'],'url':f['url'],'type':f['type']}}
                    ooofile= dynamics_file_table(dname,DFpk) 
                    if type(ooofile)==HttpResponse:
                        return ooofile 

        response = HttpResponse('Step 4 "Dynamics Information" form has been successfully submitted.',content_type='text/plain; charset=UTF-8')
        return response
 
       # return HttpResponseRedirect("/".join(["/dynadb/DYNAMICSfilled",submission_id,""]))
                    

    else:
        qDYNs=DyndbDynamics.objects.filter(submission_id=submission_id)
        qMOD=DyndbSubmissionModel.objects.filter(submission_id=submission_id).order_by('id').values('model_id')
        qSubMOD=DyndbSubmissionModel.objects.filter(model_id=qMOD)
        ModelReuse=False
        if len(qSubMOD) > 1:
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
                querySM=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(molecule_id__in=queryDC.values('id_molecule'))
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
                  #  ddctypel.append(DyndbModelComponents.MOLECULE_TYPE[smol_to_dyncomp_type[l['id_molecule__dyndbsubmissionmolecule__type']]][0]                       
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
        
 
##       return HttpResponse(qDS.values_list()[0])
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
##############################################################################################################



#       postspl={}
#       postsplmod={}
#       dmodinst={}
#       dinst={}
#       for key,val in dicpost.items():
#           if re.search('formc',key):
#               index=int(key.split("-")[1])
#               if index not in indexl:
#                   indexl.append(index)
#                   postspl[index]={}
#                   postsplmod[index]={}
#                   
#               postspl[index][key]=val
#               postsplmod[index][key.split("-")[2]]=val

#       if len(indexl)==0:
#           indexl=[1]
#           postsplmod[1]={}    
#           for key,val in dicpost.items():
#               if key not in ddi.__dict__.keys():
#                   postsplmod[1][key]=val



#       print("created by dbengine antes de validar", dd.data['created_by_dbengine'])

#       if dd.is_valid():
#           # process the data in form.cleaned_data as required
#           ddi=dd.save(commit=False)
#           with open('/protwis/sites/protwis/dynadb/DYNdd.txt', 'wb') as handle:
#               pickle.dump(ddi, handle)

#           dd.save()
#           with open('/protwis/sites/protwis/dynadb/DYNddi.txt', 'wb') as handle:
#               pickle.dump(ddi, handle)
#           dynafk=ddi.pk 
#           print(dynafk)
#           dicpost=request.POST
#           postspl={}
#           postsplmod={}
#           dmodinst={}
#           indexl=[]
#           dinst={}
#           for key,val in dicpost.items():
#               if re.search('formc',key):
#                   index=int(key.split("-")[1])
#                   if index not in indexl:
#                       indexl.append(index)
#                       postspl[index]={}
#                       postsplmod[index]={}
#                       
#                   postspl[index][key]=val
#                   postsplmod[index][key.split("-")[2]]=val

#           if len(indexl)==0:
#               indexl=[1]
#               postsplmod[1]={}    
#               for key,val in dicpost.items():
#                   if key not in ddi.__dict__.keys():
#                       postsplmod[1][key]=val
#                        

#           print("longitud postspl[1]",len(postsplmod[1]), postsplmod)
#           print("lista de indices", indexl) 
#           for val in indexl:
#               print("componente ", val, " ", postsplmod[val])
#               postsplmod[val]['id_dynamics']=dynafk
#               postsplmod[val]['id_molecule']=int(val+1) #este valor debe modificarse se le suma 1 porque si no no lo acepta el html (pide opciones entre uno y 7)
#               dinst[val]=dyndb_Dynamics_Components(postsplmod[val])
#               if dinst[val].is_valid():
#                   dmodinst[val]=dinst[val].save(commit=False)
#                   dmodinst[val]=dinst[val].save()
#                   print("diccionario ", val, "  ", dmodinst[val].__dict__) 
#               else:
#                   print("Errores de la instancia del form nº",val," ",  dinst[val].errors.as_data())

#         #  ttt=ddi.created_by_dbengine
#         #  print("created by dbengine despues de grabar", ttt)

#           # redirect to a new URL:
#           return HttpResponseRedirect('/dynadb/DYNAMICSfilled/')
#       else:
#           iii2=dd.errors.as_data()
#           print("Errores en dynamics: ",iii2)

#   # if a GET (or any other method) we'll create a blank form
#   else:
#       dd=dyndb_Dynamics()
#      # ddT= dyndb_Dynamics_tags()
#      # ddTL=dyndb_Dynamics_Tags_List()

#       return render(request,'dynadb/DYNAMICS.html', {'dd':dd})
@login_required
def DYNAMICSviewOLD(request):
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        action="/dynadb/DYNAMICSfilled/"
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted
        initDD={'id_model':'1','id_compound':'1','update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
        dd=dyndb_Dynamics(request.POST)
                



        for key,value in initDD.items():
            dd.data[key]=value

        print("\npath", os.getcwd())
        ##for key,value in data.items():
        ##    f.write(str(key,value))
#        ff.write(data)
        print("created by dbengine antes de validar", dd.data['created_by_dbengine'])

        if dd.is_valid():
            # process the data in form.cleaned_data as required
            ddi=dd.save(commit=False)

            dd.save()
            dynafk=ddi.pk 
            print(dynafk)
            dicpost=request.POST
            postspl={}
            postsplmod={}
            dmodinst={}
            indexl=[]
            dinst={}
            for key,val in dicpost.items():
                if re.search('formc',key):
                    index=int(key.split("-")[1])
                    if index not in indexl:
                        indexl.append(index)
                        postspl[index]={}
                        postsplmod[index]={}
                        
                    postspl[index][key]=val
                    postsplmod[index][key.split("-")[2]]=val

            if len(indexl)==0:
                indexl=[1]
                postsplmod[1]={}    
                for key,val in dicpost.items():
                    if key not in ddi.__dict__.keys():
                        postsplmod[1][key]=val
                         

            print("longitud postspl[1]",len(postsplmod[1]), postsplmod)
            print("lista de indices", indexl) 
            for val in indexl:
                print("componente ", val, " ", postsplmod[val])
                postsplmod[val]['id_dynamics']=dynafk
                postsplmod[val]['id_molecule']=int(val+1) #este valor debe modificarse se le suma 1 porque si no no lo acepta el html (pide opciones entre uno y 7)
                dinst[val]=dyndb_Dynamics_Components(postsplmod[val])
                if dinst[val].is_valid():
                    dmodinst[val]=dinst[val].save(commit=False)
                    dmodinst[val]=dinst[val].save()
                    print("diccionario ", val, "  ", dmodinst[val].__dict__) 
                else:
                    print("Errores de la instancia del form nº",val," ",  dinst[val].errors.as_data())

          #  ttt=ddi.created_by_dbengine
          #  print("created by dbengine despues de grabar", ttt)

            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/DYNAMICSfilled/')
        else:
            iii2=dd.errors.as_data()
            print("Errores en dynamics: ",iii2)

    # if a GET (or any other method) we'll create a blank form
    else:
        dd=dyndb_Dynamics()
       # ddT= dyndb_Dynamics_tags()
       # ddTL=dyndb_Dynamics_Tags_List()

        return render(request,'dynadb/DYNAMICS.html', {'dd':dd})

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def SUBMITTEDview(request,submission_id): 
        return render(request,'dynadb/SUBMITTED.html',{'submission_id':submission_id})
        
@login_required
def get_Author_Information(request): 
        return render(request,'dynadb/dynadb_Author_Information.html'  )

@login_required
def db_inputformMAIN(request,submission_id): 
    if submission_id is None:
        dictsubid={}
        disable_3=True
        disable_4=True
        dictsubid['user_id']=str(request.user.pk)
        fdbsub=dyndb_Submission(dictsubid)
        fdbsubobj=fdbsub.save()
        submission_id = fdbsubobj.pk
    elif is_submission_owner(request.user,submission_id):
        qSMod=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        qSDyn=DyndbDynamics.objects.filter(submission_id=submission_id)
        if len(qSMod) == 1:
            disable_3=False
        else:
            disable_3=True   
        if len(qSMod) == 1:
            disable_4=False
        else:
            disable_4=True   
    else:
        return HttpResponseRedirect(reverse('dynadb:db_inputform'))
    return render(request,'dynadb/dynadb_inputformMAIN.html', {'submission_id':submission_id, 'disable_3':disable_3 , 'disable_4':disable_4 } )

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




#      def get_Prueba(request):
#          if request.method == 'POST':
#              fdb_Dynamics = Pdyndb_Dynamics(request.POST)
#              fdb_Dynamics_tags = Pdyndb_Dynamics_tags(request.POST)
#              fdb_Dynamics_Tags_List = Pdyndb_Dynamics_Tags_List(request.POST)
#              # check whether it's valid:
#              if fdb_Dynamics.is_valid() and fdb_Dynamics_tags.is_valid() and fdb_Dynamics_Tags_List.is_valid(): 
#      
#                  # process the data in form.cleaned_data as required
#                  # ...
#                  # redirect to a new URL:
#                  return HttpResponseRedirect('/dynadb/TF/')
#      
#          # if a GET (or any other method) we'll create a blank form
#          else:
#      
#              fdb_Dynamics=Pdyndb_Dynamics()
#              fdb_Dynamics_tags=Pdyndb_Dynamics_tags()
#              fdb_Dynamics_Tags_List=Pdyndb_Dynamics_Tags_List()
#      
#              return render(request,'dynadb/pruebaDYNAname.html', {'fdb_Dynamics':fdb_Dynamics, 'fdb_Dynamics_tags':fdb_Dynamics_tags, 'fdb_Dynamics_Tags_List':fdb_Dynamics_Tags_List} )
#      
#      
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
#        formMODEL = dyndb_Model(request.POST)
#        formFILES = dyndb_Files(request.POST)
#       forma = dyndb_ProteinForm(request.POST)
#        forma = dyndb_Model(request.POST)
#        formb = dyndb_Files(request.POST)
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
        #if formMODEL.is_valid() and formFILES.is_valid():
        #if fdbproteinform.is_valid() and formb.is_valid():
        if fdb_ProteinForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Protein_SequenceForm.is_valid() and fdb_Other_Protein_NamesForm.is_valid() and fdb_Cannonical_ProteinsForm.is_valid() and fdb_Protein_MutationsForm.is_valid() and fdb_CompoundForm.is_valid() and fdb_Other_Compound_Names.is_valid() and fdb_Molecule.is_valid() and fdb_Files.is_valid() and fdb_Files_Molecule.is_valid() and fdb_Complex_Exp.is_valid() and fdb_Complex_Protein.is_valid() and fdb_Complex_Molecule.is_valid() and fdb_Complex_Molecule_Molecule.is_valid() and fdb_Modeled_Residues.is_valid() and fdb_Files_Model.is_valid() and fdb_Dynamics.is_valid() and fdb_Dynamics_tags.is_valid() and fdb_Dynamics_Tags_List.is_valid() and fdb_Files_Dynamics.is_valid() and fdb_Related_Dynamics.is_valid() and fdb_Related_Dynamics_Dynamics.is_valid() and fdb_Model.is_valid():

#        if fdb_proteinform.is_valid():

#        print (fdb_proteinform.errors)
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/TF/')

    # if a GET (or any other method) we'll create a blank form
    else:
#        formMODEL=dyndb_Model()
#        formFILES=dyndb_Files()
#        form=dyndb_Model()
#       formFILES=dyndb_Files()
#        print (fdb_proteinform.errors)

#        forma = dyndb_ProteinForm()
#        forma = dyndb_Model(request.POST)
#        formb = dyndb_Files()
        #extra_context = {'formMODEL': formMODEL,'formFILES': formFILES}

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


#    return render(request, 'dynadb/name.html', {'formMODEL': formMODEL}, {'formFILES': formFILES} )
#        return render(request,'dynadb/DYNAname.html', {'forma':dyndb_Model, 'formb':dyndb_Files})
 #       return render(request,'dynadb/DYNAnameab.html', {'fdb_ProteinForm':dyndb_ProteinForm, 'formb':dyndb_Files})


        return render(request,'dynadb/DYNAnameab.html', {'fdb_ProteinForm':fdb_ProteinForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Protein_SequenceForm':fdb_Protein_SequenceForm, 'fdb_Other_Protein_NamesForm':fdb_Other_Protein_NamesForm, 'fdb_Cannonical_ProteinsForm':fdb_Cannonical_ProteinsForm, 'fdb_Protein_MutationsForm': fdb_Protein_MutationsForm, 'fdb_CompoundForm': fdb_CompoundForm, 'fdb_Other_Compound_Names':fdb_Other_Compound_Names, 'fdb_Molecule':fdb_Molecule, 'fdb_Files':fdb_Files, 'fdb_Files_Molecule':fdb_Files_Molecule, 'fdb_Complex_Exp':fdb_Complex_Exp, 'fdb_Complex_Protein':fdb_Complex_Protein, 'fdb_Complex_Molecule':fdb_Complex_Molecule, 'fdb_Complex_Molecule_Molecule':fdb_Complex_Molecule_Molecule, 'fdb_Modeled_Residues':fdb_Modeled_Residues, 'fdb_Files_Model':fdb_Files_Model, 'fdb_Dynamics':fdb_Dynamics, 'fdb_Dynamics_tags':fdb_Dynamics_tags, 'fdb_Dynamics_Tags_List':fdb_Dynamics_Tags_List, 'fdb_Files_Dynamics':fdb_Files_Dynamics, 'fdb_Related_Dynamics':fdb_Related_Dynamics, 'fdb_Related_Dynamics_Dynamics':fdb_Related_Dynamics_Dynamics, 'fdb_Model':fdb_Model})
#    return TemplateView(request,'dynadb/DYNAname.html', {'form':form})


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
    
#   extra_context = {
#       'alert_form': AlertForm(),
#       'notifier_form': NotifierForm()}
    
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
#        form = NameForm(request.POST)
        formset = FormupSet(request.POST)

        # check whether it's valid:
#       if form.is_valid():
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
#        form = NameForm(request.POST)
        formset = NameFormSet(request.POST)

        # check whether it's valid:
#       if form.is_valid():
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
            browse_protein_response={'Message':"ERROR: There is one or more entries of mutant proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkm),'id_protein':[]}
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






#def check_molecule_exist(uniprotkbac, isoform, is_mutated, sequence):
#  qDP=DyndbMolecule.objects.filter(uniprotkbac=uniprotkbac).filter(isoform=isoform)
#  if len(qDP.values())==0:
#      browse_protein_response={'Message':"There is not protein in the db matching the UniProtKB AC and the isoform number of the one is being processed",'id_protein':[]}
#      return browse_protein_response 

#  lpkm=[]
#  lpkw=[]


#def check_model_exist(uniprotkbac, isoform, is_mutated, sequence):
#  qDP=DyndbMolecule.objects.filter(uniprotkbac=uniprotkbac).filter(isoform=isoform)
#  if len(qDP.values())==0:
#      browse_protein_response={'Message':"There is not protein in the db matching the UniProtKB AC and the isoform number of the one is being processed",'id_protein':[]}
#      return browse_protein_response 

#  lpkm=[]
#  lpkw=[]
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
        data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,entry name,organism,length,')
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
#    if request.method == 'POST' and 'uniprotkbac' in request.POST.keys():
#    uniprotkbac = request.POST['uniprotkbac']
    print("uniprotkbac=",uniprotkbac) 
    uniprotkbac_noiso = uniprotkbac #
    isoform = 1
    print("HOLA PIPOL  ", uniprotkbac_noiso)
#if uniprotkbac is not None:
# if valid_uniprotkbac(uniprotkbac):
#   if uniprotkbac.find('-') < 0:
#     uniprotkbac_noiso = uniprotkbac
#     isoform = None
#   else:
#     uniprotkbac_noiso,isoform = uniprotkbac.split('-')
    data,errdata = retreive_data_uniprot(uniprotkbac_noiso,isoform=isoform,columns='id,entry name,organism,length,')
    print(data)
    print(errdata)
    if errdata == dict():
    #   if data == dict():
    #       response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain; charset=UTF-8')
    #       print(response)
    #   if data['Entry'] != uniprotkbac_noiso and isoform is not None:
    #       response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain; charset=UTF-8')
    #       print(response)
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
#
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
# 
# ####### OTHER NAMES SOLO SE RELLENA EN LA PROTEINA CANONICA!!!!! 

#       if len(dictprot[ii]['other_names'])> 0:
#           listON[ii]=dictprot[ii]['other_names'].split(";") # for each protein a listON[ii] list containing all the aliases is created.
#           listON[ii]=list(set(listON[ii])) #convert listON[ii] in a list of unique elements
#           dictOPN[ii]={} #dictionary containing dictionaries for instantiting dyndb_Other_Protein_NamesForm for each alias
#           fdbOPN[ii]={}
#           numON=0
#       
#           for on in listON[ii]:

#               numON=numON+1
#               dictOPN[ii][numON]={}
#               fdbOPN[ii][numON]={}
#               dictOPN[ii][numON]['other_names']=on
#               dictOPN[ii][numON]['id_protein']=formPF[ii].pk
#               fdbOPN[ii][numON]=dyndb_Other_Protein_NamesForm(dictOPN[ii][numON])
#               if fdbOPN[ii][numON].is_valid():
#                   fdbOPN[ii][numON].save()
#               else:
#                   iii1=fdbOPN[ii][numON].errors.as_data()
#                   print("fdbOPN[",ii,"] no es valido")
#                   print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n") ####HASTA AQUI#####
#       else:
#           print("NO OTHER NAMES have been found\n")

#  Fill dyndb_Protein_SequenceForm fields depending on whether the protein is mutated   
#  'msequence' does not appear in models but it does in the html so the information in 
#  this html field should be tranfered into the 'sequence' field in the form instance      

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

#           if len(nummutl[ii])==0:
#               nummutl[ii].append(0)
#               dictPM[ii][0]={}
#               dictPM[ii][0]['id_protein']=formPF[ii].pk 
#               print("NO info about mutations has been provided but an entry should be registered")

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
            #   iiiT=formPF[ii].pk
            #   initPM[ii]={'resid':nm+90,'resletter_from':'X','resletter_to':'Ñ', } # nm has been changed to avoid posible matching of entries in the database
            #   initPM[ii]['id_protein']=iiiT
            #   print("len(dictPM[ii][nm])= ",len(dictPM[ii][nm]))

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
#         qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=dictprot[ii]['uniprotkbac']).filter(isoform=isoform).exclude(is_mutated=True)#NO BUSCA CANONICAL SINO EL ISOMORF ESPECIFICADO!!
        qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=dictprot[ii]['uniprotkbac']).exclude(is_mutated=True).exclude(id=formPF[ii].pk) # BUSCA CANONICAL PROTEIN !!!
#         qCanProt[ii]=DyndbProtein.objects.filter(uniprotkbac=formPF[ii].uniprotkbac).exclude(id=formPF[ii].pk).exclude(is_mutated=True)
        
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
#           
            
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

        
    # if a GET (or any other method) we'll create a blank form
#  # else:

#       fdbPF = dyndb_ProteinForm()
#       fdbPS = dyndb_Protein_SequenceForm()
#       fdbPM = dyndb_Protein_MutationsForm()
#       fdbOPN= dyndb_Other_Protein_NamesForm()
#       return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS,'fdbPM':fdbPM,'fdbOPN':fdbOPN,'submission_id':submission_id})
#       return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS, 'fdbOPN':fdbOPN})

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
    file_root = normpath(settings.MEDIA_ROOT)
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
    filenamedict['dynamics']['subtypes']["other"]["ext"] = ["tar.gz"]
    filenamedict['dynamics']['subtypes']["log"]["ext"] = ["log"]

    filenamedict['summary']['subtypes']['summary']['ext']=['txt']
    
    #define subtype part(icles)
    filenamedict['dynamics']['subtypes']["pdb"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["topology"]["part"] = "dyn"
    filenamedict['dynamics']['subtypes']["trajectory"]["part"] = "trj"
    filenamedict['dynamics']['subtypes']["parameters"]["part"] = "prm"
    filenamedict['dynamics']['subtypes']["other"]["part"] = "oth"
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

 #  def handle_uploaded_file(f,p,name):
 #      print("file name = ", f.name , "path =", p)
 #      f.name=name
 #      print("NEW name = ", f.name , "path =", p)
 #      path=p+"/"+f.name
 #      with open(path, 'wb+') as destination:
 #          for chunk in f.chunks():
 #              destination.write(chunk)

    print("Submission_id:  ",submission_id)
    user="jmr"
    def molec_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        print("inside the function molec_file_table")
        print(dname)
        fdbF={}
        fdbFobj={}
        
       ######  
       # ft=DyndbFileTypes.objects.all()
       # dict_ext_id={}
       # for l in ft:
       #     dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
       # d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
       ##############
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
#    action="/".join(["/dynadb/MOLECULEfilled",submission_id,""])
    now=timezone.now()
    onames="Pepito; Juanito; Herculito" #to be modified... scripted
    initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
    initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
    initON={'other_names': onames,'id_compound':None} 
    dicpost=postd_single_molecule
    #dicfiles=request.FILES
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
    ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
    ft=DyndbFileTypes.objects.all()
    dict_ext_id={}
    for l in ft:
        dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
        print (l.__dict__['extension'].rstrip())
    d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
#    if request.method == 'POST':
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
   # print("!!!!!indexl== ",indexl)
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
            #dictmol[index]["-".join(key.split("-")[2:])]=val
        else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
            if len(indexl)==0:
                index=0
                indexl.append(0)
                dictmol[0]={}
                dictON[0]={}
                dictcomp[0]={}
                dictPMod[index]={}
            nkey=key
       # print("indexl==V ",indexl)
            #dictmol[0][key]=val
            #dictON[0][key]=val
            #dictfmol[0][key]=val
        #print("\nINICIO: key-val== ",key," ",val,"nkey ==", nkey,"\n")
        dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
        dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
        for k,v in dfieldtype.items():
            if nkey in v:
                dfielddict[k][index][nkey]=val
                break
        continue 
    indexl.sort()
    print(indexl)
    #print ("number of pairs in request.POST ===", nl, "\n ", dfielddict['0'],"\n",dfielddict['1'],"\n",dfielddict['2'])
    indexfl=[]

#######################################
  #  if len(dicfiles) == 0:
  #      response = HttpResponse('No file has been uploaded',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
  #      return response

#   for key,val in dicfiles.items():
#       if form.search(key):
#           indexf=int(key.split("-")[1])
#           nkey="-".join(key.split("-")[2:])  
#           if indexf not in indexfl:
#               indexfl.append(indexf)
#               dictfmol[indexf]={}
#           #dictmol[index]["-".join(key.split("-")[2:])]=val
#       else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
#           if len(indexfl)==0:
#               indexf=0
#               indexfl.append(0)
#               dictfmol[0]={}
#           nkey=key
#    dictfmol[index][nkey]=val
  #  print("INDEXFL", indexfl)
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
     #   indexfli=list(map(int,indexfl))
        indexli=list(map(int,indexl))
     #   indexfl=sorted(indexfli)
        indexl=sorted(indexli)
    #print(indexfl, indexl)
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

                                     #generation of the sinchi
        #dictcomp[ii]['sinchi']=    

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
                
              # if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
              #     dictPMod[ii]['not_in_model']=False
              # else:
              #     dictPMod[ii]['not_in_model']=True
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
                
#                if qSm.filter(molecule_id=F('molecule_id__id_compound__std_id_molecule'),int_id__gte=0)
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

#________________________________________________________________________________
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
        if Std_id_mol_update[ii]:
            DyndbCompound.objects.filter(id=CFpk).update(std_id_molecule=MFpk) 
            Std_id_mol_update[ii]=False
       
    #   if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
    #       dictPMod[ii]['not_in_model']=False
    #   else:
    #       dictPMod[ii]['not_in_model']=True
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
#_____________________________________________________________________________


   #      print("\nQuery Molecule antes de la evaluacion \n ",qMF.filter(id__gt=7).values())
   #    if len(qMF.values())==1:
   #        print("Your molecule is already present in our database")               
   #    elif len(qMF.values())>1:
   #        response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain; charset=UTF-8')
   #        return response
   #    elif len(qMF.values())==0:
   #        fdbF[ii]={}
   #        fdbFobj[ii]={}
   #        dname={'dnamesdf':{'path':path_namefsdf,'url':url_namefsdf},'dnamepng':{'path':path_namefpng,'url':url_namefpng}}
   #        print(dname)
   #        ooo= molec_file_table(dname)
   #        dnameref={'dnamesdf':{'path':path_namefrefsdf,'url':url_namefrefsdf},'dnamepng':{'path':path_namereffpng,'url':url_namefrefpng}}
   #        oooref=molec_file_table(dnameref)
   ##       direct='/protwis/sites/files/Molecule/mol'+str(submission_id)
    #       print("\nDirectorio a crear ", direct)
    #       if not os.path.exists(direct):
    #           os.makedirs(direct)
         


    #   path_namefsdf=("").join([submission_path_nofile, namesdf])
    #   path_namefpng=("").join([submission_path_nofile, namepng])
    #   path_namefrefsdf=("").join([submission_path_nofile, namerefsdf])
    #   path_namefrefpng=("").join([submission_path_nofile, namerefpng])
    #   url_namereffsdf=("").join([submission_url_nofile, namerefsdf])
    #   url_namereffpng=("").join([submission_url_nofile, namerefpng])
    #   url_namefsdf=("").join([submission_url_nofile, namesdf])
    #   url_namefpng=("").join([submission_url_nofile, namepng])






     ##     for key,val in dictfmol[ii].items():
     ##         fext="".join(val.name.split(".")[1:])
     ##         print("val ",val, " ;val split",fext," Tambien id", dict_ext_id[fext])
     ##         #print("val ",val, " ;val split",fext," Tambien id")
     ##         if fext in dict_ext_id.keys():
     ##             initFiles['id_file_types']=dict_ext_id[fext]
     ##             initFiles['url']=dict_ext_id[fext]
     ##             initFiles['filename']=val.name
     ##             initFiles['filepath']=direct
     ##             initFiles['description']="sdf/mol2 requested in the molecule form"
     ##  
     ##             fdbF[ii][key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
     ##             dicfmole[ii]={}
     ##             fdbFM[ii]={}
     ##             if fdbF[ii][key].is_valid():
     ##                 fdbFobj[ii][key]=fdbF[ii][key].save()
     ##                 newname=str(fdbFobj[ii][key].pk)+"_mol_"+str(submission_id)+"."+fext
     ##                 handle_uploaded_file(dictfmol[ii][key],direct,newname)
     ##                 completepath=direct+"/"+newname
     ##                 fdbFobj[ii][key].filename=newname   #rename filename in the database after saving the initial name
     ##                 fdbFobj[ii][key].filepath=completepath   #rename filename in the database after saving the initial name
     ##                 fdbFobj[ii][key].save() 
     ##                 dicfmole[ii]['type']=d_fmolec_t['Molecule'] #Molecule
     ##                 d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
     ##                 dicfmole[ii]['id_molecule']=MFpk
     ##                 dicfmole[ii]['id_files']=fdbFobj[ii][key].pk
     ##                 fdbFM[ii][key]=dyndb_Files_Molecule(dicfmole[ii])
     ##                 if fdbFM[ii][key].is_valid():
     ##                     fdbFM[ii][key].save()
     ##                 else:
     ##                     print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[ii][key].errors.as_text())
     ##             else:
     ##                 print("Errores en el form dyndb_Files\n ", fdbF[ii][key].errors.as_text())
     ##         else:
     ##             print("This extension is not valid for submission")
     #

    #return HttpResponseRedirect("/".join(["/dynadb/MOLECULEfilled",submission_id,""]), {'submission_id':submission_id })
                        
    




#        def SMALL_MOLECULEfunction(postd_single_molecule, number_of_molecule, submission_id):
#        
#            def handle_uploaded_file(f,p,name):
#                print("file name = ", f.name , "path =", p)
#                f.name=name
#                print("NEW name = ", f.name , "path =", p)
#                path=p+"/"+f.name
#                with open(path, 'wb+') as destination:
#                    for chunk in f.chunks():
#                        destination.write(chunk)
#                               
#            author="jmr"   #to be modified with author information. To initPF dict
#            action="/".join(["/dynadb/MOLECULEfilled",str(submission_id),""])
#            now=timezone.now()
#            onames="Pepito; Juanito; Herculito" #to be modified... scripted
#            initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
#            initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
#            initON={'other_names': onames,'id_compound':None} 
#            dicpost=postd_single_molecule
#        #    dicfiles=request.FILES
#            initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
#            ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
#            ft=DyndbFileTypes.objects.all()
#            dict_ext_id={}
#            for l in ft:
#                dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
#        
# dd           d_fmolec_t={'Image':'0','Molecule':'1'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
 #   d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
#        
#            dictmol={}
#            fieldsmol=["id_compound","description","net_charge","inchi","inchikey","inchicol","smiles"]
#            dictON={}
#            fieldsON=["other_names"]
#            dictcomp={}
#            fieldscomp=["name","iupac_name","pubchem_cid","chemblid","sinchi","sinchikey","std_id_molecule","id_ligand"]
#            dictfmol={} 
#            fieldsPMod={"is_present","type"}
#            dictPMod={}
#            form=re.compile('form-')
#            indexl=[]
#            print("!!!!!indexl== ",indexl)
#            nl=0 #counter of pairs in dicpost.items()
#            for key,val in dicpost.items():
#                nl=nl+1
#                if form.search(key):
#                    index=int(key.split("-")[1])
#                    if index not in indexl:
#                        indexl.append(index)
#                        dictmol[index]={}
#                        dictON[index]={}
#                        dictcomp[index]={}
#                        dictPMod[index]={}
#                    nkey="-".join(key.split("-")[2:])  
#                    #dictmol[index]["-".join(key.split("-")[2:])]=val
#                else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
#                    if len(indexl)==0:
#                        index=0
#                        indexl.append(0)
#                        dictmol[0]={}
#                        dictON[0]={}
#                        dictcomp[0]={}
#                        dictPMod[index]={}
#                    nkey=key
#               # print("indexl==V ",indexl)
#                    #dictmol[0][key]=val
#                    #dictON[0][key]=val
#                    #dictfmol[0][key]=val
#                print("\nINICIO: key-val== ",key," ",val,"nkey ==", nkey,"\n")
#                dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
#                dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
#                for k,v in dfieldtype.items():
#                    if nkey in v:
#                        dfielddict[k][index][nkey]=val
#                        print("Index ", index, "Indexl", indexl, " key== ",key, " Lista== ", v, " nkey", nkey)
#                        print ("\n key ", nl, "dfielddict == ", dfielddict)
#                        break
#               #     else:
#               #         print("OJO!!! key== ",key, " no en Lista== ", v)
#                print ("\n key ", nl, "dfielddict == ", dfielddict)
#                continue 
#        
#            print ("number of pairs in request.POST ===", nl, "\n ", dfielddict['0'],"\n",dfielddict['1'],"\n",dfielddict['2'])
#            indexfl=[]
#        #    if len(dicfiles) == 0:
#        #        response = HttpResponse('No file has been uploaded',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
#        #        return response
#        ########### FILES!!!!!!
#        #   for key,val in dicfiles.items():
#        #       if form.search(key):
#        #           indexf=int(key.split("-")[1])
#        #           nkey="-".join(key.split("-")[2:])  
#        #           if indexf not in indexfl:
#        #               indexfl.append(indexf)
#        #               dictfmol[indexf]={}
#        #           #dictmol[index]["-".join(key.split("-")[2:])]=val
#        #       else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
#        #           if len(indexfl)==0:
#        #               indexf=0
#        #               indexfl.append(0)
#        #               dictfmol[0]={}
#        #           nkey=key
#        #       dictfmol[indexf][nkey]=val
#        #   print("INDEXFL", indexfl)
#        
#            fdbMF={}
#            fdbMFobj={}
#            fdbCF={}
#            fdbCFobj={}
#            fdbON={}
#            fdbONobj={}
#            dON={}
#            on=0
#            print("ANTES SORT",indexfl, indexl)
#            if len(indexl) > 1:
#                indexfli=list(map(int,indexfl))
#                indexli=list(map(int,indexl))
#                indexfl=sorted(indexfli)
#                indexl=sorted(indexli)
#            print(indexfl, indexl)
#            dicfmole={}
#            fdbF={}
#            fdbFobj={}
#            fdbFM={}
#            fdbSM={}
#            fdbFMobj={}
#        
#            for ii in indexl:
#                fdbCF[ii]={}
#                fdbCFobj[ii]={}
#                fdbMF[ii]={}
#                fdbSM[ii]={}
#                fdbMFobj[ii]={}
#                fdbON[ii]={}
#                fdbONobj[ii]={}
#                dON[ii]={}
#                 
#                #### Check if the molecule is already in our Database. If so the standar molecule shoud be as well!!!!!
#        
#                qMF=DyndbMolecule.objects.filter(inchikey=dictmol[ii]['inchikey']).filter(inchi=dictmol[ii]['inchi'])
#                qCFStdFormExist=DyndbCompound.objects.filter(sinchikey=dictcomp[ii]['sinchikey']).filter(sinchi=dictcomp[ii]['sinchi']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound
#        
#                if len(qMF.values())==1: #there is a entry matching this molecule
#        
#                    if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
#                        dictPMod[ii]['not_in_model']=False
#                    else:
#                        dictPMod[ii]['not_in_model']=True
#        
#                    dictPMod[ii]['int_id']=ii
#                    dictPMod[ii]['submission_id']=submission_id
#                    MFpk=qMF.values_list('pk',flat=True)[0]
#                    dictPMod[ii]['molecule_id']=MFpk
#                    fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
#        
#                    if fdbSM[ii].is_valid(): # only the submission molecule table should be filled!!!!
#                        fdbSM[ii].save()
#                    else:    
#                        iii1=fdbSM[ii].errors.as_text()
#                        print("fdbSM",ii," no es valido")
#                        print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#        
#                    if ii==indexl[-1]:#if ii is the last element of the list indexl
#                        print("Molecule #", ii, "has been found in our database")
#                        break
#                    else:
#                        print("Molecule #", ii, "has been found in our database")
#                        continue
#        
#                elif len(qMF.values())>1:
#                    response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain; charset=UTF-8')
#                    return response
#                    
#         # check if the molecule is actually the standard form of the molecule. If this specific form of the molecule is not in the database (DyndbMolecule) but other molecules corresponding the same compound are, the one we are dealing with won`t be the standard as it is previously recorded when the first molecule corresponding the compound was registered. So, if there is no any entry in the DyndbCompound table matching the sinchikey of the molecule in the form, still will be possible that the current entry would be the standard form.
#                if len(qCFStdFormExist.values())==1: #The compound and the standard form of the current molecule is in the database (Only fill the current non standard molecule)
#                    print("Compound entry matching SInChIKey and SInChI has been found in GPCRmd database")
#                elif len(qCFStdFormExist.values())>1: #the compound is found more than once in the database
#                    response("Several Compound entries have been found in the DATABASE. Please, report this ERROR to the GPCRmd database administrator")
#                    return response
#                elif len(qCFStdFormExist.values())==0: #Neither the compound nor the standard form of the molecule are in the database
#               
#             #### No compound entry has been found in GPCRmd DB.Keep track of the Compound in the DyndbCompound table and the aliases in the DyndbOtherCompoundNames
#               
#                    #### DyndbCompound
#        
#                    for key,val in initCF.items():
#                        if key not in dictcomp[ii].keys():
#                            dictcomp[ii][key]=val
#                    fdbCF[ii]=dyndb_CompoundForm(dictcomp[ii]) 
#                    if fdbCF[ii].is_valid():
#                        fdbCFobj[ii]=fdbCF[ii].save()
#                        CFpk=fdbCFobj[ii].pk
#                    else:
#                        print("Errores en el form dyndb_CompoundForm\n ", fdbCF[ii].errors.as_text())
#               
#                    #### DyndbOtherCompoundNames 
#                    ONlist=dictON[ii]["other_names"].split(";")
#               
#                    for el in ONlist:
#                        on=on+1
#                        dON[ii][on]={}
#                        dON[ii][on]["other_names"]=el
#                        dON[ii][on]["id_compound"]=CFpk
#                        fdbON[ii][on]=dyndb_Other_Compound_Names(dON[ii][on]) 
#                        if fdbON[ii][on].is_valid():
#                            fdbON[ii][on].save()
#                        else:
#                            print("Errores en el form dyndb_Other_Compound_Names\n ", fdbON[ii][on].errors.as_text())
#        ### Get the standard Molecule by providing the SInChIKey to the PubChem or CHEMBL databases if the molecule is actually the standard form of the molecule.
#        
#        # DyndbCompound and DyndbOtherCompoundNames tables have been filled. Then entries for the std molecule should be registered in DyndbMolecule and DyndbSubmissionMolecule
#                
#                    INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
#         #### Check if inchi of the standard molecule matches the inchi in the current entry (HTML form)         
#                    
#                    if INFOstdMOL['inchi']==dictmol[ii]['inchi']: #Both molecules are the standard molecule so one entry is saved
#                        print("The molecule ",ii, "is actually the standard molecule")
#                    else:
#                        print("The molecule ",ii, "is not the standard molecule. The standard one will be saved right now!!!!")
#                        auxdictmol={}
#                        for key,val in INFOstdMOL.items():# HAY QUE INTRODUCIR LOS DATOS DEL SCRIPT PARA PODER CREAR UN DICCIONARIO PARA LA INSTANCIA!!!
#                            if key in dfieldtype[0]:
#                                auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
#          
#                        for key,val in initMF.items():
#                            if key not in auxdictmol.keys():
#                                auxdictmol[key]=val  ##### completion of the dictionary
#                        auxdictmol['id_compound']=CFpk
#                        fdbMFaux=dyndb_Molecule(auxdictmol)
#                        if fdbMFaux.is_valid():
#                            fdbMFobj=fdbMFaux.save()
#                            MFauxpk=fdbMFobj.pk
#                        else:
#                            print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_text())
#          
#                    #### Entry in DyndbSubmissionMolecule corresponding to the standard molecule 
#                        auxdictPMod={}
#                        auxdictPMod['not_in_model']=True
#                        auxdictPMod['int_id']=None
#                        auxdictPMod['submission_id']=submission_id
#                        auxdictPMod['molecule_id']=MFauxpk
#                        fdbSMaux=dyndb_Submission_Molecule(auxdictPMod)
#          
#                        if fdbSMaux.is_valid(): # only the submission molecule table should be filled!!!!
#                            fdbSMaux.save()
#                        else:    
#                            iii1=fdbSMaux[ii].errors.as_text()
#                            print("fdbSMaux",ii," no es valido")
#                            print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#        
#               #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule table
#        
#                        for key,val in initMF.items():
#                            if key not in dictmol[ii].keys():
#                                dictmol[ii][key]=val
#                        dictmol[ii]['id_compound']=CFpk
#                        fdbMF[ii]=dyndb_Molecule(dictmol[ii])
#                        if fdbMF[ii].is_valid():
#                            fdbMFobj[ii]=fdbMF[ii].save()
#                            MFpk=fdbMFobj[ii].pk
#                        else:
#                            print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_text())
#                    
#                        if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
#                            dictPMod[ii]['not_in_model']=False
#                        else:
#                            dictPMod[ii]['not_in_model']=True
#                        dictPMod[ii]['int_id']=ii
#                        dictPMod[ii]['submission_id']=submission_id
#                        dictPMod[ii]['molecule_id']=MFpk
#                        fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
#                        if fdbSM[ii].is_valid():
#                            fdbSM[ii].save()
#                        else:    
#                            iii1=fdbSM[ii].errors.as_text()
#                            print("fdbSM",ii," no es valido")
#                            print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")
#        
#                    if INFOstdMOL['inchi']==dictmol[ii]['inchi']: #Both molecules are the standard molecule so one entry is saved 
#                        fdbCFobj[ii]['std_id_molecule']=MFpk
#                    else:
#                        fdbCFobj[ii]['std_id_molecule']=MFauxpk
#                    fdbCFobj[ii].save()
#        
#                if len(qMF.values())==1:
#                    print("Your molecule is already present in our database")               
#                elif len(qMF.values())>1:
#                    response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain; charset=UTF-8')
#                    return response
#                elif len(qMF.values())==0:
#                    pass
########################   FILES!!!!!!!!!!!!!!!!!!
#               direct='/protwis/sites/files/Molecule/mol'+str(submission_id)
#               print("\nDirectorio a crear ", direct)
#               if not os.path.exists(direct):
#                   os.makedirs(direct)
#            
#               fdbF[ii]={}
#               fdbFobj[ii]={}
#               for key,val in dictfmol[ii].items():
#                   fext="".join(val.name.split(".")[1:])
#                   print("val ",val, " ;val split",fext," Tambien id", dict_ext_id[fext])
#                   #print("val ",val, " ;val split",fext," Tambien id")
#                   if fext in dict_ext_id.keys():
#                       initFiles['id_file_types']=dict_ext_id[fext]
#                       initFiles['filename']=val.name
#                       initFiles['filepath']=direct
#                       initFiles['description']="sdf/mol2 requested in the molecule form"
#            
#                       fdbF[ii][key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
#                       dicfmole[ii]={}
#                       fdbFM[ii]={}
#                       if fdbF[ii][key].is_valid():
#                           fdbFobj[ii][key]=fdbF[ii][key].save()
#                           newname=str(fdbFobj[ii][key].pk)+"_mol_"+str(submission_id)+"."+fext
#                           handle_uploaded_file(dictfmol[ii][key],direct,newname)
#                           completepath=direct+"/"+newname
#                           fdbFobj[ii][key].filename=newname   #rename filename in the database after saving the initial name
#                           fdbFobj[ii][key].filepath=completepath   #rename filename in the database after saving the initial name
#                           fdbFobj[ii][key].save() 
#                           dicfmole[ii]['type']=d_fmolec_t['Molecule'] #Molecule
#                           dicfmole[ii]['id_molecule']=MFpk
#                           dicfmole[ii]['id_files']=fdbFobj[ii][key].pk
#                           fdbFM[ii][key]=dyndb_Files_Molecule(dicfmole[ii])
#                           if fdbFM[ii][key].is_valid():
#                               fdbFM[ii][key].save()
#                           else:
#                               print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[ii][key].errors.as_text())
#                       else:
#                           print("Errores en el form dyndb_Files\n ", fdbF[ii][key].errors.as_text())
#                   else:
#                       print("This extension is not valid for submission")

#        return HttpResponseRedirect("/".join(["/dynadb/MOLECULEfilled",submission_id,""]), {'submission_id':submission_id })
                        
                       

        # check whether it's valid:
#   else:

#       fdbMF = dyndb_Molecule()
#       fdbCF=dyndb_CompoundForm()
#       fdbON=dyndb_Other_Compound_Names()
#       fdbF = dyndb_Files()
#       fdbFM = dyndb_Files_Molecule()
#       fdbMM = dyndb_Complex_Molecule_Molecule()

#       return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbCF':fdbCF,'fdbON':fdbON, 'fdbF':fdbF, 'fdbFM':fdbFM, 'fdbMM':fdbMM, 'submission_id' : submission_id})

def generate_molecule_properties2(submission_id,molid):
    pngsize = 300
    RecMet = False
    formre = re.compile('^form-(\d+)-')
    data={}
    data['sinchi']={}
    data['inchi']={}
               
#  if method == 'POST':
    submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
    submission_url = get_file_paths("molecule",url=True,submission_id=submission_id)
    
    sdfnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
    file=Path(("").join([submission_path,sdfnameref]))
    
    if file.is_file():
        uploadfile=open(os.path.join(submission_path,sdfnameref),'rb')
    else:
        uploadfile=open(os.path.join(submission_path,get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")),'rb')

#    mol = open_molecule_file(SDFhandler) # EL objeto mol es necesario para trabajar en RD KIT use this function with ARGUMENT! -> filetype='sdf' #MODIFIED BY ALEJANDRO, DO NOT KEEP THIS VERSION ON MERGE
     
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
    
     #   return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
    print("AAAAAAAAAAAAAAAAAA\n")

    data['smiles'] = generate_smiles(mol,logfile=sys.stderr)
    print(data['smiles'], "= generate_smiles(mol,logfile=sys.stdout)")
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
        #print(data['msg'],file=logfile)
        #logfile.close()
       # data['msg'] = msg+' Please, see log file.'
     #   return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')

    uploadfile.close()
    
    return data





#           logfile = open(os.path.join(submission_path,logname),'w')
#           mol = open_molecule_file(uploadfile,logfile)

#   data = dict()
#   data['download_url_log'] = None
#   if 'molpostkey' in POST.keys():
#       if 'recmet' in POST.keys():
#           RecMet = True
#       if 'pngsize' in POST.keys():
#           pngsize = int(POST["pngsize"])
#       molpostkey = POST["molpostkey"]
#       
#       if molpostkey in FILES.keys():
#           m = formre.search(molpostkey)
#           if m:
#               molid = m.group(1)
#           else:
#               molid = 0
#           uploadfile =  FILES[molpostkey]  # path_namef
#           os.makedirs(submission_path,exist_ok=True)
#           logname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="log",forceext=False,subtype="log")
#           sdfname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="sdf",forceext=False,subtype="molecule")
#           pngname = get_file_name_submission("molecule",submission_id,molid,ref=False,ext="png",forceext=False,subtype="image",imgsize=pngsize)
#           submission_path = get_file_paths("molecule",url=False,submission_id=submission_id)
#           sdfnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="sdf",forceext=False,subtype="molecule")
#           pngnameref = get_file_name_submission("molecule",submission_id,molid,ref=True,ext="png",forceext=False,subtype="image",imgsize=pngsize)
#           try:
#               os.remove(os.path.join(submission_path,sdfname))
#           except:
#               pass
#           try:
#               os.remove(os.path.join(submission_path,pngname))
#           except:
#               pass
#           try:
#               os.remove(os.path.join(submission_path,pngnameref))
#           except:
#               pass
#           try:
#               os.remove(os.path.join(submission_path,sdfnameref))
#           except:
#               pass
#           logfile = open(os.path.join(submission_path,logname),'w')
#           data['download_url_log'] = join_path(submission_url,logname,url=True)
#           try:
#           
#           except:
#               print ("mol object has not been generated") 
#               pass
#           
#           data['sinchi'] = dict()
#           try:
#               print('Generating Standard InChI...',file=logfile)
#               sinchi,code,msg = generate_inchi(mol,FixedH=False,RecMet=False)
#               data['sinchi']['sinchi'] = sinchi
#               data['sinchi']['code'] = code
#               print(msg,file=logfile)
#               data['inchi'] = dict()
#               print('Generating Fixed Hydrogens InChI...',file=logfile)
#               inchi,code,msg = generate_inchi(mol,FixedH=True,RecMet=RecMet)
#               data['inchi']['inchi'] = inchi
#               data['inchi']['code'] = code
#               print(msg,file=logfile)
#               data['sinchikey'] = generate_inchikey(data['sinchi']['sinchi'])
#               data['inchikey'] = generate_inchikey(data['inchi']['inchi'])

#           except:
#               data['msg'] ='Error while computing InChI.'
#               print(data['msg'],file=logfile)
#               logfile.close()
#               data['msg'] = msg+' Please, see log file.'
#               return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#           try:
#               print('Generating Smiles...',file=logfile)
#               data['smiles'] = generate_smiles(mol,logfile)
#               data['charge'] = get_net_charge(mol)
#           except:
#               msg = 'Error while computing Smiles.'
#               print(msg,file=logfile)
#               logfile.close()
#               data['msg'] = msg+' Please, see log file.'
#               return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#               
#           data['charge'] = get_net_charge(mol)
#           
#           try:
#               mol.SetProp("_Name",sdfname)
#               write_sdf(mol,os.path.join(submission_path,sdfname))
#               data['download_url_sdf'] = join_path(submission_url,sdfname,url=True)

#           except:
#               try:
#                   os.remove(os.path.join(submission_path,sdfname))
#               except:
#                   pass
#               msg = 'Error while storing SDF file.'
#               print(msg,file=logfile)
#               logfile.close()
#               data['msg'] = msg+' Please, see log file.'
#               return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#           print('Drawing molecule...',file=logfile)
#           try:
#               generate_png(mol,os.path.join(submission_path,pngname),logfile,size=pngsize)
#           except:
#               try:
#                   os.remove(os.path.join(submission_path,sdfname))
#               except:
#                   pass
#               try:
#                   os.remove(os.path.join(submission_path,pngname))
#               except:
#                   pass
#               raise
#               msg = 'Error while drawing molecule.'
#               print(msg,file=logfile)
#               logfile.close()
#               data['msg'] = msg+' Please, see log file.'
#               return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#           data['download_url_png'] = join_path(submission_url,pngname,url=True)
#           print('Finished with molecule.',file=logfile)
#           logfile.close()
#           del mol
#           
#           return JsonResponse(data,safe=False)
#       else:
#           data['msg'] = 'Unknown molecule file reference.'
#           return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#   elif upload_handlers[0].exception is not None:
#       try:
#           raise upload_handlers[0].exception
#       except(InvalidMoleculeFileExtension,MultipleMoleculesinSDF) as e :
#           data['msg'] = e.args[0]
#           return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
#           
#           
#       
#   else:
#       data['msg'] = 'No file was selected or cannot find molecule file reference.'
#       return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def SMALL_MOLECULEview(request, submission_id):

  # def handle_uploaded_file(f,p,name):
  #     print("file name = ", f.name , "path =", p)
  #     f.name=name
  #     print("NEW name = ", f.name , "path =", p)
  #     path=p+"/"+f.name
  #     with open(path, 'wb+') as destination:
  #         for chunk in f.chunks():
  #             destination.write(chunk)
    user="jmr"   #to be modified with author information. To initPF dict

    print("Submission_id:  ",submission_id)
    def molec_file_table (dname, MFpk): #d_fmolec_t, dictext_id 
        print("inside the function molec_file_table")
        print(dname)
        fdbF={}
        fdbFobj={}
        
       ######  
       # ft=DyndbFileTypes.objects.all()
       # dict_ext_id={}
       # for l in ft:
       #     dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']
       # d_fmolec_t={'Molecule':'0','Image 100px':'1','Image 300px':'2'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
       ##############
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
#    action="/".join(["/dynadb/MOLECULEfilled",submission_id,""])
    now=timezone.now()
    onames="Pepito; Juanito; Herculito" #to be modified... scripted
    initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
    initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':def_user_dbengine, 'last_update_by_dbengine':def_user_dbengine,'created_by':def_user, 'last_update_by':def_user }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
    initON={'other_names': onames,'id_compound':None} 
    dicpost=request.POST    #postd_single_molecule
    #dicfiles=request.FILES
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
                   # SProtreuse=dyndb_Submission_Protein(entry)

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
                #return HttpResponse("FIN PROTEIN",status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
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
    #  # print("!!!!!indexl== ",indexl)
        nl=0 #counter of pairs in dicpost.items()
        dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
        dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
        
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
                #dictmol[index]["-".join(key.split("-")[2:])]=val
            else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
                if len(indexl)==0:
                    index=0
                    indexl.append(0)
                    dictmol[0]={}
                    dictON[0]={}
                    dictcomp[0]={}
                    dictPMod[index]={}
                nkey=key
           # print("indexl==V ",indexl)
                #dictmol[0][key]=val
                #dictON[0][key]=val
                #dictfmol[0][key]=val
            #print("key",key," ",val)
            #print("\nINICIO: key-val== ",key," ",val,"nkey ==", nkey,"\n")
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
        #print ("number of pairs in request.POST ===", nl, "\n ", dfielddict['0'],"\n",dfielddict['1'],"\n",dfielddict['2'])
        indexfl=[]
 
###########################################
   #  #  if len(dicfiles) == 0:
   #  #      response = HttpResponse('No file has been uploaded',status=422,reason='Unprocessable Entity',content_type='text/plain; charset=UTF-8')
   #  #      return response
 
##      for key,val in dicfiles.items():
##          if form.search(key):
##              indexf=int(key.split("-")[1])
##              nkey="-".join(key.split("-")[2:])  
##              if indexf not in indexfl:
##                  indexfl.append(indexf)
##                  dictfmol[indexf]={}
##              #dictmol[index]["-".join(key.split("-")[2:])]=val
##          else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
##              if len(indexfl)==0:
##                  indexf=0
##                  indexfl.append(0)
##                  dictfmol[0]={}
##              nkey=key
##       dictfmol[index][nkey]=val
   #  #  print("INDEXFL", indexfl)
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
         #   indexfli=list(map(int,indexfl))
            indexli=list(map(int,indexl))
         #   indexfl=sorted(indexfli)
            indexl=sorted(indexli)
        #print(indexfl, indexl)
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
#        qSm=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).exclude(int_id=None)
        qSm=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id)
        qSubreuse=DyndbSubmissionMolecule.objects.filter(int_id=None,molecule_id=None) #entry list to be reused
        qSm_moll=qSm.exclude(molecule_id=None,not_in_model=None,type=None)
        lqSubreuse_used=[] 
        if qSm.exists():
            prev_Mol_in_Sub_exists=True
            #if len(indexl) >1 and len(qSm)>len(indexl):
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
        
         
   #    if qSub.exists(): ### MIRAR HTML
   #        print("QSUB exists")
   #        qSub_protl=list(qSub.values_list('submission_id','protein_id','int_id','protein_id__dyndbproteinsequence__sequence','protein_id__is_mutated'))
   #        qSub_p_sid_int_id=[]
   #        for ll in qSub_protl:
   #            qSub_p_sid_int_id.append((ll[0],ll[2]))

        
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
                   # qSreuse=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id,int_id=None,molecule_id=None)
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
                          # row_to_update=qSreuse[0]
                          # row_to_update.int_id=ii
                          # row_to_update.submission_id=submission_id
                          # row_to_update.molecule_id=MFpk
                          # row_to_update.type=dictPMod[ii]['type']
                            print("MMMMAAAMMMM")
                            break
    
            else:
                dictmol[ii]['molecule_creation_submission_id']=submission_id
                if qSm.filter(int_id=ii).exists():
                    print("There is a molecule in the database with this submission_id and int_id not matching the one in the form which in addition is not contained in the db!!! TTPPPPP")
                    deleteModelbyUpdateMolecule(qSm.filter(int_id=ii).values_list('molecule_id',flat=True)[0],ii,submission_id)
 
                                         #generation of the sinchi
            print(dictcomp[ii])
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
                    
                  # if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
                  #     dictPMod[ii]['not_in_model']=False
                  # else:
                  #     dictPMod[ii]['not_in_model']=True
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
                        
##                       if qSm.filter(molecule_id=F('molecule_id__id_compound__std_id_molecule'),int_id__gte=0)
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
##___________________________________________________________________________________
    #  #       The code enclosed in this section is common for cases in which a previous compound entry existed and cases where the Compound entry has been registered in this submission!!!  
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
           
        #   if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
        #       dictPMod[ii]['not_in_model']=False
        #   else:
        #       dictPMod[ii]['not_in_model']=True
            if int(dictPMod[ii]['type'])>5:
                dictPMod[ii]['not_in_model']=True
            else:
                dictPMod[ii]['not_in_model']=False     
            dictPMod[ii]['int_id']=ii
            dictPMod[ii]['submission_id']=submission_id
            dictPMod[ii]['molecule_id']=MFpk
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
  
  
  
           # return HttpResponseRedirect("/".join(["/dynadb/MOLECULEfilled",submission_id,""]), {'submission_id':submission_id })
                                   
                                  
           
                   # check whether it's valid:
    else:
        #qSub=DyndbSubmissionMolecule.objects.exclude(int_id=None).order_by('int_id').filter(submission_id=submission_id,molecule_id__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'))
        #qSubstd=DyndbSubmissionMolecule.objects.exclude(int_id=None).order_by('int_id').filter(submission_id=submission_id,molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__id_file_types=19).annotate(url=F('molecule_id__dyndbfilesmolecule__id_files__url'),urlstd=F('molecule_id__id_compound__std_id_molecule__dyndbfilesmolecule__id_files__url'))
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
                print(l.url)
                print(url)
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
            print("STD molecule list of files", urlstd)
            print(alias)
            print(qCOMP)
            print(qMOL)
            listExtraMolColapse=list(range(len(qCOMP),40))
            print(listExtraMolColapse)
            fdbSub = dyndb_Submission_Molecule()
  
###  #          qMOL=DyndbMolecule.objects.filter(id__in=qSub.values_list('molecule_id',flat=True)).order_by('DyndbSubmissionMolecule.int_id')
###  #      for tt in qMOL.values_list('id',flat=True):
###  #          if  not qSub.filter(molecule_id=tt).values_list('not_in_model',flat=True)[0]:
###  #              imp.append(True)
###  #          else:
###  #              imp.append(False)	              
###  #          qALIAS=DyndbOtherCompoundNames.objects.filter(id_compound=qMOL.filter(id=tt).values_list('id_compound',flat=True)[0])
###  #          llo=("; ").join(qALIAS.values_list('other_names',flat=True))
###  #          alias.append(llo) 
###  #          qCOMP.append(qCOMPtt) 
###  #          print("AQUI", tt,alias)
  
###  #       return render(request,'dynadb/SMALL_MOLECULEreuse.html', {'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'model_id':model_id})
            return render(request,'dynadb/SMALL_MOLECULE.html', {'url':url,'urlstd':urlstd,'fdbSub':fdbSub,'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'list':listExtraMolColapse, 'saved':True})
            #return render(request,'dynadb/SMALL_MOLECULE.html', {'url':url,'fdbSub':fdbSub,'qMOL':qMOL,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'list':listExtraMolColapse, 'saved':True})
        else:    
#        qSub=DyndbSubmissionMolecule.objects.filter(submission_id=DyndbSubmissionModel.objects.filter(model_id=model_id).values_list('submission_id',flat=True)[0]).order_by('int_id')
#        print(qSub)  ######POR AQUI!!!! ORDENAR POR INT_ID LA QUERY qMOL!!! 
            labtypel=[]
            int_id=[]
            int_id0=[]
            alias=[]
            qCOMP=[]
            qMOL=[]
            imp=[]
            Type=[]
#            for l in qSub:
#               labtype=l.COMPOUND_TYPE[l.type][1]
#               labtypel.append(labtype) 
#               if  not l.not_in_model:
#                   imp.append(True)
#               else:
#                   imp.append(False)
#        
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
         
         
    return render(request,'dynadb/SMALL_MOLECULE.html', {'qMOL':qMOL,'fdbSub':fdbSub,'labtypel':labtypel,'Type':Type,'imp':imp,'qCOMP':qCOMP,'int_id':int_id,'int_id0':int_id0,'alias':alias,'submission_id':submission_id,'model_id':False})
       
#       fdbMF = dyndb_Molecule()
#       fdbSub = dyndb_Submission_Molecule()
#       fdbCF=dyndb_CompoundForm()
#       fdbON=dyndb_Other_Compound_Names()
#       fdbF = dyndb_Files()
#       fdbFM = dyndb_Files_Molecule()
#       fdbMM = dyndb_Complex_Molecule_Molecule()
#      
#       return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbSub':fdbSub,'fdbCF':fdbCF,'fdbON':fdbON, 'fdbF':fdbF, 'fdbFM':fdbFM, 'fdbMM':fdbMM, 'submission_id' : submission_id})

def save_uploadedfile(filepath,uploadedfile):
    with open(filepath,'wb') as f:
        if uploadedfile.multiple_chunks:
            for chunk in uploadedfile.chunks():
                f.write(chunk)
        else:
            f.write(uploadedfile.read())
        f.close()
def type_inverse_search(type_matrix,searchkey=None,case_sensitive=False,first_match=True):
    inverse_type = dict()
    if  searchkey is None:
        dore = False
    else:
        dore = True
        if case_sensitive:
            flags = 0
        else:
            flags=re.IGNORECASE
            
        researchkey = re.compile(re.escape(searchkey),flags=flags)
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
        raise ValueError("Object in first argument doesn't have text '"+searchkey+"'.")        
    else:
        return inverse_type

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col._asdict()['name'] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def submission_summaryiew(request,submission_id):
#protein section
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None).order_by('int_id')
    print(qSub)
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
#        MUT=qPROT.values('id','is_mutated')
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
#            MUT.values('is_mutated').filter(id=tt)[0]['is_mutated']:
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
        print(l.url)
        print(urls)
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
    print(alias)
    print(qCOMP)
    print(qMOL)
    fdbSubs = dyndb_Submission_Molecule()

#model section
     
    qModel=DyndbModel.objects.filter(dyndbsubmissionmodel__submission_id=submission_id)
    print("qModel",qModel)
    p=qModel
    print("p ", p)
    Typeval=p.values()[0]['type']
    TypeM=p.model.MODEL_TYPE[Typeval][1]
    STypeval=p.values()[0]['source_type']
    SType=p.model.SOURCE_TYPE[STypeval][1]
    model_id=qModel.values_list('id',flat=True)[0]

#dynamics section

    qDS=DyndbDynamics.objects.filter(submission_id=submission_id)
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
        #mdata[i]['numberofmol'] = ''
        data[i]['readonly'] = True
        data[i]['int_id'] = 1 + data[i]['int_id']
        data[i]['type_int'] = model_2_dynamics_molecule_type.translate(data[i]['type'],as_text=False)
        if data[i]['type_int'] is None:
            data[i]['type_int'] = other_int
        data[i]['type'] = model_2_dynamics_molecule_type.translate(data[i]['type'],as_text=True)
        i += 1
    

    print(qDS.values()[0])
    compl=[]
    dctypel=[]
    for tt in qDS.values_list('id',flat=True):
        qDC=DyndbDynamicsComponents.objects.filter(id_dynamics=tt).order_by('id')
        compl.append(qDC)
        d=0
        l_ord_mol=[]
        lcompname=[]
        for l in qDC:
            dctype=DyndbDynamicsComponents.MOLECULE_TYPE[l.type][1]
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
            if qSub.filter(molecule_id=mol.id).values("not_in_model"): 
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


    return render(request,'dynadb/SUBMISSION_SUMMARY.html', { 'qPROT':qPROT,'sci_namel':sci_na_codel,'int_id':int_id,'int_id0':int_id0,'alias':alias,'mseq':mseq,'wseq':wseq,'MUTations':MUTations,'submission_id' : submission_id,'urls':urls,'fdbSubs':fdbSubs,'qMOL':qMOL,'labtypels':labtypels,'Types':Types,'imps':imps,'qCOMP':qCOMP,'int_ids':int_ids,'int_ids0':int_ids0,'p':p,'SType':SType,'TypeM':TypeM, 'ddown':ddown,'qDC':qDC, 'dctypel':dctypel, "lcompname":lcompname, 'lcompname':l_ord_mol, 'compl':compl, 'qDS':qDS, 'data':data, 'model_id':model_id, 'SUMMARY':True, 'urlsummary':summaryurl })

@login_required
@user_passes_test_args(is_submission_owner,redirect_field_name=None)
def protein_summaryiew(request,submission_id):
#protein section
    qSub=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).order_by('int_id')
    print(qSub)
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
#        MUT=qPROT.values('id','is_mutated')
        qSEQ=DyndbProteinSequence.objects.filter(id_protein=l.protein_id).values_list('sequence',flat=True)[0]
        if l.protein_id.is_mutated: 
#            MUT.values('is_mutated').filter(id=tt)[0]['is_mutated']:
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
        print(l.url)
        print(urls)
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
    print(qCOMP)
    print(qMOL)
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

   # return render(request,'dynadb/SUBMISSION_SUMMARY.html', { 'submission_id' : submission_id,'urls':urls,'fdbSubs':fdbSubs,'qMOL':qMOL,'labtypels':labtypels,'Types':Types,'imps':imps,'qCOMP':qCOMP,'int_ids':int_ids,'int_ids0':int_ids0})



    return render(request,'dynadb/SUBMISSION_SUMMARY.html', )

@login_required
def serve_submission_files(request,obj_folder,submission_folder,path):
    ''' Function to serve private files using django-sendfile module.
    Full url is "[VIEW_URL]/obj_folder/submission_folder/path" '''
    
    if is_allowed_directory(request.user,obj_folder=obj_folder,submission_folder=submission_folder,path=path):
        
        filepath = file_url_to_file_path(request.path)
        return sendfile(request,filepath)

    raise PermissionDenied

def is_allowed_directory(user,url_path=None,obj_folder=None,submission_folder=None,path=None,prefix=None,allow_submission_dir=False):
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
                #check user permissions
                if is_submission_owner(user,submission_id=submission_id):
                    allowed_directory = get_file_paths(object_type,submission_id=submission_id,url=False)
                    filepath = file_url_to_file_path(url_path)
                    
                    if allow_submission_dir:
                        allowed_directory = os.path.realpath(allowed_directory)
                        test_dir = os.path.realpath(filepath)
                        if os.path.isdir(test_dir) and allowed_directory == test_dir:
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
@login_required
@textonly_404_handler
@textonly_500_handler
def mdsrv_redirect_login(request,path,path_dir):
    if path_dir is None:
        allow_dir = False
        url_path = path
    else:
        url_path = path_dir
        allow_dir = True
    if not is_allowed_directory(request.user,url_path=request.path,prefix='_DB',allow_submission_dir=allow_dir):
        return HttpResponseForbidden("Forbidden (403).",content_type='text/plain; charset=UTF-8')
    return mdsrv_redirect(request,url_path)

def reset_permissions(request):
    try:
        from django.core.cache import cache
        cache.clear()
        import os
        os.system("chmod -R 777 /protwis/sites/files/")
        #os.system("rm -fr /tmp/django_cache")
    except Exception as e:
        print(str(e))
        ex_type, ex, tb = sys.exc_info()
        traceback.print_tb(tb)
    return HttpResponse('Done!',content_type='text/plain; charset=UTF-8')
