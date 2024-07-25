import os

class Config:
    _version = "0.0.0"
    def __init__(self, path:str) -> None:
        if os.path.exists(f"{path}/config.txt"): 
            with open(f"{path}/config.txt", 'r') as textFile:
                version = textFile.readline()
                self._version = version
                textFile.close()
        else: self.write_to_file(path)
        pass

    def write_to_file(self, path:str):
        with open(f"{path}/config.txt", 'w+') as textFile:
            textFile.write(self._version)
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