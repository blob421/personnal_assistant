
from utilities.functions import extract_pending_prompts, extract_nouns, make_announcements
from utilities.db_calls import delay_event, save_event, save_terms, get_logged_events


from utilities.exceptions import EXCEPT_NOUNS
from controllers.notifications.controller import notif_controller
from .sound_engine import SoundEngine
import asyncio
import config

from datetime import datetime, timedelta




class Vocal_Handler():

    def __init__(self, is_windows_os, device_controller, resource_controller, keywords, timer):
        self.sound_engine = SoundEngine(is_windows_os)
        self.prompt_active = False
        self.prompted_recently = False
        self.keywords = keywords
        self.notif_engine = notif_controller()
        self.timer = timer
        self.device_controller = device_controller
        self.resource_controller=  resource_controller
        self.window = None
        self.operating_hours = True
        self.is_operating_hours()
        self.keyword_prompt_due = False
        self.contacts = {}



    def play_sound(self, string):
       
        self.sound_engine.create_sound(string)
        self.sound_engine.play_sound()
        

    async def last_asked_for_keywords(self):
        last = await get_logged_events(col="'Daily prompt'", limit=1)
        if not last:
            self.keyword_prompt_due = True
            return 
        
        time = datetime.fromisoformat(last[1])
        now = datetime.now()

        if (now - time > timedelta(days=1)):
            self.keyword_prompt_due = True
    

    def is_operating_hours(self):
        self.operating_hours = self.timer.hour_match()

        if self.timer.gui_refresh_due:
            self.window.worker.reload_requested.emit()
            self.timer.last_gui_refresh = datetime.now()
            self.timer.gui_refresh_due = False

    


    @staticmethod
    def proximity(fn):
        async def wrapper(self, *args, **kwargs):
    
            if (not self.device_controller.user_is_near or self.resource_controller.busy 
                                                        or not self.operating_hours):
                
                return await fn(self, *args, **kwargs, near=False)
            else:
                try:
                    self.sound_engine.manage_sound_apps(reduce=True)
                    return await fn(self, *args, **kwargs)
                    
                finally:
                    self.sound_engine.manage_sound_apps(reduce=False)
            
        return wrapper
    


    async def handle_pending_events(self):
            if not self.operating_hours: return

            pending_prompts = await extract_pending_prompts()
            messages = pending_prompts['result']

            has_messages = len(messages.keys()) > 0

            if has_messages:
                self.sound_engine.play_sound(prompt=True)
                self.play_sound('Are you there ? ... I might have found something interesting...')

                for k , value in messages.items():
                    if k == 'keyword found':
                       
                        await asyncio.sleep(1)
                        for m in value:
                                await asyncio.sleep(2)
                                self.play_sound(m)

                    if k == 'watch list':
                        vocal_base = f'Something in your watchlist popped up'
                        self.play_sound(vocal_base)
                        await asyncio.sleep(1)
                        for m in value:
                            await asyncio.sleep(1.5)
                            self.play_sound(m)

                if self.keyword_prompt_due:
                    await asyncio.sleep(1)
                    await self.prompt_for_terms()

    


    async def prompt_for_terms(self):
       

        if not self.prompted_recently and not config.OPTIONS['silent_mode']:

            
            self.prompt_active = True
            self.prompted_recently = True
         

            self.play_sound('Do you want me to keep an eye for other keywords ?')
           
            await asyncio.sleep(0.1)
            answer = await self.sound_engine.sound_to_string()

            if not answer or 'no' in answer.lower() or answer.lower() == '':
                await save_event('Daily prompt', None)
                return
            
            await asyncio.sleep(0.5)
            self.play_sound('All right , tell me what I should add to your list')
            await asyncio.sleep(0.1)
            answer = await self.sound_engine.sound_to_string()
            
            cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
            nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
            await asyncio.sleep(2)


            terms_string = "and".join(nouns)

            if terms_string and len(terms_string) > 1:
                self.play_sound(f"All right , I will keep an eye on {terms_string} ...")

                message = f'Saved {terms_string}'
                await save_event('Daily prompt', message)

                self.window.worker.reload_requested.emit()

              

            for t in nouns:
                self.keywords.add(t)
                await save_terms(t.lower())

            self.prompt_active = False
            self.keyword_prompt_due = False
   

       
    
    @proximity
    async def announce_keyword_found(self, keywords:dict, near=True, intro_sound=True):
        
        announcements = await make_announcements(keywords, self.notif_engine, self.window.worker)
       
        if config.OPTIONS['silent_mode']: return 


        if near and not self.prompt_active:

            if intro_sound:
                self.sound_engine.play_sound(prompt=True)

            await asyncio.sleep(0.1)
            
            self.play_sound(f'Are you there ? ... I might have found something interesting...')

            was_not_available = False

        else:
            was_not_available = True


        for idx, a in enumerate(announcements):

            if not near or was_not_available:
                await delay_event(message=a, type='Keywords found')
                continue
        
            if idx > 0:
                await asyncio.sleep(1)

            self.play_sound(a)

        if self.keyword_prompt_due and (near or not was_not_available):
                await asyncio.sleep(1)
                await self.prompt_for_terms()
                
  
    @proximity
    async def announce_messages(self, messages, near=True):

        if near:
            self.sound_engine.play_sound(prompt=True)
            await asyncio.sleep(0.5)
            vocal_base = f'Are you there ? ... Something popped up in your watchlist.'
            self.play_sound(vocal_base)
            await asyncio.sleep(0.3)

        for idx, m in enumerate(messages):
            alias = self.contacts[m['sender']]
        
            base_string =  'You also received' if idx > 0 else 'You received'

            if not m['tags']:
                m_string = f'{base_string} a message from {alias}'

            elif 'urgent' in m['tags'] and 'bad' in m['tags']:
                m_string = f'{base_string} an urgent message from {alias}, but I must warn you , it looks bad'

            elif 'urgent' in m['tags']:
                m_string = f'{base_string} a message from {alias}, it seemed urgent'

            elif 'bad' in m['tags']:
                m_string = f'{base_string} a message from {alias}, but I must warn you , it looks bad'

            elif 'good' in m['tags']:
                m_string = f"{base_string} a message from {alias}, looking good"

            self.notif_engine.notify(title='Watchlist event', message=m_string)
 
            if not near:
                await delay_event(message=m_string, type='watch list')
                continue
            else:
                self.play_sound(m_string)
                await asyncio.sleep(0.5)
       
        if self.keyword_prompt_due and near:
                await asyncio.sleep(1)
                await self.prompt_for_terms()
        

            
            
     
      





        

        

       
                


