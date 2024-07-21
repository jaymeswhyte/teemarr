import requests

class QBitManager:
    __username = ""
    __password = ""
    __cookie = ""
    __address = ""

    def __init__(self, address, username, password) -> None:
        self.__address = address
        self.__username = username
        self.__password = password
        self.qbit_login()
        pass

    def qbit_login(self):
        login_payload = {
            'username': self.__username,
            'password': self.__password
        }
        response = requests.post(f"{self.__address}/api/v2/auth/login", data=login_payload)
        if response.status_code==200: print("Connected to QBitTorrent")
        else: print("Failed to connect to QBitTorrent: "+response.content)
        return response

    def pause_all(self):
        pass

    def resume_all(self):
        pass