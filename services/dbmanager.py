from tinydb import TinyDB, Query
import logging

class DBManager:
    __path = ""
    __db = None
    __table = None
    def __init__(self, path):
        self.__path = path
        try:
            self.__db = TinyDB(f"{path}/db.json")
            self.__table = self.__db.table("requests")
        except Exception as e:
            logging.error(f"Couldn't initialize database: {e}")

    def insertRequest(self, id, user, datetime):
        self.__table.insert({'id':id, 'user':user, 'datetime':datetime})

    def getRequest(self, id):
        Request = Query()
        result = self.__table.search(Request.id == id)
        return result
    
    def updateRequest(self, id, newvals:dict):
        Request = Query()
        self.__table.update(newvals, Request.id == id)

    def removeRequest(self, id):
        Request = Query()
        self.__table.remove(Request.id == id)