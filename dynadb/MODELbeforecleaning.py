# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.forms import ModelForm, Textarea

#BORRAR Formup!!!! 
#   class Formup(models.Model):
#       UNIPROTid=models.CharField(max_length=20)
#       iso=models.CharField(max_length=100)
#       MUT=models.CharField(max_length=4)
#       Nam=models.CharField(max_length=30)
#       ORGAN=models.CharField(max_length=200)
#       
#       DescMOL=models.TextField()
#       NETc=models.IntegerField()
#       INCHI=models.TextField()
#       inchik=models.CharField(max_length=27)
#       SMI=models.TextField()
#       resnamMOL=models.CharField(max_length=5)
#       numMOL=models.IntegerField()
#   
#       MAINprot=models.TextField()
#       MAINlig=models.TextField()
#   
#       IONresn=models.CharField(max_length=5)
#       IONnum=models.IntegerField()
#   
#       COMtyp=models.CharField(max_length=50)
#       idproT= models.CharField(max_length=50)
#       idcoM=models.CharField(max_length=50)
#       Msour=models.CharField(max_length=50)
#       PDB=models.CharField(max_length=4)
#       desc=models.TextField()
#       mTEMP=models.TextField()
#       
#       METH=models.CharField(max_length=50)
#       SOFT=models.CharField(max_length=50) 
#       SOFTver=models.CharField(max_length=50) 
#       ffield=models.CharField(max_length=50) 
#       MEMB=models.CharField(max_length=50) 
#       Solv=models.CharField(max_length=50) 
#       PDBcoor=models.CharField(max_length=50) 
#       PSF=models.CharField(max_length=50) 
#       topPSF=models.CharField(max_length=50) 
#       par=models.CharField(max_length=50) 
#       DCD=models.CharField(max_length=50) 
   
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Construct(models.Model):
    deletions = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    protein_conformation = models.ForeignKey('ProteinConformation', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct'


class ConstructAuxProtein(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    uniprot_id = models.CharField(max_length=20)
    sequence = models.TextField(blank=True, null=True)
    deletions = models.TextField(blank=True, null=True)
    position = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    construct = models.ForeignKey(Construct, models.DO_NOTHING)
    protein_type = models.ForeignKey('ConstructAuxProteinType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_aux_protein'


class ConstructAuxProteinType(models.Model):
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'construct_aux_protein_type'


class ConstructChemical(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    chemical_type = models.ForeignKey('ConstructChemicalType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_chemical'


class ConstructChemicalConc(models.Model):
    concentration = models.TextField(blank=True, null=True)
    chemical = models.ForeignKey(ConstructChemical, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_chemical_conc'


class ConstructChemicalList(models.Model):

    class Meta:
        managed = False
        db_table = 'construct_chemical_list'


class ConstructChemicalListChemicals(models.Model):
    chemicallist = models.ForeignKey(ConstructChemicalList, models.DO_NOTHING)
    chemicalconc = models.ForeignKey(ConstructChemicalConc, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_chemical_list_chemicals'
        unique_together = (('chemicallist', 'chemicalconc'),)


class ConstructChemicalModification(models.Model):
    description = models.TextField()
    construct_solubilization = models.ForeignKey('ConstructSolubilization', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_chemical_modification'


class ConstructChemicalType(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'construct_chemical_type'


class ConstructCrystallization(models.Model):
    method = models.TextField(blank=True, null=True)
    settings = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    protein_conc = models.CharField(max_length=20)
    aqueous_solution_lipid_ratio = models.CharField(max_length=20, blank=True, null=True)
    lcp_bolus_volume = models.CharField(max_length=20, blank=True, null=True)
    precipitant_solution_volume = models.CharField(max_length=20, blank=True, null=True)
    temp = models.CharField(max_length=5, blank=True, null=True)
    ph = models.TextField(blank=True, null=True)
    chemical_list = models.ForeignKey(ConstructChemicalList, models.DO_NOTHING)
    construct = models.ForeignKey(Construct, models.DO_NOTHING)
    crystal_type = models.ForeignKey('ConstructCrystallizationMethodTypes', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_crystallization'


class ConstructCrystallizationMethodTypes(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'construct_crystallization_method_types'


class ConstructExpression(models.Model):
    remarks = models.TextField(blank=True, null=True)
    construct = models.ForeignKey(Construct, models.DO_NOTHING)
    expression_system = models.ForeignKey('ConstructExpressionSystem', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_expression'


class ConstructExpressionSystem(models.Model):
    expression_method = models.CharField(max_length=100)
    host_cell_type = models.CharField(max_length=100)
    host_cell = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'construct_expression_system'


class ConstructLigandConcOfCrystallization(models.Model):
    ligand_conc = models.TextField(blank=True, null=True)
    construct_crystallization = models.ForeignKey(ConstructCrystallization, models.DO_NOTHING)
    ligand = models.ForeignKey('Ligand', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_ligand_conc_of_crystallization'


class ConstructPurification(models.Model):
    remarks = models.TextField(blank=True, null=True)
    construct = models.ForeignKey(Construct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_purification'


class ConstructPurificationStep(models.Model):
    description = models.TextField(blank=True, null=True)
    purification = models.ForeignKey(ConstructPurification, models.DO_NOTHING)
    purification_type = models.ForeignKey('ConstructPurificationStepType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_purification_step'


class ConstructPurificationStepType(models.Model):
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'construct_purification_step_type'


class ConstructSolubilization(models.Model):
    remarks = models.TextField(blank=True, null=True)
    chemical_list = models.ForeignKey(ConstructChemicalList, models.DO_NOTHING)
    construct = models.ForeignKey(Construct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'construct_solubilization'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class DyndbAssayTypes(models.Model):
    type_name = models.CharField(max_length=60)

    class Meta:
        managed = False
        db_table = 'dyndb_assay_types'


class DyndbBinding(models.Model):
    id = models.ForeignKey('DyndbExpInteractionData', models.DO_NOTHING, db_column='id', primary_key=True)
    rvalue = models.FloatField()
    units = models.CharField(max_length=10)
    description = models.CharField(max_length=900, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_binding'


class DyndbCannonicalProteins(models.Model):
    id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='id_protein', primary_key=True)

    class Meta:
        managed = False
        db_table = 'dyndb_cannonical_proteins'


class DyndbComplexCompound(models.Model):
    COMPOUND_TYPE=(
        (0,'Orthosteric ligand'),
        (1,'Allosteric ligand')
    )
    id_complex_exp=models.ForeignKey('DyndbComplexExp', models.DO_NOTHING, db_column='id_complex_exp', null=True)#
    #id_complex_exp_id =models.IntegerField(blank=True, null=True)
    id_compound = models.ForeignKey('DyndbCompound',models.DO_NOTHING, db_column='id_compound',null=True)  
    #id_compound_id = models.IntegerField(blank=True, null=True)
    type = models.SmallIntegerField(choices=COMPOUND_TYPE, default=0)#modified by juanma 
 
    class Meta:
        managed = True
        db_table = 'dyndb_complex_compound'
        unique_together = (('id_complex_exp', 'id_compound'))
 

class DyndbComplexExp(models.Model):
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        managed = True #this used to be False
        db_table = 'dyndb_complex_exp'


class DyndbComplexMolecule(models.Model):
#   COMPOUND_TYPE=(
#       (0,'Orthosteric ligand'),
#       (1,'Allosteric ligand'),
#       (2,'Crystallographic waters'),
#       (3,'Other')
#   )
    #type = models.SmallIntegerField(choices=COMPOUND_TYPE, default=0)#modified by juanma 
    id_complex_exp = models.ForeignKey(DyndbComplexExp, models.DO_NOTHING, db_column='id_complex_exp')
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_complex_molecule'


class DyndbComplexMoleculeMolecule(models.Model):
    COMPOUND_TYPE=(
        (0,'Orthosteric ligand'),
        (1,'Allosteric ligand')
    )
    type = models.SmallIntegerField(choices=COMPOUND_TYPE, default=0)#modified by juanma 
    id_complex_molecule = models.ForeignKey(DyndbComplexMolecule, models.DO_NOTHING, db_column='id_complex_molecule',null=False)
    id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule',null=False)


    class Meta:
        managed = True
        db_table = 'dyndb_complex_molecule_molecule'
        unique_together = (('id_complex_molecule', 'id_molecule'),)


class DyndbComplexProtein(models.Model):
    id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='id_protein', null=True)
    id_complex_exp = models.ForeignKey(DyndbComplexExp, models.DO_NOTHING, db_column='id_complex_exp', null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_complex_protein'
        unique_together = (('id_protein', 'id_complex_exp'),)


class DyndbCompound(models.Model):
    name = models.CharField(unique=True, max_length=60)
    iupac_name = models.CharField(max_length=500)
    pubchem_cid = models.IntegerField(unique=True, blank=True, null=True)
    chemblid = models.IntegerField(unique=True, blank=True, null=True)
    sinchi = models.TextField(null=True)
#    sinchikey = models.CharField(max_length=27, db_index=True,null=True)
    sinchikey = models.CharField(max_length=27, null=True)
    std_id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='std_id_molecule', blank=True, null=True)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    id_ligand = models.ForeignKey('Ligand', models.DO_NOTHING, db_column='id_ligand', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        managed = True
        db_table = 'dyndb_compound'

class DyndbSubmission(models.Model):
    user_id=models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_submission'



class DyndbSubmissionProtein(models.Model):
    submission_id = models.ForeignKey('DyndbSubmission',models.DO_NOTHING, db_column='submission_id',  blank=True, null=True) 
    protein_id = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='protein_id', blank=True, null=True)  
    int_id=models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_submission_protein'
        unique_together = (('submission_id', 'protein_id'),('submission_id', 'int_id'),)

class DyndbSubmissionMolecule(models.Model):
    COMPOUND_TYPE=(
        (0,'Orthosteric ligand'),
        (1,'Allosteric ligand'),
        (2,'Crystallographic ions'),
        (3,'Crystallographic lipids'),
        (4,'Crystallographic waters'),
        (5,'Other co-crystalized item'),
        (6,'Bulk waters'),
        (7,'Bulk lipids'),
        (8,'Bulk ions'),
        (9,'Other bulk component'),
    )
    type = models.SmallIntegerField(choices=COMPOUND_TYPE, default=0, null=True, blank=True)#modified by juanma 
    submission_id = models.ForeignKey('DyndbSubmission', models.DO_NOTHING, db_column='submission_id', blank=True, null=True)
    molecule_id = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='molecule_id', blank=True, null=True)
    not_in_model=models.NullBooleanField()
    int_id=models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_submission_molecule'
        unique_together = (('submission_id', 'molecule_id'),('submission_id', 'int_id'),)

smol_to_dyncomp_type={0:1, 1:1, 2:0, 3:2, 4:3, 5:4, 6:3, 7:2, 8:0, 9:4} #dictionary from submission_molecule_type to Dynamics components type and Modeled components type (from 0 to 5)

class DyndbSubmissionModel(models.Model):
    submission_id = models.ForeignKey('DyndbSubmission', models.DO_NOTHING, db_column='submission_id', blank=True, null=True, unique=True)
    model_id=models.ForeignKey('DyndbModel', models.DO_NOTHING, db_column='model_id', blank=True, null=True) 

    class Meta:
        managed =True 
        db_table = 'dyndb_submission_model'

class DyndbDynamics(models.Model):
    id_model = models.ForeignKey('DyndbModel', models.DO_NOTHING, db_column='id_model', blank=True, null=True)
    id_dynamics_methods = models.ForeignKey('DyndbDynamicsMethods', models.DO_NOTHING, db_column='id_dynamics_methods', blank=True, null=True)
    software = models.CharField(max_length=30, blank=True, null=True)
    sversion = models.CharField(max_length=15, blank=True, null=True)
    ff = models.CharField(max_length=20, blank=True, null=True)
    ffversion = models.CharField(max_length=15, blank=True, null=True)
    id_assay_types = models.ForeignKey(DyndbAssayTypes, models.DO_NOTHING, db_column='id_assay_types', blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    id_dynamics_membrane_types = models.ForeignKey('DyndbDynamicsMembraneTypes', models.DO_NOTHING, db_column='id_dynamics_membrane_types', blank=True, null=True)
    id_dynamics_solvent_types = models.ForeignKey('DyndbDynamicsSolventTypes', models.DO_NOTHING, db_column='id_dynamics_solvent_types', blank=True, null=True)
    solvent_num = models.IntegerField(blank=True, null=True)
    atom_num = models.IntegerField(blank=True, null=True)
    timestep = models.FloatField(blank=False, null=False)
    delta = models.FloatField(blank=False, null=False)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    submission_id = models.ForeignKey(DyndbSubmission, models.DO_NOTHING, db_column='submission_id', blank=True, null=True) 
    is_published = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'dyndb_dynamics'

class DyndbDynamicsComponents(models.Model):
    MOLECULE_TYPE=(
        (0,'Ions'),
        (1,'Ligand'),
        (2,'Lipid'),
        (3,'Water'),
        (4,'Other')
    )    
    id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule', null=True)
    id_dynamics = models.ForeignKey('DyndbDynamics', models.DO_NOTHING, db_column='id_dynamics', null=True)
    resname = models.CharField(max_length=4)
    numberofmol = models.PositiveSmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField( choices=MOLECULE_TYPE, default=0)

    class Meta:
        managed = True
        db_table = 'dyndb_dynamics_components'
        unique_together = (('id_dynamics', 'id_molecule', 'resname'),)

class DyndbModelComponents(models.Model):
    MOLECULE_TYPE=DyndbDynamicsComponents.MOLECULE_TYPE 

    id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule',null=True)
    id_model = models.ForeignKey('DyndbModel', models.DO_NOTHING, db_column='id_model',null=True)
    resname = models.CharField(max_length=4)
    numberofmol = models.PositiveSmallIntegerField(blank=True, null=True)
    type = models.SmallIntegerField(choices=MOLECULE_TYPE, null=True, default=0)
  
    class Meta:
        managed = True
        db_table = 'dyndb_model_components'
        unique_together = (('id_model', 'id_molecule', 'resname'),)


class Model2DynamicsMoleculeType:
    def __init__(self):
        model_type_2_num = dict()
        for num,name in DyndbModelComponents.MOLECULE_TYPE:
            model_type_2_num[name] = num
        self.__dynamics_type_2_name = dict()
        for num,name in DyndbDynamicsComponents.MOLECULE_TYPE:
            self.__dynamics_type_2_name[num] = name
        self.__translation_dict = dict()
        for num,name in DyndbDynamicsComponents.MOLECULE_TYPE:
            self.__translation_dict[model_type_2_num[name]] = num 
    def translate(self,num,as_text=False):
        val = None
        if num in self.__translation_dict:
            val = self.__translation_dict[num]
            if as_text:
                val = self.__dynamics_type_2_name[val]     
        return val


class DyndbDynamicsMembraneTypes(models.Model):
    type_name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'dyndb_dynamics_membrane_types'


class DyndbDynamicsMethods(models.Model):
    type_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'dyndb_dynamics_methods'


class DyndbDynamicsSolventTypes(models.Model):
    type_name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'dyndb_dynamics_solvent_types'


class DyndbDynamicsTags(models.Model):
    id_dynamics_tag = models.ForeignKey('DyndbDynamicsTagsList', models.DO_NOTHING, db_column='id_dynamics_tag')
    id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics')

    class Meta:
        managed = False
        db_table = 'dyndb_dynamics_tags'
        unique_together = (('id_dynamics_tag', 'id_dynamics'),)


class DyndbDynamicsTagsList(models.Model):
    name = models.CharField(unique=True, max_length=45)

    class Meta:
        managed = False
        db_table = 'dyndb_dynamics_tags_list'


class DyndbEfficacy(models.Model):
    EFFICACY_TYPE=(
        (0,'Full Agonist'),
        (1,'Partial Agonist'),
        (2,'Antagonist'),
        (3, 'Inverse Agonist'),
        (4,'Other')
    )
    id = models.ForeignKey('DyndbExpInteractionData', models.DO_NOTHING, db_column='id', primary_key=True)
    rvalue = models.FloatField()
    units = models.CharField(max_length=10)
    description = models.CharField(max_length=900,blank=True, null=True)
    type = models.SmallIntegerField( choices=EFFICACY_TYPE, default=0)
    reference_id_compound = models.ForeignKey(DyndbCompound, models.DO_NOTHING, db_column='reference_id_compound',null=True)   
    id_functional = models.ForeignKey('DyndbFunctional', models.DO_NOTHING, blank=True, db_column='id_functional', null=True) 

    class Meta:
        managed = True
        db_table = 'dyndb_efficacy'


class DyndbExpInteractionData(models.Model):
    INTERACTION_TYPE=(
        (0, 'Functional'),
        (1, 'Binding'),
        (2, 'Efficacy')
    )
    id_complex_exp = models.ForeignKey(DyndbComplexExp, models.DO_NOTHING, db_column='id_complex_exp',null=True)
    type = models.SmallIntegerField( choices=INTERACTION_TYPE, default=0)
    protein1 = models.ForeignKey('DyndbProtein',  models.DO_NOTHING, db_column='protein1', related_name='DyndbExpInteractionData_protein1_fky', null=True)
    protein2 = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='protein2', blank=True, null=True, related_name='DyndbExpInteractionData_protein2_fky' )
    ligand1 = models.ForeignKey(DyndbCompound, models.DO_NOTHING, db_column='ligand1', blank=True, null=True, related_name='DyndbExpInteractionData_ligand1_fky')
    ligand2 = models.ForeignKey(DyndbCompound, models.DO_NOTHING,db_column='ligand2',   blank=True, null=True, related_name='DyndbExpInteractionData_ligand2_fky') 
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True 
        db_table = 'dyndb_exp_interaction_data'


class DyndbExpProteinData(models.Model):
    EXP_PROTEIN_TYPES=(
        (0,'Activity'),
        (1, 'Others')
    )
    id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='id_protein', null=True)
    type = models.SmallIntegerField(choices=EXP_PROTEIN_TYPES, default=0)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_exp_protein_data'


class DyndbFileTypes(models.Model):
    type_name = models.CharField(max_length=40, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    is_coordinates = models.NullBooleanField()
    is_topology = models.NullBooleanField()
    is_trajectory = models.NullBooleanField()
    is_parameter = models.NullBooleanField()
    is_anytype = models.NullBooleanField()
    is_image = models.NullBooleanField()
    is_molecule = models.NullBooleanField()
    is_model = models.NullBooleanField()
    is_accepted = models.NullBooleanField()

    class Meta:
        managed = True
        db_table = 'dyndb_file_types'
        unique_together = (('type_name', 'extension'),)


class DyndbFiles(models.Model):
    filename = models.CharField(unique=True, max_length=80)
    id_file_types = models.ForeignKey(DyndbFileTypes,  models.DO_NOTHING, db_column='id_file_types', null=True ) 
    description = models.CharField(max_length=40, blank=True, null=True)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    filepath = models.CharField(max_length=520, blank=True, null=True)
    url = models.CharField(max_length=520, blank=True, null=True)
    

    class Meta:
        managed = True
        db_table = 'dyndb_files'

class DyndbFilesDynamics(models.Model):
    file_types=(
        (0, 'Input coordinates'),
        (1, 'Input topology'),
        (2, 'Trajectory'),
        (3, 'Parameters'),
        (4, 'Others'),
    )
    id_dynamics = models.ForeignKey('DyndbDynamics', models.DO_NOTHING, db_column='id_dynamics',   null=True) 
    id_files = models.ForeignKey('DyndbFiles', models.DO_NOTHING,   db_column='id_files',  null=True)
    type = models.SmallIntegerField( choices=file_types, default=0)


    class Meta:
        managed = True
        db_table = 'dyndb_files_dynamics'
        unique_together = (('id_dynamics', 'id_files','type'),)

class DyndbSubmissionDynamicsFiles(models.Model):
    file_types = DyndbFilesDynamics.file_types
    submission_id = models.ForeignKey('DyndbSubmission',models.DO_NOTHING, db_column='submission_id',  blank=False, null=False)
    type = models.SmallIntegerField(choices=file_types,default=0,null=False)
    filename = models.CharField(unique=True, max_length=80)
    filepath = models.CharField(max_length=520, blank=False, null=False)
    url = models.CharField(max_length=520, blank=False, null=True)
    filenum = models.PositiveSmallIntegerField(null=False,default=0)
    framenum = models.PositiveIntegerField(null=True,default=None)
    class Meta:
        managed = True
        db_table = 'dyndb_submission_dynamics_files'
        unique_together = (('submission_id', 'filepath'),('submission_id','type','filenum'))

class DyndbFilesModel(models.Model):
    id_model = models.ForeignKey('DyndbModel', models.DO_NOTHING, db_column='id_model',unique=True)
    id_files = models.ForeignKey('DyndbFiles', models.DO_NOTHING, db_column='id_files',unique=True)

    class Meta:
        managed = True
        db_table = 'dyndb_files_model'


class DyndbFilesMolecule(models.Model):
    filemolec_types=(
        (0,'Molecule'),
        (1,'Image 100px'),
        (2,'Image 300px'),
        
    )
    id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule', null=True)
    id_files = models.ForeignKey('DyndbFiles', models.DO_NOTHING, db_column='id_files', unique=True,null=True) 
    type = models.SmallIntegerField(choices=filemolec_types, default=0)
    

    class Meta:
        managed = True
        db_table = 'dyndb_files_molecule'
        unique_together = (('id_molecule', 'id_files'),('id_molecule','id_files','type'))


class DyndbFunctional(models.Model):
    id = models.ForeignKey(DyndbExpInteractionData, models.DO_NOTHING, db_column='id', primary_key=True)
    description = models.CharField(max_length=60)
    go_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dyndb_functional'


#      class DyndbIonicComponents(models.Model):
#          id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule')
#          id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics')
#          resname = models.CharField(max_length=4)
#          number = models.IntegerField(blank=True, null=True)
#      
#          class Meta:
#              managed = True
#              db_table = 'dyndb_ionic_components'
#              unique_together = (('id_dynamics', 'id_molecule'),)
#      

#  class DyndbMembraneComponents(models.Model):
#      id_molecule = models.ForeignKey('DyndbMolecule', models.DO_NOTHING, db_column='id_molecule')
#      id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics')
#      resname = models.CharField(max_length=4)
#      number = models.IntegerField(blank=True, null=True)
#  
#      class Meta:
#          managed = True
#          db_table = 'dyndb_membrane_components'
#          unique_together = (('id_dynamics', 'id_molecule'),)
#  
   
class DyndbModel(models.Model):
    MODEL_TYPE=(
        (0,'Apoform (one single protein monomer)'),
        (1,'Complex')
    )
    SOURCE_TYPE=(
        (0,'X-ray'),
        (1,'NMR'),
        (2,'Docking'),
        (3,'MD'),
        (4,'Other')
    )

    name =  models.TextField(max_length=100,null=False,blank=False) 
    type = models.SmallIntegerField(choices=MODEL_TYPE, default=0) 
    id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING,  db_column='id_protein',blank=True, null=True) 
    id_complex_molecule = models.ForeignKey(DyndbComplexMolecule, models.DO_NOTHING, db_column='id_complex_molecule',blank=True, null=True) 
    source_type = models.SmallIntegerField(choices=SOURCE_TYPE, default=0) 
    pdbid = models.CharField(max_length=6, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    model_creation_submission_id=models.ForeignKey('DyndbSubmission', models.DO_NOTHING, db_column='model_creation_submission_id', blank=True, null=True, unique=True)
    template_id_model = models.ForeignKey('self', models.DO_NOTHING, db_column='template_id_model', blank=True, null=True)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    id_structure_model = models.ForeignKey('StructureModel', models.DO_NOTHING,db_column='id_structure_model',  blank=True, null=True) 
    is_published = models.BooleanField(default=False)
    
    class Meta:
        managed = True
        db_table = 'dyndb_model'

class DyndbModeledResidues(models.Model):
    SOURCE_TYPE=(
        (0,'X-ray'),
        (1,'NMR'),
        (2,'Ab-initio'),
        (3,'Homology'),
        (4,'Threading'),
        (5,'MD'),
        (6,'Other Computational Methods')
    )
    id_protein = models.ForeignKey('DyndbProtein',  models.DO_NOTHING, db_column='id_protein', null=True)
    id_model = models.ForeignKey('DyndbModel',  models.DO_NOTHING, db_column='id_model', null=True) 
    chain = models.CharField(max_length=1,blank=True, null=False,default='')
    segid = models.CharField(max_length=4,blank=True, null=False,default='')
    resid_from = models.SmallIntegerField()
    resid_to = models.SmallIntegerField()
    seq_resid_from = models.SmallIntegerField()
    seq_resid_to = models.SmallIntegerField()
    bonded_to_id_modeled_residues = models.ForeignKey('self', models.DO_NOTHING, db_column='bond_to_id_modeled_residues', blank=True, null=True, related_name='dyndbmodeledresidues_bond_to_id_modeled_residues')#!!!!
    pdbid = models.CharField(max_length=6, blank=True, null=True)
    source_type = models.SmallIntegerField(choices=SOURCE_TYPE, default=0)
    template_id_model = models.ForeignKey(DyndbModel, models.DO_NOTHING, db_column='template_id_model', blank=True, null=True, related_name='dyndbmodeledresidues_template_id_protein')

    class Meta:
        managed = True
        db_table = 'dyndb_modeled_residues'



class DyndbMolecule(models.Model):

    molecule_creation_submission_id = models.ForeignKey('DyndbSubmission', models.DO_NOTHING, db_column='molecule_creation_submission_id', blank=True, null=True)
    id_compound = models.ForeignKey(DyndbCompound, models.DO_NOTHING, db_column='id_compound' ) 
    description = models.CharField(max_length=80, blank=True, null=True)
    net_charge = models.SmallIntegerField(blank=True, null=True)
    inchi = models.TextField()
#    inchikey = models.CharField(max_length=27,db_index=True)
    inchikey = models.CharField(max_length=27,null=True)
    inchicol = models.SmallIntegerField()
    smiles = models.TextField(blank=True, null=True)
    update_timestamp = models.DateTimeField(blank=True, null=True)
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'dyndb_molecule'
        unique_together = (('inchikey', 'inchicol'),)
         

class DyndbOtherCompoundNames(models.Model):
    other_names = models.CharField(max_length=200)
    id_compound = models.ForeignKey(DyndbCompound, models.DO_NOTHING, db_column='id_compound')

    class Meta:
        managed = False
        db_table = 'dyndb_other_compound_names'
        unique_together = (('other_names', 'id_compound'),)


class DyndbOtherProteinNames(models.Model):
    other_names = models.CharField(max_length=100)
    id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING, db_column='id_protein')

    class Meta:
        managed = False
        db_table = 'dyndb_other_protein_names'
        unique_together = (('other_names', 'id_protein'),)

class DyndbUniprotSpecies(models.Model):
    code = models.CharField(max_length=5,db_index=True,null=True,blank=False)
    kingdom = models.CharField(max_length=1,null=False)
    taxon_node = models.IntegerField(null=True)
    scientific_name = models.TextField(max_length=200,db_index=True,null=False,blank=False)
    class Meta:
      db_table = 'dyndb_uniprot_species'
    
class DyndbUniprotSpeciesAliases(models.Model):
    NAME_TYPE=(
        ('C','Common name'),
        ('S','Synonym'),
    )
    id_uniprot_species = models.ForeignKey(DyndbUniprotSpecies, on_delete=models.CASCADE, db_column='id_uniprot_species',null=False)
    name = models.TextField(max_length=200,db_index=True,null=False,blank=False)
    name_type = models.CharField(max_length=1,choices=NAME_TYPE,null=False)
    class Meta:
      db_table = 'dyndb_uniprot_species_aliases'
      unique_together = ("name", "id_uniprot_species")

class DyndbProtein(models.Model):
    uniprotkbac = models.CharField(max_length=10, blank=True, null=True)
    protein_creation_submission_id = models.ForeignKey('DyndbSubmission',models.DO_NOTHING, db_column='protein_creation_submission_id',  blank=True, null=True) 
    isoform = models.SmallIntegerField()
    is_mutated = models.BooleanField()
    name = models.TextField()
    update_timestamp = models.DateTimeField(null=True)
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)
    receptor_id_protein = models.ForeignKey('Protein', on_delete=models.DO_NOTHING, db_column='receptor_id_protein', blank=True, null=True)
    id_uniprot_species = models.ForeignKey(DyndbUniprotSpecies, on_delete=models.DO_NOTHING, db_column='id_uniprot_species',null=False)
    is_published = models.BooleanField(default=False)
    class Meta:
        managed = True
        db_table = 'dyndb_protein'


class DyndbProteinActivity(models.Model):
    id = models.ForeignKey(DyndbExpProteinData, models.DO_NOTHING, db_column='id', primary_key=True)
    rvalue = models.FloatField()
    units = models.CharField(max_length=10)
    description = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'dyndb_protein_activity'


class DyndbProteinCannonicalProtein(models.Model):
    id_protein = models.ForeignKey(DyndbProtein, models.DO_NOTHING, db_column='id_protein')
    id_cannonical_proteins = models.ForeignKey(DyndbCannonicalProteins, models.DO_NOTHING, db_column='id_cannonical_proteins')

    class Meta:
        managed = False
        db_table = 'dyndb_protein_cannonical_protein'
        unique_together = (('id_protein', 'id_cannonical_proteins'),)


class DyndbProteinMutations(models.Model):
    id_protein = models.ForeignKey(DyndbProtein, models.DO_NOTHING, db_column='id_protein', null=True)
    resid = models.SmallIntegerField(null=True)
    resletter_from = models.CharField(max_length=1, null=True)
    resletter_to = models.CharField(max_length=1, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_protein_mutations'
        unique_together = (('id_protein', 'resid', 'resletter_from', 'resletter_to'),)


class DyndbProteinSequence(models.Model):
    id_protein = models.ForeignKey(DyndbProtein, models.DO_NOTHING, db_column='id_protein', primary_key=True)
    sequence = models.TextField()
    length = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'dyndb_protein_sequence'


class DyndbReferences(models.Model):
    doi = models.CharField("DOI", help_text="Digital object identifier.", unique=True, max_length=80, blank=True, null=True)
    authors = models.CharField("Authors", help_text="List of the authors separated by semicolon.", max_length=600, blank=True, null=True)
    title = models.CharField("Title",help_text="Title of the paper.", max_length=900, blank=True, null=True)
             #institution = models.CharField(max_length=100, blank=True, null=True)
    pmid = models.IntegerField("PMID", help_text="PubMed identifier or PubMed unique identifier", unique=True, blank=True, null=True)
    journal_press = models.CharField("Journal or Press", help_text="Name of the Journal or Press in case of a book.", max_length=200, blank=True, null=True)
    issue = models.CharField("Issue", help_text="Issue number.",max_length=10, blank=True, null=True)
    volume = models.CharField("Volume", help_text="Volume number.", max_length=10, blank=True, null=True)
    pages = models.CharField("Pages", help_text="Initial and final pages of the publication separated by dash." ,max_length=16, blank=True, null=True)
    pub_year = models.SmallIntegerField("Publication year", help_text="Year of publication",blank=True, null=True)
    dbname = models.CharField(max_length=30, blank=True, null=True)
    url = models.URLField("URL", help_text="Uniform Resource Locator to the publication resource", max_length=250,  blank=True, null=True)
    update_timestamp = models.DateTimeField()
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    last_update_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    last_update_by = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dyndb_references'


class DyndbReferencesCompound(models.Model):
    id_compound = models.ForeignKey(DyndbCompound, models.DO_NOTHING, db_column='id_compound')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_compound'
        unique_together = (('id_compound', 'id_references'),)


class DyndbReferencesDynamics(models.Model):
    id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_dynamics'
        unique_together = (('id_dynamics', 'id_references'),)


class DyndbReferencesExpInteractionData(models.Model):
    id_exp_interaction_data = models.ForeignKey(DyndbExpInteractionData, models.DO_NOTHING, db_column='id_exp_interaction_data')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_exp_interaction_data'
        unique_together = (('id_exp_interaction_data', 'id_references'),)


class DyndbReferencesExpProteinData(models.Model):
    id_exp_protein_data = models.ForeignKey(DyndbExpProteinData, models.DO_NOTHING, db_column='id_exp_protein_data')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_exp_protein_data'
        unique_together = (('id_exp_protein_data', 'id_references'),)


class DyndbReferencesModel(models.Model):
    id_model = models.ForeignKey(DyndbModel, models.DO_NOTHING, db_column='id_model')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_model'
        unique_together = (('id_model', 'id_references'),)


class DyndbReferencesMolecule(models.Model):
    id_molecule = models.ForeignKey(DyndbMolecule, models.DO_NOTHING, db_column='id_molecule')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_molecule'
        unique_together = (('id_molecule', 'id_references'),)


class DyndbReferencesProtein(models.Model):
    id_protein = models.ForeignKey(DyndbProtein, models.DO_NOTHING, db_column='id_protein')
    id_references = models.ForeignKey(DyndbReferences, models.DO_NOTHING, db_column='id_references')

    class Meta:
        managed = False
        db_table = 'dyndb_references_protein'
        unique_together = (('id_protein', 'id_references'),)


class DyndbRelatedDynamics(models.Model):
    id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics', primary_key=True)

    class Meta:
        managed = False
        db_table = 'dyndb_related_dynamics'


class DyndbRelatedDynamicsDynamics(models.Model):
    id_dynamics = models.ForeignKey(DyndbDynamics, models.DO_NOTHING, db_column='id_dynamics')
    id_related_dynamics = models.ForeignKey(DyndbRelatedDynamics, models.DO_NOTHING, db_column='id_related_dynamics')

    class Meta:
        managed = False
        db_table = 'dyndb_related_dynamics_dynamics'
        unique_together = (('id_dynamics', 'id_related_dynamics'),)
        


class Gene(models.Model):
    name = models.CharField(max_length=100)
    position = models.SmallIntegerField()
    species = models.ForeignKey('Species', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gene'


class GeneProteins(models.Model):
    gene = models.ForeignKey(Gene, models.DO_NOTHING)
    protein = models.ForeignKey('Protein', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gene_proteins'
        unique_together = (('gene', 'protein'),)


class InteractionProteinLigand(models.Model):
    ligand = models.ForeignKey('Ligand', models.DO_NOTHING)
    protein = models.ForeignKey('ProteinConformation', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'interaction_protein_ligand'


class InteractionResidueFragment(models.Model):
    fragment = models.ForeignKey('StructureFragment', models.DO_NOTHING)
    interaction_type = models.ForeignKey('InteractionTypeResidueFragment', models.DO_NOTHING)
    rotamer = models.ForeignKey('StructureRotamer', models.DO_NOTHING)
    structure_ligand_pair = models.ForeignKey('InteractionStructureLigand', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'interaction_residue_fragment'


class InteractionResidueFragmentAtoms(models.Model):
    atomtype = models.CharField(max_length=20)
    atomnr = models.SmallIntegerField()
    atomclass = models.CharField(max_length=20)
    residuename = models.CharField(max_length=20)
    chain = models.CharField(max_length=20)
    residuenr = models.SmallIntegerField()
    x = models.DecimalField(max_digits=6, decimal_places=3)
    y = models.DecimalField(max_digits=6, decimal_places=3)
    z = models.DecimalField(max_digits=6, decimal_places=3)
    occupancy = models.DecimalField(max_digits=6, decimal_places=2)
    temperature = models.DecimalField(max_digits=6, decimal_places=2)
    element_name = models.CharField(max_length=20)
    interaction = models.ForeignKey(InteractionResidueFragment, models.DO_NOTHING, blank=True, null=True)
    structureligandpair = models.ForeignKey('InteractionStructureLigand', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'interaction_residue_fragment_atoms'


class InteractionStructureLigand(models.Model):
    pdb_reference = models.CharField(max_length=3, blank=True, null=True)
    annotated = models.BooleanField()
    ligand = models.ForeignKey('Ligand', models.DO_NOTHING)
    ligand_role = models.ForeignKey('LigandRole', models.DO_NOTHING)
    pdb_file = models.ForeignKey('StructurePdbData', models.DO_NOTHING, blank=True, null=True)
    structure = models.ForeignKey('Structure', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'interaction_structure_ligand'


class InteractionTypeResidueFragment(models.Model):
    slug = models.CharField(max_length=40)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, blank=True, null=True)
    direction = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'interaction_type_residue_fragment'


#   class JuanmaappChoice(models.Model):
#       choice_text = models.CharField(max_length=200)
#       votes = models.IntegerField()
#       question = models.ForeignKey('JuanmaappQuestion', models.DO_NOTHING)
#   
#       class Meta:
#           managed = False
#           db_table = 'juanmaapp_choice'
#   
#   
#   class JuanmaappFormup(models.Model):
#       uniprotid = models.CharField(db_column='UNIPROTid', max_length=20)  # Field name made lowercase.
#       iso = models.CharField(max_length=100)
#       mut = models.CharField(db_column='MUT', max_length=4)  # Field name made lowercase.
#       nam = models.CharField(db_column='Nam', max_length=30)  # Field name made lowercase.
#       organ = models.CharField(db_column='ORGAN', max_length=200)  # Field name made lowercase.
#       descmol = models.TextField(db_column='DescMOL')  # Field name made lowercase.
#       netc = models.IntegerField(db_column='NETc')  # Field name made lowercase.
#       inchi = models.TextField(db_column='INCHI')  # Field name made lowercase.
#       inchik = models.CharField(max_length=27)
#       smi = models.TextField(db_column='SMI')  # Field name made lowercase.
#       resnammol = models.CharField(db_column='resnamMOL', max_length=5)  # Field name made lowercase.
#       nummol = models.IntegerField(db_column='numMOL')  # Field name made lowercase.
#       mainprot = models.TextField(db_column='MAINprot')  # Field name made lowercase.
#       mainlig = models.TextField(db_column='MAINlig')  # Field name made lowercase.
#       ionresn = models.CharField(db_column='IONresn', max_length=5)  # Field name made lowercase.
#       ionnum = models.IntegerField(db_column='IONnum')  # Field name made lowercase.
#       comtyp = models.CharField(db_column='COMtyp', max_length=50)  # Field name made lowercase.
#       idprot = models.CharField(db_column='idproT', max_length=50)  # Field name made lowercase.
#       idcom = models.CharField(db_column='idcoM', max_length=50)  # Field name made lowercase.
#       msour = models.CharField(db_column='Msour', max_length=50)  # Field name made lowercase.
#       pdb = models.CharField(db_column='PDB', max_length=4)  # Field name made lowercase.
#       desc = models.TextField()
#       mtemp = models.TextField(db_column='mTEMP')  # Field name made lowercase.
#       meth = models.CharField(db_column='METH', max_length=50)  # Field name made lowercase.
#       soft = models.CharField(db_column='SOFT', max_length=50)  # Field name made lowercase.
#       softver = models.CharField(db_column='SOFTver', max_length=50)  # Field name made lowercase.
#       ffield = models.CharField(max_length=50)
#       memb = models.CharField(db_column='MEMB', max_length=50)  # Field name made lowercase.
#       solv = models.CharField(db_column='Solv', max_length=50)  # Field name made lowercase.
#       pdbcoor = models.CharField(db_column='PDBcoor', max_length=50)  # Field name made lowercase.
#       psf = models.CharField(db_column='PSF', max_length=50)  # Field name made lowercase.
#       toppsf = models.CharField(db_column='topPSF', max_length=50)  # Field name made lowercase.
#       par = models.CharField(max_length=50)
#       dcd = models.CharField(db_column='DCD', max_length=50)  # Field name made lowercase.
#   
#       class Meta:
#           managed = False
#           db_table = 'juanmaapp_formup'
#   
#   
#   class JuanmaappQuestion(models.Model):
#       question_text = models.CharField(max_length=200)
#       pub_date = models.DateTimeField()
#   
#       class Meta:
#           managed = False
#           db_table = 'juanmaapp_question'
    

class Ligand(models.Model):
    name = models.TextField()
    canonical = models.NullBooleanField()
    ambigious_alias = models.NullBooleanField()
    properities = models.ForeignKey('LigandProperities', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ligand'
        unique_together = (('name', 'canonical'),)


class LigandProperities(models.Model):
    smiles = models.TextField(blank=True, null=True)
    inchikey = models.CharField(unique=True, max_length=50, blank=True, null=True)
    ligand_type = models.ForeignKey('LigandType', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ligand_properities'


class LigandProperitiesWebLinks(models.Model):
    ligandproperities = models.ForeignKey(LigandProperities, models.DO_NOTHING)
    weblink = models.ForeignKey('WebLink', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ligand_properities_web_links'
        unique_together = (('ligandproperities', 'weblink'),)


class LigandRole(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ligand_role'


class LigandType(models.Model):
    slug = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'ligand_type'


class Mutation(models.Model):
    amino_acid = models.CharField(max_length=1)
    mutation_type = models.ForeignKey('MutationType', models.DO_NOTHING, blank=True, null=True)
    protein = models.ForeignKey('Protein', models.DO_NOTHING)
    residue = models.ForeignKey('Residue', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mutation'


class MutationExperiment(models.Model):
    wt_value = models.FloatField()
    wt_unit = models.CharField(max_length=10)
    mu_value = models.FloatField()
    mu_sign = models.CharField(max_length=2)
    foldchange = models.FloatField()
    exp_func = models.ForeignKey('MutationFunc', models.DO_NOTHING, blank=True, null=True)
    exp_measure = models.ForeignKey('MutationMeasure', models.DO_NOTHING, blank=True, null=True)
    exp_qual = models.ForeignKey('MutationQual', models.DO_NOTHING, blank=True, null=True)
    exp_type = models.ForeignKey('MutationExperimentalType', models.DO_NOTHING, blank=True, null=True)
    ligand = models.ForeignKey(Ligand, models.DO_NOTHING, blank=True, null=True, related_name='MutationExperiment_ligand_fky')
    ligand_ref = models.ForeignKey(Ligand, models.DO_NOTHING, blank=True, null=True, related_name='MutationExperiment_ligand_ref_fky' )
    ligand_role = models.ForeignKey(LigandRole, models.DO_NOTHING, blank=True, null=True)
    mutation = models.ForeignKey(Mutation, models.DO_NOTHING)
    optional = models.ForeignKey('MutationOpt', models.DO_NOTHING, blank=True, null=True)
    protein = models.ForeignKey('Protein', models.DO_NOTHING)
    raw = models.ForeignKey('MutationRaw', models.DO_NOTHING)
    refs = models.ForeignKey('Publication', models.DO_NOTHING, blank=True, null=True)
    residue = models.ForeignKey('Residue', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'mutation_experiment'


class MutationExperimentalType(models.Model):
    type = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_experimental_type'


class MutationFunc(models.Model):
    func = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_func'


class MutationLigandClass(models.Model):
    classname = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_ligand_class'


class MutationLigandReference(models.Model):
    reference = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_ligand_reference'


class MutationMeasure(models.Model):
    measure = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_measure'


class MutationOpt(models.Model):
    type = models.CharField(max_length=100)
    wt = models.FloatField()
    mu = models.FloatField()
    sign = models.CharField(max_length=2)
    percentage = models.FloatField()
    qual = models.CharField(max_length=100)
    agonist = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_opt'


class MutationQual(models.Model):
    qual = models.CharField(max_length=100)
    prop = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_qual'


class MutationRaw(models.Model):
    reference = models.CharField(max_length=100)
    protein = models.CharField(max_length=100)
    mutation_pos = models.SmallIntegerField()
    mutation_from = models.CharField(max_length=1)
    mutation_to = models.CharField(max_length=1)
    ligand_name = models.CharField(max_length=100)
    ligand_idtype = models.CharField(max_length=100)
    ligand_id = models.CharField(max_length=100)
    ligand_class = models.CharField(max_length=100)
    exp_type = models.CharField(max_length=100)
    exp_func = models.CharField(max_length=100)
    exp_wt_value = models.FloatField()
    exp_wt_unit = models.CharField(max_length=10)
    exp_mu_effect_type = models.CharField(max_length=100)
    exp_mu_effect_sign = models.CharField(max_length=2)
    exp_mu_effect_value = models.FloatField()
    exp_fold_change = models.FloatField()
    exp_mu_effect_qual = models.CharField(max_length=100)
    exp_mu_effect_ligand_prop = models.CharField(max_length=100)
    exp_mu_ligand_ref = models.CharField(max_length=100)
    opt_type = models.CharField(max_length=100)
    opt_wt = models.FloatField()
    opt_mu = models.FloatField()
    opt_sign = models.CharField(max_length=5)
    opt_percentage = models.FloatField()
    opt_qual = models.CharField(max_length=100)
    opt_agonist = models.CharField(max_length=100)
    added_by = models.CharField(max_length=100)
    added_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'mutation_raw'


class MutationType(models.Model):
    type = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'mutation_type'


class News(models.Model):
    image = models.TextField()
    date = models.DateField()
    html = models.TextField()

    class Meta:
        managed = False
        db_table = 'news'


class Protein(models.Model):
    entry_name = models.CharField(unique=True, max_length=100)
    accession = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200)
    sequence = models.TextField()
    family = models.ForeignKey('ProteinFamily', models.DO_NOTHING)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    residue_numbering_scheme = models.ForeignKey('ResidueGenericNumberingScheme', models.DO_NOTHING)
    sequence_type = models.ForeignKey('ProteinSequenceType', models.DO_NOTHING)
    source = models.ForeignKey('ProteinSource', models.DO_NOTHING)
    species = models.ForeignKey('Species', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein'


class ProteinAlias(models.Model):
    name = models.CharField(max_length=200)
    position = models.SmallIntegerField()
    protein = models.ForeignKey(Protein, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_alias'


class ProteinAnomaly(models.Model):
    anomaly_type = models.ForeignKey('ProteinAnomalyType', models.DO_NOTHING)
    generic_number = models.ForeignKey('ResidueGenericNumber', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_anomaly'
        unique_together = (('anomaly_type', 'generic_number'),)


class ProteinAnomalyRule(models.Model):
    amino_acid = models.CharField(max_length=1)
    negative = models.BooleanField()
    generic_number = models.ForeignKey('ResidueGenericNumber', models.DO_NOTHING)
    rule_set = models.ForeignKey('ProteinAnomalyRuleSet', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_anomaly_rule'


class ProteinAnomalyRuleSet(models.Model):
    exclusive = models.BooleanField()
    protein_anomaly = models.ForeignKey(ProteinAnomaly, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_anomaly_rule_set'


class ProteinAnomalyType(models.Model):
    slug = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'protein_anomaly_type'


class ProteinConformation(models.Model):
    protein = models.ForeignKey(Protein, models.DO_NOTHING)
    state = models.ForeignKey('ProteinState', models.DO_NOTHING)
    template_structure = models.ForeignKey('Structure', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'protein_conformation'


class ProteinConformationProteinAnomalies(models.Model):
    proteinconformation = models.ForeignKey(ProteinConformation, models.DO_NOTHING)
    proteinanomaly = models.ForeignKey(ProteinAnomaly, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_conformation_protein_anomalies'
        unique_together = (('proteinconformation', 'proteinanomaly'),)


class ProteinConformationTemplateStructure(models.Model):
    protein_conformation = models.ForeignKey(ProteinConformation, models.DO_NOTHING)
    protein_segment = models.ForeignKey('ProteinSegment', models.DO_NOTHING)
    structure = models.ForeignKey('Structure', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_conformation_template_structure'


class ProteinEndogenousLigands(models.Model):
    protein = models.ForeignKey(Protein, models.DO_NOTHING)
    ligand = models.ForeignKey(Ligand, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_endogenous_ligands'
        unique_together = (('protein', 'ligand'),)


class ProteinFamily(models.Model):
    slug = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'protein_family'


class ProteinFusion(models.Model):
    name = models.CharField(unique=True, max_length=100)
    sequence = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'protein_fusion'


class ProteinFusionProtein(models.Model):
    protein = models.ForeignKey(Protein, models.DO_NOTHING)
    protein_fusion = models.ForeignKey(ProteinFusion, models.DO_NOTHING)
    segment_after = models.ForeignKey('ProteinSegment',   models.DO_NOTHING,  related_name='ProteinFusionProtein_segment_after_fky')
    segment_before = models.ForeignKey('ProteinSegment',   models.DO_NOTHING, related_name='ProteinFusionProtein_segment_before_fky')

    class Meta:
        managed = False
        db_table = 'protein_fusion_protein'


class ProteinSegment(models.Model):
    slug = models.CharField(unique=True, max_length=100)
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    fully_aligned = models.BooleanField()
    partial = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'protein_segment'


class ProteinSequenceType(models.Model):
    slug = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'protein_sequence_type'


class ProteinSet(models.Model):
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'protein_set'


class ProteinSetProteins(models.Model):
    proteinset = models.ForeignKey(ProteinSet, models.DO_NOTHING)
    protein = models.ForeignKey(Protein, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_set_proteins'
        unique_together = (('proteinset', 'protein'),)


class ProteinSource(models.Model):
    name = models.CharField(unique=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'protein_source'


class ProteinState(models.Model):
    slug = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'protein_state'


class ProteinWebLinks(models.Model):
    protein = models.ForeignKey(Protein, models.DO_NOTHING)
    weblink = models.ForeignKey('WebLink', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'protein_web_links'
        unique_together = (('protein', 'weblink'),)


class Publication(models.Model):
    title = models.TextField()
    authors = models.TextField()
    year = models.IntegerField()
    reference = models.TextField()
    journal = models.ForeignKey('PublicationJournal', models.DO_NOTHING)
    web_link = models.ForeignKey('WebLink', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'publication'


class PublicationJournal(models.Model):
    slug = models.CharField(max_length=200, blank=True, null=True)
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'publication_journal'


class ReleaseNotes(models.Model):
    date = models.DateField()
    html = models.TextField()

    class Meta:
        managed = False
        db_table = 'release_notes'


class ReleaseStatistics(models.Model):
    value = models.IntegerField()
    release = models.ForeignKey(ReleaseNotes, models.DO_NOTHING)
    statistics_type = models.ForeignKey('ReleaseStatisticsType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'release_statistics'


class ReleaseStatisticsType(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'release_statistics_type'


class Residue(models.Model):
    sequence_number = models.SmallIntegerField()
    amino_acid = models.CharField(max_length=1)
    display_generic_number = models.ForeignKey('ResidueGenericNumber', models.DO_NOTHING, blank=True, null=True, related_name='Residue_display_generic_number_fky' )
    generic_number = models.ForeignKey('ResidueGenericNumber', models.DO_NOTHING, blank=True, null=True, related_name='Residue_generic_number_fky')
    protein_conformation = models.ForeignKey(ProteinConformation, models.DO_NOTHING)
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'residue'


class ResidueAlternativeGenericNumbers(models.Model):
    residue = models.ForeignKey(Residue, models.DO_NOTHING)
    residuegenericnumber = models.ForeignKey('ResidueGenericNumber', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'residue_alternative_generic_numbers'
        unique_together = (('residue', 'residuegenericnumber'),)


class ResidueGenericNumber(models.Model):
    label = models.CharField(max_length=10)
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING, blank=True, null=True)
    scheme = models.ForeignKey('ResidueGenericNumberingScheme', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'residue_generic_number'
        unique_together = (('scheme', 'label'),)


class ResidueGenericNumberEquivalent(models.Model):
    label = models.CharField(max_length=10)
    default_generic_number = models.ForeignKey(ResidueGenericNumber, models.DO_NOTHING)
    scheme = models.ForeignKey('ResidueGenericNumberingScheme', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'residue_generic_number_equivalent'
        unique_together = (('scheme', 'label'),)


class ResidueGenericNumberingScheme(models.Model):
    slug = models.CharField(max_length=20)
    short_name = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'residue_generic_numbering_scheme'


class ResidueSet(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'residue_set'


class ResidueSetResidue(models.Model):
    residueset = models.ForeignKey(ResidueSet, models.DO_NOTHING)
    residue = models.ForeignKey(Residue, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'residue_set_residue'
        unique_together = (('residueset', 'residue'),)


class Species(models.Model):
    latin_name = models.CharField(unique=True, max_length=100)
    common_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'species'


class Structure(models.Model):
    preferred_chain = models.CharField(max_length=20)
    resolution = models.DecimalField(max_digits=5, decimal_places=3)
    publication_date = models.DateField()
    representative = models.BooleanField()
    pdb_code = models.ForeignKey('WebLink', models.DO_NOTHING)
    pdb_data = models.ForeignKey('StructurePdbData', models.DO_NOTHING, blank=True, null=True)
    protein_conformation = models.ForeignKey(ProteinConformation, models.DO_NOTHING)
    publication = models.ForeignKey(Publication, models.DO_NOTHING, blank=True, null=True)
    state = models.ForeignKey(ProteinState, models.DO_NOTHING)
    structure_type = models.ForeignKey('StructureType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure'


class StructureCoordinates(models.Model):
    description = models.ForeignKey('StructureCoordinatesDescription', models.DO_NOTHING)
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_coordinates'


class StructureCoordinatesDescription(models.Model):
    text = models.CharField(unique=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'structure_coordinates_description'


class StructureEngineering(models.Model):
    description = models.ForeignKey('StructureEngineeringDescription', models.DO_NOTHING)
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_engineering'


class StructureEngineeringDescription(models.Model):
    text = models.CharField(unique=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'structure_engineering_description'


class StructureFragment(models.Model):
    ligand = models.ForeignKey(Ligand, models.DO_NOTHING)
    pdbdata = models.ForeignKey('StructurePdbData', models.DO_NOTHING)
    residue = models.ForeignKey(Residue, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_fragment'


class StructureModel(models.Model):
    pdb = models.TextField()
    main_template = models.ForeignKey(Structure, models.DO_NOTHING)
    protein = models.ForeignKey(Protein, models.DO_NOTHING)
    state = models.ForeignKey(ProteinState, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_model'


class StructureModelAnomalies(models.Model):
    reference = models.CharField(max_length=1)
    anomaly = models.ForeignKey(ProteinAnomaly, models.DO_NOTHING)
    homology_model = models.ForeignKey(StructureModel, models.DO_NOTHING)
    template = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_model_anomalies'


class StructureModelLoopTemplates(models.Model):
    homology_model = models.ForeignKey(StructureModel, models.DO_NOTHING)
    segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    template = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_model_loop_templates'


class StructureModelResidues(models.Model):
    sequence_number = models.IntegerField()
    origin = models.CharField(max_length=15)
    homology_model = models.ForeignKey(StructureModel, models.DO_NOTHING)
    residue = models.ForeignKey(Residue, models.DO_NOTHING)
    rotamer = models.ForeignKey('StructureRotamer', models.DO_NOTHING, blank=True, null=True)
    segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    template = models.ForeignKey(Structure, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'structure_model_residues'


class StructurePdbData(models.Model):
    pdb = models.TextField()

    class Meta:
        managed = False
        db_table = 'structure_pdb_data'


class StructureProteinAnomalies(models.Model):
    structure = models.ForeignKey(Structure, models.DO_NOTHING)
    proteinanomaly = models.ForeignKey(ProteinAnomaly, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_protein_anomalies'
        unique_together = (('structure', 'proteinanomaly'),)


class StructureRotamer(models.Model):
    pdbdata = models.ForeignKey(StructurePdbData, models.DO_NOTHING)
    residue = models.ForeignKey(Residue, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_rotamer'


class StructureSegment(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_segment'


class StructureSegmentModeling(models.Model):
    start = models.IntegerField()
    end = models.IntegerField()
    protein_segment = models.ForeignKey(ProteinSegment, models.DO_NOTHING)
    structure = models.ForeignKey(Structure, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_segment_modeling'


class StructureStabilizingAgent(models.Model):
    slug = models.CharField(unique=True, max_length=50)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'structure_stabilizing_agent'


class StructureStabilizingAgents(models.Model):
    structure = models.ForeignKey(Structure, models.DO_NOTHING)
    structurestabilizingagent = models.ForeignKey(StructureStabilizingAgent, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'structure_stabilizing_agents'
        unique_together = (('structure', 'structurestabilizingagent'),)


class StructureType(models.Model):
    slug = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'structure_type'


class WebLink(models.Model):
    index = models.TextField()
    web_resource = models.ForeignKey('WebResource', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'web_link'
        unique_together = (('web_resource', 'index'),)


class WebResource(models.Model):
    slug = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    url = models.TextField()

    class Meta:
        managed = False
        db_table = 'web_resource'

class Tableform(ModelForm):
    class Meta:
        model = DyndbFiles
#       fields = ['pub_date', 'headline', 'content', 'reporter']
        fields = '__all__'

#       class dyndb_Model(ModelForm):
#               model = DyndbModel
#               fields = '__all__'
#       
#       class dyndb_Files(ModelForm):
#           class Meta:
#               model = DyndbFiles
#               fields = '__all__'
#       
