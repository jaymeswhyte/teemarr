import requests

class QBitManager:
    __username = ""
    __password = ""
    __cookie = ""
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
            print("Connected to QBitTorrent")
        else: print("Failed to connect to QBitTorrent: "+response.content.decode())
        return response

    def pause_all(self):
        pause_payload = {'hashes':'all'}
        response = self.__session.post(f"{self.__address}/api/v2/torrents/pause", data=pause_payload)
        if response.status_code != 200: 
            print(f"Failed to pause torrents: {response.content.decode()}")
            return False
        else: return True

    def resume_all(self):
        resume_payload = {'hashes':'all'}
        response = self.__session.post(f"{self.__address}/api/v2/torrents/resume", data=resume_payload)
        if response.status_code != 200: 
            print(f"Failed to resume torrents: {response.content}")
            return False
        else: return True