from modules.dynadb.models import DyndbDynamics, DyndbModel, DyndbProtein, DyndbDynamicsComponents, DyndbModelComponents, DyndbSubmissionMolecule, DyndbMolecule, DyndbSubmission, DyndbCompound
from modules.protein.models import ProteinConformation, ProteinState, Protein
from rest_framework import serializers
import copy
from collections import OrderedDict

# search_dyn_class/ 
class DynsClassSerializer(serializers.ModelSerializer):
    classname = serializers.SerializerMethodField()
    dyn_id = serializers.SerializerMethodField()
    
    def get_classname(self,obj):
        classname = f'Class {obj["classname"]}' 
    
        return classname
    
    def get_dyn_id(self,obj):
        fam_ids = obj["fam_ids"] 
        protids = Protein.objects.filter(family_id__in=fam_ids).values_list("id", flat = True)
        dynprotids = DyndbProtein.objects.filter(receptor_id_protein__in=protids).values_list("id", flat = True)
        model_ids = DyndbModel.objects.filter(id_protein__in=dynprotids).values_list("id", flat = True)
        ldynids = DyndbDynamics.objects.filter(id_model__in=model_ids).values_list("id", flat = True)
        dynids = list(ldynids)
        dynids.sort()

        return dynids
    
    class Meta:
        model = DyndbDynamics
        fields = ['classname', 
            'dyn_id']

# search_comp/ 
class CompRoleSerializer(serializers.ModelSerializer):
    ligrole = serializers.SerializerMethodField()
    liginfo = serializers.SerializerMethodField()
    
    def get_ligrole(self,obj):
        ligrole = obj["ligrole"] 

        return ligrole
    
    def get_liginfo(self,obj):
        lig_info = {}
        mol_ids = obj["molecule_ids"] 
        sub_ids = obj["submission_ids"]
        for i, mol in enumerate(mol_ids):
            sub_info = DyndbSubmission.objects.filter(id=sub_ids[i]).values()[0]
            published = sub_info["is_published"]
            if published: 
                mol_ind = {}
                mol_ind_info = DyndbMolecule.objects.filter(id=mol).values()[0]
                id_comp = mol_ind_info["id_compound_id"]
                comp_info = DyndbCompound.objects.filter(id=id_comp).values()[0]
                name = comp_info["name"]
                smiles = mol_ind_info["smiles"]
                inchikey = mol_ind_info["inchikey"]
                mol_ind["smiles"] = smiles
                mol_ind["inchikey"] = inchikey
                lig_info[name] = mol_ind
        return lig_info
    
    class Meta:
        model = DyndbSubmissionMolecule
        fields = ['ligrole', 
            'liginfo']

# search_dyn_lig_type/ 
class DynsLigTypeSerializer(serializers.ModelSerializer):
    ligtype = serializers.SerializerMethodField()
    dyn_id = serializers.SerializerMethodField()
    
    def get_ligtype(self,obj):
        ligtype = obj["ligtype"] 

        return ligtype
    
    def get_dyn_id(self,obj):
        model_ids = obj["model_ids"] 
        ldynids = DyndbDynamics.objects.filter(id_model__in=model_ids).values_list("id", flat = True)
        dynids = list(ldynids)
        dynids.sort()

        return dynids
    
    class Meta:
        model = DyndbDynamics
        fields = ['ligtype', 
            'dyn_id']

# search_allpdbs
class AllPdbsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DyndbModel
        fields = ['pdbid']

# search_dyn_pdbs/ & # search_dyn_uniprots/
class DynsPdbsSerializer(serializers.ModelSerializer):
    pdb = serializers.SerializerMethodField()
    dyn_id = serializers.SerializerMethodField()
    
    def get_pdb(self,obj):
        pdbid = obj["pdbid"]
        
        return pdbid
    
    def get_dyn_id(self,obj):
        model_ids = obj["mol_ids"]
        dynids = DyndbDynamics.objects.filter(id_model__in=model_ids).values_list("id", flat = True)

        return dynids
    class Meta:
        model = DyndbDynamics
        fields = ['pdb', 
            'dyn_id']

class DynsUniprotsSerializer(serializers.ModelSerializer):
    uniprot = serializers.CharField(source = 'uniprotkbac', allow_null=True)
    # dyn_id = serializers.IntegerField(source = 'id') 
    dyn_id = serializers.SerializerMethodField()
    
    def get_dyn_id(self,obj):
        model_ids = DyndbModel.objects.filter(id_protein=obj.id).values_list('id', flat=True)
        dynids = DyndbDynamics.objects.filter(id_model__in=model_ids).values_list("id", flat = True)
        return dynids
    
    class Meta:
        model = DyndbProtein
        fields = ['uniprot', 
            'dyn_id']
        
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
    dyn_id = serializers.IntegerField(source='id') 
    pdb_namechain = serializers.CharField(source = "id_model.pdbid", allow_null=True)
    uniprot = serializers.CharField(source = 'id_model.id_protein.uniprotkbac', allow_null=True)
    protname = serializers.CharField(source = 'id_model.id_protein.name', allow_null=True)
    species = serializers.CharField(source = 'id_model.id_protein.id_uniprot_species.scientific_name', allow_null=True)
    state = serializers.SerializerMethodField()
    try:
        fam_slug = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.slug', allow_null=True)
    except:
        fam_slug = ""
    try:
        fam_name = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.parent.name', allow_null=True)
    except:
        fam_name = ""
    try:
        class_name = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.family.parent.parent.parent.name', allow_null=True)
    except:
        class_name = ""
    try:
        uprot_entry = serializers.CharField(source = 'id_model.id_protein.receptor_id_protein.entry_name', allow_null=True)
    except:
        uprot_entry = ""
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
        try:
            protcomps = ProteinConformation.objects.filter(protein=obj.id_model.id_protein.receptor_id_protein)
            return ProteinConformationSerializer(protcomps, many=True).data
        except:
            return ""
    
    class Meta:
        model = DyndbDynamics
        fields = [
            'dyn_id',
            'pdb_namechain', 
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
        
class SubsSearchSerializer(serializers.ModelSerializer):
    dyn_id = serializers.IntegerField(source='id') 
    class Meta:
        model = DyndbDynamics
        fields = [ 
                  'submission_id', 'dyn_id'
                  ] 

# search_list_dyn      
class ListDynsSearchSerializer(serializers.ListField):
    dyn_id = serializers.IntegerField(source='id') 
    class Meta:
        model = DyndbDynamics
        fields = ['dyn_id']
    
