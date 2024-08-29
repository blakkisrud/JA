import sqlite3

def init_db():
    conn = sqlite3.connect('data/publications.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS publications(
              title text, 
              summary text, 
              link text, 
              doi text, 
              date_retrieved text)'''
              )
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()