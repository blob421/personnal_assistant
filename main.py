from modules.email_main_controller import Email_Main_Controller

import asyncio
import sqlite3
import contextlib
from datetime import datetime

CONFIRMED_PROVIDERS = ['Google']

async def init():
    global controller
    controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    await controller.connect()
  
async def get_messages():
    messages = await controller.get_emails('Google', 'INBOX')
    print(messages)
    await asyncio.sleep(1800)

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

    
async def main():

    await init()
    await asyncio.gather(get_messages())


asyncio.run(main())