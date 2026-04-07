import subprocess
import os
import sqlite3
import contextlib
from datetime import datetime, timezone
from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
from .sound_utilities import add_silence

current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, "Amy", "en_US-amy-medium.onnx")
welcome_text = "Hello Gabriel, how can I help you today?"

db_path = os.path.abspath(os.path.join(current_dir, '..\\user_data.sqlite'))




class SoundEngine():
    def __init__(self):

        self.audio_bytes = None
        self.rate = 22050
        self.text = None
        prompt_sound = self.load_sound('tones', 'name', 'Prompt sound A')
        self.prompt_sound = prompt_sound['sound']
        self.prompt_rate = prompt_sound['rate']
     
        self.stt_model = WhisperModel("base", device="cpu", compute_type="int8")
    


    def load_sound(self, table='TTS', name='text', text=None):

        try:
            with sqlite3.connect(db_path) as conn:
                with contextlib.closing(conn.cursor()) as cur:
                    cur.execute(f"""SELECT * FROM {table} WHERE {name}=?""", [text])
                    sound = cur.fetchone()
                    if table == 'tones':
                        return {'rate': sound[2], 'sound':sound[1]}
                    else:
                        self.audio_bytes = sound[2]
                   
        except sqlite3.Error as e:
            print(f'Error writing soudn to db : {e}')


    def create_wav(self, text, output_path):

        # Piper expects UTF‑8 text on stdin
        process = subprocess.Popen(
            [
                "piper",
                "--model", model_path,
                "--output_file", output_path
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        stdout, stderr = process.communicate(text.encode("utf-8"))

        
        print("stderr:", len(stderr.decode()))

        if len(stderr.decode()) == 0:
            print("Done. WAV generated at:", output_path)
        else:
            print('Error converting text to sound')


    def create_sound(self, text, blob=False):
        # Piper expects UTF‑8 text on stdin
       
        process = subprocess.Popen(
            ["piper", "--model", model_path, "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
     

        pcm_data , stderr = process.communicate(text.encode("utf-8"))
        self.text = text
        self.audio_bytes = add_silence(pcm_bytes=pcm_data)

    def save_to_blob(self):
        now = datetime.now(timezone.utc)
        time_to_string = now.isoformat()
        try:
            with sqlite3.connect(db_path) as conn:
                with contextlib.closing(conn.cursor()) as cur:
                        cur.execute("""CREATE TABLE IF NOT EXISTS TTS(
                                                                date TEXT,
                                                                text TEXT UNIQUE,
                                                                audio BLOB,
                                                                sample_rate INTEGER
                                                                ) 
                                """)
                        cur.execute(f"""CREATE INDEX IF NOT EXISTS idx_text ON TTS (text)""")

                        cur.execute("""INSERT OR IGNORE INTO TTS(date, text, audio, sample_rate) 
                                                VALUES (?,?,?,?)""",
                                                [time_to_string, self.text, self.audio_bytes, 
                                                 self.rate])
        except sqlite3.Error as e:
            print(f'Error writing sound to db : {e}')


    def play_sound(self, prompt=False):
        if not prompt:
            if not self.audio_bytes:
                print('load_sound or create_sound must be called before using play_sound')
                return 
            rate=self.rate
            sound = self.audio_bytes
        else:
            rate = self.prompt_rate * 2
            sound = self.prompt_sound


        pcm = np.frombuffer(bytes(sound), dtype=np.int16)
        sd.play(pcm, rate)
        sd.wait()


    async def sound_to_string(self, duration=5, sample_rate = 16000):
        try:
        
            audio = sd.rec(int(duration * sample_rate),samplerate=sample_rate,channels=1,
                                                                              dtype='int16')
            sd.wait()
            
            pcm_bytes = audio.tobytes()
            audio = np.frombuffer(bytes(pcm_bytes), dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = self.stt_model.transcribe(audio, language="en")
            return " ".join([seg.text for seg in segments])
        
        except Exception as e:
            print(f'Error converting sound input to string : {e}')





