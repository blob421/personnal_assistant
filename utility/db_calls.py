import sqlite3
import contextlib
from config import DB_PATH
from datetime import datetime


def with_sqlite3(fn):
    async def wrapper(*args, **kwargs):
        with sqlite3.connect(DB_PATH) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                try:
                    return await fn(cur, *args, **kwargs)
                
                except sqlite3.Error as e:
                    print(f'{kwargs.get("err_str", "")}: {e}')
    return wrapper


@with_sqlite3
async def init_db(cur, err_str='Error creating tables during init'):
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
async def save_terms(cur, term, err_str='Error inserting term in the database:'):
    now = datetime.now().isoformat()

    cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                [now, term])

  


@with_sqlite3
async def get_logged_events(cur, col:str=None, many:int=None, 
                            err_str='Error fetching event logs from the database:'):

    col_string = f'WHERE type={col} ORDER BY id DESC' if col else "ORDER BY id DESC"
   
    cur.execute(f"""SELECT * FROM events {col_string}""")
    
    if not many:
    
        results = cur.fetchone()
    else: 
        results = cur.fetchmany(many)
    
    if results:
        return results
    
    return None


@with_sqlite3
async def save_event(cur, type:str, err_str='Error saving event to database:'):
    now = datetime.now().isoformat()

    cur.execute("""INSERT INTO events(date, type) VALUES (?,?)""", [now, type])



@with_sqlite3
async def delay_event(cur, message:str, type:str, err_str='Error writing delayed event to db:'):
    now = datetime.now().isoformat()
 
    cur.execute("""INSERT INTO missed_prompts (date, message, type) VALUES (?,?,?)""",
                   [now, message, type])


    


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
async def mark_emails_read(cur, emails:list, err_str='Error inserting read email in the database:'):
    now = datetime.now().isoformat()

    for e in emails:
        subject = e['subject']
        id = e['id']
        cur.execute("""INSERT OR IGNORE INTO emails(date, id, subject) VALUES (?,?,?)""",
                    [now, id, subject])



@with_sqlite3
async def email_was_processed(cur, id:int, err_str='Error fetching emails in email_was_processed:'):
    
    cur.execute("""SELECT * FROM emails WHERE id=?""", [id])
    result = cur.fetchone()
    if result:
        return True
    return False



