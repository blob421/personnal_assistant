import sqlite3
import contextlib
from config import DB_PATH
from datetime import datetime


def with_sqlite3(fn):
    async def wrapper(*args, **kwargs):
        with sqlite3.connect(DB_PATH) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                return await fn(cur, *args, **kwargs)
    return wrapper


@with_sqlite3
async def init_db(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS search_terms(date TEXT, 
                                                            term TEXT UNIQUE
                            
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS emails(id BIGINT UNIQUE, date TEXT, subject TEXT)""")
    cur.execute("""CREATE INDEX IF NOT EXISTS emails_id_idx on emails(id)""")
    
    cur.execute("""CREATE INDEX IF NOT EXISTS term_idx on search_terms(term)""")


    cur.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        date TEXT,
                                                        type VARCHAR(60)
                                                        )""")
    
    cur.execute("""CREATE INDEX IF NOT EXISTS event_type_idx on events(type)""")

    cur.execute("""CREATE INDEX IF NOT EXISTS event_id_idx on events(id)""")

    cur.execute("""CREATE TABLE IF NOT EXISTS missed_prompts (date TEXT,
                                                              message TEXT,
                                                              type TEXT
                )""")
    
@with_sqlite3
async def load_keywords(cur):
    keywords = set()


    cur.execute('SELECT * FROM search_terms')
    terms = cur.fetchall()
    for t in terms:
        keywords.add(t[1])

    return keywords

@with_sqlite3
async def save_terms(cur, term):
    now = datetime.now().isoformat()

    try:
        cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                [now, term])

    except sqlite3.Error as e:
        print(f'Error inserting term in the database : {e}')


@with_sqlite3
async def get_logged_events(cur, col:str=None, many:int=None):

    col_string = f'WHERE type={col} ORDER BY id DESC' if col else "ORDER BY id DESC"

    try:


        
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

@with_sqlite3
async def save_event(cur, type:str):
    now = datetime.now().isoformat()

    try:
        cur.execute("""INSERT INTO events(date, type) VALUES (?,?)""", [now, type])

    except sqlite3.Error as e:
        print(f'Error saving event to database : {e}')


@with_sqlite3
async def delay_event(cur, message:str, type:str):
    now = datetime.now().isoformat()
    try:
       cur.execute("""INSERT INTO missed_prompts (date, message, type) VALUES (?,?,?)""",
                   [now, message, type])

    except sqlite3.Error as e:
        print(f'Error writing delayed event to db: {e}')

    


@with_sqlite3
async def get_pending_events(cur):
    missed_prompts = []
    cur.execute("""SELECT * FROM missed_prompts""")

    results = cur.fetchall()
    if results:
        for r in results:
            missed_prompts.append({'date': r[0], 'message': r[1], 'type': r[2]})

    return missed_prompts

@with_sqlite3
async def mark_emails_read(cur, emails:list):
    now = datetime.now().isoformat()
    try:
        for e in emails:
            subject = e['subject']
            id = e['id']
            cur.execute("""INSERT OR IGNORE INTO emails(date, id, subject) VALUES (?,?,?)""",
                        [now, id, subject])

    except sqlite3.Error as e:
        print(f'Error inserting read email in the database : {e}')

@with_sqlite3
async def email_was_processed(cur, id:int):
    try:
        cur.execute("""SELECT * FROM emails WHERE id=?""", [id])
        result = cur.fetchone()
        if result:
            return True
        return False

    except sqlite3.Error as e:
        print(f'Error fetching emails in email_was_processed: {e}')

