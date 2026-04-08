import ctypes
import sys
import asyncio
from datetime import datetime, timezone, timedelta
# Force COM into MTA mode
ctypes.windll.ole32.CoInitializeEx(0, 0x0)

# Force selector loop
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from controllers.email_controller.email_main_controller import Email_Main_Controller
from controllers.bluetooth.controller import Device_Controller

from controllers.Sound.sound_engine import SoundEngine


from utility.db_calls import (load_keywords, save_terms, get_logged_events)
from utility.functions import (are_keywords_in_messages, extract_nouns)
from utility.exceptions import EXCEPT_NOUNS

from config import DB_PATH, CONFIRMED_PROVIDERS

keywords = set()
time_until_next_prompt=None


async def init():
    global controller, sound_engine, keywords, time_until_next_prompt
    now = datetime.now()
    last_prompt = await get_logged_events("'Daily prompt'")

    if last_prompt:
        last_time = datetime(last_prompt[1]).fromisoformat()
        next_round = (now - (last_time + timedelta(days=1))).total_seconds()
 
        time_until_next_prompt = 5 if next_round < 0 else next_round + 5
    
    else: 
        time_until_next_prompt = 5



    controller = Email_Main_Controller(CONFIRMED_PROVIDERS)
    sound_engine = SoundEngine()
    keywords = await load_keywords()
    await controller.connect()

def play_sound(string):
    sound_engine.create_sound(string)
    sound_engine.play_sound()

async def get_messages():
    
    while True:
        messages = await controller.get_emails('Google', 'INBOX')
      
        if messages:
            found_keywords = await are_keywords_in_messages(messages, keywords)
            if found_keywords:
                await announce_keyword_found(found_keywords)
        await asyncio.sleep(1800)







async def prompt_for_terms():
    await asyncio.sleep(time_until_next_prompt)
    while True:
        sound_engine.play_sound(prompt=True)

        prompt_string = 'Should I look for a specific keyword when parsing your mail ?'
        play_sound(prompt_string)
        await asyncio.sleep(0.1)
        answer = await sound_engine.sound_to_string()
        if not answer or 'no' in answer.lower() or answer.lower() == '':
            return
        
        cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
        nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
        await asyncio.sleep(2)


        terms_string = "and".join(nouns)

        response_string = f"All right , I will keep an eye on {terms_string} ..."

        play_sound(response_string)

        for t in nouns:
            keywords.add(t)
            await save_terms(t.lower())

        await asyncio.sleep(3600 * 24)


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
    if not device_controller.address:
        await device_controller.scan_and_save()
        device_controller.address = device_controller.best_rssi['address']
    await init()
    await asyncio.gather(get_messages(), device_controller.proximity_scan(), prompt_for_terms())



asyncio.run(main())

