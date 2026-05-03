import asyncio
from controllers.movies.controller import MovieController


async def main():
    controller = MovieController()
    
    while True:
        await controller.is_fillup_due()
        if controller.fill_up_due:
             await controller.fill_up()
        await asyncio.sleep(24 * 60 * 60)


asyncio.run(main())