import pandas as pd
import requests
import re 
import json
from unidecode import unidecode
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError

from django.db.models import CharField,TextField, Case, When, Value as V, F, Q, Count, Prefetch
from modules.dynadb.models import DyndbDynamics, DyndbReferencesDynamics, DyndbReferences
from modules.news.models import Article

def doitopmid(doi):
    """
    Return the PMID for a given DOI.
    """

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + doi + "&format=json"
    r = requests.get(url)
    info_pubmed_dict = json.loads(r.text)
    pmid = info_pubmed_dict["esearchresult"]["idlist"][0]# PMID:
    return str(pmid)

def pmidtoabstract(pmid):
    """
    Get abstract from pmid
    """

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="+ pmid + "&retmode=XML&rettype=abstract" 
    print(url)
    #   headers = {"accept": "application/x-bibtex"}
    r = requests.get(url) #, headers = headers)
    pubmed = r.text
    #   p_list = pubmed.split("")
    if "AbstractText" in pubmed:
        abstract = re.search(r'AbstractText.*?>(.*?)<\/AbstractText', pubmed).group(1)
    else:
        abstract = ""
    return unidecode(BeautifulSoup(abstract, "lxml").text)

class Command(BaseCommand):
    help = "Get individual contributions."
    
    def handle(self, *args, **kwargs):
        # Get published, individual dynamics 
        dynobj=DyndbDynamics.objects.filter(is_published=True).filter(submission_id__is_gpcrmd_community=False)
        dyn_ids = dynobj.values_list("id")
        
        # Get references of this dynamics
        dynref=DyndbReferencesDynamics.objects.filter(id_dynamics__in = list(dyn_ids))
        ref_ids = dynref.values_list("id_references").distinct().values_list('id_references',flat=True)
        # data
        gpcrmd_refs = DyndbReferences.objects.filter(id__in = list(ref_ids))
        
        gpcrmd_refs_dois = Article.objects.all().values_list("doi").distinct().values_list('doi', flat=True)
        for ref in gpcrmd_refs:
            try:
                pmid = doitopmid(ref.doi)
                abstract = pmidtoabstract(pmid)
                if not ref.doi in gpcrmd_refs_dois:
                    entry = Article(doi = ref.doi, 
                                    authors = ref.authors, 
                                    title = ref.title, 
                                    abstract = abstract,
                                    pmid = pmid, 
                                    journal = ref.journal_press, 
                                    pub_year = ref.pub_year, 
                                    issue = ref.issue, 
                                    volume = ref.volume, 
                                    pages = ref.pages, 
                                    url = ref.url, 
                                    url_image = "", 
                                    date=ref.creation_timestamp
                    )
                    entry.save()
                    print(f"{ref.doi} - New article!")
                else:
                    print(f"{ref.doi} - Already in the database!")

            except:
                print(f"Error in {ref.doi}")
