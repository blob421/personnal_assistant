from modules.email_main_controller import Email_Main_Controller

import asyncio
import sqlite3
import contextlib
from datetime import datetime
from Sound.sound_engine import SoundEngine

DB_PATH = 'user_data.sqlite'
CONFIRMED_PROVIDERS = ['Google']

keywords = set()



async def load_keywords():
    with sqlite3.connect(DB_PATH) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            cur.execute('SELECT * FROM search_terms')
            terms = cur.fetchall()
            for t in terms:
                keywords.add(t[1])


async def are_keywords_in_messages(messages:list):
     found = []
     for m in messages:
         for k in keywords:
             
             if k.lower() in m.lower():
                 found.append(k)
     return found
        

async def init():
    global controller, sound_engine

    controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    sound_engine = SoundEngine()
    await load_keywords()
    await controller.connect()


async def get_messages():
    while True:
        messages = await controller.get_emails('Google', 'INBOX')
        found_keywords = await are_keywords_in_messages(messages)
        if found_keywords:
            await announce_keyword_found(found_keywords)
        await asyncio.sleep(1800)

async def save_terms(term):
    keywords.add(term)
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


async def prompt_for_terms():
 
    sound_engine.play_sound(prompt=True)
    prompt_string = 'Is there anything worth keeping an eye on for today ?'
    sound_engine.create_sound(prompt_string)


    sound_engine.play_sound()
    await asyncio.sleep(0.05)

    answer = await sound_engine.sound_to_string()
    await asyncio.sleep(1.9)
    terms = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '').split()
    terms_string = ",".join(answer.split())

    response_string = f"All right , I will keep an eye on {terms_string} ..."
    sound_engine.create_sound(response_string)
    sound_engine.play_sound()

    for t in terms:
        await save_terms(t.lower())


async def announce_keyword_found(keywords):
    keyword_string = 'and'.join(keywords)
    sound_engine.play_sound(prompt=True)
  
    voice_string = f'Good news, I have found something in your mails concerning {keyword_string}'

    sound_engine.create_sound(voice_string)
    sound_engine.play_sound()
    

async def main():
    
    await init()
    await asyncio.gather(get_messages(), prompt_for_terms())


asyncio.run(main())