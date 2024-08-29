"""
Script to have the database handling for the application
"""

import sqlite3
from datetime import datetime

from rss_feed_listener import Article
import rss_feed_listener as rss_l

import os

def create_table(conn):
    create_table_sql = """ CREATE TABLE IF NOT EXISTS articles (
										id integer PRIMARY KEY,
										title text NOT NULL,
										summary text,
										link text NOT NULL,
										doi text NOT NULL UNIQUE,
										date_retrieved text NOT NULL,
                                        read_later boolean NOT NULL,
										export boolean NOT NULL,
										exported boolean NOT NULL,
										delete_after boolean NOT NULL,
                                        read boolean NOT NULL
									); """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def insert_article(conn, article):
    sql = ''' INSERT OR IGNORE INTO articles(title, summary, link, doi, date_retrieved, read_later, export, exported, delete_after, read)
              VALUES(?,?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (
            article.title, 
            article.summary, 
            article.link, 
            article.doi, 
            article.date_retrieved, 
            article.read_later, 
            article.export, 
            article.exported, 
            article.delete_after,
            article.read))
        conn.commit()
        return cur.lastrowid
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def get_articles(conn, keep_open = False, override_delete_after = False, only_exported = False):

    cursor = conn.cursor()

    if override_delete_after:

        try:
            cursor.execute('SELECT * FROM articles;')
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    else:

        if only_exported:
            try:
                cursor.execute('SELECT * FROM articles WHERE export = 1 AND exported = 0;')
                rows = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
        else:

            try:
                cursor.execute('SELECT * FROM articles WHERE delete_after = 0;')
                rows = cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Database error: {e}")

        

    
    articles = []
    for row in rows:
        article = Article(
            title=row[1],
            summary=row[2],
            link=row[3],
            doi=row[4],
            date_retrieved=row[5]
        )
        article.read_later = bool(row[6])
        article.export = bool(row[7])
        article.exported = bool(row[8])
        article.delete_after = bool(row[9])
        article.read = bool(row[10])

        articles.append(article)

    if not keep_open: 
        conn.close()
    return articles

def update_article(conn, article):
    sql = ''' UPDATE articles
              SET read_later = ? ,
                  export = ? ,
                  exported = ? ,
                  delete_after = ? ,
                  read = ?
              WHERE doi = ?'''
    cur = conn.cursor()
    try:
        cur.execute(sql, (article.read_later, article.export, article.exported, article.delete_after, article.read, article.doi))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def make_and_insert(skip_insert = False, db_name = 'publications.db', path = 'data'):

    # Dummy function to make a database and insert some articles

    path_to_db = os.path.join(path, db_name)

    #conn = sqlite3.connect('data/publications.db')
    conn = sqlite3.connect(path_to_db)

    create_table(conn)

    if not skip_insert:

        articles = rss_l.fetch_all_feeds()

        for art in articles:
            insert_article(conn, art)

    conn.close()

if __name__ == "__main__":

    make_and_insert()

    conn = sqlite3.connect('data/publications.db')

    articles = get_articles(conn)

    print(len(articles))
    conn.close()
