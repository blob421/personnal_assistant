import wave
from sound_utilities import add_silence
import sqlite3
import contextlib
import os 
import io

current_dir = os.path.dirname(__file__)
path = os.path.abspath(os.path.join(current_dir, '../../user_data.sqlite' ))
DB_PATH = path
def save_to_db(audio_bytes, name, rate):
     
    try:
        with sqlite3.connect(DB_PATH) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                    cur.execute("""CREATE TABLE IF NOT EXISTS tones (
                                                            name TEXT UNIQUE,
                                                            audio BLOB,
                                                            sample_rate INTEGER) 
                            """)
                    cur.execute(f"""CREATE INDEX IF NOT EXISTS idx_name ON tones (name)""")

                    cur.execute("""INSERT OR IGNORE INTO tones(name, audio, sample_rate) 
                                            VALUES (?,?,?)""",
                                            [name, audio_bytes, rate])
    except sqlite3.Error as e:
            print(f'Error writing sound to db : {e}')

def wav_to_bytes(file_name, name):
   path = os.path.join(current_dir, 'Tones', file_name)
   buffer = io.BytesIO()

   with wave.open(path, 'rb') as wav:
        sample_rate = wav.getframerate()
        frames = wav.readframes(wav.getnframes())
        buffer.write(frames)
        
   save_to_db(add_silence(buffer.getvalue()) , name, sample_rate)


wav_to_bytes('sine_263Hz_1s.wav', 'Prompt sound A')