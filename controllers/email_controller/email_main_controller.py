from .email_auth_manager import Email_Auth_Manager

from .extract_email import extract_mail
import aioimaplib
import logging
from utilities.db_calls import mark_emails_read, email_was_processed
from utilities.functions import extract_gmail_msgid, are_keywords_in_messages
import asyncio

logger = logging.getLogger(__name__)

logging.basicConfig(filename='./logs/email_controller.log', level=logging.INFO)

from datetime import datetime

class Email_Main_Controller():

    
    def __init__(self, providers, vocal_handler, keywords):
       self.auth_managers = {}
       self.keywords = keywords
       self.providers = providers
       self.vocal_handler = vocal_handler

       self.create_auth_managers()
    
      

    async def get_messages(self):
    
        while True:
            await self.connect()
            messages = await self.get_emails('Google', 'INBOX')
        
            if messages:
                found_keywords = await are_keywords_in_messages(messages, self.keywords)
                if found_keywords:
                    await self.vocal_handler.last_asked_for_keywords()
                    await self.vocal_handler.announce_keyword_found(found_keywords)
            await asyncio.sleep(1800)


    def create_auth_managers(self):
       
       for p in self.providers:
          self.auth_managers[p] = {'manager': Email_Auth_Manager(p), 'imap': None}
          
    async def connect(self):
       
       for provider, auth_manager in self.auth_managers.items():
            manager = auth_manager['manager']
           
            if manager.user_email: 

                manager.token_valid()
                now = datetime.now()
                for n in range(4):
                    try:
                        imap = aioimaplib.IMAP4_SSL(manager.imap_uri, port=manager.imap_port)
                        await imap.wait_hello_from_server()

                        
                        result = await imap.xoauth2(manager.user_email, manager.access_token)
                        break

                    except TimeoutError as e:
                        logger.info(f'Time : {now.isoformat()}  Error connecting to imap box , retrying in {1 + n} s')
                       
                        if n == 3:
                            logger.warning(f'Time : {now.isoformat()}  Error connecting to imap box : {e}')
                            return
                        
                        await asyncio.sleep(1 + n)
                        continue

                if not result.result == 'OK':
                    error_message = result.lines[0].decode()
                    print(f"Connection with box.xoauth2 failed: {error_message}")

                self.auth_managers[provider]['imap'] = imap
                logger.info(f'Time: {now.isoformat()}    Successfully connected to imap box')

            else:
                print('Could not connect , did not get the email from the api')
    

    
    async def get_emails(self, provider, folder):
        imap = self.auth_managers[provider]['imap']

        await imap.select(folder)

        result, data = await imap.search('UNSEEN')
        if result == 'OK' and data[0]:
            msg_ids = data[0].split()
        else:
            msg_ids = []

        emails = []
        for i in msg_ids:
            id = i.decode()
        
            _ , msg_data = await imap.fetch(id, '(X-GM-MSGID BODY.PEEK[])')
        
            raw = msg_data[1]
            X_GM_ID = extract_gmail_msgid(msg_data)

            if not await email_was_processed(X_GM_ID):
            
                email = extract_mail(raw)
        
                
                emails.append({'text': email['text_body'] , 'sender': email['sender'], 
                                                            'subject': email['subject'], 
                                                            'id':X_GM_ID})
                
                # imap.store(msg_id, '+FLAGS', '\\Seen') Mark then as seen

        await imap.logout()
        if len(emails) > 0:  
            await mark_emails_read(emails)
            return emails
                
        return None


## DATA[0] : [b'FLAGS', b'(\\Answered', b'\\Flagged', b'\\Draft', b'\\Deleted', b'\\Seen', b'$NotPhishing', b'$Phishing)']