from utilities.db.async_calls import with_sqlite3
import json



@with_sqlite3
async def not_interested_movie(cur, id , value, err_str='Error marking movie as not interested'):
   await cur.execute("""UPDATE movies SET interested=? WHERE imdbId=?""", [value, id])

@with_sqlite3
async def match_movie_term(cur, word, err_str='Error while matching movie term word'):
    
    await cur.execute("""SELECT * FROM movie_terms WHERE term MATCH ?""", [word + '*'])
    result = await cur.fetchone()
    if result:
        print(word)
        print(result)
        return result 
    
    return None

@with_sqlite3
async def mark_seen(cur, id, value, err_str='Error marking the movie as seen'):
    await cur.execute("""UPDATE movies SET seen=? WHERE imdbId=?""", [value, id])  

@with_sqlite3
async def like_movie(cur, id, value, err_str='Error marking the movie as seen'):
    print('called')
    print(id)
    print(value)
    await cur.execute("""UPDATE movies SET liked=? WHERE imdbId=?""", [value, id])  



@with_sqlite3
async def get_unseen_movies(cur, err_str='Error fetching movies from db'):
   
  
    await cur.execute("""SELECT * FROM events WHERE type='Movie update' ORDER BY id DESC LIMIT 5""")
    results = await cur.fetchall()
    
    exclusions = ''
    if results:
        for idx, result in enumerate(results):
            if idx != 0:
               exclusions += ','
            exclusions += ",".join(map(lambda r: f"'{r}'",json.loads(result[3])))
            

    exclusions_str = f" AND imdbId NOT IN ({exclusions})" if results else ''
  
    print(exclusions)



    await cur.execute(f"""SELECT * FROM movies WHERE seen=? AND interested=? 
                                                            AND poster != 'N/A' 
                                                            AND poster IS NOT NULL{exclusions_str} LIMIT 80""", 
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
        movies.append({'title': r[1], 'year': r[2], 'imdbId': r[3], 'poster': r[4], 
                       'plot': r[5] , 'seen': r[7], 'liked': r[8], 'interested': r[9]})
    if movies:
        return movies
    


@with_sqlite3
async def movie_fillup_due(cur , err_str ='Error fetching last movie event'):
    await cur.execute("""SELECT COUNT(*) FROM movies WHERE seen=? AND interested=?""", [False, True])
    result = await cur.fetchone()
    count = result[0] if result else 0

    if count < 100:
        return True
    else:
        return False
    

@with_sqlite3
async def save_imdb_id(cur, id, err_str='Error saving imdb ids'):
    await cur.execute("""INSERT OR IGNORE INTO movies (imdbId) VALUES(?)""", [id])
    if cur.rowcount == 1:
        return 1
    
    return 0


@with_sqlite3
async def save_movie(cur, movie:dict, err_str='Err saving movies'):
  
    imdbId= movie.get('imdbID', None) 
    title = movie.get('Title', None)
    year = movie.get("Year", None)
    plot = movie.get("Plot", None)
    genres = movie.get("Genre", None)
    poster = movie.get("Poster", None)
    
    if not title or not imdbId or not plot or not poster:
        return

    await cur.execute("""UPDATE movies SET title=?, year=?, genres=?, poster=?, plot=? 
                         WHERE imdbId=?""",
                                            [title, year, genres, poster, plot, imdbId])

@with_sqlite3
async def descore_terms(cur, terms, err_str="Error descoring movie terms"):
    for t in terms:
        term = t[:6]

        await cur.execute("""UPDATE movie_terms SET score = score - 1 WHERE term MATCH ?""", [term + '*'])
        exists = cur.rowcount == 1
     
        if not exists:
      
           await cur.execute("""INSERT OR IGNORE INTO movie_terms VALUES (?,?)""", [t, -1])

@with_sqlite3
async def save_liked_movie_terms(cur, terms, err_str='Error saving plot terms for liked movie'):
    for t in terms:
        term = t[:6]

        await cur.execute("""UPDATE movie_terms SET score = score + 1 WHERE term MATCH ?""", [term + '*'])
        exists = cur.rowcount == 1
     
        if not exists:
      
           await cur.execute("""INSERT OR IGNORE INTO movie_terms VALUES (?,?)""", [t, 1])
       


        
     
