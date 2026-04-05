
import os 
from google_auth_oauthlib.flow import InstalledAppFlow
import sqlite3
import contextlib
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
from datetime import datetime
import requests

file_path = os.path.dirname(__file__)


def init_google():
    global SECRETS_PATH
    secret_path = '../Oauth2/client_secrets.json'
    SECRETS_PATH = os.path.abspath(os.path.join(file_path, secret_path))

class Email_Auth_Manager():

    def __init__(self, provider):
        self.user_email = None
        self.access_token = None
        self.refresh_token = None
        self.token_expiry = None
        self.imap_uri = None

        if provider == 'Google':
           
            init_google()
            self.provider = 'Google'
            self.scopes = ["https://mail.google.com/","openid",
                           "https://www.googleapis.com/auth/userinfo.email"]

            with open(SECRETS_PATH, 'r') as f:
                json_secrets = json.load(f)["installed"]

            self.imap_uri = 'imap.gmail.com'
            self.imap_port = 993
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
                    creds = flow.run_local_server(port=0, prompt='consent', access_type='offline')
               
                    self.access_token = creds.token
                    self.refresh_token = creds.refresh_token
                    self.token_expiry = creds.expiry.isoformat()

                except Exception as e:
                    print("OAuth failed:", e)

                if all([self.access_token, self.refresh_token, self.token_expiry]):

                    self.save_tokens()
                    self.user_email = self.fetch_user_email()
                else:
        
                    print('Could not fetch tokens from Google , Terminating...  ')
            else: 

                self.token_valid(tokens=db_tokens)
                self.user_email = self.fetch_user_email()
            

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
               tokens = {'token': self.access_token, 
                         'refresh': self.refresh_token, 'expiry': self.token_expiry}
       
      
        now = datetime.now()
        expiry = datetime.fromisoformat(tokens['expiry'])

        if (expiry - now).total_seconds() <= 300:
            self.refresh_tokens(tokens)
                
        else:
            self.access_token = tokens['token']
            self.refresh_token = tokens['refresh']
            self.token_expiry = tokens['expiry']

       
       
    def fetch_user_email(self):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)

        if resp.status_code == 200:
            data = resp.json()
            return data.get("email")
        else:
            print("Failed to fetch user email:", resp.text)
            return None
    


