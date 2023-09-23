from bs4 import BeautifulSoup
from requests import get
from contextlib import closing
import os
import re
import io

"""Funcion para realizar peticiones web"""
def get_req(url):
    with closing(get(url, stream = True)) as resp:
        html = BeautifulSoup(resp.content, 'html.parser')

    return html

# URLs
mainUrl = "http://www.ijmlc.org/list-6-1.html"
urlsLists = list()
urlsArticles = list()
articleNames = list()

# Peticion a la URL principal
mainHtml = get_req(mainUrl)

for link in mainHtml.find_all('a'):
    match = re.match('^http://www.ijmlc.org/list-[0-9]+-[0-9]+.html$', \
        link.get('href'))
    if match:
        urlsLists.append(match[0])

# Peticiones a las URLs con listas de articulos
for urlList in urlsLists[:50]:
    listHtml = get_req(urlList)
    for link in listHtml.find_all('a'):
        if link.get('href') != None:
            match = re.match('^http://www.ijmlc.org/index.php\?m=content\&c=index\&a=show\&catid=[0-9]+\&id=[0-9]+$', link.get('href'))
            if match:
                urlsArticles.append(match[0])

# Peticiones a las URLs con los articulos en PDFs
for urlArticle in urlsArticles:
    articleHtml = get_req(urlArticle)
    for link in articleHtml.find_all('a'):
        if link.get('href') != None:
            match = re.match('^vol[0-9]+/[0-9]+-[A-Z]+[0-9]+\.pdf$', \
                link.get('href'))
            if match:
                articleNames.append(match[0])

# Descarga de los archivos PDF
for articleName in articleNames[:250]:
    with closing(get('http://www.ijmlc.org/' + articleName, \
        stream = True)) as resp:
        nameArchive = re.search('^vol[0-9]+/([0-9]+-[A-Z]+[0-9]+)\.pdf$', \
            articleName)
        with open('pdf/' + nameArchive.group(1) + '.pdf', 'wb') as pdfFile:
            for chunk in resp.iter_content(chunk_size=1024): 
                if chunk:
                    pdfFile.write(chunk)

# Obtencion del texto de los PDFs
os.chdir('./corpus')
for pdf in os.listdir('../pdf'):
    nameArchive = re.search('^([0-9]+-[A-Z]+[0-9]+)\.pdf$', \
            pdf)
    bash = "pdf2txt.py -o " + nameArchive.group(1) + ".txt " + "../pdf/" + pdf
    os.system(bash)