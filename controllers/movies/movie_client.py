import config as config 
import json
import os
from aiohttp import ClientSession
from .db_calls import movie_fillup_due
import asyncio
from controllers.movies.db_calls import save_imdb_id

secrets_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', '../', 'secrets'))
omdb_path = os.path.join(secrets_folder ,'omdb.json')
tbdb_path = os.path.join(secrets_folder, 'tmdb.json')

OMDB_API_URL = "https://www.omdbapi.com/"

GENRES = ['Horror', 'Sci-fi', 'Crime', 'Comedy']
GENRE = ['Horror']

with open(omdb_path, 'r') as f:
    omdb_key = json.load(f)['key']

with open(tbdb_path, 'r') as f:
    tmdb_key = json.load(f)['read_token']
    tmdb_creds ={'Authorization': f'Bearer {tmdb_key}'}

TMDB_CODES = {'horror':27 , 'sci-fi': 878, 'crime':80}

db_string = config.DB_PATH



class Movie_Client():
    def __init__(self):
        self.suggested = []
        self.fill_up_due = False
        self.session = None
      

    async def create_session(self):
        self.session = ClientSession()

    async def terminate_session(self):
        await self.session.close()
    
    async def is_fillup_due(self):
        self.fill_up_due = await movie_fillup_due()          
         
    async def fetch_with_session(self, string, creds=None):
            async with self.session.get(string, headers=creds) as response:
                if response.ok:
                    return await response.json()
                return None

    async def get_ids(self, amount_pages, genres):
        codes = [TMDB_CODES[g] for g in genres]
        codestring = '|'.join([str(c) for c in codes])
    
        page = 1 
        while page < amount_pages + 1:
            tmdb_string = f"https://api.themoviedb.org/3/discover/movie?with_genres={codestring}&page={page}"
            results = await self.fetch_with_session(tmdb_string, tmdb_creds)

            if not results or not results['results']:
                break

            page += 1
            yield results['results']


    async def handle_imdb_id(self, ids_gen):
        
        async for r in ids_gen:
            urls = [f"https://api.themoviedb.org/3/movie/{m['id']}/external_ids" for m in r]
            tasks = [self.fetch_with_session(url, tmdb_creds) for url in urls]
            results = await asyncio.gather(*tasks)
            for r in results:
                id = r['imdb_id']
                if id :
                    saved = await save_imdb_id(id)
                    if saved:
                       yield id
                        
            
              
          
    
    async def get_movie_data(self, imdbId_generator):
        async for id in imdbId_generator:
         
            search_string = f"{OMDB_API_URL}?i={id}&apikey={omdb_key}"
    
            data = await self.fetch_with_session(search_string)

            if data :

                yield data
           
              


    async def make_imdbId_generator(self ,pages=1, genres=None):
        return (
                self.get_movie_data(
                    self.handle_imdb_id(
                        self.get_ids(pages, genres)
                        )
                  
                    )
                )