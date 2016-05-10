
class DyndbModeledResidues(models.Model):
    SOURCE_TYPE=(
        ('ABINIT','Ab-initio'),
        ('HOMOL','Homology'),
        ('Thread','Threading'),
        ('OTHER','Other Computational Methods')
    )
    id_protein = models.IntegerField(blank=True, null=True)
    id_model = models.ForeignKey(DyndbModel,  models.DO_NOTHING, db_column='id_model', related_name='DyndbModeledResidues_id_model_fky')
    chain = models.CharField(max_length=1)
    resid_from = models.SmallIntegerField()
    resid_to = models.SmallIntegerField()
    pdbid = models.CharField(max_length=6, blank=True, null=True)
    source_type = models.CharField(max_length=8, choices=SOURCE_TYPE, default=SOURCE_TYPE)
    template_id_model = models.ForeignKey(DyndbModel, models.DO_NOTHING, db_column='template_id_model', blank=True, null=True, related_name='DyndbModeledResidues_template_id_protein_fky')

    class Meta:
        managed = False
        db_table = 'dyndb_modeled_residues'

