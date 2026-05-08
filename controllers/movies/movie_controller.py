
from controllers.movies.movie_client import Movie_Client
from controllers.movies.db_calls import (save_movie, get_unseen_movies, 
                                         save_liked_movie_terms, get_movies_by_id, like_movie,
                                         not_interested_movie,descore_terms,
                                         match_movie_term, mark_seen, movie_fillup_due)
import random
from utilities.functions.functions import extract_nouns, prefix
from utilities.db.async_calls import get_logged_events, save_event
import json
from datetime import datetime, timedelta
import os
import config
from PyQt6.QtCore import pyqtSignal, QObject
import asyncio

class Movie_Signals(QObject):
    liked = pyqtSignal()
    seen = pyqtSignal()
    interested = pyqtSignal()
    scramble = pyqtSignal()

    def __init__(self, controller):
        super().__init__()
        self.controller:Movie_Controller = controller
        self.liked.connect(self.handle_like)
        self.seen.connect(self.handle_seen)
        self.interested.connect(self.handle_interest)
        self.scramble.connect(self.handle_scramble)
        
    def handle_like(self):
      self.controller.loop.call_soon_threadsafe(
                            asyncio.create_task,
                            self.controller.like_movie()
                        )
         
    def handle_seen(self):
         self.controller.loop.call_soon_threadsafe(       
            asyncio.create_task, self.controller.mark_seen()
            )
      

    def handle_interest(self):
         self.controller.loop.call_soon_threadsafe(
            asyncio.create_task, self.controller.mark_interested())
        
    def handle_scramble(self):
        self.controller.loop.call_soon_threadsafe(asyncio.create_task, self.controller.select_best_movies())

class Movie_Controller():
    def __init__(self):
        self.loop = None
        self.client = Movie_Client()
        self.best_movies = []
        self.gui = None
        self.signals_worker = Movie_Signals(self)
 
    @staticmethod
    def client_needed(fn):
        async def wrapper(self, *args, **kwargs):
            try:
                await self.client.create_session()
                return await fn(self, *args, **kwargs)
            
            finally:
                await self.client.terminate_session()
        return wrapper

    async def movie_fillup_due(self):
        due = await movie_fillup_due()
        if due:
            await self.fetch_movies()


    async def init_best_movies(self):
        last_event = await get_logged_events("'Movie update'", limit=1)
        if last_event:
            time = datetime.fromisoformat(last_event[1])
            if not datetime.now() - time > timedelta(days=1):
                self.best_movies = await get_movies_by_id(json.loads(last_event[3]))
                
                return
        
        await self.select_best_movies()
        

    @client_needed
    async def save_posters(self):

        for p in self.best_movies:
       
            async with self.client.session.get(p['poster']) as r:
                data = await r.read()
                with open(os.path.join(config.POSTERS_PATH, f'{p['imdbId']}.jpg'), 'wb') as pic:
                    pic.write(data)



    @client_needed
    async def fetch_movies(self):
        generator = await self.client.make_imdbId_generator(genres=['horror', 'crime', 'sci-fi'])
        async for movie in generator:
            await save_movie(movie)
            
        self.client.n_of_ids_fetched = 0




    async def select_best_movies(self):

        movies:dict = await get_unseen_movies()
        scored_movies = {}
      
        for id, m in movies.items():
         
            if not m.get('title') or not m.get('plot') or not m.get('poster'):
                continue
            title_nouns:set = extract_nouns(m['title'].lower())
            plot_nouns:set = extract_nouns(m['plot'].lower())
            for w in plot_nouns.union(title_nouns):
                if len(w) < 5: continue
                w = prefix(w)

                match = await match_movie_term(w)
                if match:
                    scored_movies[id] = scored_movies.get(id, 0) + match[1]
              
           

        best = []
        if scored_movies:
            for i in range(3):

                best_recommendation = max(scored_movies, key=scored_movies.get)
                best.append(best_recommendation)
                scored_movies.pop(best_recommendation)

        else:
            best = random.sample(list(movies.keys()), 3)

        for m in self.best_movies:
            id = m['imdbId']
       
            os.remove(os.path.join(config.POSTERS_PATH, f'{id}.jpg'))
            
        self.best_movies = await get_movies_by_id(best)
        await self.save_posters()
        await save_event('Movie update', json.dumps([i for i in best]))
        self.gui.movie_worker.reload_requested.emit()
        


    ############################# GUI BUTTONS #######################################

    async def like_movie(self):
    
        movie_id, new_value = self.handle_gui_data('liked')
    
  
        
        movie = await get_movies_by_id([movie_id])
        m = movie[0]
 
        nouns_title:set = extract_nouns(m['title'].lower())
        nouns = nouns_title.union(extract_nouns(m['plot'].lower()))

        if new_value == False:
            await descore_terms(terms=nouns)
      
        else:
            await save_liked_movie_terms(nouns)
  
        await like_movie(id=movie_id, value=new_value)

    async def mark_seen(self):
        movie_id, new_value = self.handle_gui_data('seen')  
        await mark_seen(id=movie_id, value=new_value)

    async def mark_interested(self):
        movie_id, new_value = self.handle_gui_data('interested')
        if new_value == False:
            movie = await get_movies_by_id([movie_id])
            m = movie[0]
 
            nouns_title:set = extract_nouns(m['title'].lower())
            nouns = nouns_title.union(extract_nouns(m['plot'].lower()))
            await descore_terms(terms=nouns)

        await not_interested_movie(id=movie_id, value=new_value)


    def handle_gui_data(self, type):
        index = self.gui.screens['movie'].MovieBox.poster_idx
    
        movie_id = self.best_movies[index]['imdbId']
       
        value = self.best_movies[index][type] 
   
 
        self.best_movies[index][type] = not value
    
        return movie_id, not value

        
        









