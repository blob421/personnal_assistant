
from controllers.movies.movie_client import Movie_Client
from controllers.movies.db_calls import (save_movie, get_unseen_movies, get_liked_terms, 
                                         save_liked_movie_terms, get_movies_by_id, 
                                         get_movie_by_id,
                                         match_movie_term, mark_seen)
import random
from utilities.functions.functions import extract_nouns, prefix
from utilities.db.async_calls import get_logged_events, save_event
import json
from datetime import datetime, timedelta
import os
import config


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
        
               
    async def save_posters(self):
        await self.client.create_session()
  
        for p in self.best_movies:
       
            async with self.client.session.get(p['poster']) as r:
                data = await r.read()
                with open(os.path.join(config.POSTERS_PATH, f'{p['imdbId']}.jpg'), 'wb') as pic:
                    pic.write(data)

        await self.client.terminate_session()


    async def fetch_movies(self, pages=1):
        await self.client.create_session()

        generator = await self.client.make_imdbId_generator(pages, 
                                                        genres=['horror', 'crime', 'sci-fi'])
        async for movie in generator:
            await save_movie(movie)

        await self.client.terminate_session()

    #### DO TRIGRAM SEARCH INSTEAD WITH prefix function faster

    async def select_best_movies(self):
        movies:dict = await get_unseen_movies()

        scored_movies = {}
     
        for id, m in movies.items():
         

            title_nouns:set = extract_nouns(m['title'].lower())
            plot_nouns:set = extract_nouns(m['plot'].lower())
            for w in plot_nouns.union(title_nouns):
                if len(w) < 5: continue
                w = prefix(w)

                match = await match_movie_term(w)
                if match:
                    scored_movies[id] = scored_movies.get(id, 0) + match[1]
           

        print(scored_movies)
        best = []

        if scored_movies:
            for i in range(3):

                best_recommendation = max(scored_movies, key=scored_movies.get)
                best.append(best_recommendation)
                scored_movies.pop(best_recommendation)

        else:
            best = random.sample(list(movies.keys()), 3)

        self.best_movies = await get_movies_by_id(best)
        await self.save_posters()
        await save_event('Movie update', json.dumps([i for i in best]))
           
 
    def like_movie(self, movie_id):
        m = get_movie_by_id(movie_id)
       
        nouns_title:set = extract_nouns(m['title'].lower())
        nouns = nouns_title.union(extract_nouns(m['plot'].lower()))
                
        save_liked_movie_terms(nouns)

    async def mark_seen(self, movie_id):
        await mark_seen(movie_id)


        
        









