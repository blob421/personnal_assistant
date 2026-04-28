
from config import DB_PATH
from datetime import datetime
import aiosqlite
import sqlite3
from contextlib import closing
from config import default_options
import config
import json
def with_sqlite3_sync(fn):
    def wrapper(*args, **kwargs):
        with sqlite3.connect(DB_PATH) as conn:
            with closing(conn.cursor()) as cur:
                try:
                   results = fn(cur, *args, **kwargs)
                   conn.commit()
                   return results
                
                except sqlite3.Error as e:
                    print(f'{kwargs.get("err_str", "")}: {e}')

           
    return wrapper

def with_sqlite3(fn):
    async def wrapper(*args, **kwargs):
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.cursor() as cur:
                try:
                   results = await fn(cur, *args, **kwargs)
                   await conn.commit()
                   return results
                
                except aiosqlite.Error as e:
                    print(f'{kwargs.get("err_str", "")}: {e}')

           
    return wrapper



    
@with_sqlite3
async def load_keywords(cur):
    keywords = set()


    await cur.execute('SELECT * FROM search_terms')
    terms = await cur.fetchall()
    for t in terms:
        keywords.add(t[1])

    return keywords

@with_sqlite3
async def save_terms(cur, term, err_str='Error inserting term in the database:'):
    now = datetime.now().isoformat()

    await cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                [now, term])

  


@with_sqlite3
async def get_logged_events(cur, col:str=None, many:int=None, 
                            err_str='Error fetching event logs from the database:', limit=None):

   
    if limit :
        col_string = f'WHERE type={col} ORDER BY id DESC LIMIT {limit}' if col else f"ORDER BY id DESC LIMIT {limit}"
    else:
        col_string = f'WHERE type={col} ORDER BY id DESC' if col else "ORDER BY id DESC"

    await cur.execute(f"""SELECT * FROM events {col_string}""")
    
    if not many:
    
        results = await cur.fetchone()
    else: 
        results = await cur.fetchmany(many)
    
    if results:
 
        return results
    
    return None


@with_sqlite3
async def save_event(cur, type:str, message, err_str='Error saving event to database:'):
    now = datetime.now().isoformat()
    
    await cur.execute("""INSERT INTO events(date, type, message) VALUES (?,?,?)""", [now, type, message])



@with_sqlite3
async def delay_event(cur, message:str, type:str, err_str='Error writing delayed event to db:'):
    now = datetime.now().isoformat()
 
    await cur.execute("""INSERT INTO missed_prompts (date, message, type) VALUES (?,?,?)""",
                   [now, message, type])


    


@with_sqlite3
async def get_pending_events(cur):
    missed_prompts = []
    await cur.execute("""SELECT * FROM missed_prompts""")

    results = await cur.fetchall()
    if results:
        for r in results:
            missed_prompts.append({'date': r[0], 'message': r[1], 'type': r[2]})
    await cur.execute("""DELETE FROM missed_prompts""")
    return missed_prompts


@with_sqlite3
async def mark_emails_read(cur, emails:list, err_str='Error inserting read email in the database:'):
    now = datetime.now().isoformat()

    for e in emails:
        subject = e['subject']
        id = e['id']
        intent = e['tags']
        sender = e['sender']
   
        await cur.execute("""INSERT OR IGNORE INTO emails(date, id, subject, tags , sender) VALUES (?,?,?,?,?)""",
                    [now, id, subject, intent, sender])



@with_sqlite3
async def email_was_processed(cur, id:int, err_str='Error fetching emails in email_was_processed:'):
    
    await cur.execute("""SELECT * FROM emails WHERE id=?""", [id])
    result = await cur.fetchone()
    if result:
        return True
    return False



@with_sqlite3
async def init_db(cur, err_str='Error creating tables during init'):
    await cur.execute("""CREATE TABLE IF NOT EXISTS search_terms(date TEXT, 
                                                            term TEXT UNIQUE
                            
        )""")
    await cur.execute("""CREATE TABLE IF NOT EXISTS emails(id BIGINT UNIQUE, date TEXT, subject TEXT, tags TEXT, sender TEXT)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS emails_id_idx on emails(id)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS emails_tags_idx on emails(tags)""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS term_idx on search_terms(term)""")


    await cur.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        date TEXT,
                                                        type VARCHAR(60),
                                                        message TEXT
                                                        )""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS event_type_idx on events(type)""")

    await cur.execute("""CREATE INDEX IF NOT EXISTS event_id_idx on events(id)""")

    await cur.execute("""CREATE TABLE IF NOT EXISTS missed_prompts (date TEXT,
                                                              message TEXT,
                                                              type TEXT
                )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS options(name VARCHAR(30), 
                                                            bool BOOLEAN , 
                                                            value VARCHAR(255)
                )""")
    await cur.execute("""CREATE TABLE IF NOT EXISTS contacts(alias VARCHAR(30), 
                                                             email VARCHAR(50) UNIQUE 
                                                             )""")

    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()

    if not options or len(options) < 1:
        for k, v in default_options.items():
            boo = None if type(v) == str else v
            value = None if type(v) == bool else v
            await cur.execute("""INSERT INTO options (name, bool, value) VALUES (?,?,?)""", 
                            [k, boo, value])
            
@with_sqlite3
async def load_options(cur, err_str='Error fetching options for the GUI'):
    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()
    options_dict = {}

    for o in options:
        options_dict[o[0]] = o[2] or o[1]
        
    return options_dict

@with_sqlite3
async def load_contacts_async(cur, err_str='Error loading contacts from the database'):
    await cur.execute("""SELECT * FROM contacts""")
    contacts = await cur.fetchall()
    if contacts:
        return [c[1] for c in contacts]
    return None


@with_sqlite3_sync
def save_options(cur, err_str='Error saving options to DB'):
    print(config.OPTIONS)
   
    for n, v in config.OPTIONS.items():
        boo = None if type(v) == str else v
        value = None if type(v) == bool else v


        cur.execute("""UPDATE options SET bool=?, value=? WHERE name=?""",
                                                              [boo, value, n])


@with_sqlite3_sync
def delete_keyword(cur, keyword, err_str='Error deleting keyword'):
    cur.execute(f"""DELETE FROM search_terms WHERE term=? """, [keyword])


@with_sqlite3_sync
def add_keyword_gui(cur, term, err_str='Error inserting term in the database:'):
    now = datetime.now().isoformat()

    cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                [now, term])
    
@with_sqlite3_sync
def get_events_gui(cur, err_str='Err fetching events from the db (gui)'):
    cur.execute(f"""SELECT * FROM events ORDER BY id DESC LIMIT 20""")

    results = cur.fetchall()

    return results

@with_sqlite3_sync
def add_contact(cur,  contact:dict, err_str='Error adding contact to the database'):
    cur.execute("""INSERT OR IGNORE INTO contacts VALUES(?,?)""", [contact['alias'], contact['email']])

@with_sqlite3_sync
def load_contacts(cur, err_str='Error loading contacts from the database'):
    cur.execute("""SELECT * FROM contacts""")
    contacts = cur.fetchall()
    if contacts:
        return [{'alias': c[0], 'email': c[1]} for c in contacts]
    return None

@with_sqlite3_sync
def delete_contact(cur, name, err_str='Error deleting contacts from the database'):
    cur.execute("""DELETE FROM contacts WHERE alias=?""", [name])

@with_sqlite3_sync
def get_watchlist_messages(cur, err_str='Error fetching messages from db for watchlist'):
    emails = []
    cur.execute("""SELECT * FROM emails WHERE tags IS NOT NULL ORDER BY id DESC LIMIT 30""")
    results = cur.fetchall()
    for r in results:
        emails.append({'date': r[1], 'subject': r[2], 'tags': json.loads(r[3]), 'sender': r[4]})
    
    if emails:
       return emails
    return None
