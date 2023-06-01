from django import forms
import os
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
import requests
from modules.covid19.models import CovidModel
import json

class UploadDescriptorsForm(forms.Form):
    csv_file = forms.FileField(label="CSV file" , widget=forms.FileInput(attrs={'class':'form-control-file'}))
 
#    def clean_csv_file(self):
#        file_data=self.cleaned_data['csv_file']
#        if file_data:
#            if file_data._size > max_upload_size:
#                raise ValidationError(('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(file_data._size)))



class UploadFileForm(forms.Form):
    MODEL_SOURCE = CovidModel.MODEL_SOURCE
    #Protein
    uniprotkbac = forms.CharField(max_length=10,label="Uniprot ID",widget=forms.TextInput(attrs={'class': 'form-control'}))
    prot_name = forms.CharField(required=False)
    uniprot_entry= forms.CharField(max_length=11,required=False)
    species = forms.CharField(max_length=200,required=False)
    pdb_id = forms.CharField(max_length=6, label="PDB ID",widget=forms.TextInput(attrs={'class': 'form-control'}))
    model_source = forms.ChoiceField(choices=MODEL_SOURCE, label="Source", widget=forms.Select(attrs={"class":"modify_label form-control myselectform", "data-target":"pdb_id", "data-val":json.dumps({0:"PDB ID",1:"PDB ID (template)"})}))

    PROT_OPTIONS = (
        ("Spike", "Spike glycoprotein"),
        ("N", "Nucleoprotein"),
        ("M", "Membrane protein"),
        ("E", "Envelope small membrane protein"),
        ("NSP1", "NSP1"),
        ("NSP2", "NSP2"),
        ("NSP3", "NSP3"),
        ("NSP4", "NSP4"),
        ("NSP5", "NSP5"),
        ("NSP6", "NSP6"),
        ("NSP7", "NSP7"),
        ("NSP8", "NSP8"),
        ("NSP9", "NSP9"),
        ("NSP10", "NSP10"),
        ("NSP11", "NSP11"),
        ("NSP12", "NSP12"),
        ("NSP13", "NSP13"),
        ("NSP14", "NSP14"),
        ("NSP15", "NSP15"),
        ("NSP16", "NSP16"),
        ("ORF3a", "ORF3a"),
        ("ORF6", "ORF6"),
        ("ORF7a", "ORF7a"),
        ("ORF7b", "ORF7b"),
        ("ORF8", "ORF8"),
        ("ORF9b", "ORF9b"),
        ("ORF9c", "ORF9c"),
       # ("ORF10", "ORF10"),
        ("ORF14", "ORF14"),
        ("Others", "Others"),
    )
    final_prots = forms.MultipleChoiceField(label="Proteins included", widget=forms.SelectMultiple,
                      choices=PROT_OPTIONS, help_text="(hold ctrl or shift to select more than one)")



    #Author
    first_name=forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name=forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class': 'form-control'}))
    institution = forms.CharField(max_length=200,widget=forms.TextInput(attrs={'class': 'form-control'})) 

    #Simulation
    dyn_name = forms.CharField(max_length=100, label="Simulation name", widget=forms.TextInput(attrs={'placeholder': "E.g. <Prot. name> in complex with <lig. name>",'class': 'form-control'}))
    delta = forms.FloatField(help_text="Time lapse between frames in a trajectory file (ns).",widget=forms.NumberInput(attrs={'step': "0.01",'class': 'form-control'}))
    timestep = forms.FloatField(help_text="Time step: Simulation integration step (fs).",label="Time step",widget=forms.NumberInput(attrs={'class': 'form-control'}))
    software = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class': 'form-control'}))
    sversion = forms.CharField(max_length=15, label="Software version",widget=forms.TextInput(attrs={'class': 'form-control'}))
    ff = forms.CharField(max_length=20, label="Force field",widget=forms.TextInput(attrs={'class': 'form-control'}))
    ffversion = forms.CharField(max_length=15, label="Force field version",widget=forms.TextInput(attrs={'class': 'form-control'}))
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs={"rows":2,'class': 'form-control'}), help_text="Optional: other relevant information that it is not contained on other fields.",required = False)

    #Files
    coord_file = forms.FileField(label="Coordinate file" , widget=forms.FileInput(attrs={'accept':'.pdb,.gro','class':'form-control-file'}))
    traj_files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True , 'accept':'.dcd,.xtc'}) , label="Trajectory files"  )
    other_files = forms.FileField(label="Other files",required = False, help_text="Optional: upload other relevant files (.tar.gz,.tgz)",  widget=forms.FileInput(attrs={'accept':'.tar.gz,.tgz'}))

    #Ligand
    HASLIG_CHOICES = (("No", 'No'),("Yes", 'Yes'),)
    has_lig = forms.ChoiceField(choices=HASLIG_CHOICES, label="Includes ligand", widget=forms.Select(attrs={"class":"has_extra_element form-control myselectform"}))
    ligand_count = forms.CharField(widget=forms.HiddenInput())
    #lig_name = forms.CharField(max_length=100, label="Ligand name",required = False)
    #lig_resid = forms.CharField(max_length=4, label="Ligand resid",required = False)
    #LIGTYPE_CHOICES = (('orthosteric', 'Orthosteric'),('allosteric', 'Allosteric'),)
    #lig_type = forms.ChoiceField(choices=LIGTYPE_CHOICES, label="Ligand type",required = False)

    #Membrane
    HASMEMB_CHOICES = (("No", 'No'),("Yes", 'Yes'),)
    has_membrane = forms.ChoiceField(choices=HASMEMB_CHOICES, label="Includes membrane", widget=forms.Select(attrs={"class":"has_extra_element form-control myselectform"}))
    membrane_count = forms.CharField(widget=forms.HiddenInput())    

    def __init__(self, *args, **kwargs):
        #https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form
        extra_fields = kwargs.pop('extra', None)
        if extra_fields:
            ligand_fields=extra_fields[0]
            membrane_fields=extra_fields[1]
        else:
            ligand_fields = 0
            membrane_fields = 0

        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['ligand_count'].initial = ligand_fields
        for index in range(int(ligand_fields)):
            # generate extra fields in the number specified via ligand_fields
            self.fields['ligand_name_{index}'.format(index=index)] =  forms.CharField(required = False)
            self.fields['ligand_resname_{index}'.format(index=index)] =  forms.CharField(required = False)
            self.fields['ligand_type_{index}'.format(index=index)] =  forms.CharField(required = False)

        self.fields['membrane_count'].initial = membrane_fields
        for index in range(int(membrane_fields)):
            # generate extra fields in the number specified via membrane_fields
            self.fields['membmol_name_{index}'.format(index=index)] =  forms.CharField(required = False)
            self.fields['membmol_resname_{index}'.format(index=index)] =  forms.CharField(required = False)

    def query_uprot(self,uniprotkbac,fields):
        payload = {'query': 'id:%s'%uniprotkbac,'format': 'tab','columns': ",".join(fields)}
        result = requests.get("http://www.uniprot.org/uniprot/", params=payload)
        if result.ok and result.text:
            result_str=result.text
            (headers,vals)=result_str.split("\n")[:2]
            results_dict=dict(zip(headers.split("\t"),vals.split("\t")))
        else:
            results_dict={}
        return results_dict

    def clean_uniprotkbac(self):
        uniprotkbac=self.cleaned_data['uniprotkbac']
        fields=["entry_name","protein_names","organism"]

        results_dict=self.query_uprot(uniprotkbac,fields)
        if results_dict:
            #cleaned_data = super(UploadFileForm, self).clean()
            prot_names_all=results_dict["Protein names"]
            prot_name=prot_names_all[:prot_names_all.find("(")].strip()
            self.data["prot_name"] = prot_name
            self.data["uniprot_entry"] = results_dict["Entry name"]
            self.data["species"] =results_dict["Organism"]
            return uniprotkbac
        else:
            raise ValidationError(u'Uniprot ID not found')


    def clean_other_files(self):
        max_upload_size=536870912000
        file_data=self.cleaned_data['other_files']
        if file_data:
            if file_data._size > max_upload_size:
                raise ValidationError(('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(file_data._size)))


    def clean_coord_file(self):
        max_upload_size=536870912000
        file_data=self.cleaned_data['coord_file']
        file_name = file_data.name
        ext = os.path.splitext(file_name)[1]
        valid_extensions = ['.pdb','.gro']
        if not ext in valid_extensions:
          raise ValidationError(u'File not supported!')
        if file_data._size > max_upload_size:
            raise ValidationError(('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(file_data._size)))


    def clean_traj_files(self):
        max_upload_size=536870912000        
        all_files = self.files.getlist('traj_files')
        for file_data in all_files:
            file_name = file_data.name 
            ext = os.path.splitext(file_name)[1]
            valid_extensions = ['.xtc','.dcd']
            if not ext in valid_extensions:
              raise ValidationError(u'File not supported!')

            if file_data._size > max_upload_size:
                raise ValidationError(('Please keep filesize under %s. Current filesize %s') % (filesizeformat(max_upload_size), filesizeformat(file_data._size)))
    def clean(self):
        cleaned_data = super().clean()
        ligand_count = cleaned_data.get("ligand_count")
        added_resnames=set()
        if ligand_count:
            for index in range(int(ligand_count)):
                ligand_resname = cleaned_data.get("ligand_resname_%s" % index)
                if ligand_resname:
                    if ligand_resname in added_resnames:
                        msg=ValidationError(('Repeated resname'), code='invalid')
                        self.add_error("has_lig", msg)
                    else:
                        added_resnames.add(ligand_resname)
        membrane_count = cleaned_data.get("membrane_count")
        if membrane_count:
            for index in range(int(membrane_count)):
                membmol_resname = cleaned_data.get("membmol_resname_%s" % index)
                if membmol_resname:
                    if membmol_resname in added_resnames:
                        msg=ValidationError(('Repeated resname'), code='invalid')
                        self.add_error("has_membrane", msg)
                    else:
                        added_resnames.add(membmol_resname)





#class covid_Model(ModelForm):
#    class Meta:
#        model = CovidModel
#        fields = '__all__'
#
#class covid_DynamicsComponents(ModelForm):
#    class Meta:
#        model = CovidDynamicsComponents
#        fields = '__all__'
#
#class covid_Protein(ModelForm):
#    class Meta:
#        model = CovidProtein
#        fields = '__all__'
#
#class covid_Dynamics(ModelForm):
#    class Meta:
#        model = CovidDynamics
#        fields = '__all__'
#
#class covid_Files(ModelForm):
#    class Meta:
#        model = CovidFiles
#        fields = '__all__'
#
#class covid_FilesDynamics(ModelForm):
#    class Meta:
#        model = CovidFilesDynamics
#        fields = '__all__'
#
