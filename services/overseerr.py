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
        else: print(f"Failed to connect to Overseer @ {self.__address}: {response.content.decode()}")
        