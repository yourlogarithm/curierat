import os
from typing import ClassVar
from pymongo import MongoClient
from dotenv import get_key


class CollectionProvider:
    @staticmethod
    def get_database_name():
        if "PYTEST_CURRENT_TEST" in os.environ:
            return "test_curierat"
        return "curierat"

    _client: ClassVar[MongoClient] = MongoClient(get_key(".env", "MONGO_URL"))
    
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
