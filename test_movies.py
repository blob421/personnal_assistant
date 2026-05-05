import asyncio
from controllers.movies.movie_controller import Movie_Controller
from utilities.db.init_tables import init_db
from controllers.movies.db_calls import save_liked_movie_terms



async def main():
    await init_db()
    controller = Movie_Controller()
    await controller.init_best_movies()
    print(controller.best_movies)
   # await controller.like_movie('tt31728330')

asyncio.run(main())