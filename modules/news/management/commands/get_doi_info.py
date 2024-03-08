import requests
import re
import json
from unidecode import unidecode

def doitopmid(doi):
    """
    Return the PMID for a given DOI.
    """

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=" + doi + "&format=json"
    r = requests.get(url)
    return r.text


def doitobib(doi):
  """
  Return a bibTeX string of metadata for a given DOI.
  """

  url = "https://doi.org/" + doi

  headers = {"accept": "application/x-bibtex"}
  r = requests.get(url, headers = headers)

  return r.text

# Indicate the doi where we will obtain the data
doi = "10.1038/s41586-023-05789-z"
doi = "10.1093/bioinformatics/btaa117"

# Obtain the information from doi
info = doitobib(doi)
print(info)
# Clean the data
info = info.replace("\n", "").replace("\t", "").split(",") 

auth_switch = 0
authors = ""

# Extract info and store it on different variables
for data in info: 
#    if "doi" in data: #DOI
#        l_doi = data.split("{")
#        doi = l_doi[-1].replace("}","")
    if "title" in data: #Title
        auth_switch = 0
        l_title = data.split("=")
        title = l_title[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "journal" in data: #Journal or Press
        auth_switch = 0
        l_journal = data.split("=")
        journal = l_journal[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "year" in data: #Publication year::
        auth_switch = 0
        l_year = data.split("=")
        year = l_year[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "number" in data: #Issue:
        auth_switch = 0
        l_number= data.split("=")
        number = l_number[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "volume" in data: #Volume:
        auth_switch = 0
        l_volume = data.split("=")
        volume = l_volume[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "pages" in data: #Pages:
        auth_switch = 0
        l_pages = data.split("=")
        pages = l_pages[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "url" in data: #URL:
        auth_switch = 0
        l_url = data.split("=")
        ref_url = l_url[-1].replace("{","").replace("}","").rstrip().lstrip()
    elif "editor" in data: 
        auth_switch = 0
    elif "author" in data or auth_switch == 1: #Author
        auth_switch = 1
        print(data)
        if "=" in data:
            l_auth = data.split("=")
            auth = l_auth[-1].replace("{","").replace("\\", "").replace("'","").replace("}","")
        else:
            auth = data
        # auth =re.sub("[^A-Z0-9_\s-]", "", auth,0,re.IGNORECASE)
        if authors == "":#First author 
            authors = unidecode(auth).replace(" ,",",").replace("}","").rstrip().lstrip()
        else:
            authors = authors + ", " + unidecode(auth).replace(" ,",",").replace("}","").rstrip().lstrip()
        print(authors)

# Get PMID from PUBMED with DOI
info_pubmed = doitopmid(doi)
info_pubmed_dict = json.loads(info_pubmed)
pmid = info_pubmed_dict["esearchresult"]["idlist"][0]# PMID:

print("DOI: " + doi)
print("Authors: " + authors)
print("Title: " + title)
print("PMID: " + pmid)
print("Journal: " + journal)
print("Publication year: " + year)
print("Issue: " + number)
print("Volume: " + volume)
print("Pages: " + pages)
print("Url: " + ref_url)





