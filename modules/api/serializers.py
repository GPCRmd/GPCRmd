from modules.dynadb.models import DyndbDynamics, DyndbModel, DyndbProtein, DyndbDynamicsComponents, DyndbModelComponents 
from modules.protein.models import ProteinConformation, ProteinState
from rest_framework import serializers
import copy
from collections import OrderedDict

# search_allpdbs
class AllPdbsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DyndbModel
        fields = ['pdbid']

# search_dyn_pdbs/ & # search_dyn_uniprots/
class DynsSerializer(serializers.ModelSerializer):
    dyn_id = serializers.IntegerField(source='id') 
    class Meta:
        model = DyndbDynamics
        fields = ['dyn_id']

# search_alluniprots
class AllUniprotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DyndbProtein
        fields = ['uniprotkbac']
        # depth = 1

# search_dyn
class DyndbComponentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DyndbDynamicsComponents
        fields = ['resname']

class ProteinConformationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source = "state.name", allow_null=True)
    class Meta:
        model = ProteinConformation
        fields = ['name']
class DynsSearchSerializer(serializers.ModelSerializer):
    pdb_namechain = serializers.CharField(source = "id_model.pdbid", allow_null=True)
    uniprot = serializers.CharField(source = 'id_model.id_protein.uniprotkbac', allow_null=True)
    protname = serializers.CharField(source = 'id_model.id_protein.name', allow_null=True)
    state = serializers.SerializerMethodField()
    species = serializers.CharField(source = 'id_model.id_protein.id_uniprot_species.scientific_name', allow_null=True)
    fam_slug = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.slug', allow_null=True)
    fam_name = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.parent.name', allow_null=True)
    class_name = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.parent.parent.parent.name', allow_null=True)
    uprot_entry = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.entry_name', allow_null=True)
    modelname = serializers.CharField(source = 'id_model.name', allow_null=True)
    dyncomp = serializers.SerializerMethodField()
    mysoftware = serializers.CharField(source = 'software', allow_null=True)
    software_version = serializers.CharField(source = 'sversion', allow_null=True)
    forcefield = serializers.CharField(source = 'ff', allow_null=True)
    forcefield_version = serializers.CharField(source = 'ffversion', allow_null=True)

    def get_dyncomp(self, obj):
        dyncomps = DyndbDynamicsComponents.objects.filter(id_dynamics=obj)
        return DyndbComponentsSerializer(dyncomps , many=True).data
    
    def get_state(self,obj):
        #(source = '.states.name')#, allow_null=True)
        protcomps = ProteinConformation.objects.filter(protein=obj.id_model.id_protein.receptor_id_protein)
        return ProteinConformationSerializer(protcomps, many=True).data
    
    class Meta:
        model = DyndbDynamics
        fields = ['pdb_namechain', 
            'uniprot', 
            'protname',
            'state', 
            'species', 
            'fam_slug', 
            'fam_name', 
            'class_name', 
            'uprot_entry', 
            'modelname', 
            'dyncomp', 
            'mysoftware', 
            'software_version',
            'forcefield', 
            'forcefield_version', 
            ] 

# search_list_dyn      
class ListDynsSearchSerializer(serializers.ListField):
    dyn_id = serializers.IntegerField(source='id') 
    class Meta:
        model = DyndbDynamics
        fields = ['dyn_id']
    
