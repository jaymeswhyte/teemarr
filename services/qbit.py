import requests

def qbit_login(address, username, password):
    login_payload = {
        'username': username,
        'password': password
    }
    response = requests.post(f"{address}/api/v2/auth/login", data=login_payload)
    if response.status_code==200: print("Connected to QBitTorrent")
    else: print("Failed to connect to QBitTorrent: "+response.content)
    return response