
from controllers.movies.movie_client import Movie_Client
from controllers.movies.db_calls import (save_movie, get_unseen_movies, get_liked_terms, 
                                         save_liked_movie_terms, get_movies_by_id)
import random
from utilities.functions.functions import extract_nouns
from utilities.db.async_calls import get_logged_events, save_event
import json
from datetime import datetime, timedelta


class Movie_Controller():
    def __init__(self):
        self.client = Movie_Client()
        self.best_movies = []

        
    async def init_best_movies(self):
        last_event = await get_logged_events("'Movie update'", limit=1)
        if last_event:
            time = datetime.fromisoformat(last_event[1])
            if not datetime.now() - time > timedelta(days=1):
                self.best_movies = await get_movies_by_id(json.loads(last_event[3]))
                return
        
        await self.select_best_movies()
        
               


    async def fetch_movies(self, pages=1):
        await self.client.create_session()

        generator = await self.client.make_imdbId_generator(pages, 
                                                        genres=['horror', 'crime', 'sci-fi'])
        async for movie in generator:
            await save_movie(movie)

        await self.client.terminate_session()


    async def select_best_movies(self):
        movies:dict = await get_unseen_movies()
        liked_terms:list = await get_liked_terms()

        scored_movies = {}
        for t in liked_terms:
            short_term = t['term'][:6]
            for id, m in movies.items():
                if short_term in m['title'] or short_term in m['plot']:
                    scored_movies[id] = scored_movies.get(id, 0) + t['score']

        print(scored_movies)
        best = []

        if scored_movies:
            for i in range(3):

                best_recommendation = max(scored_movies, key=scored_movies.get)
                best.append(best_recommendation)

        else:
            best = random.sample(list(movies.keys()), 3)

        self.best_movies = await get_movies_by_id(best)
        await save_event('Movie update', json.dumps([i for i in best]))
           
        

        


    async def like_movie(self, movie_id):
        for m in self.best_movies:
            if m['id'] == movie_id:
                nouns_title:set = extract_nouns(m['title'].lower())
                nouns = nouns_title.union(extract_nouns(m['plot'].lower()))
                
                await save_liked_movie_terms(nouns)

        
        









