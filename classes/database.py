import os
from typing import ClassVar
from pymongo import MongoClient
from dotenv import get_key
from constants import ENV_PATH


class CollectionProvider:
    @staticmethod
    def get_database_name():
        if os.environ.get("TESTING"):
            return "test_curierat"
        return "curierat"

    _client: ClassVar[MongoClient] = MongoClient(get_key(ENV_PATH, "MONGO_URL"))
    
    @classmethod
    def _database(cls):
        return cls._client[cls.get_database_name()]

    @classmethod
    def users(cls):
        return cls._database()["users"]

    @classmethod
    def tickets(cls):
        return cls._database()["tickets"]

    @classmethod
    def packages(cls):
        return cls._database()["packages"]

    @classmethod
    def transports(cls):
        return cls._database()["transports"]

    @classmethod
    def routes(cls):
        return cls._database()["routes"]

    @classmethod
    def cities(cls):
        return cls._database()["cities"]
