
from utilities.functions.functions import make_announcements, extract_nouns
from utilities.db.async_calls import delay_event

from utilities.words.exceptions import EXCEPT_NOUNS

from controllers.notifications.controller import notif_controller
from .sound_engine import SoundEngine
import asyncio
import config as config


class Vocal_Handler():

    def __init__(self, is_windows_os, keywords):
        self.sound_engine = SoundEngine(is_windows_os)
        self.prompt_active = False
        self.prompted_recently = False
        self.keywords = keywords
        self.notif_engine = notif_controller()

        self.contacts = {}



    def play_sound(self, string):
       
        self.sound_engine.create_sound(string)
        self.sound_engine.play_sound()
        
    


    @staticmethod
    def manage_sound(fn):
        async def wrapper(self, *args, **kwargs):

            try:
                self.sound_engine.manage_sound_apps(reduce=True)
                return await fn(self, *args, **kwargs)
                
            finally:
                self.sound_engine.manage_sound_apps(reduce=False)
            
        return wrapper
    

    @manage_sound
    async def prompt_for_terms(self, near=True):
       
        if not near: return None, None, False

        if not self.prompted_recently and not config.OPTIONS['silent_mode']:
       
            self.prompt_active = True
            self.prompted_recently = True
            self.play_sound('Do you want me to keep an eye for other keywords ?')
           
            await asyncio.sleep(0.1)
            answer = await self.sound_engine.sound_to_string()

            if not answer or 'no' in answer.lower() or answer.lower() == '':
               
                return None, None, True
            
            await asyncio.sleep(0.5)
            self.play_sound('All right , tell me ... what should I add to your list ?')
            await asyncio.sleep(0.1)
            answer = await self.sound_engine.sound_to_string()
            
            cleaned_answer = answer.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
            nouns = [n for n in extract_nouns(cleaned_answer) if n.lower() not in EXCEPT_NOUNS]
            await asyncio.sleep(2)


            terms_string = "and".join(nouns)
          
            if nouns and len(nouns) > 1:
                self.play_sound(f"All right , I will keep an eye on {terms_string} ...")

            else: 
                terms_string, nouns = None, None
                
   
            self.prompt_active = False
            return nouns, terms_string, True
        
    
    async def process_pending_events(self, messages:dict):
    
        self.sound_engine.play_sound(prompt=True)
        self.play_sound('Are you there ? ... I might have found something interesting...')

        for k , value in messages.items():
            if k == 'Keyword found':
                
                await asyncio.sleep(1)
                for m in value:
                        await asyncio.sleep(0.3)
                        self.play_sound(m)

            if k == 'watch list':
                vocal_base = f'Something in your watchlist popped up'
                self.play_sound(vocal_base)
                await asyncio.sleep(1)
                for m in value:
                    await asyncio.sleep(1.5)
                    self.play_sound(m)



   


    
    @manage_sound
    async def announce_keyword_found(self, keywords:dict, gui, near=True, intro=True):
        
        announcements = await make_announcements(keywords, self.notif_engine, gui)
       
        if config.OPTIONS['silent_mode']: return 
   

        if near and not self.prompt_active:

            if intro:
                self.sound_engine.play_sound(prompt=True)

                await asyncio.sleep(0.1)
                
                self.play_sound(f'Are you there ? ... I might have found something interesting...')

            else:

                await asyncio.sleep(0.1)
                
                self.play_sound(f'There is also something else ...')
            
            was_not_available = False

        else:
            was_not_available = True
 
        full_announcement_string = ' '.join(announcements)

        if not near or was_not_available:
            await delay_event(message=full_announcement_string, type='Keyword found')
        
        else:       
            self.play_sound(full_announcement_string)


                
  
    @manage_sound
    async def announce_messages(self, messages:dict, near=True):

        if near:
            self.sound_engine.play_sound(prompt=True)
            await asyncio.sleep(0.5)
            vocal_base = f'Are you there ? ... Something came up in your watchlist.'
            self.play_sound(vocal_base)
            await asyncio.sleep(0.3)

     
        for idx, (sender, msgs) in enumerate(messages.items()):
            number_of_messages = len(msgs)
            amnt_string = 'a message' if number_of_messages == 1 else f'{number_of_messages} messages'
            alias = self.contacts[sender]
            
            base_string =  'You also received' if idx > 0 else 'You received'

            m_string = f'{base_string} {amnt_string} from {alias} ,'

         
       
            if number_of_messages > 1:
                fist_tags_msg = None
                for idx , n in enumerate(msgs):

                    if not n['tags']:
                        continue
                    
                    state = ' but '.join(n['tags'])
                    if idx == 0 or fist_tags_msg is None:
                        m_string += f' One seemed {state}'
                        fist_tags_msg = True

 
                    elif idx == number_of_messages - 1:
                        m_string += f' and the last one seemed {state}'
                    
                    else:
                        m_string += f', an other seemed {state}'
            else:
                if not msgs[0]['tags']:
                    pass
                state = ' but '.join(msgs[0]['tags'])
                m_string += f'it seemed {state}'

     
                
       

            self.notif_engine.notify(title='Watchlist event', message=m_string)
 
            if not near:
                await delay_event(message=m_string, type='watch list')
                continue
            else:
                self.play_sound(m_string)
                await asyncio.sleep(0.5)
       
      
        

            
            
     
      





        

        

       
                


