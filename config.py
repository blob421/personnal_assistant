import os 

ROOT = os.path.dirname(__file__)

DB_PATH = os.path.join(ROOT, 'user_data.sqlite')

OAUTH_GOOGLE_SECRETS_PATH = os.path.join(ROOT, 'secrets', 'google_secrets.json')

CONFIRMED_PROVIDERS = ['Google']

PROCESS_NAME = 'python.exe'

POSTERS_PATH =  os.path.join(
                        os.path.dirname(__file__), 'GUI', 'assets', 'posters')


default_options = {
                   'op_h_start': '09:00',
                   'op_h_end': '21:00',
                   'silent_mode': False,
                   'notifications': True,
                   'font_scaling': '0.9',
                   'window_size': '1400:750',
                   'sound_level' : '0.7'
                   }

OPTIONS = {}