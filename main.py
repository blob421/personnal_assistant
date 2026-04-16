#!/usr/bin//env python3

import ctypes
import sys
import asyncio
import threading
from datetime import datetime, timezone, timedelta

from controllers.notifications.controller import notif_controller
from controllers.email_controller.email_main_controller import Email_Main_Controller
from controllers.bluetooth.controller import Device_Controller
from controllers.Sound.sound_engine import SoundEngine
from controllers.ressource_controller.controller import Ressource_Controller

from utility.db_calls import (load_keywords, save_terms, get_logged_events, save_event, 
                              delay_event, get_pending_events,
                              init_db)
from utility.functions import (are_keywords_in_messages, extract_nouns)

from utility.exceptions import EXCEPT_NOUNS
from config import CONFIRMED_PROVIDERS

keywords = set()
time_until_next_prompt=None

is_windows_os = sys.platform.startswith("win")
prompted_recently = False
prompt_active = False

async def init():
    global email_controller, sound_engine, keywords, time_until_next_prompt, ressource_controller, notif
    await init_db()
    now = datetime.now()
    last_prompt = await get_logged_events("'Daily prompt'")
    
    if last_prompt:
     
        last_prompt = datetime.fromisoformat(last_prompt[1])
        next_prompt = last_prompt + timedelta(days=1)
        time_remaining = (next_prompt - now).total_seconds()
     
 
        time_until_next_prompt = 5 if time_remaining < 0 else time_remaining + 5
    
    else: 
        time_until_next_prompt = 5
    

    notif = notif_controller()
    ressource_controller = Ressource_Controller()
    email_controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    sound_engine = SoundEngine(is_windows_os)
    keywords = await load_keywords()
    


def proximity(fn):
    async def wrapper(*args, **kwargs):
        if not device_controller.user_is_near or ressource_controller.busy:
            return await fn(*args, **kwargs, near=False)
        else:
            try:
                sound_engine.manage_sound_apps(reduce=True)
                return await fn(*args, **kwargs)
                
            finally:
                sound_engine.manage_sound_apps(reduce=False)
           
    return wrapper


def play_sound(string):
    sound_engine.create_sound(string)
    sound_engine.play_sound()

async def get_messages():
    
    while True:
        await email_controller.connect()
        messages = await email_controller.get_emails('Google', 'INBOX')
      
        if messages:
            found_keywords = await are_keywords_in_messages(messages, keywords)
            if found_keywords:
     
                await announce_keyword_found(found_keywords)
        await asyncio.sleep(1800)


@proximity
async def prompt_for_terms(near=True):
    global prompted_recently, prompt_active
    if not prompted_recently:
        if not near:
      
            await delay_event(message='', type='Daily prompt')
            return
        
        prompt_active = True
        prompted_recently = True
        sound_engine.play_sound(prompt=True)

        prompt_string = 'Should I look for a specific keyword when parsing your mail ?'
        play_sound(prompt_string)
        await asyncio.sleep(0.1)
        answer = await sound_engine.sound_to_string()
        if not answer or 'no' in answer.lower() or answer.lower() == '':
            await save_event('Daily prompt')
            return
        
        cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
        await asyncio.sleep(2)


        terms_string = "and".join(nouns)

        if terms_string and len(terms_string) > 1:
            response_string = f"All right , I will keep an eye on {terms_string} ..."
            
            play_sound(response_string)
        
        await save_event('Daily prompt')

        for t in nouns:
            keywords.add(t)
            await save_terms(t.lower())

        prompt_active = False
    
   

       

@proximity
async def announce_keyword_found(keywords:dict, near=True):
    global prompt_active, notif
    aggregated = {}
    for k in keywords:
        sender = k['sender']
        keyword = k['keyword']

        if not aggregated.get(keyword):
            aggregated[keyword] = []

        aggregated[keyword].append(sender)

    if near and not prompt_active:
        sound_engine.play_sound(prompt=True)
        await asyncio.sleep(0.1)
        intro_string = f'Good news, I have found something in your mailbox'
        play_sound(intro_string)
        was_not_available = False
    else:
        was_not_available = True

    for idx, (k, senders) in enumerate(aggregated.items()):
        senders_string = ',      '.join(senders)
        if idx == 0:
            full_string = f'The keyword {k} was found in messages sent by {senders_string}'
        else:
            full_string = f', the keyword {k} was found in mails coming from {senders_string}'

        notif.notify('Keyword found', f'the keyword {k} was found in mails coming from {senders_string}')

        if not near or was_not_available:
            await delay_event(message=full_string, type='Keywords found')
            return 
        if idx > 0:
            await asyncio.sleep(1)
        play_sound(full_string)



async def proximity_loop():
    global prompted_recently, prompt_active

    if not device_controller.address:
        await device_controller.scan_and_save()
        device_controller.address = device_controller.best_rssi
        
    while True:
        prompt_types = {}
        await device_controller.proximity_scan()
        await ressource_controller.check_load()
                                                      ## Will anounce in 5 minutes if prompt_active
        if device_controller.user_is_near and not ressource_controller.busy and not prompt_active:
            pending = await get_pending_events()
            if pending:
               
                for o in pending:
                    if not prompt_types.get(o['type']):
                        prompt_types[o['type']] = [o['message']]

                for k, v in prompt_types.items():
                    if k == 'Daily prompt':
                        prompt_missed = True
                    if k == 'Keywords found':
                        sound_engine.play_sound(prompt=True)
                        intro_string = f'Good news, I have found something in your mailbox'
                        play_sound(intro_string)

                        for m in v:
                            await asyncio.sleep(0.5)
                            play_sound(m)

                if prompt_missed:
                    await prompt_for_terms()

        
        await asyncio.sleep(300)  
        prompted_recently = False 
        
async def prompt_loop():
  
    await asyncio.sleep(time_until_next_prompt)
    while True:
        await prompt_for_terms()
        await asyncio.sleep(3600 * 24)     


device_controller = Device_Controller()

def MTA_thread():
    
    if is_windows_os:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        ctypes.windll.ole32.CoInitializeEx(0, 0x0)

    asyncio.run(proximity_loop())

async def main():

    await init()
    await asyncio.gather(get_messages(), prompt_loop())


mta_thread = threading.Thread(target=MTA_thread, daemon=True).start()
asyncio.run(main())


