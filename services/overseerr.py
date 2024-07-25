import requests

class OverseerrManager:
    __address = ""
    __key = ""
    __session = None
    def __init__(self, address, key) -> None:
        self.__address = address
        self.__key = key
        self.__session = requests.Session()
        self.overseerr_login()
        pass

    def overseerr_login(self):
        login_payload = { 'X-Api-Key':self.__key }
        response = self.__session.get(f"{self.__address}/api/v1/status", data=login_payload)
        if response.status_code==200:
            print(f"Connected to Overseerr @ {self.__address}")
            self.__session.cookies.set(name="connect.sid", value=self.__key)
        else: print(f"Failed to connect to Overseer @ {self.__address}: {response.content.decode()}")

    def search(self, query):
        search_payload = {
            'query': self.sanitize(query),
            'page':1,
            'language':"en"
        }
        search_headers = {'X-Api-Key':self.__key}
        response = self.__session.get(f"{self.__address}/api/v1/search", params=search_payload, headers=search_headers)
        if response.status_code==200:
            results = response.json()
            queryResults = []
            for title in results['results']:
                name = ""
                date = ""
                type = ""
                if title['mediaType'] == "tv": 
                    name = title['name']
                    date = title['firstAirDate']
                    type = "Series"
                elif title['mediaType'] == "movie": 
                    name = title['originalTitle']
                    date = title['releaseDate']
                    type = "Movie"
                else: continue
                queryResults.append(SearchResult(name, date, title['overview'], title, type))
            return queryResults
        else:
            print(f"Failed to search for {query}: {response.content.decode()}")

    def request(self, title):
        titleData = title.rawData
        request_payload = {
            'mediaType': titleData['mediaType'],
            'mediaId': titleData['id']
        }
        if titleData['mediaType'] == 'tv': request_payload['seasons'] = 'all'
        request_headers = {'X-Api-Key':self.__key}
        response = self.__session.post(f"{self.__address}/api/v1/request", json=request_payload, headers=request_headers)
        if response.status_code==201:
            return True
        else:
            print(f"Failed to request {title._title}: {response.status_code}:{response.content.decode()}")
            return False


    def sanitize(self, query:str)->str:
        query = query.replace(" ", "-")
        reservedChars = ["!", "*", "'", "(", ")", ";", ":", "@", "&", "=", "+", "$", ",", "/", "?", "%", "#", "[", "]"]
        for char in reservedChars:
            query = query.replace(char, "")
        return query

class SearchResult:
    _title = ""
    _year = ""
    _description = ""
    rawData = None
    _type = ""
    def __init__(self, title, date, description, rawData, type) -> None:
        self._title = title
        self._year = str(date).split("-")[0]
        self._description = description
        self.rawData = rawData
        self._type = type
        pass