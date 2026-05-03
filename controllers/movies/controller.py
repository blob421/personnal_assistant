import config as config 
import json
import os
from aiohttp import ClientSession
from .db_calls import movie_fillup_due, save_movies


api_key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../', 'secrets', 'omdb.json'))
OMDB_API_URL = "https://www.omdbapi.com/"

GENRES = ['Horror', 'Sci-fi', 'Crime', 'Comedy']
GENRE = ['Horror']
with open(api_key_path, 'r') as f:
    api_key = json.load(f)['key']


db_string = config.DB_PATH



class MovieController():
    def __init__(self):
        self.suggested = []
        self.fill_up_due = False

    
    async def fetch_movies(self, string):
        async with ClientSession() as session:
            async with session.get(string) as response:
                   return await response.json()
              
               

    async def fill_up(self):

        if not self.fill_up_due: 
            return 
        
        for g in GENRE:
            for i in range(1):

                search_string = f"{OMDB_API_URL}?s={g}&type=movie&page={i + 1}&apikey={api_key}"
                data = await self.fetch_movies(search_string)
                await save_movies(data)



    async def is_fillup_due(self):
        self.fill_up_due = await movie_fillup_due()



