from utilities.db.async_calls import with_sqlite3



    
@with_sqlite3
async def get_unseen_movies(cur, err_str='Error fetching movies from db'):
    await cur.execute("""SELECT * FROM movies WHERE seen=? AND interested=? LIMIT 80""", 
                                                                           [False, True])
    
    results = await cur.fetchall()
    return {r[3] : {'title': r[1], 'plot': r[5]} for r in results}


@with_sqlite3
async def get_movies_by_id(cur, ids, err_str='Error fetching movies by id'):
    movies = []
    print(ids)
    for i in ids:
     
        await cur.execute("""SELECT * FROM movies WHERE imdbId=?""", [i])
        r = await cur.fetchone()
        movies.append({'title': r[1], 'year': r[2], 'imdbId': r[3], 'poster': r[4], 'plot': r[5] })
    if movies:
        return movies


@with_sqlite3
async def get_liked_terms(cur, err_str='Error getting liked terms movies'):
    await cur.execute("""SELECT * FROM movie_terms""")
    results = await cur.fetchall()

    return [{'term': r[0], 'score': r[1]} for r in results]


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

        
@with_sqlite3
async def save_liked_movie_terms(cur, terms, err_str='Error saving plot terms for liked movie'):
    for t in terms:
        term = t[:6]

        await cur.execute("""UPDATE movie_terms SET score = score + 1 WHERE term MATCH ?""", [term + '*'])
        exists = cur.rowcount == 1
     
        if not exists:
      
            await cur.execute("""INSERT OR IGNORE INTO movie_terms VALUES (?,?)""", [t, 1])
       


        
     
