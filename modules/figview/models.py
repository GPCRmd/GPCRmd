from django.db import models

class Figview(models.Model):
    #Basic set 
    # defines the type of data
    title = models.TextField()
    figname = models.TextField()
    date = models.DateField()
    figfile = models.TextField()
    strucfile = models.TextField()

    def __str__(self):
        return self.title

    class Meta():
        db_table = "figview"