from utilities.db.async_calls import with_sqlite3
from datetime import datetime 


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
async def save_movies(cur, data, err_str='Err saving movies'):
    for m in data:
        title = m['Title']
        year = m['Year']
        imdbId = m['imdbId']
        poster = m['Poster']
    print(data)
        
     
