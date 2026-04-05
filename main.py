from modules.email_main_controller import Email_Main_Controller
import time
import asyncio
import sqlite3
import contextlib
from datetime import datetime

CONFIRMED_PROVIDERS = ['Google']

def init():
    global controller
    controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    controller.connect()
  
def get_messages():
    messages = controller.get_emails('Google', 'INBOX')
    print(messages)

def save_terms(term):
    now = datetime.now().isoformat()

    with sqlite3.connect('user_data.sqlite') as conn:
        with contextlib.closing(conn.cursor()) as cur:
            try:
                cur.execute("""CREATE TABLE IF NOT EXISTS search_terms(date TEXT, 
                                                                    term TEXT
                                    
                )""")
                cur.execute("""INSERT INTO search_terms(date, term) VALUES (?,?)""", [now, term])

            except sqlite3.Error as e:
                print(f'Error inserting term in the database : {e}')


def prompt_for_terms():
    terms = []
    while True:
        term = input('Is there anything worth keeping an eye on for today ?')
        print(f"All right , keeping an eye on {term}")
        terms.append(term)
        more_terms = input('Do you want to look for other terms ? (Y, N)')

        if more_terms.lower() == 'n':
            break
        if more_terms.lower != 'y' or 'n':
            print('Please enter (y or n)')
 
      
    for term in terms:
        save_terms(term)

    

init()
while True:
   get_messages()
   time.sleep(1800)