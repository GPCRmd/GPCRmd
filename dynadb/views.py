# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import connection
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.template import loader
from django.forms import formset_factory, ModelForm, modelformset_factory
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import re, os, pickle
import time
import json
import mimetypes
import requests
import math
from django.db.models.functions import Concat
from django.db.models import CharField,TextField, Case, When, Value as V
from .customized_errors import StreamSizeLimitError, StreamTimeoutError, ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from .sequence_tools import get_mutations, check_fasta
from .csv_in_memory_writer import CsvDictWriterNoFile, CsvDictWriterRowQuerySetIterator
from .uploadhandlers import TemporaryFileUploadHandlerMaxSize,TemporaryMoleculeFileUploadHandlerMaxSize
from .molecule_properties_tools import open_molecule_file, check_implicit_hydrogens, check_non_accepted_bond_orders, generate_inchi, generate_inchikey, generate_smiles, get_net_charge, write_sdf, generate_png, stdout_redirected
#from .models import Question,Formup
#from .forms import PostForm
from .models import DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, StructureType, WebResource, StructureModelLoopTemplates, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames, DyndbCannonicalProteins, Protein, DyndbSubmissionMolecule, DyndbSubmissionProtein
from .models import DyndbSubmissionProtein, DyndbFilesDynamics, DyndbReferencesModel, DyndbModelComponents,DyndbProteinMutations,DyndbExpProteinData,DyndbModel,DyndbDynamics,DyndbDynamicsComponents,DyndbReferencesDynamics,DyndbRelatedDynamicsDynamics,DyndbModelComponents,DyndbProteinCannonicalProtein,DyndbModel, StructureType, WebResource, StructureModelLoopTemplates, DyndbProtein, DyndbProteinSequence, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases, DyndbOtherProteinNames, DyndbProteinActivity, DyndbFileTypes, DyndbCompound, DyndbMolecule, DyndbFilesMolecule,DyndbFiles,DyndbOtherCompoundNames                
#from django.views.generic.edit import FormView
from .forms import FileUploadForm, NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, Formup, dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model
from .forms import NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_File_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model_Components, dyndb_Modeled_Residues,  dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, Formup, dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, dyndb_File_Types, dyndb_Submission, dyndb_Submission_Protein, dyndb_Submission_Molecule, dyndb_Submission_Model, dyndb_Protein_Cannonical_Protein, dyndb_Complex_Compound 
#from .forms import NameForm, TableForm
from .pipe4_6_0 import *
from time import sleep
from random import randint

# Create your views here.


def REFERENCEview(request, submission_id=None):
 
    if request.method == 'POST':
        if submission_id is None:
            sub =''
        else:
            sub = submission_id
        action="/".join(["/dynadb/REFERENCEfilled",sub])
        now=timezone.now()
        author="jmr"
#        forminfo={'issue':'1','url':'http://localhost:8000/ttt/prueba','doi':'8382938','title':'prinncii','journal_press':'marca','pub_year':'1996', 'volume':'agosto', 'pages':'2-3','authors':'pepe; luis', 'pmid':'4'}
        initREFF={'dbname':None,'update_timestamp':now,'creation_timestamp':now,'created_by_dbengine':author, 'last_update_by_dbengine':author, 'created_by':None }
        fdbREFF = dyndb_ReferenceForm(request.POST)
        with open('/protwis/sites/protwis/dynadb/REFpost.txt', 'wb') as handle:
            pickle.dump(request.POST, handle)

#####  Fill the empty fields in the fdbREFF instance with data from the initREFF dictionary

            

##### Check whether the fdbREFF instance of dyndb_ReferenceForm is valid:
        if fdbREFF.is_valid(): 
            # process the data in form.cleaned_data as required
            formREFF=fdbREFF.save(commit=False)
            for (key,value) in initREFF.items():
                setattr(formREFF, key, value)
#                print("valor de", key, "  ", formREFF.__dict__.values())
            
            print(fdbREFF.data,"  datos objeto fdbREFF")
            formREFF.save()
#            print("\n primary  key: ", formREFFi.pk )
#        else:
#            print("Errores del formulario ",fdbREFF.errors)
            

            return HttpResponseRedirect("/".join(["/dynadb/REFERENCEfilled",submission_id]), {'submission_id':submission_id} )

        else:
           # for field in fdbPF:
            iii=fdbREFF.errors.as_data()
            print("Errors", iii)
            
            pass
        
    # if a GET (or any other method) we'll create a blank form
    else:

        fdbREFF = dyndb_ReferenceForm()
        return render(request,'dynadb/REFERENCES.html', {'fdbREFF':fdbREFF, 'submission_id':submission_id})

def show_alig(request):
    if request.method=='POST':
        wtseq=request.POST.get('wtseq')
        mutseq=request.POST.get('mutant')
        result=align_wt_mut(wtseq,mutseq)
        result='>uniprot:\n'+result[0]+'\n>mutant:\n'+result[1]
        key=randint(1,1000000)
        request.session[key]=result
        tojson={'alignment':result, 'message':'' , 'userkey':key}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

def popup_alig(request, alignment_key):
    alignment=request.session[int(alignment_key)]
    return render(request,'dynadb/show_alignment.html', {'alig':alignment})

def PROTEINview(request, submission_id):
    p= submission_id
    print ("submission_id ==",submission_id)
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        with open('/protwis/sites/protwis/PROTEINpost.txt', 'wb') as handle:
            pickle.dump(request.POST, handle)
        action="/".join(["/dynadb/PROTEINfilled",submission_id," "])
        now=timezone.now()
#####  inintPF dictionary containing fields of the form dynadb_ProteinForm not
#####  available in the request.POST
#####
#####  initOPN dictionary dyndb_Other_Protein_NamesForm. To be updated in the
#####  view. Not depending on is_mutated field in dynadb_ProteinForm 
        initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initOPN={'id_protein':'1','other_names':'Lulu' } #other_names should be updated from UniProtKB Script Isma


        form=re.compile('form-')
        dictpost=request.POST
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

        for ii in indexl:
            if 'is_mutated' in dictprot[ii].keys():
                is_mutated_val=True
            else:
                is_mutated_val=False
            
            #### Check if the Protein in the HTML is already in the database 
            browse_protein_response=check_protein_entry_exist(dictprot[ii]['uniprotkbac'],dictprot[ii]['isoform'],is_mutated_val,dictprot[ii]['sequence'])#### POR AQUI!!!!!!!!!!!!!! 
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
                    response = HttpResponse(browse_protein_response['Message'],content_type='text/plain')
                    return response

#### If the protein ii is not found in our database create a new entry

            print("valor ii=", ii, "dictprot[ii]=\n", dictprot[ii])
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

##### Check whether the fdbPF instance of dyndb_ProteinForm is valid and save formPF entry in the database:
            if fdbPF[ii].is_valid(): 
                formPF[ii]=fdbPF[ii].save()
                print("\n primary  key: ", formPF[ii].pk )
            else:
                iii1=fdbPF[ii].errors.as_data()
                print("fdbPF",ii," no es valido")
                print("!!!!!!Errores despues del fdbPF[",ii,"]\n",iii1,"\n")

##### Fill the submission protein table  (Submission PROTEIN dictionary dictSP) 
            dictSP[ii]={'submission_id':int(submission_id), 'protein_id':formPF[ii].pk, 'int_id':ii} #int_id is 0 for the protein #1, 1 for the protein #2, ...
            print("dictSP[ii]=\n",dictSP[ii])
            fdbSP[ii]=dyndb_Submission_Protein(dictSP[ii])
            
            if fdbSP[ii].is_valid():
                fdbSP[ii].save()
            else:
                iii1=fdbSP[ii].errors.as_data()
                print("fdbSP[",ii,"] no es valido")

                print("!!!!!!Errores despues del fdbSP[",ii,"]\n",iii1,"\n")

#### Complex protein should be filled in the Model form

#           if 'receptor' in dictprot[ii].keys():
#               dictCP[ii]={'is_receptor':dictprot[ii]['receptor'],'id_protein':formPF[ii].pk,'id_complex_exp':1} #id_complex_exp should be Corrected!!!!
#               fdbCP[ii]=dyndb_Complex_Protein(dictCP[ii])
#               if fdbCP[ii].is_valid():
#                   fdbCP[ii].save()
#               else:
#                   iii1=fdbCP[ii].errors.as_data()
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
#                       iii1=fdbOPN[ii][numON].errors.as_data()
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
                if mseq is None:
                    response = HttpResponse('Mutated sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
                    return response
                if seq is None:
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
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
                    response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
                    return response
    
#########   Intance of the forms depending on the is_mutated value in dyndb_ProteinForm
    
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
                translate={'Entry':'uniprotkbac','Isoform':'isoform','Name':'name','Aliases':'other_names','Sequence':'sequence','Organism':'id_species_autocomplete','speciesid':'id_species'} #dictionary for the translation between the data in uniprot and the data in our tables
                for key,val in translate.items():
                    auxdictprot[ii][val]=dunikb[key]
                
  #####         We have to check if the current Protein entry matches the cannonical sequence. If not a new entry for the canonical sequence must be tracked. 

                if auxdictprot[ii]['sequence']!=initPS[ii]['sequence']:
                      # auxdictprot[ii]['sequence'] stands for the canonical sequence from UniProtKB DB
                      # initPS[ii]['sequence'] stands for the sequence of the protein to be tracked (either wild type or mutant depending on the field is_mutated)

                   #Let's create entries in DyndbProtein, DyndbProteinSequence, DyndbSubmissionProtein, 
                
                    auxdictprot[ii]['is_mutated']=False
                    initPF['id_uniprot_species']=dictprot[ii]['id_species']
                
                    for key,value in initPF.items():
                        auxdictprot[ii][key]=value
                
                    fdbPFaux[ii]=dyndb_ProteinForm(auxdictprot[ii])
                
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

##### Createe a  a dictionary for each alias of each protein (a.k.a. 'other_names'). A dyndb_Other_Protein_NamesForm instace correspond to each alias.
#####           
                
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

                    vformPFPCaP=formPF[ii].pk##  For completing the dyndbProteinCanonicalProtein table!!!! If sequence in the form is the Canonical Sequence!!!! Otherwise the value is taken from the UniProtKB entry

                    fdbCaP[ii]=dyndb_Cannonical_ProteinsForm({'id_protein':formPF[ii].pk})
                
                    if fdbCaP[ii].is_valid():
                        fdbCaP[ii].save()
                    else:
                        iii1=fdbCaP[ii].errors.as_data()
                        print("fdbCaPaux[",ii,"] no es valido")
                        print("!!!!!!Errores despues del fdbCaPaux[",ii,"]\n",iii1,"\n") 

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
        return HttpResponseRedirect("/".join(["/dynadb/PROTEINfilled",submission_id]), {'submission_id':submission_id} )

        
    # if a GET (or any other method) we'll create a blank form
    else:

        fdbPF = dyndb_ProteinForm()
        fdbPS = dyndb_Protein_SequenceForm()
        fdbPM = dyndb_Protein_MutationsForm()
        fdbOPN= dyndb_Other_Protein_NamesForm()
        return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS,'fdbPM':fdbPM,'fdbOPN':fdbOPN,'submission_id':submission_id})
#       return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS, 'fdbOPN':fdbOPN})

def delete_protein(request,submission_id):
    if request.method == "POST":
        protein_num = request.POST["protein_num"]
        
        
        response = HttpResponse('Success.',content_type='text/plain')
    else:
        response = HttpResponseForbidden()
    return response
    


def query_protein(request, protein_id):
    fiva=dict()
    actlist=list()
    fiva['mutations']=list()
    fiva['models']=list()
    fiva['other_names']=list()
    fiva['activity']=list()
    fiva['Uniprot_id']=DyndbProtein.objects.get(pk=protein_id).uniprotkbac    
    fiva['Protein_name']=DyndbProtein.objects.get(pk=protein_id).name
    fiva['cannonical']=DyndbProteinCannonicalProtein.objects.get(id_protein=protein_id).id_cannonical_proteins.id_protein.id
    fiva['is_mutated']=DyndbProtein.objects.get(pk=protein_id).is_mutated
    fiva['scientific_name']=DyndbProtein.objects.get(pk=protein_id).id_uniprot_species.scientific_name
    
    for match in DyndbProteinMutations.objects.filter(id_protein=protein_id):
        fiva['mutations'].append( (match.resid,match.resletter_from, match.resletter_to) )

    for match in DyndbOtherProteinNames.objects.filter(id_protein=protein_id): #checked
        fiva['other_names'].append(match.other_names)

    for match in DyndbModel.objects.filter(id_protein=protein_id):
        fiva['models'].append(match.id)

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

    for match in DyndbExpProteinData.objects.filter(id_protein=protein_id): #not working, but table incomplete so dont know if my fault.
        for match2 in DyndbProteinActivity.objects.filter(pk=match.id):
            fiva['activity'].append((match2.rvalue,match2.units,match2.description))

    print(fiva['activity'])
    return render(request, 'dynadb/protein_query_result.html',{'answer':fiva})


def query_protein_fasta(request,protein_id):
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

    with open('/tmp/'+protein_id+'_gpcrmd.fasta','w') as fh:
        fh.write('> GPCRmd:'+protein_id+'|Uniprot ID:'+uniprot_id.replace(" ","")+':\n')
        fh.write(fseq)
    with open('/tmp/'+protein_id+'_gpcrmd.fasta','r') as f:
        data=f.read()
        response=HttpResponse(data, content_type=mimetypes.guess_type('/tmp/'+protein_id+'_gpcrmd.fasta')[0])
        response['Content-Disposition']="attachment;filename=%s" % (protein_id+'_gpcrmd.fasta') #"attachment;'/tmp/'+protein_id+'_gpcrmd.fasta'"
        response['Content-Length']=os.path.getsize('/tmp/'+protein_id+'_gpcrmd.fasta')
    return response
            
def query_molecule(request, molecule_id):
    molec_dic=dict()
    molec_dic['inmodels']=list()
    molec_dic['link_2_compound']=list()
    molec_dic['sdf']=list()
    molec_dic['smiles']=DyndbMolecule.objects.get(pk=molecule_id).smiles
    molec_dic['description']=DyndbMolecule.objects.get(pk=molecule_id).description
    molec_dic['netcharge']=DyndbMolecule.objects.get(pk=molecule_id).net_charge
    molec_dic['inchi']=DyndbMolecule.objects.get(pk=molecule_id).inchi
    molec_dic['inchikey']=DyndbMolecule.objects.get(pk=molecule_id).inchikey
    molec_dic['inchicol']=DyndbMolecule.objects.get(pk=molecule_id).inchicol

    for match in DyndbModelComponents.objects.filter(id_molecule=molecule_id):
        molec_dic['inmodels'].append(match.id_model.id)

    for molfile in DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).filter(type=0):
        #molec_dic['sdf'].append(molfile.id_files.filepath)
        #intext=open('/protwis/sites/protwis/dynadb/3_mol_4.sdf','r')
        intext=open(molfile.id_files.filepath,'r')
        string=intext.read()
        molec_dic['sdf']=string
    for result in DyndbCompound.objects.filter(std_id_molecule=molecule_id):
        molec_dic['link_2_compound'].append(result.id) #pick the pk of the compounds pointing to the queried molecule

    return render(request, 'dynadb/molecule_query_result.html',{'answer':molec_dic})

def query_molecule_sdf(request, molecule_id):
    for molfile in DyndbFilesMolecule.objects.filter(id_molecule=molecule_id).filter(type=0): #MAKE SURE ONLY ONE FILE IS POSSIBLE
        intext=open(molfile.id_files.filepath,'r')
        string=intext.read()
    with open('/tmp/'+molecule_id+'_gpcrmd.sdf','w') as fh:
        fh.write(string)
    with open('/tmp/'+molecule_id+'_gpcrmd.sdf','r') as f:
        data=f.read()
        response=HttpResponse(data, content_type=mimetypes.guess_type('/tmp/'+molecule_id+'_gpcrmd.sdf')[0])
        response['Content-Disposition']="attachment;filename=%s" % (molecule_id+'_gpcrmd.sdf') #"attachment;'/tmp/'+protein_id+'_gpcrmd.fasta'"
        response['Content-Length']=os.path.getsize('/tmp/'+molecule_id+'_gpcrmd.sdf')
    return response
            

def query_compound(request,compound_id):
    comp_dic=dict()
    comp_dic['link_2_molecule']=list()
    #comp_dic['imagelink']=list()
    comp_dic['othernames']=list()
    for oname in DyndbOtherCompoundNames.objects.filter(id_compound=compound_id):
        comp_dic['othernames'].append(oname.other_names)
    comp_dic['name']=DyndbCompound.objects.get(pk=compound_id).name
    comp_dic['iupac_name']=DyndbCompound.objects.get(pk=compound_id).iupac_name
    comp_dic['pubchem_cid']=DyndbCompound.objects.get(pk=compound_id).pubchem_cid
    comp_dic['chembleid']=DyndbCompound.objects.get(pk=compound_id).chembleid
    comp_dic['sinchi']=DyndbCompound.objects.get(pk=compound_id).sinchi
    comp_dic['sinchikey']=DyndbCompound.objects.get(pk=compound_id).sinchikey
    try:
    	pk2filesmolecule=DyndbCompound.objects.get(pk=compound_id).std_id_molecule.id
    	comp_dic['imagelink']=DyndbFilesMolecule.objects.filter(id_molecule=pk2filesmolecule).filter(type=2)[0].id_files.filepath
    	comp_dic['imagelink']=comp_dic['imagelink'].replace("/protwis/sites/","/dynadb/") #this makes it work
    except:
        pass
    #print (comp_dic['imagelink'])
    for molecule in DyndbMolecule.objects.filter(id_compound=compound_id):
        comp_dic['link_2_molecule'].append(molecule.id)
    #    for molfile in DyndbFilesMolecule.objects.filter(id_molecule=molecule.id).filter(type=2):
    #        #comp_dic['imagelink'].append(molfile.id_files.filepath)

    return render(request, 'dynadb/compound_query_result.html',{'answer':comp_dic})


def query_model(request,model_id):
    model_dic=dict()
    #model_dic['description']=DyndbModel.objects.get(pk=model_id).description #NOT WORKING BECAUSE OF MISSING INFOMRATION
    model_dic['pdbid']=DyndbModel.objects.get(pk=model_id).pdbid
    model_dic['type']=DyndbModel.objects.get(pk=model_id).type
    #model_dic['link2protein']=DyndbModel.objects.get(pk=model_id).id_protein.id #NOT WORKING BECAUSE OF MISSING INFORMATION
    model_dic['references']=list()
    model_dic['components']=list()
    model_dic['dynamics']=list()
    for match in DyndbModelComponents.objects.filter(id_model=model_id):
        model_dic['components'].append(match.id_molecule.id)
    for match in DyndbDynamics.objects.filter(id_model=model_id):
        model_dic['dynamics'].append(match.id)
    for match in DyndbReferencesModel.objects.filter(id_model=model_id):
        model_dic['references'].append( (match.id_references.doi, match.id_references.title) )
    return render(request, 'dynadb/model_query_result.html',{'answer':model_dic})

def query_dynamics(request,dynamics_id):
    dyna_dic=dict()
    dyna_dic['link_2_molecules']=list()
    dyna_dic['files']=list()
    dyna_dic['references']=list()
    dyna_dic['related']=list()
    dyna_dic['soft']=DyndbDynamics.objects.get(pk=dynamics_id).software
    dyna_dic['softv']=DyndbDynamics.objects.get(pk=dynamics_id).sversion
    dyna_dic['forcefield']=DyndbDynamics.objects.get(pk=dynamics_id).ff
    dyna_dic['forcefieldv']=DyndbDynamics.objects.get(pk=dynamics_id).ffversion
    dyna_dic['link_2_model']=DyndbDynamics.objects.get(pk=dynamics_id).id_model.id
    dyna_dic['description']=DyndbDynamics.objects.get(pk=dynamics_id).description
    dyna_dic['timestep']=DyndbDynamics.objects.get(pk=dynamics_id).timestep
    dyna_dic['delta']=DyndbDynamics.objects.get(pk=dynamics_id).delta
    dyna_dic['solventtype']=DyndbDynamics.objects.get(pk=dynamics_id).id_dynamics_solvent_types.type_name
    dyna_dic['membranetype']=DyndbDynamics.objects.get(pk=dynamics_id).id_dynamics_membrane_types.type_name

    for match in DyndbDynamicsComponents.objects.filter(id_dynamics=dynamics_id):
        dyna_dic['link_2_molecules'].append(match.id_molecule.id)

    for match in DyndbRelatedDynamicsDynamics.objects.filter(id_dynamics=dynamics_id):
        dyna_dic['related'].append(match.id_related_dynamics.id_dynamics.id)
    
    for match in DyndbReferencesDynamics.objects.filter(id_dynamics=dynamics_id):
        dyna_dic['references'].append(match.id_references.doi)

    for match in DyndbFilesDynamics.objects.filter(id_dynamics=dynamics_id):
        dyna_dic['files'].append( ( match.id_files.filepath.replace("/protwis/sites/","/dynadb/") , match.id_files.filename ) ) 
    
    return render(request, 'dynadb/dynamics_query_result.html',{'answer':dyna_dic})

def protein_get_data_upkb(request, uniprotkbac=None):
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
            response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain')
            return response
          if data['Entry'] != uniprotkbac_noiso and isoform is not None:
            response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain')
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
              response = HttpResponseNotFound('No data found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain')
            else:
              response = HttpResponse('Problem downloading from UniProtKB:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from UniProtKB:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain')
          else:
            response = HttpResponse('Cannot connect to UniProt server:\n'+errdata['reason'],status=504,content_type='text/plain')
            
        else:
          datakeys = set([i.lower() for i in data.keys()])
          if datakeys == KEYS:
            response = JsonResponse(data) 
            #response={'dict':data,'json':JsonResponse(data)}
            #print (response) ###JUANMA
          else:
            response = HttpResponse('Invalid response from UniProtKB.',status=502,content_type='text/plain')
        
        
        
      else:
        response = HttpResponse('Invalid UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain')
    else:
      response = HttpResponse('Missing UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain')
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
      response = HttpResponse('Parsing error: '+str(e),status=422,reason='Unprocessable Entity',content_type='text/plain')
      return response
    except:
      raise


def upload_pdb(request):
    if request.method == 'POST':
        form = FileUploadForm(data=request.POST, files=request.FILES) #"upload_pdb"
        myfile = request.FILES["file_source"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        request.session['newfilename']=uploaded_file_url
        pdbname='/protwis/sites'+request.session['newfilename']
        if form.is_valid():
            print('valid form')                     
        else:
            print ('invalid form')
            print (form.errors)
        tojson={'chain': 'A','message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

def search_top(request):
    if request.method=='POST':
        url=request.POST.get('url')
        pdbname='/protwis/sites'+request.session['newfilename'] 
        sub_id=url[url.rfind('/model/')+7:-1] 
        arrays=request.POST.getlist('bigarray[]')
        counter=0
        resultsdict=dict()
        for array in arrays:
            array=array.split(',') #array is a string with commas.
            prot_id= 1 #int(request.POST.get('id_protein')) #current submission ID.

            if array[3].replace(" ", "")=='' or not (array[3].isdigit()) or array[4].replace(" ", "")=='' or not (array[4].isdigit()):
                results={'type':'string_error','title':'Missing information or wrong information', 'message':'Missing or incorrect information in the "Res from" or "Res to" fields. Maybe some whitespace?'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json') 
            start=int(array[3])
            stop=int(array[4])
            if start>=stop:
                results={'type':'string_error','title':'Missing information or wrong information', 'message':'"Res from" greater or equal than "Res to"'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json') 
            chain=array[1].replace(" ", "").upper() #avoid whitespace problems
            segid=array[2].replace(" ", "").upper() #avoid whitespace problems
            protid=DyndbSubmissionProtein.objects.filter(int_id=prot_id).filter(submission_id=sub_id)[0].protein_id.id
            sequence=DyndbProteinSequence.objects.filter(id_protein=protid)[0].sequence
            res=searchtop(pdbname,sequence, start,stop,chain,segid)
            if isinstance(res,tuple):
                seq_res_from,seq_res_to=res
                resultsdict[counter]=[seq_res_from,seq_res_to]
                resultsdict['message']=''
            elif isinstance(res,str):
                 resultsdict['message']=res
            counter+=1

    data = json.dumps(resultsdict)
    return HttpResponse(data, content_type='application/json')




def pdbcheck(request,combination_id):
    if request.method=='POST': #See pdbcheck.js
        results=dict()
        url=request.POST.get('url')
        #fastaname='/protwis/sites/protwis/dynadb/1fat.fa'
        pdbname='/protwis/sites'+request.session['newfilename'] 
        sub_id=url[url.rfind('/model/')+7:-1] 
        results['strlist']=list()
        results['pathlist']=list()
        finalguide=[]
        arrays=request.POST.getlist('bigarray[]')
        counter=0
        for array in arrays:
            array=array.split(',')
            results['strlist'].append('Protein: '+array[0]+' Chain: '+ array[1]+'| SEGID: '+array[2]+'| ResFrom: '+array[3]+'| Resto: '+array[4]+'| SeqResFrom: '+array[5]+'| SeqResTo: '+array[6]+'| Bond?: '+array[7]+'| PDB ID: '+array[8]+'| Source type: '+array[9]+'| Template ID model: '+array[10]+'|') #title for the results pop-up table

            for r in range(3,7):
                if array[r].replace(" ", "")=='' or not array[r].isdigit():
                    results={'type':'string_error','title':'Missing information or wrong information', 'message':'Residue or sequence range is not completely defined, or you did not used a number.'}
                    tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop, 'error':'now we are screwed', 'message':'surely we are',}
                    data = json.dumps(tojson) #CHANGE TO results!!!!!!!!!!!!!!!!!!!!!!
                    request.session[combination_id] = results
                    return HttpResponse(data, content_type='application/json') 

            prot_id= 1 #int(array[0]) #OLD: int(request.POST.get('id_protein')) #current submission ID.
            start=int(array[3])
            stop=int(array[4])
            seqstart=int(array[5])
            seqstop=int(array[6])
            if seqstart>=seqstop:
                results={'type':'string_error','title':'Range error', 'message':'"Seq Res from" equal or greater than "Seq Res to"'}
                data = json.dumps(results)
                return HttpResponse(data, content_type='application/json')                 
            chain=array[1].replace(" ", "").upper()
            segid=array[2].replace(" ", "").upper()     
            protid=DyndbSubmissionProtein.objects.filter(int_id=prot_id).filter(submission_id=sub_id)[0].protein_id.id
            sequence=DyndbProteinSequence.objects.filter(id_protein=protid)[0].sequence
            sequence=sequence[seqstart-1:seqstop]

            if stop-start<1:
                results={'type':'string_error','title':'Range error', 'errmess':'"Res from" value is bigger or equal to the "Res to" value','message':''}
                tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,}
                data = json.dumps(tojson)
                request.session[combination_id] = results
                return HttpResponse(data, content_type='application/json')

            uniquetest=unique(pdbname, chain!='',segid!='')
            if uniquetest==True:
                checkresult=checkpdb(pdbname,segid,start,stop,chain)

                if isinstance(checkresult,tuple):
                    tablepdb,simplified_sequence,hexflag=checkresult
                    guide=matchpdbfa(sequence,simplified_sequence,tablepdb,hexflag,seqstart)

                    if isinstance(guide, list):
                        path_to_repaired=repairpdb(pdbname,guide,segid,start,stop,chain)
                        results['pathlist'].append(path_to_repaired)
                        segments=segment_id(path_to_repaired, segid, start, stop, chain)
                        finalguide.append(guide)
                    elif isinstance(guide, tuple):
                        results={'type':'tuple_error', 'title':'Mismatch found', 'mismatchlist':guide[1],'errmess':guide[0]}
                        request.session[combination_id] = results
                        request.session.modified = True
                        tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
                        data = json.dumps(tojson)
                        return HttpResponse(data, content_type='application/json')
                    else: #PDB has insertions error
                        results={'type':'string_error', 'title':'Insertion in PDB according to FASTA file' ,'errmess':guide,'message':''}
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

            counter=+1

        if isinstance(finalguide, list) and len(finalguide)>0:
            results['type']='fullrun'
            results['table']=finalguide
            results['seg']=segments
            results['path']=path_to_repaired

        request.session[combination_id] = results
        request.session.modified = True
        tojson={'chain': chain, 'segid': segid, 'start': start, 'stop': stop,'message':''}
        data = json.dumps(tojson)
        return HttpResponse(data, content_type='application/json')

    else: #NOT POST, simply display of results in the POP UP window. See pdbcheck.js
        fav_color = request.session[combination_id]
        if fav_color['type']=='tuple_error':
            return render(request,'dynadb/tuple_error.html', {'answer':fav_color})

        elif fav_color['type']=='string_error':
            return render(request,'dynadb/string_error.html', {'answer':fav_color})

        elif fav_color['type']=='fullrun':
            return render(request,'dynadb/fullrun.html', {'answer':fav_color})

        else:
            fav_color={'errmess':'Most common causes are: \n -Missing one file\n -Too short interval\n -Very bad alignment\n ','title':'Unknown error'}
            return render(request,'dynadb/string_error.html', {'answer':fav_color})

def servecorrectedpdb(request,pdbname):
    with open('/tmp/'+pdbname,'r') as f:
        data=f.read()
        response=HttpResponse(data, content_type=mimetypes.guess_type('/tmp/'+pdbname)[0])
        response['Content-Disposition']="attachment;filename=%s" % (pdbname) #"attachment;'/tmp/'+protein_id+'_gpcrmd.fasta'"
        response['Content-Length']=os.path.getsize('/tmp/'+pdbname)
    return response

def MODELview(request, submission_id):
    # Function for saving files
    def handle_uploaded_file(f,p,name):
        print("file name = ", f.name , "path =", p)
        f.name=name
        print("NEW name = ", f.name , "path =", p)
        path=p+"/"+f.name
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
    print("REQUEST SESSIONS",request.session.items())
    request.session['info']="PASAR a SESSION"
    print("REQUEST SESSIONS",request.session.items())
    # Dealing with POST data
    if request.method == 'POST':
        #Defining variables and dictionaries with information not available in the html form. This is needed for form instances.
        action="/".join(["/dynadb/MODELfilled",submission_id,""])
        now=timezone.now()
        author="jmr"
        author_id=1
        initMOD={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
        initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
        
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
        indexpsl.sort()
        indexmcl.sort()
        print("MIRAR INDICES",indexpsl,"\n",indexmcl)

        for i in indexpsl:
            print ("\ndictprotsour",i,":\n", dictprotsour[i])
            print ("\ndictprotsourmod",i,":\n", dictprotsourmod[i])
            
        for i in indexmcl:
            print ("\ndictmodcomp",i,":\n", dictmodcomp[i])
            print ("\ndictmodcompmod",i,":\n", dictmodcompmod[i])

######## 
        ########   Query for obtaining molecules submitted in the current submission!!!!
        qSMol=DyndbSubmissionMolecule.objects.filter(submission_id=submission_id).filter(not_in_model=False).exclude(int_id=None)
        molid_typel=dict(list(set(qSMol.values_list('molecule_id','type'))))
        #molid_typel=dict(set(qSMol.values_list('molecule_id','type')))
        lmol_in_modelbs =qSMol.values_list('molecule_id',flat=True)
        lmol_in_model=list(set(lmol_in_modelbs)) ###Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only care about the type of element involved in the model, not about the number of elements
 
        ########   Query for obtaining Proteins submitted in the current submission!!!!
        qSProt=DyndbSubmissionProtein.objects.filter(submission_id=submission_id).exclude(int_id=None)
        lprot_in_model=qSProt.values_list('protein_id',flat=True)
        lprot_in_model=list(set(lprot_in_model))  ###Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only care about the type of element involved in the model, not about the number of elements

        ########   Query for obtaining Proteins submitted in the current submission!!!!
        qM=DyndbMolecule.objects.filter(id__in=lmol_in_model)
        comptomol=dict(list(set(qM.values_list('id_compound','id'))))
        lcomp_in_modelbs=qM.values_list('id_compound',flat=True)  
        lcomp_in_model=list(set(lcomp_in_modelbs)) ####Creating a list with unique elements Complex Exp Complex Compound and Complex Molecule only care about the type of element involved in the model, not about the number of elements


########   Check if the complex is already in the GPCRmd DB 
            # Complex stand for the protein and molecule disregarding the number of items involved in the model
            #lists for creating the query targeting the COMPLEX_EXP matching the current that is being submitted if it exist previously in the database!!!!!
            # COMPLEX_EXP involves proteins and Compounds in the Model. COMPLEX_MOLECULE involves proteins and the specific form of the compounds (molecules) in the model
        scolmol=[]
        FromMOL=[]
        where=[]
        p=0
        
        for pid in lprot_in_model:
            p=p+1
            tp=("").join(["t",str(p)])
            if pid==lprot_in_model[0]:
                tinit=tp
                scolmol.append(("").join(["SELECT ",tp,".id_complex_exp, ",tp,".id_protein"]))
                FromMOL.append(("").join(["FROM dyndb_complex_protein AS ",tp]))
                where.append(("").join(["WHERE ",tp,".id_protein = ", str(pid)]))
            else:
                scolmol.append(("").join([", ",tp,".id_protein "]))
                FromMOL.append(("").join([" INNER JOIN dyndb_complex_protein AS ",tp," ON ",tinit,".id_complex_exp = ", tp,".id_complex_exp "]))
                where.append(("").join([" AND ",tp,".id_protein = ", str(pid)]))

        scolComp=scolmol[:]
        FromComp=FromMOL[:]
        whereComp=where[:]
        s=p
        
        ### important dyndb_complex_molecule will be used for obtaining the id_complex_exp linked with the set of molecules 
        p=p+1
        tcm=("").join(["t",str(p)])
        scolmol.append(("").join([", ",tcm,".id_complex_exp"]))
        FromMOL.append(("").join(["LEFT OUTER JOIN dyndb_complex_molecule AS ", tcm, " ON ", tcm,".id_complex_exp = t1.id_complex_exp" ] ))
        
        if len(lmol_in_model)==0: #If there is not any molecule in the model the query is based in the proteins
            where.append(("AND tcm.id_complex_exp IS NULL;"))
            SELp=(" ").join(scolmol)
            FROMp=(" ").join(FromMOL)
            WHEREp=(" ").join(where)
            QUERYp=(" ").join([SEL,FROM,WHERE])

            with connection.cursor() as cursor:
                cursor.execute(QUERY)
                row=cursor.fetchall()
                if len(list(row))==0:
                    rowl=[]
                else:
                    rowl=list(row[0]) 

        else: # otherwise molecules should be included in the query. Two queries are needed... Complex_Compound and Complex_Molecule 
            for mid in lmol_in_model:  #Query Complex_molecule
                p=p+1
                tp=("").join(["t",str(p)])
                scolmol.append(("").join([", ",tp,".id_molecule"]))
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
        
            for cid in lcomp_in_model: #Query complex_compound
                s=s+1
                sp=("").join(["t",str(s)])
                scolComp.append(("").join([", ",sp,".id_compound"]))
                FromComp.append(("").join([" LEFT OUTER JOIN dyndb_complex_compound AS ", sp, " ON ",tinit,".id_complex_exp = ", sp,".id_complex_exp"]))
                whereComp.append(("").join([" AND ",sp,".id_compound = ", str(cid)]))
                if cid==lcomp_in_model[-1]:
                    where.append(";")
        
            SELComp=(" ").join(scolComp)
            FROMComp=(" ").join(FromComp)
            WHEREComp=(" ").join(whereComp)
            QUERYComp=(" ").join([SELComp,FROMComp,WHEREComp])
        
            with connection.cursor() as cursor:
                cursor.execute(QUERY)
                row=cursor.fetchall()
                if len(list(row))==0:
                    rowl=[]
                else:
                    rowl=list(row[0]) 
        
            with connection.cursor() as cursor:
                cursor.execute(QUERYComp)
                rowComp=cursor.fetchall()
                if len(list(rowComp))==0:
                    rowCompl=[]
                else:
                    rowCompl=list(rowComp[0]) 
 
        CE_exists=False
        CM_exists=False
        if len(lmol_in_model)==0: #Protein_Protein Complex
            
            if len(rowl) > 0: #A Complex_Exp exists for the current model. The query in rowl only consider proteins!!!!
                print("COMPLEX_EXP: ", rowl[0],"\nCOMPLEX_MOLECULE (MOLECULES+PROTEINS) ", rowl[-1]) 
                print("This Model has a Complex MOLECULE, A complex Compound and a Complex EXP stored in the database")
                CE_exists=True
                CEpk=rowl[0]
#                CM_exists=True## The entries in Complex_Compound and Complex_Molecule do not have to be registered

        if len(lmol_in_model)>0: #There are molecules in the model!!!!
            if len(rowCompl) > 0: #The corresponding complex_compound is in the GPCRmd database
                print("COMPLEX_EXP: ", rowCompl[0],"\n")
                CE_exists=True # If Complex_Exp exists Complex_Compound exist for sure
                CEpk=rowCompl[0]
                CEpk=rowCompl[0]
                if len(rowl) >0: # The Complex_molecule is also in the GPCRmd database
                    print("COMPLEX_MOLECULE: ", rowl[-1],"\n The current Complex molecule already exists in the database")
                    CM_exists=True
                    id_complex_molecule=rowl[-1]
                    print("CM_exists= True ",id_complex_molecule)
        
        if CE_exists==False:
            fdbCE=dyndb_Complex_Exp({'creation_timestamp':timezone.now(),'update_timestamp':timezone.now()}) 
            if fdbCE.is_valid():
                fdbCEobj=fdbCE.save()
                CEpk=fdbCEobj.pk
            else:
                print("Errores en el form dyndb_Complex_Exp\n ", fdbCE.errors.as_data())                
            for prot in lprot_in_model:
                fdbComP=dyndb_Complex_Protein({'id_protein':prot,'id_complex_exp':CEpk})
                if fdbComP.is_valid():
                    fdbComPobj=fdbComP.save()
                else:
                    print("Errores en el form dyndb_Complex_Protein\n ", fdbComP.errors.as_data())    

            if len(lmol_in_model)>0: 
                for comp in  lcomp_in_model: #no Complex containing these set of compounds and proteins exists in the database. Record a new entry
                    fdbComComp=dyndb_Complex_Compound({'id_complex_exp':CEpk,'id_compound':comp ,'type':molid_typel[comptomol[comp]],'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() })
                    if fdbComComp.is_valid():
                        fdbComComp.save()
                    else:
                        print("Errores en el form dyndb_Complex_Compound\n ", fdbComComp.errors.as_data())
        if CM_exists==False:  #No Complex containing the set of compounds has been recorded.
        
            fdbComMol=dyndb_Complex_Molecule({'id_complex_exp':CEpk,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now(),'created_by_dbengine':author, 'last_update_by_dbengine':author, 'created_by':author_id,'last_update_by':author_id})
            if fdbComMol.is_valid():
                fdbComMolobj=fdbComMol.save()
                ComMolpk=fdbComMolobj.pk
                id_complex_molecule=ComMolpk
                print("CM_exist= False ",id_complex_molecule)
            else:
                print("Errores en el form dyndb_Complex_Molecule\n ", fdbComMol.errors.as_data())
            for obj in qSMol.values():
               
                fdbComMolMol=dyndb_Complex_Molecule_Molecule({'id_complex_molecule':id_complex_molecule,'id_molecule':obj['molecule_id_id'],'type':obj['type']})
                if fdbComMolMol.is_valid():
                    fdbComMolMol.save()
                else:
                    print("Errores en el form dyndb_Complex_Molecule_Molecule\n ", fdbComMolMol.errors.as_data())

        if dictmodel['type']=='1':
            dictmodel['id_protein']=None
            dictmodel['id_complex_molecule']=id_complex_molecule
            
        else:
            dictmodel['id_protein']=lprot_in_model[-1]
            dictmodel['id_complex_molecule']=None

        fdbMF = dyndb_Model(dictmodel)
        for key,value in initMOD.items():
            fdbMF.data[key]=value
        if fdbMF.is_valid():
            fdbMFobj=fdbMF.save(commit=False)
            fdbMFobj=fdbMF.save()
            MFpk=fdbMFobj.pk
        else:
            print("Errores en el form dyndbModels\n ", fdbMF.errors.as_data())
        
        #Fill the dyndb_Submission_Model form. Remember there is just a single Model for each submission !!!!
        dictSMd={'model_id':MFpk,'submission_id':submission_id}
        fdbSMd=dyndb_Submission_Model(dictSMd)
        if fdbSMd.is_valid():
            fdbSMd.save()
        else:
            iii1=fdbSMd[ii].errors.as_data()
            print("fdbSMd",ii," no es valido")
            print("!!!!!!Errores despues del fdbSMd[",ii,"]\n",iii1,"\n")

        #Create storage directory: Every MODEL has its own directory in which the corresponding pdb file is saved. This directory is labeled as "PDBmodel"+ MFpk (primary key of the model)
        #Maybe we have to label the directory with submissionID?????
        PDBmodel=request.FILES['upload_pdb']
        direct='/protwis/sites/files/Model/model'+str(submission_id)
        print("\nDirectorio a crear ", direct)
        print("\nNombre del fichero ", PDBmodel)
        if not os.path.exists(direct):
            os.makedirs(direct)


        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']

        fext="".join(PDBmodel.name.split(".")[1:]) 
        dictfile={}
        dictfiles['filename']=PDBmodel
        dictfiles['description']="PDB file containing Model coordinates"
        dictfiles['id_file_types']=dict_ext_id[fext]
        dictfiles['filepath']=direct
        for key,val in initFiles.items():   
            dictfiles[key]=val
        fdbFile=dyndb_Files(dictfiles)
        if fdbFile.is_valid():
            fdbFileobj=fdbFile.save()
            newname=str(fdbFileobj.pk)+"_model_"+str(submission_id)+"."+fext
            handle_uploaded_file(PDBmodel,direct,newname)
            completepath=direct+"/"+newname
            fdbFileobj.filename=newname   #rename filename in the database after saving the initial name
            fdbFileobj.filepath=completepath   #rename filepath to the one including the new filename in the database after saving the initial name
            fdbFileobj.save()
            dictFModel={}
            dictFModel['id_files']=fdbFileobj.pk
            dictFModel['id_model']=MFpk
            fdbFModel=dyndb_Files_Model(dictFModel)
            if fdbFModel.is_valid():
                fdbFModel.save() 
            else:
                print("Errores en el form dyndb_Files_Model\n ", fdbFile.errors.as_data())
        else:
            print("Errores en el form dyndb_Files\n ", fdbFile.errors.as_data())

        request.session['newfilename']=direct+'/'+newname #added on 27/9 to access the path of the uploaded PDB file from pdbcheck view. Alex.

        fdbPS={} 
        fdbPSobj={} 
        for ii in indexpsl:
            if ii != indexpsl[0]: 
                if "bonded_to_id_modeled_residues" in dictprotsourmod[ii].keys():
                    dictprotsourmod[ii]['bonded_to_id_modeled_residues']=fdbPSobj[int(ii)-1].pk
                else:
                    dictprotsourmod[ii]['bonded_to_id_modeled_residues']=None
            else:
                dictprotsourmod[ii]['bonded_to_id_modeled_residues']=None

            dictprotsourmod[ii]['id_model']=MFpk
            dictprotsourmod[ii]['template_id_model']=None
            dictprotsourmod[ii]['id_protein']=qSProt.values().filter(int_id=int(dictprotsourmod[ii]['prot'])-1)[0]['protein_id_id']
            dictprotsourmod[ii]['source_type']=dictprotsourmod[ii].pop('source_typeps')
            dictprotsourmod[ii]['pdbid']=dictprotsourmod[ii].pop('pdbidps')
            fdbPS[ii] = dyndb_Modeled_Residues(dictprotsourmod[ii])
            print("dictprotsourmod[ii]=", dictprotsourmod[ii])
            if fdbPS[ii].is_valid():
                fdbPSobj[ii]=fdbPS[ii].save(commit=False)
                fdbPSobj[ii]=fdbPS[ii].save()
                fdbPSobj[ii].pk
            else:
                print("Errores en el form dyndb_Modeled_Residues\n ", fdbPS[ii].errors.as_data())

        fdbMC={} 
        fdbMCobj={} 
        
        for ii in indexmcl:  
            dictmodcompmod[ii]['id_model']=MFpk
            dictmodcompmod[ii]['name']=dictmodcompmod[ii].pop('namemc')
            dictmodcompmod[ii]['id_molecule']= qSMol.values().filter(int_id=int(dictmodcompmod[ii]['molecule'])-1)[0]['molecule_id_id']
            dictmodcompmod[ii]['type']=dictmodcompmod[ii].pop('typemc')
            print ("\ndictmodcompmod type  name y id_model",i,":\n", dictmodcompmod[ii]['type'], dictmodcompmod[ii]['name'],  dictmodcompmod[ii]['id_model'])
            fdbMC[ii] = dyndb_Model_Components(dictmodcompmod[ii])
            if fdbMC[ii].is_valid():
                fdbMCobj[ii]=fdbMC[ii].save(commit=False)
                fdbMCobj[ii]=fdbMC[ii].save()
            else:
                print("Errores en el form dyndb_Model_Components\n ", fdbMC[ii].errors.as_data())
                         
            



#            form.user=request.user
#            form.save()
            # redirect to a new URL:
        return HttpResponseRedirect("/".join(["/dynadb/MODELfilled",submission_id,""]), {'submission_id':submission_id} )

    # if a GET (or any other method) we'll create a blank form
    else:

        fdbMF = dyndb_Model()
        fdbPS = dyndb_Modeled_Residues()
        fdbMC = dyndb_Model_Components()
        return render(request,'dynadb/MODEL.html', {'fdbMF':fdbMF,'fdbPS':fdbPS,'fdbMC':fdbMC,'submission_id':submission_id})


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
        
        fdbMF=dyndb_CompoundForm(request.POST)
        for key,value in initCF.items():
            initCF[key]=value

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
def generate_molecule_properties(request,submission_id):
  request.upload_handlers[1] = TemporaryMoleculeFileUploadHandlerMaxSize(request,50*1024**2)
  return _generate_molecule_properties(request,submission_id)

@csrf_protect
def _generate_molecule_properties(request,submission_id):
  url_prefix = "/dynadb/"
  moleculepath = 'Molecule'
  pngsize = 300
  RecMet = False
  formre = re.compile('^form-(\d+)-')
  submission_folder = os.path.join(moleculepath,'mol'+str(submission_id))
             
  if request.method == 'POST':
    

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
            os.makedirs(os.path.join(settings.MEDIA_ROOT,submission_folder),exist_ok=True) 
            molname = 'tmp_mol_'+str(molid)+'_'+str(submission_id)
            logpath = os.path.join(submission_folder, molname+'.log')
            logfile = open(os.path.join(settings.MEDIA_ROOT,logpath),'w')
            
            data['download_url_log'] = os.path.join(url_prefix,settings.MEDIA_URL.replace('/', '',1),logpath)
            try:
                mol = open_molecule_file(uploadfile,logfile)
            except (ParsingError, MultipleMoleculesinSDF, InvalidMoleculeFileExtension) as e:
                print(e.args[0],file=logfile)
                logfile.close()
                data['msg'] = e.args[0]
                return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
            except:
                logfile.close()
                data['msg'] = 'Cannot load molecule from uploaded file. Please, see log file.'
                print(data['msg'],file=logfile)
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
            mol.SetProp("_Name",molname)
            sdfpath = os.path.join(submission_folder, molname+'.sdf')
            write_sdf(mol,os.path.join(settings.MEDIA_ROOT,sdfpath))
            data['download_url_sdf'] = os.path.join(url_prefix,settings.MEDIA_URL.replace('/', '',1),sdfpath)
            pngpath = os.path.join(submission_folder,molname+'_'+str(pngsize)+'.png')
            print('Drawing molecule...',file=logfile)
            try:
                generate_png(mol,os.path.join(settings.MEDIA_ROOT,pngpath),logfile,size=pngsize)
            except:
                msg = 'Error while drawing molecule.'
                print(msg,file=logfile)
                logfile.close()
                data['msg'] = msg+' Please, see log file.'
                return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
            print(url_prefix)
            print(os.path.join(url_prefix,settings.MEDIA_URL.replace('/', '',1),pngpath))

            data['download_url_png'] = os.path.join(url_prefix,settings.MEDIA_URL.replace('/', '',1),pngpath)
            print('Finished with molecule.',file=logfile)
            logfile.close()
            del mol
            
            return JsonResponse(data,safe=False)
        else:
            data['msg'] = 'Unknown molecule file reference.'
            return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
    elif request.upload_handlers[0].exception is not None:
        try:
            raise request.upload_handlers[0].exception
        except(InvalidMoleculeFileExtension,MultipleMoleculesinSDF) as e :
            data['msg'] = e.args[0]
            return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')
            
            
        
    else:
        data['msg'] = 'No file was selected or cannot find molecule file reference.'
        return JsonResponse(data,safe=False,status=422,reason='Unprocessable Entity')


def SMALL_MOLECULEview(request, submission_id):

    def handle_uploaded_file(f,p,name):
        print("file name = ", f.name , "path =", p)
        f.name=name
        print("NEW name = ", f.name , "path =", p)
        path=p+"/"+f.name
        with open(path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

    author="jmr"   #to be modified with author information. To initPF dict
    action="/".join(["/dynadb/MOLECULEfilled",submission_id,""])
    now=timezone.now()
    onames="Pepito; Juanito; Herculito" #to be modified... scripted
    initMF={'inchicol':1,'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  } #####HAY QUE CAMBIAR INCHICOL!!!!!!!!! OJO!!!!!!!!!
    initCF={'sinchi':"AAAABAAAABAAAA-AAAABAAAAB-A",'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }#####HAY QUE CAMBIAR SINCHI!!!!!!!!! OJO!!!!!!!!!
    initON={'other_names': onames,'id_compound':None} 
    dicpost=request.POST
    dicfiles=request.FILES
    initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
    ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
    ft=DyndbFileTypes.objects.all()
    dict_ext_id={}
    for l in ft:
        dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']

    d_fmolec_t={'Image':'0','Molecule':'1'} ######VOY POR AQUI!!!!!!!!!!!!!!!!!!!!!!!
    if request.method == 'POST':
        dictmol={}
        fieldsmol=["id_compound","description","net_charge","inchi","inchikey","inchicol","smiles"]
        dictON={}
        fieldsON=["other_names"]
        dictcomp={}
        fieldscomp=["name","iupac_name","pubchem_cid","chembleid","sinchi","sinchikey","std_id_molecule","id_ligand"]
        dictfmol={} 
        fieldsPMod={"is_present"}
        dictPMod={}
        form=re.compile('form-')
        indexl=[]
        print("!!!!!indexl== ",indexl)
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
            print("\nINICIO: key-val== ",key," ",val,"nkey ==", nkey,"\n")
            dfieldtype={'0':fieldsmol,'1':fieldsON,'2':fieldscomp,'3':fieldsPMod}
            dfielddict={'0':dictmol,'1':dictON,'2':dictcomp,'3':dictPMod}
            for k,v in dfieldtype.items():
                if nkey in v:
                    dfielddict[k][index][nkey]=val
                    print("Index ", index, "Indexl", indexl, " key== ",key, " Lista== ", v, " nkey", nkey)
                    print ("\n key ", nl, "dfielddict == ", dfielddict)
                    break
           #     else:
           #         print("OJO!!! key== ",key, " no en Lista== ", v)
            print ("\n key ", nl, "dfielddict == ", dfielddict)
            continue 

        print ("number of pairs in request.POST ===", nl, "\n ", dfielddict['0'],"\n",dfielddict['1'],"\n",dfielddict['2'])
        indexfl=[]
        if len(dicfiles) == 0:
            response = HttpResponse('No file has been uploaded',status=422,reason='Unprocessable Entity',content_type='text/plain')
            return response
        for key,val in dicfiles.items():
            if form.search(key):
                indexf=int(key.split("-")[1])
                nkey="-".join(key.split("-")[2:])  
                if indexf not in indexfl:
                    indexfl.append(indexf)
                    dictfmol[indexf]={}
                #dictmol[index]["-".join(key.split("-")[2:])]=val
            else: # the keys does not have to be modifyied as a single simulation has been submitted in the html form
                if len(indexfl)==0:
                    indexf=0
                    indexfl.append(0)
                    dictfmol[0]={}
                nkey=key
            dictfmol[indexf][nkey]=val
        print("INDEXFL", indexfl)
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
            indexfli=list(map(int,indexfl))
            indexli=list(map(int,indexl))
            indexfl=sorted(indexfli)
            indexl=sorted(indexli)
        print(indexfl, indexl)
        dicfmole={}
        fdbF={}
        fdbFobj={}
        fdbFM={}
        fdbSM={}
        fdbFMobj={}

        for ii in indexl:
            fdbCF[ii]={}
            fdbCFobj[ii]={}
            fdbMF[ii]={}
            fdbSM[ii]={}
            fdbMFobj[ii]={}
            fdbON[ii]={}
            fdbONobj[ii]={}
            dON[ii]={}
             
            #### Check if the molecule is already in our Database. If so the standar molecule shoud be as well!!!!!

            qMF=DyndbMolecule.objects.filter(inchikey=dicfmole[ii]['inchikey']).filter(inchi=dicfmole[ii]['inchi'])
            qCFStdFormExist=DyndbCompound.objects.filter(sinchikey=dictcomp[ii]['sinchikey']).filter(sinchi=dictcomp[ii]['sinchi']) #if std form of the molecule is in the database compound. It is possible that other forms of the molecule are in DyndbMolecule and the std form would be in DyndbCompound

            if len(qMF.values())==1: #there is a entry matching this molecule

                if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
                    dictPMod[ii]['not_in_model']=False
                else:
                    dictPMod[ii]['not_in_model']=True

                dictPMod[ii]['int_id']=ii
                dictPMod[ii]['submission_id']=submission_id
                MFpk=qMF.values_list('pk',flat=True)[0]
                dictPMod[ii]['molecule_id']=MFpk
                fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])

                if fdbSM[ii].is_valid(): # only the submission molecule table should be filled!!!!
                    fdbSM[ii].save()
                else:    
                    iii1=fdbSM[ii].errors.as_data()
                    print("fdbSM",ii," no es valido")
                    print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")

                if ii==indexl[-1]:#if ii is the last element of the list indexl
                    print("Molecule #", ii, "has been found in our database")
                    break
                else:
                    print("Molecule #", ii, "has been found in our database")
                    continue

            elif len(qMF.values())>1:
                response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain')
                return response
                
#### check if the molecule is actually the standard form of the molecule. If this specific form of the molecule is not in the database (DyndbMolecule) but other molecules corresponding the same compound are, the one we are dealing with won`t be the standard as it is previously recorded when the first molecule corresponding the compound was registered. So, if there is no any entry in the DyndbCompound table matching the sinchikey of the molecule in the form, still will be possible that the current entry would be the standard form.
            if len(qCFStdFormExist.values())==1: #The compound and the standard form of the current molecule is in the database (Only fill the current non standard molecule)
                print("Compound entry matching SInChIKey and SInChI has been found in GPCRmd database")
            elif len(qCFStdFormExist.values())>1: #the compound is found more than once in the database
                response("Several Compound entries have been found in the DATABASE. Please, report this ERROR to the GPCRmd database administrator")
                return response
            elif len(qCFStdFormExist.values())==0: #Neither the compound nor the standard form of the molecule are in the database
           
         #### No compound entry has been found in GPCRmd DB.Keep track of the Compound in the DyndbCompound table and the aliases in the DyndbOtherCompoundNames
           
                #### DyndbCompound

                for key,val in initCF.items():
                    if key not in dictcomp[ii].keys():
                        dictcomp[ii][key]=val
                fdbCF[ii]=dyndb_CompoundForm(dictcomp[ii]) 
                if fdbCF[ii].is_valid():
                    fdbCFobj[ii]=fdbCF[ii].save()
                    CFpk=fdbCFobj[ii].pk
                else:
                    print("Errores en el form dyndb_CompoundForm\n ", fdbCF[ii].errors.as_data())
           
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
                        print("Errores en el form dyndb_Other_Compound_Names\n ", fdbON[ii][on].errors.as_data())
   #### Get the standard Molecule by providing the SInChIKey to the PubChem or CHEMBL databases if the molecule is actually the standard form of the molecule.

#### DyndbCompound and DyndbOtherCompoundNames tables have been filled. Then entries for the std molecule should be registered in DyndbMolecule and DyndbSubmissionMolecule
            
                INFOstdMOL =SCRIPT_ISMA(sinchikey) #genera datos del post a partir de la sinchikey. Se obtienen los datos de la standar molecule
     #### Check if inchi of the standard molecule matches the inchi in the current entry (HTML form)         
                
                if INFOstdMOL['inchi']==dictmol[ii]['inchi']: #Both molecules are the standard molecule so one entry is saved
                    print("The molecule ",ii, "is actually the standard molecule")
                else:
                    print("The molecule ",ii, "is not the standard molecule. The standard one will be saved right now!!!!")
                    auxdictmol={}
                    for key,val in INFOstdMOL.items():# HAY QUE INTRODUCIR LOS DATOS DEL SCRIPT PARA PODER CREAR UN DICCIONARIO PARA LA INSTANCIA!!!
                        if key in dfieldtype[0]:
                            auxdictmol[key]=val  ###dictionary for the entry corresponding to the standard molecule in the table DyndbMolecule  
      
                    for key,val in initMF.items():
                        if key not in auxdictmol.keys():
                            auxdictmol[key]=val  ##### completion of the dictionary
                    auxdictmol['id_compound']=CFpk
                    fdbMFaux=dyndb_Molecule(auxdictmol)
                    if fdbMFaux.is_valid():
                        fdbMFobj=fdbMFaux.save()
                        MFauxpk=fdbMFobj.pk
                    else:
                        print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_data())
      
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
                        iii1=fdbSMaux[ii].errors.as_data()
                        print("fdbSMaux",ii," no es valido")
                        print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")

           #### the foreign key 'std_id_molecule ' in the DyndbCompound pointing to DyndbMolecule table is properly updated with info from the standard molecule table

                    for key,val in initMF.items():
                        if key not in dictmol[ii].keys():
                            dictmol[ii][key]=val
                    dictmol[ii]['id_compound']=CFpk
                    fdbMF[ii]=dyndb_Molecule(dictmol[ii])
                    if fdbMF[ii].is_valid():
                        fdbMFobj[ii]=fdbMF[ii].save()
                        MFpk=fdbMFobj[ii].pk
                    else:
                        print("Errores en el form dyndb_Molecule\n ", fdbMF[ii].errors.as_data())
                
                    if 'is_present' in dictPMod[ii]: # is_present = NOT (Not_in_Model)!!!!! table dyndb_submission_molecule!!!!
                        dictPMod[ii]['not_in_model']=False
                    else:
                        dictPMod[ii]['not_in_model']=True
                    dictPMod[ii]['int_id']=ii
                    dictPMod[ii]['submission_id']=submission_id
                    dictPMod[ii]['molecule_id']=MFpk
                    fdbSM[ii]=dyndb_Submission_Molecule(dictPMod[ii])
                    if fdbSM[ii].is_valid():
                        fdbSM[ii].save()
                    else:    
                        iii1=fdbSM[ii].errors.as_data()
                        print("fdbSM",ii," no es valido")
                        print("!!!!!!Errores despues del fdbSM[",ii,"]\n",iii1,"\n")

                if INFOstdMOL['inchi']==dictmol[ii]['inchi']: #Both molecules are the standard molecule so one entry is saved 
                    fdbCFobj[ii]['std_id_molecule']=MFpk
                else:
                    fdbCFobj[ii]['std_id_molecule']=MFauxpk
                fdbCFobj[ii].save()

            if len(qMF.values())==1:
                print("Your molecule is already present in our database")               
            elif len(qMF.values())>1:
                response = HttpResponse("More than one entries with the same inchikey and the same inchi have been found in our Database. Please, report this ERROR to the GPCRmd administrator",content_type='text/plain')
                return response
            elif len(qMF.values())==0:
                direct='/protwis/sites/files/Molecule/mol'+str(submission_id)
                print("\nDirectorio a crear ", direct)
                if not os.path.exists(direct):
                    os.makedirs(direct)
             
                fdbF[ii]={}
                fdbFobj[ii]={}
                for key,val in dictfmol[ii].items():
                    fext="".join(val.name.split(".")[1:])
                    print("val ",val, " ;val split",fext," Tambien id", dict_ext_id[fext])
                    #print("val ",val, " ;val split",fext," Tambien id")
                    if fext in dict_ext_id.keys():
                        initFiles['id_file_types']=dict_ext_id[fext]
                        initFiles['filename']=val.name
                        initFiles['filepath']=direct
                        initFiles['description']="sdf/mol2 requested in the molecule form"
             
                        fdbF[ii][key]=dyndb_Files(initFiles) #CAmbiar a submissionID Segun las reglas de ISMA
                        dicfmole[ii]={}
                        fdbFM[ii]={}
                        if fdbF[ii][key].is_valid():
                            fdbFobj[ii][key]=fdbF[ii][key].save()
                            newname=str(fdbFobj[ii][key].pk)+"_mol_"+str(submission_id)+"."+fext
                            handle_uploaded_file(dictfmol[ii][key],direct,newname)
                            completepath=direct+"/"+newname
                            fdbFobj[ii][key].filename=newname   #rename filename in the database after saving the initial name
                            fdbFobj[ii][key].filepath=completepath   #rename filename in the database after saving the initial name
                            fdbFobj[ii][key].save() 
                            dicfmole[ii]['type']=d_fmolec_t['Molecule'] #Molecule
                            dicfmole[ii]['id_molecule']=MFpk
                            dicfmole[ii]['id_files']=fdbFobj[ii][key].pk
                            fdbFM[ii][key]=dyndb_Files_Molecule(dicfmole[ii])
                            if fdbFM[ii][key].is_valid():
                                fdbFM[ii][key].save()
                            else:
                                print("Errores en el form dyndb_Files_Molecule\n ", fdbFM[ii][key].errors.as_data())
                        else:
                            print("Errores en el form dyndb_Files\n ", fdbF[ii][key].errors.as_data())
                    else:
                        print("This extension is not valid for submission")

        return HttpResponseRedirect("/".join(["/dynadb/MOLECULEfilled",submission_id,""]), {'submission_id':submission_id })
                        
                       

        # check whether it's valid:
    else:

        fdbMF = dyndb_Molecule()
        fdbCF=dyndb_CompoundForm()
        fdbON=dyndb_Other_Compound_Names()
        fdbF = dyndb_Files()
        fdbFM = dyndb_Files_Molecule()
        fdbMM = dyndb_Complex_Molecule_Molecule()

        return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbCF':fdbCF,'fdbON':fdbON, 'fdbF':fdbF, 'fdbFM':fdbFM, 'fdbMM':fdbMM, 'submission_id' : submission_id})

def DYNAMICSview(request, submission_id):

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
        action="/dynadb/DYNAMICSfilled/"
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted
        qM=DyndbSubmissionModel.objects.filter(submission_id=submission_id)
        model_id=qM.values('model_id')[0]
        initDyn={'id_model':model_id,'id_compound':'1','update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
        initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':submission_id }
        ### RETRIEVING FILE_TYPES from the DyndbFileTypes table. dict_ext_id is a dyctionary containing the key:value extension:id
        ft=DyndbFileTypes.objects.all()
        dict_ext_id={}
        for l in ft:
            dict_ext_id[l.__dict__['extension'].rstrip()]=l.__dict__['id']

        with open('/protwis/sites/protwis/dynadb/dict_ext_id.txt', 'wb') as handle:
            pickle.dump(dict_ext_id, handle)
          
        # Defining a dictionary "d_fdyn_t" containing choices in the table dyndb_files_dynamics (field 'type')

        d_fdyn_t={'coor':'0','top':'1','traj':'2','parm':'3','other':'3'}

        dicpost=request.POST
        dicfiles=request.FILES
        print(dicfiles)
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
        with open('/protwis/sites/protwis/dynadb/POSTimod.txt', 'wb') as handle:
            pickle.dump(POSTimod, handle)
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
            with open('/protwis/sites/protwis/dynadb/Pscompmod.txt', 'wb') as handle:
                pickle.dump(Pscompmod, handle)
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
                    
        with open('/protwis/sites/protwis/dynadb/POSTimod.txt', 'wb') as handle:
            pickle.dump(POSTimod, handle)

        with open('/protwis/sites/protwis/dynadb/Pscompmod.txt', 'wb') as handle:
            pickle.dump(Pscompmod, handle)

    else:
        dd=dyndb_Dynamics()
        ddC=dyndb_Dynamics_Components()

        return render(request,'dynadb/DYNAMICS.html', {'dd':dd,'ddC':ddC, 'submission_id' : submission_id})
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

def DYNAMICSviewOLD(request):
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        action="/dynadb/DYNAMICSfilled/"
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted
        initDD={'id_model':'1','id_compound':'1','update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
        dd=dyndb_Dynamics(request.POST)
                


        with open('/protwis/sites/protwis/dynadb/DYNpost.txt', 'wb') as handle:
            pickle.dump(request.POST, handle)

        for key,value in initDD.items():
            dd.data[key]=value

        print("\npath", os.getcwd())
        ##for key,value in data.items():
        ##    f.write(str(key,value))
        ff=open('/protwis/sites/protwis/dynadb/filePOST.txt','w')
#        ff.write(data)
        print("created by dbengine antes de validar", dd.data['created_by_dbengine'])

        if dd.is_valid():
            # process the data in form.cleaned_data as required
            ddi=dd.save(commit=False)
            with open('/protwis/sites/protwis/dynadb/DYNdd.txt', 'wb') as handle:
                pickle.dump(ddi, handle)

            dd.save()
            with open('/protwis/sites/protwis/dynadb/DYNddi.txt', 'wb') as handle:
                pickle.dump(ddi, handle)
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


def SUBMITTEDview(request,submission_id): 
        return render(request,'dynadb/SUBMITTED.html',{'submission_id':submission_id})

def get_Author_Information(request): 
        return render(request,'dynadb/dynadb_Author_Information.html'  )


def db_inputformMAIN(request,submission_id): 
    if submission_id is None:
        dictsubid={}
        dictsubid['user_id']='1'
        fdbsub=dyndb_Submission(dictsubid)
        fdbsubobj=fdbsub.save()
        submission_id = fdbsubobj.pk
    return render(request,'dynadb/dynadb_inputformMAIN.html', {'submission_id':submission_id} )


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

AlertCountFormset = modelformset_factory(StructureModelLoopTemplates,form = AlertForm)
NotifierFormset = modelformset_factory(StructureType, form = NotifierForm)

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


def sub_sim(request):
    return render(request, 'dynadb/sub_sim_form.html')



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


def check_compound_entry_exist(pubchem_cid, chembleid, sinchikey, inchikey):
    qdcompound=DyndbCompound.objects.filter(pubchem_cid=uniprotkbac).filter(chembleid=chembleid)
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
            browse_protein_response={'Message':"ERROR: There is one or more wild type proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkw)+"\nIn addition if there are more than one pk several entries exists for the same isoform and UniProtKB AC which is redundat... fix this if it occurs",'id_protein':[]}
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














def check_protein_entry_exist(uniprotkbac, isoform, is_mutated, sequence):
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
            browse_protein_response={'Message':"ERROR: There is one or more wild type proteins in DyndbProtein matching the UniProtKB AC and the isoform number of the one is being processed but there is not any sequence for them in DyndbProteinSequence...  This should be checked and fixed. The pk of these proteins in DyndbProtein is "+str(lpkw)+"\nIn addition if there are more than one pk several entries exists for the same isoform and UniProtKB AC which is redundat... fix this if it occurs",'id_protein':[]}
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
            response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain')
            return response
          if data['Entry'] != uniprotkbac_noiso and isoform is not None:
            response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain')
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
              response = HttpResponseNotFound('No data found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain')
            else:
              response = HttpResponse('Problem downloading from UniProtKB:\nStatus: '+str(errdata['status_code']) \
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'StreamSizeLimitError' or errdata['ErrorType'] == 'StreamTimeoutError' \
            or errdata['ErrorType'] == 'ParsingError':
            response = HttpResponse('Problem downloading from UniProtKB:'\
                +'\n'+errdata['reason'],status=502,content_type='text/plain')
          elif errdata['ErrorType'] == 'Internal':
            response = HttpResponse('Unknown internal error.',status=500,content_type='text/plain')
          else:
            response = HttpResponse('Cannot connect to UniProt server:\n'+errdata['reason'],status=504,content_type='text/plain')
            
        else:
          datakeys = set([i.lower() for i in data.keys()])
          if datakeys == KEYS:
            response = data 
          else:
            response = HttpResponse('Invalid response from UniProtKB.',status=502,content_type='text/plain')
        
        
        
      else:
        response = HttpResponse('Invalid UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain')
    else:
      response = HttpResponse('Missing UniProtKB accession number.',status=422,reason='Unprocessable Entity',content_type='text/plain')
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
    #       response = HttpResponseNotFound('No entries found for UniProtKB accession number "'+uniprotkbac+'".',content_type='text/plain')
    #       print(response)
    #   if data['Entry'] != uniprotkbac_noiso and isoform is not None:
    #       response = HttpResponse('UniProtKB secondary accession numbers with isoform ID are not supported.',status=410,content_type='text/plain')
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
        browse_protein_response=check_protein_entry_exist(dictprot[ii]['uniprotkbac'],dictprot[ii]['isoform'],is_mutated_val,dictprot[ii]['sequence'])#### POR AQUI!!!!!!!!!!!!!! 
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
                response = HttpResponse(browse_protein_response['Message'],content_type='text/plain')
                return response

# If the protein ii is not found in our database create a new entry

        print("valor ii=", ii, "dictprot[ii]=\n", dictprot[ii])
        initPF['id_uniprot_species']=dictprot[ii]['id_species']
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
                response = HttpResponse('Mutated sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
                return response
            if seq is None:
                response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
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
                response = HttpResponse('Wild Type sequence has not been provided',status=422,reason='Unprocessable Entity',content_type='text/plain')
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
                initPF['id_uniprot_species']=dictprot[ii]['id_species']
            
                for key,value in initPF.items():
                    auxdictprot[ii][key]=value
            
                fdbPFaux[ii]=dyndb_ProteinForm(auxdictprot[ii])
            
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

