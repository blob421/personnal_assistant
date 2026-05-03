
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
    
    await cur.execute("""CREATE TABLE IF NOT EXISTS movies(id BIGINT,
                                                            title VARCHAR(60),
                                                            year VARCHAR(10),
                                                            imdbId VARCHAR(20),
                                                            poster TEXT,
                                                            synopsis TEXT,
                                                            genre VARCHAR(60),
                                                            image BLOB,
                                                            seen BOOLEAN,
                                                            liked BOOLEAN

                      )""")
    
    await cur.execute("""CREATE INDEX IF NOT EXISTS movie_seen_idx on movies(seen)""")

    await cur.execute("""SELECT * FROM options""")

    options = await cur.fetchall()

    if not options or len(options) < 1:
        for k, v in default_options.items():
            boo = None if type(v) == str else v
            value = None if type(v) == bool else v
            await cur.execute("""INSERT INTO options (name, bool, value) VALUES (?,?,?)""", 
                            [k, boo, value])