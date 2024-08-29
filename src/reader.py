"""
Functions to read articles from a database and change attributes 
of them depending on user input

"""

import feedparser
import sqlite3
from db_handling import get_articles, update_article
from rss_feed_listener import Article
import msvcrt
import sys
import pickle

def change_state_of_article(article, user_input):
    if "r" in user_input:
        article.toggle_read()
    if "l" in user_input:
        article.toggle_read_later()
    if "e" or "E" in user_input:
        article.export = not article.export
    if "d" in user_input:
        article.delete_after = not article.delete_after

    return article

def filter_export(articles):
    return [article for article in articles if article.export]

# Take input from user

def navigator(article_list, current_articles_index=0, return_export = True):

    num_total_art = len(article_list)

    while True:
        current_article = article_list[current_articles_index]
        # Empty the screen
        print("\033c")
        print(str(current_articles_index + 1) + "/" + str(num_total_art))
        print(current_article.title)
        #current_article.print_status()
        current_article.read = True
        #user_input = input("What would you like to do? (r)ead, (l)ater, (e)xport, (d)elete, (j)ext, (k)revious, (q)uit: ")
        print("What would you like to do? (r)ead, (l)ater, (e)xport, (d)elete, (j)ext, (k)revious, (q)uit: ")
        user_input = msvcrt.getch().decode()
        # Should provide a series of state changes as input


        if user_input == "j" or user_input == "":
            current_articles_index += 1
        elif user_input == "k":
            current_articles_index -= 1
        elif user_input == "s":
            print(current_article.summary)
            user_input = input("Press any key to continue")
        elif user_input == "E":
            user_input = "e"
            current_articles_index += 1
            print(user_input)
            print(current_articles_index)
        elif user_input == "q":

            # Filter out the articles marked for export

            if return_export:

                return filter_export(articles)

            break
        
        current_article = change_state_of_article(current_article, user_input)
        update_article(conn, current_article)

        print(current_article)

        if current_articles_index < 0:
            current_articles_index = 0
        if current_articles_index >= len(articles):
            current_articles_index = 0

conn = sqlite3.connect('data/publications.db')
articles = get_articles(conn, keep_open=True, override_delete_after=True)

# Filter out the already read articles, the ones marked for deletion, or the exported

articles_not_marked_for_deletion = [article for article in articles if not article.delete_after]
articles_not_already_read = [article for article in articles_not_marked_for_deletion if not article.read]
articles_not_already_exported = [article for article in articles_not_already_read if not article.exported]
articles = articles_not_already_read

articles_to_export = navigator(articles)

conn.close()
