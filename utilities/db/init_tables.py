
from .async_calls import with_sqlite3
from config import default_options

@with_sqlite3
async def init_db(cur, err_str='Error creating tables during init'):
    await cur.execute("""CREATE TABLE IF NOT EXISTS search_terms(date TEXT, 
                                                            term TEXT UNIQUE
                            
        )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS emails(id BIGINT UNIQUE, date TEXT, subject TEXT, tags TEXT, sender TEXT)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS emails_id_idx on emails(id)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS emails_tags_idx on emails(tags)""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS term_idx on search_terms(term)""")


    await cur.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                        date TEXT,
                                                        type VARCHAR(60),
                                                        message TEXT,
                                                        count INTEGER
                                                        )""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS event_type_idx on events(type)""")

    await cur.execute("""CREATE INDEX IF NOT EXISTS event_id_idx on events(id)""")

    await cur.execute("""CREATE TABLE IF NOT EXISTS missed_prompts (date TEXT,
                                                              message TEXT,
                                                              type TEXT
                )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS options(name VARCHAR(30), 
                                                            bool BOOLEAN , 
                                                            value VARCHAR(255)
                )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS contacts(alias VARCHAR(30), 
                                                             email VARCHAR(50) UNIQUE,
                                                             active BOOLEAN
                                                             )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS movies(id INTEGER PRIMARY KEY,
                                                            title VARCHAR(60),
                                                            year VARCHAR(10),
                                                            imdbId VARCHAR(20) UNIQUE,
                                                            poster TEXT,
                                                            plot TEXT,
                                                            genres VARCHAR(60),
                                                            seen BOOLEAN DEFAULT false,
                                                            liked BOOLEAN DEFAULT false,
                                                            interested BOOLEAN DEFAULT true

                      )""")
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS movie_genres_score(id INTEGER PRIMARY KEY,
                                                                       name VARCHAR(20) UNIQUE,
                                                                       score INTEGER DEFAULT 0)""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS movie_seen_idx on movies(seen)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS movie_imdbId_idx on movies(imdbId)""")
    await cur.execute("""CREATE INDEX IF NOT EXISTS movie_interest_idx on movies(interested)""")

    await cur.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS movie_terms USING fts5(term, 
                                                                     score, 
                                                                     tokenize = 'trigram')""")

    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()

    if not options or len(options) < 1:
        for k, v in default_options.items():
            boo = None if type(v) == str else v
            value = None if type(v) == bool else v
            await cur.execute("""INSERT INTO options (name, bool, value) VALUES (?,?,?)""", 
                            [k, boo, value])