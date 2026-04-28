import os 

ROOT = os.path.dirname(__file__)

DB_PATH = os.path.join(ROOT, 'user_data.sqlite')

OAUTH_GOOGLE_SECRETS_PATH = os.path.join(ROOT, 'secrets', 'google_secrets.json')

CONFIRMED_PROVIDERS = ['Google']

PROCESS_NAME = 'python.exe'


default_options = {
                   'op_h_start': '09:00',
                   'op_h_end': '21:00',
                   'silent_mode': False,
                   'notifications': True,
                   'font_scaling': '0.9'
                   }

OPTIONS = {}