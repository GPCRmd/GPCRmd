from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.template import loader
from django.forms import formset_factory, ModelForm, modelformset_factory
#from .models import Question,Formup
#from .forms import PostForm
from .models import DyndbModel, StructureType, WebResource, StructureModelLoopTemplates
#from .forms import DyndbModelForm
#from django.views.generic.edit import FormView
from .forms import NameForm, dyndb_ProteinForm, dyndb_Model, dyndb_Files, AlertForm, NotifierForm,  dyndb_Protein_SequenceForm, dyndb_Other_Protein_NamesForm, dyndb_Cannonical_ProteinsForm, dyndb_Protein_MutationsForm, dyndb_CompoundForm, dyndb_Other_Compound_Names, dyndb_Molecule, dyndb_Files, dyndb_Files_Types, dyndb_Files_Molecule, dyndb_Complex_Exp, dyndb_Complex_Protein, dyndb_Complex_Molecule, dyndb_Complex_Molecule_Molecule,  dyndb_Files_Model, dyndb_Files_Model, dyndb_Dynamics, dyndb_Dynamics_tags, dyndb_Dynamics_Tags_List, dyndb_Files_Dynamics, dyndb_Related_Dynamics, dyndb_Related_Dynamics_Dynamics, dyndb_Model, dyndb_Modeled_Residues,  Pdyndb_Dynamics, Pdyndb_Dynamics_tags, Pdyndb_Dynamics_Tags_List, Formup
#from .forms import NameForm, TableForm

# Create your views here.

def PROTEINview(request):
    if request.method == 'POST':
        author="jmr"
        action="/dynadb/PROTEINFILLED/"
        fdbPF = dyndb_ProteinForm(request.POST)
        fdbPS = dyndb_Protein_SequenceForm(request.POST)
        fdbPM = dyndb_Protein_MutationsForm(request.POST)
        initial={'update_timestamp':timezone.now() , 'creation_timestamp':timezone.now() ,'created_by_dbengine':author, 'last_update_by_dbengine':timezone.now() , 'created_by':author, 'last_update_by':'jmr', 'submission_id':'1' }
        # check whether it's valid:
        if fdbPF.is_valid() and fdbPF.is_valid() and fdbPF.is_valid(): 
            # process the data in form.cleaned_data as required

          #  formPF=fdbPF.save(commit=False)
          #  formPS=fdbPS.save(commit=False)
          #  formPM=fdbPM.save(commit=False)
            formPF=fdbPF.save(commit=True)
            formPS=fdbPS.save(commit=True)
            formPM=fdbPM.save(commit=True)

    #        form.user=request.user
    #        form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/PROTEINfilled/')

    # if a GET (or any other method) we'll create a blank form
    else:

        fdbPF = dyndb_ProteinForm()
        fdbPS = dyndb_Protein_SequenceForm()
        fdbPM = dyndb_Protein_MutationsForm()
        return render(request,'dynadb/PROTEIN.html', {'fdbPF':fdbPF,'fdbPS':fdbPS,'fdbPM':fdbPM })

def MODELview(request):
    if request.method == 'POST':
        fdbMF = dyndb_Model(request.POST)
        fdbMR = dyndb_Modeled_Residues(request.POST)

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
    if request.method == 'POST':
        dd=dyndb_CompoundForm(request.POST)
        ddC= dyndb_Other_Compound_Names(request.POST)
        ddT= dyndb_Dynamics_tags(request.POST)
        ddTL=dyndb_Dynamics_Tags_List(request.POST)

        # check whether it's valid:
        if dd.is_valid() and ddC.is_valid() and ddT.is_valid() and ddTL.is_valid(): 
            # process the data in form.cleaned_data as required

            dd=dd.save(commit=False)
            ddC=ddC.save(commit=False)
            ddT=ddT.save(commit=False)

            form.user=request.user
            form.save()
            # redirect to a new URL:
            return HttpResponseRedirect('/dynadb/DYNAMICS/')

    # if a GET (or any other method) we'll create a blank form
    else:
        dd=dyndb_CompoundForm()
        ddC= dyndb_Other_Compound_Names()
        ddT= dyndb_Dynamics_tags()
        ddTL=dyndb_Dynamics_Tags_List()


        return render(request,'dynadb/DYNAMICS.html', {'dd':dd,'ddC':ddC,'ddT':ddT, 'ddTL':ddTL})


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
