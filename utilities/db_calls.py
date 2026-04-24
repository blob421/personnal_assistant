
from config import DB_PATH
from datetime import datetime
import aiosqlite
from config import default_options

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
async def save_event(cur, type:str, err_str='Error saving event to database:'):
    now = datetime.now().isoformat()

    await cur.execute("""INSERT INTO events(date, type) VALUES (?,?)""", [now, type])



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
        await cur.execute("""INSERT OR IGNORE INTO emails(date, id, subject) VALUES (?,?,?)""",
                    [now, id, subject])



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
    await cur.execute("""CREATE TABLE IF NOT EXISTS emails(id BIGINT UNIQUE, date TEXT, subject TEXT)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS emails_id_idx on emails(id)""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS term_idx on search_terms(term)""")


    await cur.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        date TEXT,
                                                        type VARCHAR(60)
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
    
    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()
    if len(options) < 1:
        for k, v in default_options.items():

            await cur.execute("""INSERT INTO options (name, bool, value) VALUES (?,?,?)""", 
                            [k, v['bool'], v['value']])
            
@with_sqlite3
async def load_options(cur, err_str='Error fetching options for the GUI'):
    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()
    options_dict = {}

    for o in options:
        options_dict[o[0]] = {'bool': o[1], 'value': o[2]}
        
    return options_dict