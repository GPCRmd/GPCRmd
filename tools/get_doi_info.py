import requests
import re
import json

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
doi = "10.1093/bioinformatics/btaa117"

# Obtain the information from doi
info = doitobib(doi)

# Clean the data
info = info.replace("\n", "").replace("\t", "").split(",") 

# Extract info and store it on different variables
for data in info: 
    if "doi =" in data: #DOI
        l_doi = data.split("{")
        doi = l_doi[-1].replace("}","")
    elif "author =" in data: #Author
        l_auth = data.split("=")
        auth = l_auth[-1].replace("{","").replace("\\", "").replace("'","").replace("}","")
        auth =re.sub("[^A-Z0-9_\s-]", "", auth,0,re.IGNORECASE).replace("and", ",").replace(" ,",",")[1:]
    elif "title =" in data: #Title
        l_title = data.split("=")
        title = l_title[-1].replace("{","").replace("}","")[1:]
    elif "journal =" in data: #Journal or Press
        l_journal = data.split("=")
        journal = l_journal[-1].replace("{","").replace("}","")[1:]
    elif "year =" in data: #Publication year::
        l_year = data.split("=")
        year = l_year[-1][1:]
    elif "number =" in data: #Issue:
        l_number= data.split("=")
        number = l_number[-1].replace("{","").replace("}","")[1:]
    elif "volume =" in data: #Volume:
        l_volume = data.split("=")
        volume = l_volume[-1].replace("{","").replace("}","")[1:]
    elif "pages =" in data: #Pages:
        l_pages = data.split("=")
        pages = l_pages[-1].replace("{","").replace("}","")[1:]
    elif "url =" in data: #URL:
        l_url = data.split("=")
        url = l_url[-1].replace("{","").replace("}","")[1:]

# Get PMID from PUBMED with DOI
info_pubmed = doitopmid(doi)
info_pubmed_dict = json.loads(info_pubmed)
pmid = info_pubmed_dict["esearchresult"]["idlist"][0]# PMID:

print("DOI: " + doi)
print("Authors: " + auth)
print("Title: " + title)
print("PMID: " + pmid)
print("Journal: " + journal)
print("Publication year: " + year)
print("Issue: " + number)
print("Volume: " + volume)
print("Pages: " + pages)
print("Url: " + url)





