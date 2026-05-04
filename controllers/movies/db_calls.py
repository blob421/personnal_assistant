from utilities.db.async_calls import with_sqlite3
from datetime import datetime 
import json

@with_sqlite3
async def get_movies(cur, err_str='Error fetching movies from db'):
    await cur.execute("""SELECT * FROM movies""")


@with_sqlite3
async def movie_fillup_due(cur , err_str ='Error fetching last movie event'):
    await cur.execute("""SELECT COUNT(*) FROM movies WHERE seen=?""", [False])
    result = await cur.fetchone()
    count = result[0] if result else 0

    if count < 100:
        return True
    else:
        return False
@with_sqlite3
async def get_movies_count(cur, err_str='Error getting count movies'):
    await cur.execute("""SELECT COUNT(*) FROM movies""") 
    results = await cur.fetchone()
    count = results[0] if results else 0
    return count 

@with_sqlite3
async def save_imdb_id(cur, id, err_str='Error saving imdb ids'):
    await cur.execute("""INSERT OR IGNORE INTO movies (imdbId) VALUES(?)""", [id])

    return cur.rowcount == 1

@with_sqlite3
async def save_movie(cur, movie:dict, err_str='Err saving movies'):
  
    imdbId= movie['imdbID'] or None
    title = movie["Title"] or None
    year = movie["Year"] or None
    plot = movie['Plot'] or None
    genres = movie['Genre'] or None
    poster = movie['Poster'] or None

    await cur.execute("""UPDATE movies SET title=?, year=?, genres=?, poster=?, plot=? 
                         WHERE imdbId=?""",
                                            [title, year, genres, poster, plot, imdbId])

        
   
        
     
