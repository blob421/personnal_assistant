
from config import DB_PATH
from datetime import datetime
import sqlite3
from contextlib import closing
import config as config
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


############################## MAIL ###############################################
@with_sqlite3_sync
def get_watchlist_messages(cur, email=None, err_str='Error fetching messages from db for watchlist'):
    emails = []
    if not email:
        cur.execute("""SELECT * FROM emails WHERE tags IS NOT NULL ORDER BY id DESC LIMIT 30""")
    else:
        cur.execute("""SELECT * FROM emails WHERE tags IS NOT NULL AND sender=? ORDER BY id DESC LIMIT 30""", [email])
    results = cur.fetchall()
    for r in results:
        emails.append({'date': r[1], 'subject': r[2], 'tags': json.loads(r[3]), 'sender': r[4]})
    
    if emails:
       return emails
    return None

        

############################## KEYWORDS ###############################################

@with_sqlite3_sync
def delete_keyword(cur, keyword, err_str='Error deleting keyword'):
    cur.execute(f"""DELETE FROM search_terms WHERE term=? """, [keyword])


@with_sqlite3_sync
def add_keyword_gui(cur, term, err_str='Error inserting term in the database:'):
    now = datetime.now().isoformat()

    cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                [now, term])
############################## EVENTS #######################################################    

@with_sqlite3_sync
def get_events_gui(cur, err_str='Err fetching events from the db (gui)'):
    cur.execute(f"""SELECT * FROM events WHERE message IS NOT NULL ORDER BY id DESC LIMIT 20""")

    results = cur.fetchall()

    return results

############################## CONTACTS #######################################################

@with_sqlite3_sync
def add_contact(cur,  contact:dict, err_str='Error adding contact to the database'):
    
    cur.execute("""INSERT OR REPLACE INTO contacts VALUES(?,?,?)""", [contact['alias'], contact['email'], True])

@with_sqlite3_sync
def load_contacts(cur, err_str='Error loading contacts from the database'):
    cur.execute("""SELECT * FROM contacts WHERE active=?""", [True])
    contacts = cur.fetchall()
    if contacts:
        return {c[1]: c[0] for c in contacts} 
    return None

@with_sqlite3_sync
def load_contacts_ref(cur ,err_str = 'Error loading all contacts'):
    cur.execute("""SELECT * FROM contacts""")
    contacts = cur.fetchall()
    if contacts:
        return {c[1]: c[0] for c in contacts} 
    return None


@with_sqlite3_sync
def delete_contact(cur, name, err_str='Error deleting contacts from the database'):
    cur.execute("""UPDATE contacts SET active=? WHERE alias=?""", [False,name])


################################ OPTIONS ###############################################

@with_sqlite3_sync
def save_options(cur, err_str='Error saving options to DB'):
    print(config.OPTIONS)
   
    for n, v in config.OPTIONS.items():
        boo = None if type(v) == str else v
        value = None if type(v) == bool or v == 0 or v == 1 else v


        cur.execute("""UPDATE options SET bool=?, value=? WHERE name=?""",
                                                              [boo, value, n])