from django.db import models 
from modules.dynadb.models import DyndbDynamics, DyndbFileTypes

# # Create your models here. 
class AllDownloads(models.Model):
    tmpname = models.CharField(unique=True, max_length=80)
    dyn_ids = models.CharField(max_length=1000)
    creation_timestamp = models.DateTimeField()
    created_by_dbengine = models.CharField(max_length=40)
    created_by = models.IntegerField(blank=True, null=True)
    filepath = models.CharField(max_length=520, blank=True, null=True)
    class Meta:
        managed = True
        db_table = 'download_files'