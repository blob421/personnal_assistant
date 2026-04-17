
from utilities.functions import extract_pending_prompts, extract_nouns
from utilities.db_calls import delay_event, save_event, save_terms

from utilities.exceptions import EXCEPT_NOUNS
from controllers.notifications.controller import notif_controller
from .sound_engine import SoundEngine

import asyncio



class Vocal_Handler():

    def __init__(self, is_windows_os, device_controller, resource_controller, keywords):
        self.sound_engine = SoundEngine(is_windows_os)
        self.prompt_active = False
        self.prompted_recently = False
        self.keywords = keywords
        self.notif_engine = notif_controller()
        self.device_controller = device_controller
        self.resource_controller=  resource_controller


    def play_sound(self, string):
        self.sound_engine.create_sound(string)
        self.sound_engine.play_sound()


    @staticmethod
    def proximity(fn):
        async def wrapper(self, *args, **kwargs):
            if not self.device_controller.user_is_near or self.resource_controller.busy:
                return await fn(self, *args, **kwargs, near=False)
            else:
                try:
                    self.sound_engine.manage_sound_apps(reduce=True)
                    return await fn(self, *args, **kwargs)
                    
                finally:
                    self.sound_engine.manage_sound_apps(reduce=False)
            
        return wrapper
    


    async def handle_pending_events(self):
            
            pending_prompts = await extract_pending_prompts()
            keywords_prompt_pending =  pending_prompts['prompt_pending']
            messages = pending_prompts['result']

            has_messages = len(messages) > 0

            if has_messages:
                self.sound_engine.play_sound(prompt=True)
                self.play_sound('Hey are you there ? ... I have found something in your mailbox ...')
                for key, value in messages.items():
                    await asyncio.sleep(1)
                    self.play_sound(f'{key}:')
                    for m in value:
                            await asyncio.sleep(2)
                            self.play_sound(m)

                if not keywords_prompt_pending:
                    self.play_sound("... and that's about it , I'll be there if you need me ...")
                            

            
            if keywords_prompt_pending:
                await asyncio.sleep(1)
                intro_sound_needed = False if has_messages else True
                await self.prompt_for_terms(intro_sound=intro_sound_needed)



    @proximity
    async def prompt_for_terms(self, near=True, intro_sound=True):

        if not self.prompted_recently:
            if not near:
        
                await delay_event(message='', type='Daily prompt')
                return
            
            self.prompt_active = True
            self.prompted_recently = True
            if intro_sound:
                self.sound_engine.play_sound(prompt=True)


            self.play_sound('Should I look for a specific keyword when parsing your mail ?')

            await asyncio.sleep(0.1)
            answer = await self.sound_engine.sound_to_string()
            if not answer or 'no' in answer.lower() or answer.lower() == '':
                await save_event('Daily prompt')
                return
            
            cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
            nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
            await asyncio.sleep(2)


            terms_string = "and".join(nouns)

            if terms_string and len(terms_string) > 1:
                self.play_sound(f"All right , I will keep an eye on {terms_string} ...")
            
            await save_event('Daily prompt')

            for t in nouns:
                self.keywords.add(t)
                await save_terms(t.lower())

            self.prompt_active = False
    
   

       

    @proximity
    async def announce_keyword_found(self, keywords:dict, near=True, intro_sound=True):
        global  notif
        aggregated = {}
        for k in keywords:
            sender = k['sender']
            keyword = k['keyword']

            if not aggregated.get(keyword):
                aggregated[keyword] = []

            aggregated[keyword].append(sender)

        if near and not self.prompt_active:

            if intro_sound:
                self.sound_engine.play_sound(prompt=True)

            await asyncio.sleep(0.1)
         
            self.play_sound(f'Good news, I have found something in your mailbox')

            was_not_available = False

        else:
            was_not_available = True


        for idx, (k, senders) in enumerate(aggregated.items()):
            senders_string = ',      '.join(senders)

            if idx == 0:
                full_string = f'The keyword {k} was found in messages sent by {senders_string}'
            else:
                full_string = f', the keyword {k} was found in mails coming from {senders_string}'


            self.notif_engine.notify('Keyword found', 
                                     f'the keyword {k} was found in mails coming from {senders_string}')

            if not near or was_not_available:
                await delay_event(message=full_string, type='Keywords found')
                return 
            
            if idx > 0:
                await asyncio.sleep(1)

            self.play_sound(full_string)


