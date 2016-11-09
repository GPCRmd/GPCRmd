
# -*- coding: utf-8 -*-
from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.template import loader
from django.db.models import Count
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.core.files.storage import FileSystemStorage
import re, os, pickle
import time
import json
import mimetypes
import requests
import math
from django.db.models.functions import Concat
from django.db.models import CharField,TextField, Case, When, Value as V
from .customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from .sequence_tools import get_mutations, check_fasta
from .csv_in_memory_writer import CsvDictWriterNoFile, CsvDictWriterRowQuerySetIterator
#from .models import Question,Formup
#from .forms import PostForm
from .models import DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, StructureType, WebResource, StructureModelLoopTemplates, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbCannonicalProteins, Protein, DyndbSubmissionMolecule, DyndbSubmissionProtein, DyndbComplexCompound, DyndbComplexProtein, DyndbComplexMoleculeMolecule, DyndbComplexMolecule
from .models import DyndbSubmissionProtein, DyndbFilesDynamics, DyndbReferencesModel, DyndbModelComponents,DyndbProteinMutations,DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, StructureType, WebResource, StructureModelLoopTemplates, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbModeledResidues 
#from django.views.generic.edit import FormView
from .forms import FileUploadForm, NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, Formup, dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model
from .forms import NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, Formup, dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model, dyndb_Protein_Cannonical_Protein, dyndb_Complex_Compound 
#from .forms import NameForm, TableForm
from .pipe4_6_0 import *
from time import sleep
from random import randint
# Create your views here.

submission_id=3

if 1==1:
    if 1==1:

        qSMol=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).filter(not_in_model=False).exclude(int_id=None)
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

        
        if len(lmol_in_model)==0: #If there is not any molecule in the model the query is based in the proteins (QUERYp)
            where.append(("AND tcm.id_complex_exp IS NULL;"))
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
                    for line in row:# row may contain one or several hits!! let's obtain their corresponding id_complex_exp(line[0])
                        ROWLp.append(line[0]) 
                    # Let's get the id_complex_exp of complexes involving just the same proteins in our submission and NO ONE ELSE!!!!! There should be only one result
                    p=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLp).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model))  
                    if(len(p)>1):# Complexes involving exactly the same proteins in our submission is higher than one
                        response = HttpResponse('Several complex_exp entries for the same set of proteins and no molecules exist in the DB... Please Report that error to the GPCRdb administrator',status=422,reason='Unprocessable Entity',content_type='text/plain')
                        #return response
                    elif(len(p)==1):
                        ce=p[0]['id_complex_exp']
                        rowl=[ce] #Complex exp


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

   ##### MAKING THE COMPOUND-WISE QUERY 
            ROWLCompp=[]
            ROWLCompe=[]
            #the QUERYComp is needed in order to check if the Complex_Exp exists regardless the specific Complex_molecule does
            with connection.cursor() as cursor:
                cursor.execute(QUERYComp)
                rowComp=cursor.fetchall()
                if len(list(rowComp))==0:
                    rowCompl=[]
                else:
                    for line in rowComp:# rowComp may contain one or several hits!! let's obtain their corresponding id_complex_exp(line[0] and id_complex_molecule (line[-1])
                        ROWLCompe.append(line[0]) 
                    # id_complex_exp of complexes with the same exactly the same compounds in our submission
                    cec=DyndbComplexCompound.objects.filter(id_complex_exp__in=ROWLCompe).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lcomp_in_model))
                    # id_complex_exp of complexes with the same number of protein than our submission
                    cep=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLCompe).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model))  
                    if(len(cec)<len(cep)):# Complexes with the same number of molecules than our submission is lower than complexes with the same number of proteins than our submission. There should be only one. Then complex_exp value is taken from the DyndbComplexCompound query "c"
                        rowCompl=[cec[0]['id_complex_exp']]
                    else:# Number of Complexes involving the same number of proteins than our submission is lower or equal than the number of complexes involving the same number of compounds considered in our submission. Only one Complex involving the same number of proteins must exist. if 'equal' just a single complex_exp and complex_molecule exist
                        rowCompl=[cep[0]['id_complex_exp']]
        
      # for el in row:
      #     elok=DyndbComplexMolecule_Molecule.filter(
        CE_exists=False
        CM_exists=False
        if len(lmol_in_model)==0: #Protein_Protein Complex
            
            if len(row) > 0: #A Complex_Exp exists for the current model. The query in rowl only consider proteins!!!!
                print("COMPLEX_EXP: ", ce,"\nCOMPLEX_MOLECULE (MOLECULES+PROTEINS) None No molecule " ) 
                print("This Model has a Complex EXP but neither a Complex MOLECULE nor A complex Compound and stored in the database")
                CE_exists=True #The entries in Complex_Exp and Complex_Molecule do not have to be registered
                CEpk=rowl[0] #defined in the block making the QUERYp and its processing:

        if len(lmol_in_model)>0: #There are molecules in the model!!!!

            if len(rowCompl) > 0: #The corresponding complex_compound is in the GPCRmd database
                print("COMPLEX_EXP: ", rowCompl[0],"\n")
                CE_exists=True # If Complex_Exp exists Complex_Compound exist for sure
                CEpk=rowCompl[0]
                ##### MAKING THE MOLECULE-WISE QUERY 

                scolmol=[] #SELECT clause of the QUERY
                FromMOL=[] #FROM clause of the QUERY
                where=[]   #WHERE clause of the QUERY
                p=1
                ### importantly dyndb_complex_molecule will be used for obtaining the id_complex_exp linked with the set of molecules 
             
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
                ROWLp=[]#list of complex_exp matching the set of proteins in the QUERY
                ROWLm=[]#list of complex_molecules matching the  set of Molecules from the QUERY
                with connection.cursor() as cursor:
                    cursor.execute(QUERY)
                    row=cursor.fetchall()
                    if len(list(row))==0:
                        rowl=[]
                    else:
                        for line in row:# row may contain one or several hits!! let's obtain their corresponding id_complex_exp(line[0] and id_complex_molecule (line[-1])
                            ROWLp.append(line[0]) 
                            ROWLm.append(line[-1]) 
                        # id_complex_molecule of complexes with the same number of molecules than our submission
                        a=DyndbComplexMoleculeMolecule.objects.filter(id_complex_molecule__in=ROWLm).values('id_complex_molecule').annotate(num=Count('id_complex_molecule')).filter(num=len(lmol_in_model))
                        # id_complex_exp of complexes with the same number of protein than our submission
                        p=DyndbComplexProtein.objects.filter(id_complex_exp__in=ROWLp).values('id_complex_exp').annotate(num=Count('id_complex_exp')).filter(num=len(lprot_in_model))  
                        if(len(a)<len(p)):# Complexes with the same number of molecules than our submission is lower than complexes with the same number of proteins than our submission. 
                      #  actually one single complex_molecule involving the same number of molecules exist
                            ce=DyndbComplexMolecule.objects.filter(id=a[0]['id_complex_molecule']).values()[0]['id_complex_exp_id']
                            cm=a[0]['id_complex_molecule']
                            rowl=[ce,cm]
                        else:# Number of Complexes involving the same number of proteins than our submission is lower or equal than the number of complexes involving the same number of molecules than our submission. Only one Complex involving the same number of proteins must exist. if 'equal' just a single complex_exp and complex_molecule exist
                            cm=DyndbComplexMolecule.objects.filter(id_complex_exp=p[0]['id_complex_exp']).values()[0]['id']  
                            ce=p[0]['id_complex_exp']
                            rowl=[ce,cm]
                if len(rowl) >0: # The Complex_molecule is also in the GPCRmd database
                    print("COMPLEX_MOLECULE: ", rowl[-1],"\n The current Complex molecule already exists in the database")
                    CM_exists=True
                    id_complex_molecule=rowl[-1]
                    print("CM_exists= True ",id_complex_molecule)
        
