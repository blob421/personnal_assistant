from email_auth_manager import Email_Auth_Manager
from imap_tools import MailBox, AND
from extract_email import extract_mail
import imaplib


def generate_oauth2_string(email, access_token):
    return f"user={email}\x01auth=Bearer {access_token}\x01\x01"

 



class Email_Main_Controller():
    
    def __init__(self, providers):
       self.auth_managers = {}
       self.providers = providers
       self.create_auth_managers()
      
    def create_auth_managers(self):
       
       for p in self.providers:
          self.auth_managers[p] = {'manager': Email_Auth_Manager(p), 'imap': None}
          
    def connect(self):
       
       for provider, auth_manager in self.auth_managers.items():
            manager = auth_manager['manager']
           
            if manager.user_email: 

                manager.token_valid()

                imap = imaplib.IMAP4_SSL(auth_manager['manager'].imap_uri)

                connection_string = generate_oauth2_string(manager.user_email, 
                                                            manager.access_token)
                
                imap.authenticate("XOAUTH2", lambda _: connection_string)

                self.auth_managers[provider]['imap'] = imap

            else:
                print('Could not connect , did not get the email from the api')
    
    def get_emails(self, provider, folder):
       imap = self.auth_managers[provider]['imap']
       imap.select(folder)
       status, data = imap.search(None, "ALL") # or UNSEEN

       emails = []
       for msg_id in data[0].split():
            status, msg_data = imap.fetch(msg_id, "(RFC822)")
            print(status)
            raw = msg_data[0][1]
           
            
            emails.append(extract_mail(raw)['text_body'])
           # imap.store(msg_id, '+FLAGS', '\\Seen') Mark then as seen
            if len(emails)> 1: 
                return emails
           
       return emails


