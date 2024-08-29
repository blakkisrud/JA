"""

Script(s) to form the digest, potentially
from a template.

Step 1 - make a markdown-file

"""

import feedparser
import sqlite3
from datetime import datetime
from rss_feed_listener import Article
from db_handling import get_articles, update_article
import requests
import sys
from bs4 import BeautifulSoup
import os
from tqdm import tqdm

# Here import the utils

path_to_digest = "digests"

url = "http://jnm.snmjournals.org/cgi/content/short/jnumed.124.267966v1?rss=1"

def fetch_doi_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        doi = soup.find("meta", {"name": "citation_doi"})['content']
        return doi
    else:
        raise Exception(f"Error fetching webpage: {response.status_code}")

def fetch_reference_by_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['message']
    else:
        raise Exception(f"Error fetching data for DOI {doi}: {response.status_code}")
    
def create_bibtex(reference_data):
    bibtex = f"""
@article{{{reference_data.get('DOI', '')},
    title={{ {reference_data.get('title', [''])[0]} }},
    author={{ { ' and '.join([f"{author['family']}, {author['given']}" for author in reference_data.get('author', [])])} }},
    journal={{ {reference_data.get('container-title', [''])[0]} }},
    volume={{ {reference_data.get('volume', '')} }},
    number={{ {reference_data.get('issue', '')} }},
    pages={{ {reference_data.get('page', '')} }},
    year={{ {reference_data.get('published-print', {}).get('date-parts', [[None]])[0][0]} }},
    publisher={{ {reference_data.get('publisher', '')} }},
    doi={{ {reference_data.get('DOI', '')} }},
    url={{ {reference_data.get('URL', '')} }}
}}
    """
    return bibtex

def fetch_reference_by_pmid(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['result'][str(pmid)]
    else:
        raise Exception(f"Error fetching data for PMID {pmid}: {response.status_code}")

def create_bibtex_from_pubmed(pubmed_data):
    authors = []
    if 'authors' in pubmed_data:
        authors = [f"{author['name']}" for author in pubmed_data['authors']]
    
    bibtex = f"""
@article{{{pubmed_data['uid']},
    title={{ {pubmed_data['title']} }},
    author={{ { ' and '.join(authors)} }},
    journal={{ {pubmed_data['source']} }},
    volume={{ {pubmed_data.get('volume', '')} }},
    issue={{ {pubmed_data.get('issue', '')} }},
    pages={{ {pubmed_data.get('pages', '')} }},
    year={{ {pubmed_data.get('pubdate', '')} }},
    pmid={{ {pubmed_data['uid']} }},
    url={{ https://pubmed.ncbi.nlm.nih.gov/{pubmed_data['uid']} }}
}}
    """
    return bibtex

pmid_test = "39083067"

def link_to_bib(link):

    if "pubmed" in link:
        pmid = link.split("/")[-2] # Magic number
        reference_data = fetch_reference_by_pmid(pmid)
        bib = create_bibtex_from_pubmed(reference_data)
        return bib
    
    elif "/10." in link:
        doi = link.split("/")[-2:]
        doi = "/".join(doi)
        reference_data = fetch_reference_by_doi(doi)
        bib = create_bibtex(reference_data)
        return bib
    
    else:
        print("Trying to fetch DOI from url")

        try:

            doi = fetch_doi_from_url(link)
            reference_data = fetch_reference_by_doi(doi)
            bib = create_bibtex(reference_data)
            return bib
        
        except Exception as e:
            print(e)

    return None

link = "https://pubmed.ncbi.nlm.nih.gov/39037596/?utm_source=Other&utm_medium=rss&utm_campaign=pubmed-2&utm_content=1p1HIAUta7OjCZclRraaziC-Vfo8-D2DqHebJVS13P5gI7lYJ4&fc=20240718080630&ff=20240801100808&v=2.18.0.post9+e462414"
bib = link_to_bib(link)
print(bib)

def make_digest(debug = False, database_path = "data/publications.db"):
    if debug:
        print("Beginning making digest")

    digest = []
    bib_elements = []

    today = datetime.now().strftime("%Y-%m-%d")
    today_timestamp = datetime.now().strftime("%Y-%m-%d_%H_%M_%S")

    digest.append(f"# Digest for {today}")

    conn = sqlite3.connect(database_path)
    articles = get_articles(conn, keep_open=True, only_exported=True)

    for i in tqdm(range(len(articles)), desc="Constructing digest"):

        for art in articles:
            digest.append("# " + art.title)
            digest.append(art.summary)
            digest.append(art.link)
            digest.append("\n")

            # Extract doi

            link = art.link
            try:
                bib = link_to_bib(link)

                if bib == None:
                    print(f"Could not fetch bib for {link}")

                bib_elements.append(bib)

            except Exception as e:
                print(e)

            # Set the article to exported

            art.exported = True

            # Update the article

            update_article(conn, art)


    conn.close()

    file_content = "\n".join(digest)
    bib_content = "\n".join(bib_elements)

    # Remove non-utf-8 characters

    file_content = file_content.encode("ascii", errors="ignore").decode()
    bib_content = bib_content.encode("ascii", errors="ignore").decode()

    # File names

    digest_markdown = os.path.join(path_to_digest, f"digest_{today_timestamp}.md")
    digest_bib = os.path.join(path_to_digest, f"digest_{today_timestamp}.bib")

    with open(digest_markdown, "w") as f:
        f.write(file_content)

    with open(digest_bib, "w") as f:
        f.write(bib_content)

make_digest()

