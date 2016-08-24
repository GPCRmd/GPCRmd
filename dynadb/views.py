# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse, StreamingHttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.template import loader
from django.forms import formset_factory, ModelForm, modelformset_factory
import re, os, pickle
import time
import json
import requests
from django.db.models.functions import Concat
from django.db.models import CharField,TextField, Case, When, Value as V
from .uniprotkb_utils import valid_uniprotkbac, retreive_data_uniprot, retreive_protein_names_uniprot, get_other_names, retreive_fasta_seq_uniprot, retreive_isoform_data_uniprot
from .csv_in_memory_writer import CsvDictWriterNoFile, CsvDictWriterRowQuerySetIterator
#from .models import Question,Formup
#from .forms import PostForm
from .models import DyndbModel, StructureType, WebResource, StructureModelLoopTemplates, DyndbProtein, DyndbUniprotSpecies, DyndbUniprotSpeciesAliases
#from .forms import DyndbModelForm
#from django.views.generic.edit import FormView
from .forms import NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_Files_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model, dyndb_Modeled_Residues,  Pdyndb_Dynamics, Pdyndb_Dynamics_tags, Pdyndb_Dynamics_Tags_List, Formup, dyndb_ReferenceForm, dyndb_Dynamics_Membrane_Types, dyndb_Dynamics_Components, DyndbFileTypes
#from .forms import NameForm, TableForm

# Create your views here.




def REFERENCEview(request):
    if request.method == 'POST':
        action="/dynadb/REFERENCEfilled/"
        now=timezone.now()
        author="jmr"
#        forminfo={'issue':'1','url':'http://localhost:8000/ttt/prueba','doi':'8382938','title':'prinncii','journal_press':'marca','pub_year':'1996', 'volume':'agosto', 'pages':'2-3','authors':'pepe; luis', 'pmid':'4'}
        initREFF={'dbname':None,'update_timestamp':now,'creation_timestamp':now,'created_by_dbengine':author, 'last_update_by_dbengine':author, 'created_by':None }
        fdbREFF = dyndb_ReferenceForm(request.POST)
        with open('/protwis/sites/protwis/dynadb/REFpost.txt', 'wb') as handle:
            pickle.dump(request.POST, handle)

#       with open('/protwis/sites/protwis/dynadb/REFpost.txt', 'rb') as handle:
#           b = pickle.loads(handle.read())


#        f=open('/protwis/sites/protwis/dynadb/REFpost.txt','w') 
#        f.write(request.POST)
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
            

            return HttpResponseRedirect('/dynadb/REFERENCEfilled/')

        else:
           # for field in fdbPF:
            iii=fdbREFF.errors.as_data()
            print("Errors", iii)
            
            pass
        
    # if a GET (or any other method) we'll create a blank form
    else:

        fdbREFF = dyndb_ReferenceForm()
        return render(request,'dynadb/REFERENCES.html', {'fdbREFF':fdbREFF})


def PROTEINview(request):
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        action="/dynadb/PROTEINfilled/"
        now=timezone.now()
#####  inintPF dictionary containing fields of the form dynadb_ProteinForm not
#####  available in the request.POST
#####
#####  initOPN dictionary dyndb_Other_Protein_NamesForm. To be updated in the
#####  view. Not depending on is_mutated field in dynadb_ProteinForm 
        initPF={'id_uniprot_species':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initOPN={'id_protein':'1','other_names':'Lulu' } #other_names should be updated from UniProtKB Script Isma


#####  instantiate fdbPF and fdbOPN (this one is not affected by the is_mutated field in dynadb_ProteinForm)
        fdbPF = dyndb_ProteinForm(request.POST)
        fdbOPN= dyndb_Other_Protein_NamesForm(initOPN)
        initPM={'id_protein':'1','id_resid':'90','id_resletter_from':'D','id_resletter_to':'E' }

#####  Fill dyndb_Protein_SequenceForm fields depending on whether the protein is mutated   
#####  'msequence' does not appear in models but it does in the html so the information in 
#####  this html field should be tranfered into the 'sequence' field in the form instance      

        if 'is_mutated' in fdbPF.data: 
            mseq=request.POST['msequence']
            lmseq=len(mseq)
            initPS={'id_protein':None,'sequence':mseq,'length':lmseq} 
            #id_protein will be eventually taken from the pk value in the dyndb_Protein table entry
        else:
 #           print("Valor de is_mutated",fdbPF.data['is_mutated'])
            seq="HOLA COLEGA"  ########## esta parte debe ser cambiada por Isma para leer la secuencia
            lseq=len(seq)
            initPS={'id_protein':None,'sequence':seq,'length':lseq} 
            #id_protein will be eventually taken from the pk value in the dyndb_Protein table entry

#####  Fill the empty fields in the fdbPF instance with data from the initPF dictionary

        for key,value in initPF.items():
            fdbPF.data[key]=value
            
#####   Intance of the forms depending on the is_mutated value in dyndb_ProteinForm

        fdbPS = dyndb_Protein_SequenceForm(initPS)
       #fdbPM = dyndb_Protein_MutationsForm(request.POST,initial=initPM)

#        print("\nQue hay en el POST:", request.POST['msequence'])
#        iii2=fdbPF.errors.as_data()

##### Check whether the fdbPF instance of dyndb_ProteinForm is valid:
        if fdbPF.is_valid(): 
            # process the data in form.cleaned_data as required
            formPF=fdbPF.save(commit=False)
            formPFi=fdbPF.save()
            print("\n primary  key: ", formPFi.pk )

##### Once fdbPF has been saved process fields with primary keys involving the dyndb_protein table
            initPS['id_protein']=formPFi.pk
            initOPN['id_protein']=formPFi.pk
            
          # for key,value in initPS.items():
          #     fdbPS.data[key]=value
          # for key,value in initOPN.items():
          #     fdbOPN.data[key]=value

            fdbPS.data['id_protein']=formPFi.pk
            fdbOPN.data['id_protein']=formPFi.pk
            print("\n datos desde el diccionario initPS", fdbPS.data.values())
            print("\n datos desde el diccionario initOPN", fdbOPN.data.values())
            
#           formPM=fdbPM.save(commit=False)
          #  formPF=fdbPF.save(commit=True)
          #  formPS=fdbPS.save(commit=True)
          #  formPM=fdbPM.save(commit=True)
#            formPS.user=request.user
            if fdbPS.is_valid() and fdbOPN.is_valid():
                formPS=fdbPS.save(commit=False)
                formOPN=fdbOPN.save(commit=False) 
                formPS=fdbPS.save()
                formOPN=fdbOPN.save() 
                print ("hasta aqui")
            else:
                iii1=fdbPS.errors.as_data()
                iii2=fdbOPN.errors.as_data()
                print("fdbPS no es valido")
                print("!!!!!!Errores despues del fdbPS\n",iii1,"\n")
                print("!!!!!!Errores despues del fdbOPN\n",iii2,"\n")
            # redirect to a new URL:

            return HttpResponseRedirect('/dynadb/PROTEINfilled/')

        else:
           # for field in fdbPF:
            iii=fdbPF.errors.as_data()
            print(iii)
            
            
#           for field in fdbPF:
#               field.clean()
#               print (field, field.clean())

            pass
            #return HttpResponseRedirect('/dynadb/PROTEINerror/')    
        
    # if a GET (or any other method) we'll create a blank form
    else:

        fdbPF = dyndb_ProteinForm()
        fdbPS = dyndb_Protein_SequenceForm()
#       fdbPM = dyndb_Protein_MutationsForm()
        fdbOPN= dyndb_Other_Protein_NamesForm()
#        return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS,'fdbPM':fdbPM,'fdbOPN':fdbOPN})
        return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS, 'fdbOPN':fdbOPN})

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

  
  
  

def MODELview(request):
    if request.method == 'POST':


        fdbMF = dyndb_Model(request.POST)
        fdbMR = dyndb_Modeled_Residues(request.POST)
        fdbON = dyndb_
        # check whether it's valid:
        if fdbMF.is_valid() and fdbMR.is_valid(): 
            # process the data in form.cleaned_data as required

            formMF=fdbPF.save(commit=False)
            formMR=fdbMR.save(commit=False)

            form.user=request.user
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/PROTEIN/')

    # if a GET (or any other method) we'll create a blank form
    else:

        fdbMF = dyndb_Model()
        fdbMR = dyndb_Modeled_Residues()
        return render(request,'dynadb/MODEL.html', {'fdbMF':fdbMF,'fdbMR':fdbMR})


def SMALL_MOLECULEview2(request):
    if request.method == 'POST':
        author="jmr"   #to be modified with author information. To initPF dict
        action="/dynadb/PROTEINfilled/"
        now=timezone.now()
        onames="Pepito; Juanito; Herculito" #to be modified... scripted

        initMF={'id_compound':None,'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initCF={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author  }
        initON={'other_names': onames,'id_compound':None} 

        fdbrMF=dyndb_CompoundForm(request.POST)
        for key,value in initCF.items():
            initCF.data[key]=value


        fdbMF=dyndb_CompoundForm(request.POST)
        fdbCN= dyndb_Other_Compound_Names(request.POST)
        fdbMF = dyndb_Molecule(request.POST)
        fdbMfl = dyndb_Files_Molecule(request.POST)
        fdbMM = dyndb_Complex_Molecule_Molecule(request.POST)

        # check whether it's valid:
        if fdbMF.is_valid() and fdbMfl.is_valid() and fdbMM.is_valid() and fdbCF.is_valid() and fdbCN.is_valid(): 
            # process the data in form.cleaned_data as required

            formMF=fdbMF.save(commit=False)
            formMfl=fdbMfl.save(commit=False)
            formMM=fdbMM.save(commit=False)

            form.user=request.user
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/PROTEIN/')

    # if a GET (or any other method) we'll create a blank form
    else:

        fdbMF = dyndb_Molecule()
        fdbMfl = dyndb_Files_Molecule()
        fdbMM = dyndb_Complex_Molecule_Molecule()
        fdbCF=dyndb_CompoundForm()
        fdbCN=dyndb_Other_Compound_Names()

        return render(request,'dynadb/SMALL_MOLECULE2.html', {'fdbMF':fdbMF,'fdbMfl':fdbMfl,'fdbMM':fdbMM, 'fdbCF':fdbCF, 'fdbCN':fdbCN })

def SMALL_MOLECULEview(request):
    if request.method == 'POST':
        fdbCF=dyndb_CompoundForm(request.POST)
        fdbCN= dyndb_Other_Compound_Names(request.POST)
        fdbMF = dyndb_Molecule(request.POST)
        fdbMfl = dyndb_Files_Molecule(request.POST)
        fdbMM = dyndb_Complex_Molecule_Molecule(request.POST)

        # check whether it's valid:
        if fdbMF.is_valid() and fdbMfl.is_valid() and fdbMM.is_valid() and fdbCF.is_valid() and fdbCN.is_valid(): 
            # process the data in form.cleaned_data as required

            formMF=fdbMF.save(commit=False)
            formMfl=fdbMfl.save(commit=False)
            formMM=fdbMM.save(commit=False)

            form.user=request.user
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/PROTEIN/')

    # if a GET (or any other method) we'll create a blank form
    else:

        fdbMF = dyndb_Molecule()
        fdbMfl = dyndb_Files_Molecule()
        fdbMM = dyndb_Complex_Molecule_Molecule()
        fdbCF=dyndb_CompoundForm()
        fdbCN=dyndb_Other_Compound_Names()

        return render(request,'dynadb/SMALL_MOLECULE.html', {'fdbMF':fdbMF,'fdbMfl':fdbMfl,'fdbMM':fdbMM, 'fdbCF':fdbCF, 'fdbCN':fdbCN })

def DYNAMICSview(request):
    # Function for saving files
    def handle_uploaded_file(f,p):
        print("file name = ", f.name , "path =", p)
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
        initDyn={'id_model':'1','id_compound':'1','update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
        initFiles={'update_timestamp':timezone.now(),'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':author,'submission_id':None }
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
                FILEmod[indexf]["-".join(key.split("-")[2:])]=val
            else:
                if len(indexfl)==0:
                    indexfl.append(0)
                    print("indexf=0")
                    FILEmod[0]={}
                print("key en dicfiles ", key, val)
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
            direct='/protwis/sites/files/Dynamics/dyn'+str(dyn_obj[ii].pk)
            print("\nDirectorio a crear ", direct)
            if not os.path.exists(direct):
                os.makedirs(direct)
      
            print("Dynamica ",ii," print FILEmod[ii] ",FILEmod[ii].items())
            for key,val in FILEmod[ii].items():
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
                handle_uploaded_file(FILEmod[ii][key],direct)
                if file_ins[ii][key].is_valid(): 
                    dicfyndyn={}
                    file_obj[ii][key]=file_ins[ii][key].save(commit=False)
                    file_obj[ii][key]=file_ins[ii][key].save()
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
 
        return HttpResponseRedirect('/dynadb/DYNAMICSfilled/')
                    
        with open('/protwis/sites/protwis/dynadb/POSTimod.txt', 'wb') as handle:
            pickle.dump(POSTimod, handle)

        with open('/protwis/sites/protwis/dynadb/Pscompmod.txt', 'wb') as handle:
            pickle.dump(Pscompmod, handle)

    else:
        dd=dyndb_Dynamics()
        ddC=dyndb_Dynamics_Components()

        return render(request,'dynadb/DYNAMICS.html', {'dd':dd,'ddC':ddC})
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


def SUBMITTEDview(request): 
        return render(request,'dynadb/SUBMITTED.html'  )

def get_Author_Information(request): 
        return render(request,'dynadb/dynadb_Author_Information.html'  )


def db_inputformMAIN(request): 
        return render(request,'dynadb/dynadb_inputformMAIN.html'  )


def get_FilesCOMPLETE(request): 
    # MEZCLA DE TABLAS PARA HACER 
    if request.method == 'POST':
        fdb_Files1 = dyndb_Files(request.POST)
        fdb_Files2 = dyndb_Files_Dynamics(request.POST)
        fdb_Files3 = dyndb_Files_Types(request.POST)
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
        fdb_Files3 = dyndb_Files_Types()
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




def get_Prueba(request):
    if request.method == 'POST':
        fdb_Dynamics = Pdyndb_Dynamics(request.POST)
        fdb_Dynamics_tags = Pdyndb_Dynamics_tags(request.POST)
        fdb_Dynamics_Tags_List = Pdyndb_Dynamics_Tags_List(request.POST)
        # check whether it's valid:
        if fdb_Dynamics.is_valid() and fdb_Dynamics_tags.is_valid() and fdb_Dynamics_Tags_List.is_valid(): 

            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/TF/')

    # if a GET (or any other method) we'll create a blank form
    else:

        fdb_Dynamics=Pdyndb_Dynamics()
        fdb_Dynamics_tags=Pdyndb_Dynamics_tags()
        fdb_Dynamics_Tags_List=Pdyndb_Dynamics_Tags_List()

        return render(request,'dynadb/pruebaDYNAname.html', {'fdb_Dynamics':fdb_Dynamics, 'fdb_Dynamics_tags':fdb_Dynamics_tags, 'fdb_Dynamics_Tags_List':fdb_Dynamics_Tags_List} )



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
