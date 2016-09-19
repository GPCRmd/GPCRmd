from dynadb.models import DyndbComplexCompound, DyndbFiles, DyndbFileTypes, DyndbModel, DyndbModeledResidues, DyndbProtein, DyndbOtherProteinNames, DyndbProteinSequence, DyndbCannonicalProteins, DyndbProteinMutations, DyndbCompound, DyndbOtherCompoundNames, DyndbMolecule, DyndbFiles, DyndbFilesMolecule, DyndbComplexExp, DyndbComplexProtein, DyndbComplexMolecule, DyndbComplexMoleculeMolecule, DyndbModelComponents, DyndbDynamicsComponents, DyndbFilesModel, DyndbDynamics,DyndbDynamicsComponents, DyndbDynamicsTags, DyndbDynamicsTagsList, DyndbFilesDynamics, DyndbRelatedDynamics, DyndbRelatedDynamicsDynamics, WebResource, StructureType, StructureModelLoopTemplates, DyndbReferences, DyndbDynamicsMembraneTypes, DyndbSubmission, DyndbSubmissionModel, DyndbSubmissionProtein, DyndbSubmissionMolecule
from django import forms
from django.forms import ModelForm, formset_factory, modelformset_factory, Textarea


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
#class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
#    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
#    cc_myself = forms.BooleanField(required=False)

class FormsetForm(forms.Form):
    delete= forms.BooleanField(required=False, initial=False)

#################################

class dyndb_ProteinForm(ModelForm):
#    is_mutated=forms.BooleanField(required=False,initial=False)

    class Meta:
        model = DyndbProtein
#        exclude=['is_mutated']
        fields = '__all__'
#        widgets = {
#            'is_mutated': forms.CheckboxInput(attrs={'required':False, 'initial':False})
#        }
#        exclude=['update_timestamp','creation_timestamp','created_by_dbengine','last_update_by_dbengine','created_by','last_update_by','receptor_id_protein','id_species']

class dyndb_ReferenceForm(ModelForm):
    class Meta:
        model = DyndbReferences
 #       fields = '__all__'
        exclude=['dbname','update_timestamp','creation_timestamp','created_by_dbengine','last_update_by_dbengine','created_by','last_update_by','receptor_id_protein','id_species']



class dyndb_Other_Protein_NamesForm(ModelForm):
    class Meta:
        model = DyndbOtherProteinNames
        fields = '__all__'

class dyndb_Protein_SequenceForm(ModelForm):
    class Meta:
        model = DyndbProteinSequence
        fields = '__all__'
 #       exclude=['id_protein','length']
        widgets= {'sequence':Textarea(attrs={'cols': 40, 'rows': 3})}
  
class dyndb_Cannonical_ProteinsForm(ModelForm):
    class Meta:
        model = DyndbCannonicalProteins
        fields = '__all__'

class dyndb_Protein_MutationsForm(ModelForm):
    class Meta:
        model = DyndbProteinMutations
        fields = '__all__'

class dyndb_CompoundForm(ModelForm):
    class Meta:
        model = DyndbCompound
        fields = '__all__'

class dyndb_Other_Compound_Names(ModelForm):
    class Meta:
        model = DyndbOtherCompoundNames
        fields = '__all__'

class dyndb_Molecule(ModelForm):
    class Meta:
        model = DyndbMolecule
        fields = '__all__'
      #  exclude=['update_timestamp','creation_timestamp','created_by_dbengine','last_update_by_dbengine','created_by','last_update_by']

class dyndb_Files(ModelForm):
    class Meta:
        model = DyndbFiles
        fields = '__all__'

class dyndb_Submission(ModelForm):
    class Meta:
        model = DyndbSubmission
        fields = '__all__'

class dyndb_Submission_Model(ModelForm):
    class Meta:
        model = DyndbSubmissionModel
        fields = '__all__'

class dyndb_Submission_Protein(ModelForm):
    class Meta:
        model = DyndbSubmissionProtein
        fields = '__all__'

class dyndb_Submission_Molecule(ModelForm):
    class Meta:
        model = DyndbSubmissionMolecule
        fields = '__all__'

class dyndb_File_Types(ModelForm):
    class Meta:
        model = DyndbFileTypes
        fields = '__all__'

class dyndb_Files_Molecule(ModelForm):
    class Meta:
        model = DyndbFilesMolecule
        fields = '__all__'

class dyndb_Complex_Exp(ModelForm):
    class Meta:
        model = DyndbComplexExp
        fields = '__all__'

class dyndb_Complex_Protein(ModelForm):
    class Meta:
        model = DyndbComplexProtein
        fields = '__all__'

class dyndb_Complex_Molecule(ModelForm):
    class Meta:
        model = DyndbComplexMolecule
        fields = '__all__'

class dyndb_Complex_Molecule_Molecule(ModelForm):
    class Meta:
        model = DyndbComplexCompound
        fields = '__all__'

class dyndb_Complex_Compound(ModelForm):
    class Meta:
        model = DyndbComplexCompound
        fields = '__all__'

class dyndb_Modeled_Residues(ModelForm):
   class Meta:
       model = DyndbModeledResidues
       fields = '__all__'

class dyndb_Files_Model(ModelForm):
    class Meta:
        model = DyndbFilesModel
        fields = '__all__'

class dyndb_Dynamics_Membrane_Types(ModelForm):
    class Meta:
        model = DyndbDynamicsMembraneTypes
        fields = '__all__'

class dyndb_Dynamics(ModelForm):
    class Meta:
        model = DyndbDynamics
        fields = '__all__'

class dyndb_Dynamics_Components(ModelForm):
    class Meta:
        model = DyndbDynamicsComponents
        fields = '__all__'

# falta dyndb_dynamics_components
class dyndb_Dynamics_tags(ModelForm):
    class Meta:
        model = DyndbDynamicsTags
        fields = '__all__'

class dyndb_Dynamics_Tags_List(ModelForm):
    class Meta:
        model = DyndbDynamicsTagsList
        fields = '__all__'
####################################
class Pdyndb_Dynamics(ModelForm):
    class Meta:
        model = DyndbDynamics
        fields = '__all__'
        exclude = ['id_model', 'id_dynamics_methods']
# falta dyndb_dynamics_components
class Pdyndb_Dynamics_tags(ModelForm):
    class Meta:
        model = DyndbDynamicsTags
        fields = '__all__'

class Pdyndb_Dynamics_Tags_List(ModelForm):
    class Meta:
        model = DyndbDynamicsTagsList
        fields = '__all__'
####################################
class dyndb_Files_Dynamics(ModelForm):
    class Meta:
        model = DyndbFilesDynamics
        fields = '__all__'

class dyndb_Related_Dynamics(ModelForm):
    class Meta:
        model = DyndbRelatedDynamics
        fields = '__all__'

class dyndb_Related_Dynamics_Dynamics(ModelForm):
    class Meta:
        model = DyndbRelatedDynamicsDynamics
        fields = '__all__'


#################################
class dyndb_Model(ModelForm):       
    class Meta:
        model = DyndbModel
        fields = '__all__'
     #   exclude=['update_timestamp','creation_timestamp','created_by_dbengine','last_update_by_dbengine','created_by','last_update_by','id_structure_model']

    #class Media:
    #    js = ('addInput.js',)     
              
##########################
class dyndb_Model_Components(ModelForm):       
    class Meta:
        model = DyndbModelComponents
        fields = '__all__'


class AlertForm(forms.ModelForm):
    class Meta:
        model=StructureModelLoopTemplates
        fields = '__all__'
        widgets = {
            'user':  forms.HiddenInput()
        }
    
#    AlertCountFormset = modelformset_factory(WebResource,form = AlertForm)
    
class NotifierForm(forms.ModelForm):
#    high = forms.ChoiceField(choices=NOTIFIER_TYPE)
#    medium = forms.ChoiceField(choices=NOTIFIER_TYPE)
#    low = forms.ChoiceField(choices=NOTIFIER_TYPE)  
    
    def save(self, commit=True):
        alert = super(NotifierForm, self).save(commit=False)
#       alert.high = self.cleaned_data["high"]
#       alert.medium = self.cleaned_data["medium"]
#       alert.low = self.cleaned_data["low"]
        alert.save()
        return alert
    
    class Meta:
        model=StructureType
        fields = '__all__'
#        fields = ('high','medium', 'low', 'user')
        widgets = {
            'user': forms.HiddenInput()
        }

#NotifierFormset = modelformset_factory(Notifier, form = NotifierForm)
class Formup(forms.Form):
    UNIPROTid = forms.CharField(max_length=20)
    iso = forms.CharField(max_length=100)
    MUT = forms.CharField(max_length=4)
    Nam = forms.CharField(max_length=30)
    ORGAN = forms.CharField(max_length=200)
    DescMOL = forms.CharField()
    NETc = forms.IntegerField()
    INCHI = forms.CharField()
            
