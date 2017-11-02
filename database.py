from pymongo import MongoClient


class Database(object):
    """
    Return database connection to avoid creating multiple instances
    """
    __db = None

    @classmethod
    def getConn(cls):
        if cls.__db is None:
            client = MongoClient()
            cls.__db = client.crawler.crawler

        return cls.__db
