from bs4 import BeautifulSoup
from urllib.request import Request, urlopen 
import re 

req = Request('https://opm.phar.umich.edu/proteins?search=4dkl', headers={'User-Agent': 'Mozilla/5.0'})
html_page = urlopen(req).read()

soup = BeautifulSoup(html_page, 'html.parser')
print(soup)
links = []
for link in soup.findAll('a', attrs={'href': re.compile("^/movie/")}):
    links.append(link.get('href'))
