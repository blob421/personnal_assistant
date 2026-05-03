
from config import DB_PATH
from datetime import datetime
import aiosqlite
import json



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


############################### MAIL #################################################
@with_sqlite3
async def mark_emails_read(cur, emails:dict, err_str='Error inserting read email in the database:'):
    now = datetime.now().isoformat()

    for sender, mail in emails.items():
        for e in mail:
            subject = e['subject']
            id = e['id']
           
            intent = json.dumps(list(e['tags'])) if e['tags'] else None
    
            sender = e['sender']
    
            await cur.execute("""INSERT OR IGNORE INTO emails(date, id, subject, tags , sender) VALUES (?,?,?,?,?)""",
                        [now, id, subject, intent, sender])



@with_sqlite3
async def email_was_processed(cur, id:int, err_str='Error fetching emails in email_was_processed:'):
    
    await cur.execute("""SELECT 1 FROM emails WHERE id=?""", [id])

    return await cur.fetchone() is not None


############################### CONTACTS #################################################
@with_sqlite3
async def load_contacts_async(cur, err_str='Error loading contacts from the database'):
    await cur.execute("""SELECT * FROM contacts""")
    contacts = await cur.fetchall()
    if contacts:
        return [c[1] for c in contacts]
    return None



############################### TERMS #################################################
@with_sqlite3
async def save_terms(cur, term=None, occurences=None, err_str='Error inserting term in the database:'):

    if term:
        now = datetime.now().isoformat()
        await cur.execute("""INSERT OR IGNORE INTO search_terms(date, term, count) VALUES (?,?,?)""", 
                                                                                    [now, term, 0])
    elif occurences:
        for k, v in occurences.items():
            await cur.execute("""UPDATE search_terms SET count=? WHERE term=?""", [v, k])


############################### KEYWORDS #################################################
    
@with_sqlite3
async def load_keywords(cur):
    keywords = {}


    await cur.execute('SELECT * FROM search_terms')
    terms = await cur.fetchall()
    for t in terms:
        keywords[t[1]] = t[2]

    return keywords



############################### EVENTS #################################################

@with_sqlite3
async def get_logged_events(cur, col:str=None, many:int=None, 
                            err_str='Error fetching event logs from the database:', limit=None):

   
    if limit :
        col_string = f'WHERE type={col} ORDER BY id DESC LIMIT {limit}' if col else f"ORDER BY id DESC LIMIT {limit}"
    else:
        col_string = f'WHERE type={col} ORDER BY id DESC' if col else "ORDER BY id DESC"

    await cur.execute(f"""SELECT * FROM events {col_string}""")
    
    results = await cur.fetchone() if not many else await cur.fetchmany(many)
    
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

############################### OPTIONS #################################################
    
@with_sqlite3
async def load_options(cur, err_str='Error fetching options for the GUI'):
    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()
    options_dict = {}

    for o in options:
        options_dict[o[0]] = o[2] or o[1]
        
    return options_dict



