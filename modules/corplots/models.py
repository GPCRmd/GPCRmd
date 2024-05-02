from django.db import models

# Create your models here.
class Corplots(models.Model):
    dyn_id = models.IntegerField(blank=True, null=True)
    drug = models.CharField(max_length=30, blank=True, null=True)
    name = models.TextField(max_length=100,null=False,blank=False) 
    receptor = models.CharField(max_length=30, blank=True, null=True)

    class Meta():
        db_table = "corplots"