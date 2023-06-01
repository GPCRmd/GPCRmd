import django
from django.db import models
from django.utils import timezone

# Create your models here.

class CovidModelProtein(models.Model):
    id_protein = models.ForeignKey('CovidProtein', null=True, on_delete=models.CASCADE)
    id_model = models.ForeignKey("CovidModel", null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'covid_model_protein'
        unique_together = (('id_protein', 'id_model'),)

class CovidModelFinalProtein(models.Model):
    id_final_protein = models.ForeignKey('CovidFinalProtein', null=True, on_delete=models.CASCADE)
    id_model = models.ForeignKey("CovidModel", null=True, on_delete=models.CASCADE)

    class Meta:
        managed = True
        db_table = 'covid_model_finalprotein'
        unique_together = (('id_final_protein', 'id_model'),)

class CovidFinalProtein(models.Model):
    name=models.CharField(max_length=50)

class CovidModel(models.Model):
    MODEL_TYPE=(
        (0,'Apoform (one single protein monomer)'),
        (1,'Complex')
    )
    MODEL_SOURCE=(
        (0,'Experimental structure'),
        (1,'Theoretical model')
    )
    type = models.SmallIntegerField(choices=MODEL_TYPE, default=0,null=False) 
    source = models.SmallIntegerField(choices=MODEL_SOURCE, default=0,null=False) 
    #id_protein = models.ForeignKey('DyndbProtein', models.DO_NOTHING,  db_column='id_protein',blank=True, null=True) 
    #id_complex_molecule = models.ForeignKey(DyndbComplexMolecule, models.DO_NOTHING, db_column='id_complex_molecule',blank=True, null=True) 
    pdbid = models.CharField(max_length=6, blank=True, null=True)
    #description = models.CharField(max_length=100, blank=True, null=True)
    #id_protein = models.ForeignKey('CovidProtein', blank=True, null=True, related_name="singleprot") 
    proteins = models.ManyToManyField('CovidProtein',through='CovidModelProtein')
    final_proteins = models.ManyToManyField('CovidFinalProtein',through='CovidModelFinalProtein')

    creation_timestamp = models.DateField(default=django.utils.timezone.now)
    class Meta:
        db_table = 'covid_model'


class CovidDynamicsComponents(models.Model):
    LIGAND_TYPE=(
        (0,'None'),
        (1,'Orthosteric'),
        (2,'Allosteric')
    )
    #id_molecule = models.ForeignKey('CovidMolecule', models.DO_NOTHING, db_column='id_molecule', null=True)
    id_dynamics = models.ForeignKey('CovidDynamics', db_column='id_dynamics', null=True, on_delete=models.DO_NOTHING)
    resname = models.CharField(max_length=4)
    molecule_name=models.CharField(max_length=200,blank=True, null=True)
    numberofmol = models.PositiveIntegerField(blank=True, null=True)
    creation_timestamp = models.DateField(default=django.utils.timezone.now)
    is_ligand= models.BooleanField(default=False)
    is_membrane= models.BooleanField(default=False)
    ligand_type = models.SmallIntegerField( choices=LIGAND_TYPE, default=0)
    is_solvent = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'covid_dynamics_components'
        unique_together = (('id_dynamics', 'resname'),)


class CovidDomains(models.Model):
    frompos =  models.IntegerField()
    topos = models.IntegerField()
    region_name =  models.CharField(max_length=200)
    uniprotkbac = models.CharField(max_length=10)
    note = models.CharField(max_length=200,blank=True, null=True)
    evidence = models.CharField(max_length=200,blank=True, null=True)
    domain_seq=models.CharField(max_length=1000,blank=True, null=True)

class CovidProteinFinalprotein(models.Model):
    id_protein = models.ForeignKey('CovidProtein', null=True, on_delete=models.CASCADE)
    id_finalprotein = models.ForeignKey("CovidFinalProtein", null=True, on_delete=models.CASCADE)
    finalprot_seq_start=models.IntegerField(blank=True, null=True)
    finalprot_seq_end=models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'covid_protein_finalprotein'
        unique_together = (('id_protein', 'id_finalprotein'),)


class CovidProtein(models.Model):
    uniprotkbac = models.CharField(max_length=10, blank=True, null=True)
    name = models.TextField(blank=True, null=True)
    uniprot_entry= models.CharField(max_length=11, blank=True, null=True)
    species = models.TextField(max_length=200,null=True,blank=True)
    creation_timestamp = models.DateTimeField(default=django.utils.timezone.now)
    final_proteins = models.ManyToManyField('CovidFinalProtein',through='CovidProteinFinalprotein')

    class Meta:
        managed = True
        db_table = 'covid_protein'

class CovidDynamics(models.Model):
    creation_timestamp = models.DateField(default=django.utils.timezone.now)
    author_first_name=models.CharField(max_length=200)
    author_last_name=models.CharField(max_length=200,blank=True, null=True)
    author_institution=models.CharField(max_length=200,blank=True, null=True)
    citation = models.CharField(max_length=1000, blank=True, null=True)
    doi = models.CharField("DOI", help_text="Digital object identifier.",  max_length=80, blank=True, null=True)
    dyn_name=models.CharField(max_length=200)
    id_model = models.ForeignKey('CovidModel', blank=True, null=True, on_delete=models.DO_NOTHING)
    is_published= models.BooleanField(default=False)
    is_shared_sc2md= models.BooleanField(default=False)
    #delta = models.FloatField(blank=False, null=False)
    delta = models.FloatField(null=True)
    timestep = models.FloatField(blank=True, null=True)
    atom_num = models.IntegerField(blank=True, null=True)
    software = models.CharField(max_length=100, blank=True, null=True)
    sversion = models.CharField(max_length=15, blank=True, null=True)
    ff = models.CharField(max_length=20, blank=True, null=True)
    ffversion = models.CharField(max_length=15, blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True, null=True)
    extracted_from_db=models.CharField(max_length=200,blank=True, null=True)
    extracted_from_db_entry=models.CharField(max_length=200,blank=True, null=True)

    solvent_types=(
        (0,'Unknown'),#Not shown in report
        (1,'Implicit'),
        (2,'None'),#Shown in report as 'None'
        (3,'Other'),
        (4,'TIP3P'),
        (5,'TIP4P'),
        (6,'TIPS'),
        (7,'SPC'),
        (8,'OPC'),
    )
    solvent_type = models.SmallIntegerField( choices=solvent_types, default=0)
    solvent_is_filtered= models.BooleanField(default=False)

    class Meta:
        db_table = 'covid_dynamics'

class CovidFiles(models.Model):
    filename = models.CharField(unique=True, max_length=80)
    id_file_types = models.ForeignKey("dynadb.DyndbFileTypes", null=True, on_delete=models.DO_NOTHING) 
    creation_timestamp = models.DateTimeField(default=django.utils.timezone.now)
    filepath = models.CharField(max_length=520, blank=True, null=True)
    url = models.CharField(max_length=520, blank=True, null=True)
    class Meta:
        db_table = 'covid_files'

class CovidFilesDynamics(models.Model):
    file_types=(
        (0, 'Input coordinates'),
        (1, 'Input topology'),
        (2, 'Trajectory'),
        (3, 'Parameters'),
        (4, 'Others'),
    )
    id_dynamics = models.ForeignKey('CovidDynamics', null=True, on_delete=models.DO_NOTHING) 
    id_files = models.ForeignKey('CovidFiles', null=True, on_delete=models.DO_NOTHING)
    framenum = models.PositiveIntegerField(null=True,blank=True,default=None)
    type = models.SmallIntegerField( choices=file_types, default=0)


    class Meta:
        db_table = 'covid_files_dynamics'
        unique_together = (('id_dynamics', 'id_files','type'),)

class CovidModelSeqPositions(models.Model):
    id_file = models.ForeignKey('CovidFiles', on_delete=models.CASCADE)     
    seqpos = models.IntegerField()
    aa =  models.CharField(max_length=1)
    chainid =  models.CharField(max_length=1,null=True,blank=True)
    id_uniprotpos= models.ForeignKey('CovidUniprotSeqPositions',null=True,blank=True, on_delete=models.CASCADE)    
    ca_atom_index=models.PositiveIntegerField(null=True,blank=True,default=None)


class CovidUniprotSeqPositions(models.Model):
    id_protein = models.ForeignKey('CovidProtein', on_delete=models.CASCADE)     
    seqpos = models.IntegerField()
    aa =  models.CharField(max_length=1)
    #models_position = models.ManyToManyField('CovidModelSeqPositions',through='CovidSeqPositionsUniprotModel',blank=True)
    class Meta:
        db_table = 'covid_uniprot_seq_positions'
        unique_together = (('id_protein', 'seqpos','aa'),)


class CovidMutfuncDataInterface(models.Model):
    id_mutfunc_data = models.ForeignKey('CovidMutfuncData', blank=True, null=True, on_delete=models.DO_NOTHING)

    int_uniprot=models.CharField(max_length=10,null=True, blank=True)
    interaction_energy=models.FloatField(null=True, blank=True)
    diff_interface_residues=models.FloatField(null=True, blank=True)
    int_name=models.CharField(max_length=100,null=True, blank=True)
    int_template=models.CharField(max_length=8,null=True, blank=True)
    diff_interaction_energy=models.FloatField(null=True, blank=True)

class CovidMutfuncData(models.Model):
    id_final_protein = models.ForeignKey('CovidFinalProtein', blank=True, null=True, on_delete=models.DO_NOTHING)

    mutfunc_name=models.CharField(max_length=10,null=True, blank=True)
    uniprot=models.CharField(max_length=10,null=True, blank=True)
    position=models.SmallIntegerField(null=True, blank=True)
    wt= models.CharField(max_length=1, null=True, blank=True)
    mut= models.CharField(max_length=1, null=True, blank=True)
    freq=models.FloatField(null=True, blank=True)
    freqpermille=models.FloatField(null=True, blank=True)
    ptm=models.CharField(max_length=100,null=True, blank=True)
    sift_score=models.FloatField(null=True, blank=True)
    sift_median=models.FloatField(null=True, blank=True)
    template=models.CharField(max_length=8,null=True, blank=True)
    relative_surface_accessibility=models.FloatField(null=True, blank=True)
    foldx_ddg=models.FloatField(null=True, blank=True)
    mut_escape_mean=models.FloatField(null=True, blank=True)
    mut_escape_max=models.FloatField(null=True, blank=True)
    annotation=models.CharField(max_length=1000,null=True, blank=True)

    class Meta:
        unique_together = (('mutfunc_name', 'position', 'mut'),)


class CovidIsolate(models.Model):
    isolate_name = models.CharField(max_length=200, blank=True, null=True) #   hCoV-19/Wuhan/WIV04/2019
    isolate_date =  models.DateField(blank=True, null=True) #                 2019-12-30
    isolate_id = models.CharField(max_length=100, unique=True) #             EPI_ISL_402124
    history = models.CharField(max_length=200, blank=True, null=True) #                   Original
    tloc = models.CharField(max_length=200, blank=True, null=True) #             hCoV-19^^Hubei
    host = models.CharField(max_length=200, blank=True, null=True) #                      Human
    originating_lab = models.CharField(max_length=500, blank=True, null=True) #   Wuhan Jinyintan Hospital
    submitting_lab = models.CharField(max_length=500, blank=True, null=True) #Wuhan Institute of Virology
    submitter = models.CharField(max_length=500, blank=True, null=True) #Wuhan Institute of Virology
    location = models.CharField(max_length=200, blank=True, null=True) #                      Hubei
    isolate_type = models.CharField(max_length=200, blank=True, null=True) #                    hCoV-19



#class CovidMutations(models.Model):
#    resid = models.SmallIntegerField(null=True)
#    resletter_from = models.CharField(max_length=1, null=True)
#    resletter_to = models.CharField(max_length=1, null=True)
#    id_sequence = models.ForeignKey('CovidSequence', models.DO_NOTHING, blank=True, null=True)


#class CovidMutatedPosMutation(models.Model):
#    id_mutated_pos = models.ForeignKey('CovidMutatedPos', null=True)
#    id_mutation_fromto = models.ForeignKey("CovidMutation", null=True)
#    class Meta:
#        managed = True
#        unique_together = (('id_mutated_pos', 'id_mutation_fromto'),)
#
#class CovidMutation(models.Model):
#    resletter_from = models.CharField(max_length=1, null=True)
#    resletter_to = models.CharField(max_length=1, null=True)
#    class Meta:
#        unique_together = (('resletter_from', 'resletter_to'),)


class CovidSequenceMutatedPos(models.Model):
    id_mutated_pos = models.ForeignKey('CovidMutatedPos', null=True, on_delete=models.CASCADE)
    id_sequence = models.ForeignKey("CovidSequence", null=True, on_delete=models.CASCADE)
    class Meta:
        managed = True
        unique_together = (('id_mutated_pos', 'id_sequence'),)


class CovidMutatedPos(models.Model):
   # id_sequence = models.ForeignKey('CovidSequence', models.DO_NOTHING, blank=True, null=True)
    id_final_protein = models.ForeignKey('CovidFinalProtein', blank=True, null=True, on_delete=models.DO_NOTHING)
    resid = models.SmallIntegerField(null=True)

    resletter_from = models.CharField(max_length=1, null=True)
    resletter_to = models.CharField(max_length=1, null=True)


    #pos_mutations = models.ManyToManyField('CovidMutation',through='CovidMutatedPosMutation')
    class Meta:
        unique_together = (('resid', 'id_final_protein','resletter_from','resletter_to'),)

class CovidSequence(models.Model):
    is_wt= models.BooleanField(default=True)
    seq= models.CharField(max_length=3000,blank=True, null=True)
    seq_idx_table = models.IntegerField(unique=True,blank=True, null=True)
    seq_mutations = models.ManyToManyField('CovidMutatedPos',through='CovidSequenceMutatedPos')


class CovidSequencedGene(models.Model):
    id_final_protein = models.ForeignKey('CovidFinalProtein', blank=True, null=True, on_delete=models.DO_NOTHING)
    id_isolate = models.ForeignKey('CovidIsolate', blank=True, null=True, on_delete=models.DO_NOTHING)
    id_sequence = models.ForeignKey('CovidSequence', blank=True, null=True, on_delete=models.DO_NOTHING)
    alt_name = models.CharField(max_length=50, blank=True, null=True)