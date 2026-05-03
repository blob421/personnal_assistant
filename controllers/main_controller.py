
from utilities.functions.functions import are_keywords_in_messages
from utilities.db.async_calls import (get_logged_events, save_terms, load_contacts_async, 
                                      mark_emails_read, save_event)
from utilities.functions.get_intent import get_intent
from utilities.functions.functions import extract_pending_prompts
from controllers.timer.timer import Timer
import asyncio
from datetime import datetime, timedelta

class MainController():

    def __init__(self, email_controller, vocal_handler, device_controller, resource_controller):
        self.email_controller = email_controller
        self.vocal_handler = vocal_handler
        self.device_controller = device_controller
        self.resource_controller=  resource_controller
        self.timer = Timer()
        self.gui = None
        self.keyword_prompt_due = False

        self.watchlist = None
        
        self.timer.is_operating_hours()


    @staticmethod     
    def proximity(fn):
        async def wrapper(self, *args, **kwargs):
            if (not self.device_controller.user_is_near or self.resource_controller.busy 
                                                or not self.timer.operating_hours):
                return await fn(self, *args, **kwargs, near=False)
            
            return await fn(self, *args, **kwargs, near=True)
        
        return wrapper
            
     
        
    async def last_asked_for_keywords(self):
        last = await get_logged_events(col="'Daily prompt'", limit=1)
        if not last:
            self.keyword_prompt_due = True
            return 
        
        time = datetime.fromisoformat(last[1])
        now = datetime.now()

        if (now - time > timedelta(days=1)):
            self.keyword_prompt_due = True



    ##################################### MAIL #########################################################
    @proximity
    async def process_mail(self, near=False):
         
        await self.email_controller.connect()
        messages = await self.email_controller.get_emails('Google', 'INBOX')
        processed , something_was_announced = await self.handle_messages(messages, near)
        
        if processed:
            found_keywords, occurences = await are_keywords_in_messages(processed, 
                                                                        self.vocal_handler.keywords.keys())
            if found_keywords:
                await self.vocal_handler.announce_keyword_found(found_keywords, 
                                                                intro = not something_was_announced, 
                                                                gui=self.gui, near=near)
                
            if occurences:
                for k, v in occurences.items():
                    self.vocal_handler.keywords[k] += v
                    occurences[k] = self.vocal_handler.keywords[k]
                self.gui.keywords_updater.reload_requested.emit()


                await save_terms(occurences=occurences)


            
  
    async def handle_messages(self, emails, near=False):

        if len(emails) > 0:
            self.watchlist = await load_contacts_async()
            intent_emails, need_reload = await get_intent(emails, self)
            await mark_emails_read(intent_emails)
            
            if need_reload:
                self.gui.watchlist_worker.reload_requested.emit()
              
                await self.vocal_handler.announce_messages(intent_emails, near=near)

            return emails, need_reload
                
        return None, False
    
    ######################################## EVENTS  #############################################

    @proximity
    async def handle_pending_events(self, near=False):
            if not self.timer.operating_hours or not near: return
            await self.last_asked_for_keywords()

            pending_prompts = await extract_pending_prompts()
            messages = pending_prompts['result']

            has_messages = len(messages.keys()) > 0

            if has_messages:
                await self.vocal_handler.process_pending_events()

            
            if self.keyword_prompt_due:
                await asyncio.sleep(1)
                await self.handle_prompt()


    @proximity
    async def handle_prompt(self, near=False):
        nouns, terms_string, prompted = await self.vocal_handler.prompt_for_terms(near=near)

        if not terms_string or not nouns:
             await save_event('Daily prompt', None)
        else:
            message = f'Saved {terms_string}'
            await save_event('Daily prompt', message)

            for t in nouns:
                self.vocal_handler.keywords[t] = 0
                await save_terms(t.lower())
        
            self.gui.worker.reload_requested.emit()

        self.keyword_prompt_due = not prompted

#########################################################################################