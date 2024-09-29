import requests
import logging
from components.torrentListing import TorrentListing

class QBitManager:
    __username = ""
    __password = ""
    __cookie = None
    __address = ""
    __session = None

    def __init__(self, address, username, password) -> None:
        self.__address = address
        self.__username = username
        self.__password = password
        self.__session = requests.Session()
        self.qbit_login()
        pass

    def qbit_login(self):
        login_payload = {
            'username': self.__username,
            'password': self.__password
        }
        response = self.__session.post(f"{self.__address}/api/v2/auth/login", data=login_payload)
        if response.status_code==200: 
            #self.__cookie = {"SID":response.cookies["SID"]}
            logging.info(f"Connected to QBitTorrent @ {self.__address}")
            
        else: logging.warning(f"Failed to connect to QBitTorrent @ {self.__address}: {response.content.decode()}")
        return response

    def pause_all(self):
        try:
            self.qbit_login() #QBitTorrent seems to arbitrarily timeout issued tokens, so this is a bruteforce solution - validate every time a command is sent
            pause_payload = {'hashes':'all'}
            response = self.__session.post(f"{self.__address}/api/v2/torrents/pause", data=pause_payload)
            if response.status_code != 200: 
                logging.warning(f"Failed to pause torrents: {response.content.decode()}")
                return False
            else: return True
        except Exception as e:
            logging.error(f"Exception while pausing all torrents: {e}")

    def resume_all(self):
        try:
            self.qbit_login() #QBitTorrent seems to arbitrarily timeout issued tokens, so this is a bruteforce solution - validate every time
            resume_payload = {'hashes':'all'}
            response = self.__session.post(f"{self.__address}/api/v2/torrents/resume", data=resume_payload)
            if response.status_code != 200: 
                logging.warning(f"Failed to resume torrents: {response.content}")
                return False
            else: return True
        except Exception as e:
            logging.error(f"Exception while resuming all torrents: {e}")

    def info(self) -> list[TorrentListing]:
        try:
            self.qbit_login()
            info_payload = {'filter':'downloading'}
            response = self.__session.post(f"{self.__address}/api/v2/torrents/info", data=info_payload)
            if response.status_code!=200:
                logging.warning(f"Failed to get torrent info: {response.content}")
            else:
                returnList = []
                responseJson = response.json()
                if(len(responseJson))>0:
                    for torrent in responseJson:
                        returnList.append(TorrentListing(torrent['name'], torrent['progress'], torrent['state'], torrent['num_seeds']))
                return returnList
                
        except Exception as e:
            logging.error(f"Exception while getting torrent info: {e}")

