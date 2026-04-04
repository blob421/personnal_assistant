from email_auth_manager import Email_Auth_Manager
from imap_tools import MailBox, AND
import base64
import imaplib

def generate_oauth2_string(email, access_token):
    auth_string = f"user={email}\1auth=Bearer {access_token}\1\1"
    return base64.b64encode(auth_string.encode()).decode()


CONFIRMED_PROVIDERS = ['Google']

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
            
            if auth_manager['manager'].user_email:

                auth_manager['manager'].token_valid()

                imap = imaplib.IMAP4_SSL(auth_manager['manager'].imap_uri)

                connection_string = generate_oauth2_string(auth_manager['manager'].user_email, 
                                                            auth_manager['manager'].access_token)
                
                imap.authenticate("XOAUTH2", lambda _: connection_string)

                self.auth_managers[provider]['imap'] = imap

            else:
                print('Could not connect , did not get the email from the api')
    
    def get_emails(self):
       pass


controller = Email_Main_Controller(CONFIRMED_PROVIDERS)