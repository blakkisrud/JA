"""
Test code to run smaller parts of the code base to check functionality
of the listening and parsing functions

When this test passes, a database is made with the correct links, DOIs and
set ups

"""

import os
import sys
import pickle as pc

from db_handling import make_and_insert
from rss_feed_listener import Article, fetch_all_feeds, fetch_generic
from utils import fetch_doi_from_url

test_object_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_objects"))
test_database_name = "test.db"
#rss_url =  "https://jnm.snmjournals.org/rss/ahead.xml"
#rss_url =  "https://ejnmmiphys.springeropen.com/articles/most-recent/rss.xml"
#rss_url =  "https://jnm.snmjournals.org/rss/ahead.xml"
#rss_url =  "https://jnm.snmjournals.org/rss/current.xml"
rss_url =  "https://www.frontiersin.org/journals/nuclear-medicine/rss"
#rss_url =  "https://pubmed.ncbi.nlm.nih.gov/rss/search/1p1hiauta7ojczclrraazic-vfo8-d2dqhebjvs13p5gi7lyj4/?limit=100&utm_campaign=pubmed-2&fc=20240718080630"

#make_and_insert(db_name=test_database_name)

articles = fetch_generic(rss_url, debug=True)

## pickle some articles
#with open(os.path.join(test_object_path, "articles.pkl"), "wb") as f:
#    pc.dump(articles, f)

# unpickle some articles

#with open(os.path.join(test_object_path, "articles.pkl"), "rb") as f:
#    articles = pc.load(f)

sys.exit()

print(articles[50].doi)

if "10." not in articles[50].doi:
    print("DOI not found in article 50")
    print(articles[50].doi)

    doi_retreived = fetch_doi_from_url(articles[50].doi)

    complete_doi = f"https://doi.org/{doi_retreived}"

    print(complete_doi)

else:
    print("DOI found in article 50")
    print(articles[50].doi)








