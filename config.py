import os 

ROOT = os.path.dirname(__file__)

DB_PATH = os.path.join(ROOT, 'user_data.sqlite')

OAUTH_GOOGLE_SECRETS_PATH = os.path.join(ROOT, 'secrets', 'google_secrets.json')

CONFIRMED_PROVIDERS = ['Google']