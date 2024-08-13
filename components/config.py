import os
import json

class Config:
    _version = "0.0.0"
    _overnightDownloads = True
    def __init__(self, path:str) -> None:
        if os.path.exists(f"{path}/config.txt"): 
            with open(f"{path}/config.txt", 'r') as textFile:
                jsonRead = json.loads(textFile.read())
                textFile.close()
            self._version = jsonRead.get("version", self._version)
            self._overnightDownloads = jsonRead.get("overnight_downloads", self._overnightDownloads)  
        else: self.write_to_file(path)
        pass

    def write_to_file(self, path:str):
        selfDict = {"version":self._version, "overnight_downloads":self._overnightDownloads}
        selfJson = json.dumps(selfDict)
        with open(f"{path}/config.txt", 'w+') as textFile:
            textFile.write(selfJson)
            textFile.close()

    def is_older_than(self, version:str):
        myVersionList = self._version.split('.')
        givenVersionList = version.split('.')
        for i in range(len(myVersionList)):
            if int(givenVersionList[i]) > int(myVersionList[i]): return True
            elif int(givenVersionList[i]) < int(myVersionList[i]): return False
        return False

    @property
    def version(self):
        return self._version
    @version.setter
    def version(self, newVersion):
        self._version = newVersion

    @property
    def overnightDownloads(self):
        return self._overnightDownloads
    @overnightDownloads.setter
    def overnightDownloads(self, newVal):
        self._overnightDownloads = newVal