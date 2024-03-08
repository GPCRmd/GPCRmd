from django.db import models

# Create your models here.

class News(models.Model):
    #Basic set 
    # defines the type of data
    image = models.TextField()
    date = models.DateField()
    html = models.TextField()

    def __str__(self):
        return self.title

    class Meta():
        db_table = "news"
        
class Article(models.Model):
    doi = models.CharField("DOI", unique=True, max_length=80, blank=True, null=True)
    authors = models.CharField("Authors", max_length=1000, blank=True, null=True)
    title = models.CharField("Title", max_length=900, blank=True, null=True)
    abstract = models.TextField("Abstract", blank=True, null=True)
    pmid = models.IntegerField("PMID", unique=True, blank=True, null=True)
    journal = models.CharField("Journal or Press", max_length=200, blank=True, null=True)
    pub_year = models.SmallIntegerField("Publication year", blank=True, null=True)
    issue = models.CharField("Issue", max_length=10, blank=True, null=True)
    volume = models.CharField("Volume", max_length=10, blank=True, null=True)
    pages = models.CharField("Pages", max_length=16, blank=True, null=True)
    url = models.URLField("URL", max_length=250, blank=True, null=True)
    url_image = models.URLField("URL image", max_length=1000, blank=True, null=True)
    date = models.DateTimeField() 
    
    class Meta():
        db_table = "article"
    
