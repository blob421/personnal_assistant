from modules.email_main_controller import Email_Main_Controller
from bluetooth.controller import Device_Controller

import asyncio
import sqlite3
import contextlib
from datetime import datetime
from Sound.sound_engine import SoundEngine
import spacy

DB_PATH = 'user_data.sqlite'
CONFIRMED_PROVIDERS = ['Google']

keywords = set()
nlp = spacy.load("en_core_web_sm")

def extract_nouns(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]

async def load_keywords():
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


async def are_keywords_in_messages(messages:list):
    found = []
     
    for m in messages:
        sender = m['sender']
        text = m['text']
       
        subject = m['subject']
    
        for k in keywords:
            if text:
                if k.lower() in text.lower() or k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
            else:
                if k.lower() in subject.lower():
                    found.append({'keyword': k, 'sender': sender})
                
    return found
        

async def init():
    global controller, sound_engine

    controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    sound_engine = SoundEngine()
    await load_keywords()
    await controller.connect()

def play_sound(string):
    sound_engine.create_sound(string)
    sound_engine.play_sound()

async def get_messages():
    while True:
        messages = await controller.get_emails('Google', 'INBOX')
      
        if messages:
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
               
                cur.execute("""INSERT OR IGNORE INTO search_terms(date, term) VALUES (?,?)""", 
                                                                                     [now, term])

            except sqlite3.Error as e:
                print(f'Error inserting term in the database : {e}')


EXCEPT_NOUNS = {"email", "emails", "inbox", "message", "messages", "mail", 'alert' ,
                'keyword', 'keywords', 'noun', 'nouns', 'word', 'words', 'search', 'look', 'lookup'}


async def prompt_for_terms():
 
    sound_engine.play_sound(prompt=True)
    prompt_string = 'Should I look for a specific keyword when parsing your mail ?'

    play_sound(prompt_string)
    await asyncio.sleep(0.05)

    answer = await sound_engine.sound_to_string()

    if not answer or 'no' in answer.lower() or answer.lower() == '':
        return
    
    cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
    nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
    await asyncio.sleep(2)
    print(nouns)

    terms_string = "and".join(nouns)

    response_string = f"All right , I will keep an eye on {terms_string} ..."

    play_sound(response_string)

    for t in nouns:
        await save_terms(t.lower())

## Handle the case when the same keyword is found in many emails
async def announce_keyword_found(keywords:dict):
    aggregated = {}

    for k in keywords:
        sender = k['sender']
        keyword = k['keyword']

        if not aggregated[keyword]:
            aggregated[keyword] = []

        aggregated[keyword].append(sender)

    sound_engine.play_sound(prompt=True)
    intro_string = f'Good news, I have found something in your mailbox'
    play_sound(intro_string)

    for k, senders in aggregated.items():
        senders_string = 'and'.join(senders)
        full_string = f'The keyword {k} was found in messages sent by {senders_string}'
        play_sound(full_string)



    
        
        

device_controller = Device_Controller()

async def main():
    
    await init()
    await asyncio.gather(get_messages(), device_controller.proximity_scan())


asyncio.run(main())

