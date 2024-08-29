
import feedparser
from datetime import datetime, timedelta
import sqlite3
import requests
from urllib.parse import quote
import sys
from bs4 import BeautifulSoup
import yaml
import requests
from utils import fetch_webpage_content, fetch_doi_from_url

DEBUG = True

class Article:
    def __init__(self, title, summary, link, doi, date_retrieved):

        self.title = title
        self.summary = summary
        self.link = link
        self.doi = doi
        self.date_retrieved = date_retrieved

        # Add more attributes for later logic

        self.read_later = False
        self.export = False
        self.exported = False
        self.delete_after = False
        self.read = False

    def __str__(self):
        return f"Title: {self.title}\nSummary: {self.summary}\nLink: {self.link}\n DOI: {self.doi}\n Date Retrieved: {self.date_retrieved}\n"

    def toggle_read(self):
        self.read = not self.read

    def toggle_read_later(self):
        self.read_later = not self.read_later

    def print_status(self):
        print(f"Title: {self.title}\nRead Later: {self.read_later}\nRead: {self.read}\nExport: {self.export}\nExported: {self.exported}\nDelete After: {self.delete_after}\n")


def construct_search_query(term, start_date, end_date):
    query = f'("{term}") AND (("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication]))'
    return query


def fetch_search_results(term, start_date, end_date, retmax=100, debug=False):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        'db': 'pubmed',
        'term': construct_search_query(term, start_date, end_date),
        'retmax': retmax,
        'retmode': 'json'
    }

    if debug:
        print(params['term'])
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(
            f"Error fetching search results: {response.status_code}")


def fetch_article_details(ids):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        'db': 'pubmed',
        'id': ','.join(ids),
        'retmode': 'xml'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(
            f"Error fetching article details: {response.status_code}")


def parse_article_details(xml_content):
    soup = BeautifulSoup(xml_content, 'xml')
    articles = []
    article_object_list = []
    date_retreived = datetime.now().strftime("%Y-%m-%d")

    for article in soup.find_all('PubmedArticle'):

        title = article.find('ArticleTitle').text
        abstract = article.find('AbstractText').text if article.find(
            'AbstractText') else 'No abstract available'
        link = f"https://pubmed.ncbi.nlm.nih.gov/{article.find('PMID').text}/"
        doi = article.find('ArticleId', {'IdType': 'doi'}).text if article.find(
            'ArticleId', {'IdType': 'doi'}) else 'No DOI available'

        article_object_list.append(
            Article(title, abstract, link, doi, date_retreived))

        articles.append({
            'title': title,
            'link': link,
            'summary': abstract,
            'doi': doi
        })

    return articles, article_object_list


def fetch_last_pubmed(term, days_prior=1):
    today = datetime.now()  # Get today's date
    start_date = today - timedelta(days=days_prior)  # Get the date 7 days ago

    # Format the time

    today = today.strftime("%Y/%m/%d")
    start_date = start_date.strftime("%Y/%m/%d")

    article_ids = fetch_search_results(term, start_date, today)[
        'esearchresult']['idlist']

    article_details = fetch_article_details(article_ids)
    _, article_objects = parse_article_details(article_details)

    return article_objects


def fetch_feed(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries


def retreive_date():
    return datetime.now().strftime("%Y-%m-%d")


def fetch_ejnmmi_physics_recent(debug=False):

    ejnmmi_physics_url = "https://ejnmmiphys.springeropen.com/articles/most-recent/rss.xml"

    feed = fetch_feed(ejnmmi_physics_url)
    date_retrieved = retreive_date()

    article_list = []

    for entry in feed:
        title = entry.title
        summary = entry.summary
        link = entry.link
        identifier = entry.id

        article = Article(title, summary, link, identifier, date_retrieved)

        article_list.append(article)

        if debug:

            print(article)

    return article_list


def fetch_jnm_ahead_of_print(debug=False):

    jnm_ahead_url = "https://jnm.snmjournals.org/rss/ahead.xml"

    feed = fetch_feed(jnm_ahead_url)
    date_retreived = retreive_date()

    article_list = []

    for entry in feed:
        title = entry.title
        summary = entry.summary
        link = entry.link
        identifier = entry.dc_identifier

        article = Article(title, summary, link, identifier, date_retreived)

        article_list.append(article)

        if debug:

            print(article)

    return article_list


def fetch_frontiers(debug=False):

    ejnmmi_url = "https://www.frontiersin.org/journals/nuclear-medicine/rss"

    feed = fetch_feed(ejnmmi_url)
    date_retreived = retreive_date()

    article_list = []

    for entry in feed:
        title = entry.title
        summary = entry.summary
        link = entry.link
        identifier = entry.id

        article = Article(title, summary, link, identifier, date_retreived)

        article_list.append(article)

        if debug:

            print(article)

    return article_list


def fetch_pubmed(debug=False):

    pubmed_url = "https://pubmed.ncbi.nlm.nih.gov/rss/search/1p1HIAUta7OjCZclRraaziC-Vfo8-D2DqHebJVS13P5gI7lYJ4/?limit=100&utm_campaign=pubmed-2&fc=20240718080630"

    feed = fetch_feed(pubmed_url)

    date_retreived = retreive_date()

    article_list = []

    for entry in feed:
        title = entry.title
        summary = entry.summary
        link = entry.link
        identifier = entry.id

        article = Article(title, summary, link, identifier, date_retreived)

        article_list.append(article)

        if debug:

            print(article)

    return article_list


def fetch_generic(rss_url, debug=False):

    if debug:
        print(f"Fetching from: {rss_url}")
    
    feed = fetch_feed(rss_url)
    date_retreived = retreive_date()

    if debug:
        print(f"Date retrieved: {date_retreived}")

    article_list = []

    for entry in feed:
        title = entry.title
        summary = entry.summary
        link = entry.link

        identifier = entry.id

        # Should in the end end up with a DOI

        if "10." in identifier:
            index_of_start_doi = identifier.index("10.")
            identifier = f"https://doi.org/{identifier[index_of_start_doi:]}"
            
            if debug:
                print(identifier)
                print("DOI found in identifier")

        else:
            doi_retrevied = fetch_doi_from_url(link)

            complete_doi = f"https://doi.org/{doi_retrevied}"
            identifier = complete_doi

            if debug:
                print(complete_doi)
                print("DOI not found in identifier")

        article = Article(title, summary, link, identifier, date_retreived)

        article_list.append(article)

        if debug:

            print(article)

    return article_list


def fetch_all_feeds(use_pre_defined=True):

    all_articles = []

    if use_pre_defined:

        rss_url_feeds = {
            "ejnmmi_physics": "https://ejnmmiphys.springeropen.com/articles/most-recent/rss.xml",
            "jnm_ahead": "https://jnm.snmjournals.org/rss/ahead.xml",
            "jnm_current": "https://jnm.snmjournals.org/rss/current.xml",
            "frontiers": "https://www.frontiersin.org/journals/nuclear-medicine/rss",
            "pubmed": "https://pubmed.ncbi.nlm.nih.gov/rss/search/1p1hiauta7ojczclrraazic-vfo8-d2dqhebjvs13p5gi7lyj4/?limit=100&utm_campaign=pubmed-2&fc=20240718080630"
        }

    for key, value in rss_url_feeds.items():
        tmp = fetch_generic(value, debug=False)
        all_articles.extend(tmp)

    return all_articles


def read_search_terms(file_path):
    with open(file_path, 'r') as file:
        search_terms = yaml.safe_load(file)

        return [item["term"] for item in search_terms["search_terms"]]
    
def read_rss_feeds(file_path):
    with open(file_path, 'r') as file:
        rss_urls = yaml.safe_load(file)

        return [item["feed"] for item in rss_urls["rss_feeds"]]

if __name__ == "__main__":

    from db_handling import insert_article

    terms = read_search_terms("src/pubmed_terms.yaml")
    rss_feeds = read_rss_feeds("src/rss_feeds.yaml")

    conn = sqlite3.connect('data/publications.db')

    for term in terms:

        last_articles = (fetch_last_pubmed(term, days_prior=3))

        for ar in last_articles:
            insert_article(conn, ar)

        if DEBUG:
            print(term, len(last_articles))
    
    if DEBUG:
        print("Done pubmed-fetching")

    for feed in rss_feeds:
            
            last_articles = fetch_generic(feed)
    
            for ar in last_articles:
                insert_article(conn, ar)
    
            if DEBUG:
                print(feed, len(last_articles))
    if DEBUG:
        print("Done feed-fetch")

    

    conn.close()
