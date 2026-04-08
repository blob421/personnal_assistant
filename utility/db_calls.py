import sqlite3
import contextlib
from config import DB_PATH
from datetime import datetime

async def load_keywords():
    keywords = set()
    with sqlite3.connect(DB_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute("""CREATE TABLE IF NOT EXISTS search_terms(date TEXT, 
                                                                    term TEXT UNIQUE
                                    
                )""")
            cur.execute("""CREATE INDEX IF NOT EXISTS term_idx on search_terms(term)""")
            cur.execute('SELECT * FROM search_terms')
            terms = cur.fetchall()
            for t in terms:
                keywords.add(t[1])

            return keywords


async def save_terms(term):
 
    now = datetime.now().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            try:
               
                cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                     [now, term])

            except sqlite3.Error as e:
                print(f'Error inserting term in the database : {e}')



async def get_logged_events(col:str=None, many:int=None):

    col_string = f'WHERE type={col} ORDER BY id DESC' if col else "ORDER BY id DESC"

    with sqlite3.connect(DB_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            try:
                cur.execute("""CREATE TABLE IF NOT EXISTS events(id PRIMARY KEY,
                                                                 date TEXT,
                                                                 type VARCHAR(60)
                                                                    )""")
                
                cur.execute("""CREATE INDEX IF NOT EXISTS event_type_idx on events(type)""")

                cur.execute("""CREATE INDEX IF NOT EXISTS event_id_idx on events(id)""")

               
                cur.execute(f"""SELECT * FROM events {col_string}""")
                
                if not many:
               
                    results = cur.fetchone()
                else: 
                    results = cur.fetchmany(many)
                
                if results:
                    return results
                
                return None


            except sqlite3.Error as e:
                print(f'Error fetching event logs from the database : {e}')