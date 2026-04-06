from .email_auth_manager import Email_Auth_Manager

from .extract_email import extract_mail
import aioimaplib


class Email_Main_Controller():
    
    def __init__(self, providers):
       self.auth_managers = {}
       self.providers = providers
       self.create_auth_managers()
      
    def create_auth_managers(self):
       
       for p in self.providers:
          self.auth_managers[p] = {'manager': Email_Auth_Manager(p), 'imap': None}
          
    async def connect(self):
       
       for provider, auth_manager in self.auth_managers.items():
            manager = auth_manager['manager']
           
            if manager.user_email: 

                manager.token_valid()

                imap = aioimaplib.IMAP4_SSL(manager.imap_uri, port=manager.imap_port)
                await imap.wait_hello_from_server()

                
                result = await imap.xoauth2(manager.user_email, manager.access_token)

                if not result.result == 'OK':
                    error_message = result.lines[0].decode()
                    print(f"Connection with box.xoauth2 failed: {error_message}")

                self.auth_managers[provider]['imap'] = imap

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
        for id in msg_ids:
                msg_data = await imap.fetch(id.decode(), "(BODY.PEEK[])")
             
                raw = msg_data.lines[1]
            
                
                emails.append(extract_mail(raw)['text_body'])
            # imap.store(msg_id, '+FLAGS', '\\Seen') Mark then as seen
                if len(emails)> 0: 

                    await imap.logout()
                    return emails
                
        await imap.logout()
        return emails


## DATA[0] : [b'FLAGS', b'(\\Answered', b'\\Flagged', b'\\Draft', b'\\Deleted', b'\\Seen', b'$NotPhishing', b'$Phishing)']