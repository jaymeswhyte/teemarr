import requests

def get_release_notes(version:str):
    tag = f"v{version}"
    url = f"https://api.github.com/repos/jaymeswhyte/teemarr/releases/tags/{tag}"

    response = requests.get(url)
    
    if response.status_code == 200:
        jsonResponse = response.json()
        return jsonResponse['body']
    else:
        print(f"Failed to fetch release: {response.status_code}")
        return "Could not get notes for this release."