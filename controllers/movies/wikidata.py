async def fetch_wikidata(self, imdb_id):
     
        query = f"""
        SELECT ?imdb ?item ?itemLabel ?year ?genreLabel ?image WHERE {{
        VALUES ?imdb {{ {f'"{imdb_id}"'} }}

        ?item wdt:P345 ?imdb .

        OPTIONAL {{ ?item wdt:P577 ?date .
                    BIND(YEAR(?date) AS ?year) }}

        OPTIONAL {{ ?item wdt:P136 ?genre . }}
        OPTIONAL {{ ?item wdt:P18 ?image . }}

        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        """

        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/sparql-results+json", 
                   "User-Agent": "PersonalAssistantBot/1.0 (https://example.com)"}

       
        async with self.session.get(url, params={"query": query}, headers=headers) as r:
            return await r.json()
        

async def get_movie_data(self, id_gen):
            for id in id_gen:
                data = await self.fetch_wikidata(id)
                movie = {}

                row =  data["results"]["bindings"]
                
                movie = {
                        'imdbId': row["imdb"]["value"],
                        "title": row["itemLabel"]["value"],
                        "year": int(row["year"]["value"]) if "year" in row else None,
                        "genres": set(),
                        "image": row["image"]["value"] if "image" in row else None
                    }

                if "genreLabel" in row:
                    movie["genres"].add(row["genreLabel"]["value"].split(' ')[0])

                # Convert genre sets to lists
            
                movie["genres"] = list(movie["genres"])

                yield movie