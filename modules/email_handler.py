from imap_tools import MailBox, AND
import os 
from google_auth_oauthlib.flow import InstalledAppFlow
import sqlite3
import contextlib
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
from datetime import datetime

file_path = os.path.dirname(__file__)


def init_google():
    global SECRETS_PATH
    secret_path = '../Oauth2/client_secrets.json'
    SECRETS_PATH = os.path.abspath(os.path.join(file_path, secret_path))

class Email_Manager:

    def __init__(self, provider):
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None

        if provider == 'Google':
           
            init_google()
            self.provider = 'Google'
            self.scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

            with open(SECRETS_PATH, 'r') as f:
                json_secrets = json.load(f)["installed"]

            self.client_secret = json_secrets['client_secret']
            self.client_id = json_secrets['client_id']
            self.token_uri = json_secrets['token_uri']

            self.get_google_oauth()

    def refresh_tokens(self, credentials):
        payload = Credentials(
                            None,  # no access token yet
                            refresh_token=credentials['refresh'],
                            token_uri=self.token_uri,
                            client_id=self.client_id,
                            client_secret=self.client_secret,
                            scopes= self.scopes
                        )

        payload.refresh(Request())

        self.refresh_token = payload.refresh_token or credentials['refresh']
        self.access_token = payload.token 
        self.token_expiry = payload.expiry.isoformat()

        if all([self.token_expiry, self.access_token, self.refresh_token]):
            self.save_tokens()
            

            
    def get_google_oauth(self):
        try:
            db_tokens = self.get_tokens()
            if not db_tokens:
                # Create the flow using the client secrets file
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(SECRETS_PATH,  self.scopes)
                    creds = flow.run_local_server(port=0)
                    self.access_token = creds.token
                    self.refresh_token = creds.refresh_token
                    self.token_expiry = creds.expiry.isoformat()

                except Exception as e:
                    print("OAuth failed:", e)

                if all([self.access_token, self.refresh_token, self.token_expiry]):

                    self.save_tokens()
                else:
                    print('Could not fetch tokens from Google , Terminating...  ')
            else: 

                self.token_valid(tokens=db_tokens)
            

        except Exception as e:
            print("Authentication failed:", e)

    def save_tokens(self):
        with sqlite3.connect('user_data.sqlite') as conn:
            with contextlib.closing(conn.cursor()) as cur :
                cur.execute("""
                CREATE TABLE IF NOT EXISTS keys(
                                                provider VARCHAR(50),
                                                tokens VARCHAR(255), 
                                                refresh_token VARCHAR(255),
                                                token_expiry TEXT
                            );""")
                
                cur.execute("DELETE FROM keys WHERE provider=?", [self.provider])

                cur.execute('INSERT INTO keys VALUES (?, ?, ?, ?)',[self.provider,
                                                                   self.access_token, 
                                                                   self.refresh_token, 
                                                                   self.token_expiry])
                
    def get_tokens(self):
        try:
            with sqlite3.connect('user_data.sqlite') as conn:
                with contextlib.closing(conn.cursor()) as cur:
                    cur.execute('SELECT * FROM keys WHERE provider=?', [self.provider])
                    data = cur.fetchone()
                
                    if data:
                        return {'expiry' : data[3], 
                                'token': data[1], 'refresh': data[2]}
                return None
            
        except sqlite3.Error as e:
            print(f'Error fetching tokens from sqlite : {e}')
            return None
 

    def token_valid(self, tokens=None):
        if not tokens:
             tokens = self.get_tokens()
             if not tokens:
                 return False
       
      
        now = datetime.now()
        expiry = datetime.fromisoformat(tokens['expiry'])

        if (expiry - now).total_seconds() <= 0:
            self.refresh_tokens(tokens)
                

        else:
            self.access_token = tokens['token']
            self.refresh_token = tokens['refresh']
            self.token_expiry = tokens['expiry']

        return True
          
    
    
Google_manager = Email_Manager('Google')

