import asyncio
from controllers.movies.controller import MovieController
from controllers.movies.db_calls import save_movie
from utilities.db.init_tables import init_db




async def fetch_movies(controller:MovieController):
    await controller.create_client()

    generator = await controller.make_imdbId_generator(pages=1, 
                                                       genres=['horror', 'crime', 'sci-fi'])
    async for movie in generator:
         await save_movie(movie)

    await controller.terminate_client()


async def main():
    await init_db()

    controller = MovieController()
    await fetch_movies(controller)
  

asyncio.run(main())