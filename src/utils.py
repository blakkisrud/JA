"""

Utlitiy functions for the rss-feed-reader

This is a work-around to avoid circular imports. The functions in this file are used in multiple modules.

"""

import requests
from bs4 import BeautifulSoup

def fetch_webpage_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error fetching webpage: {response.status_code}")

def fetch_doi_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            doi = soup.find("meta", {"name": "citation_doi"})['content']
        except:
            doi = None

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