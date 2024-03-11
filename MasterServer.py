from abc import ABC, abstractmethod
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MasterServer(ABC):
    def __init__(self) -> None:
        self._key = ''
        uri = os.getenv('DATABASE_URL')
        self.client = MongoClient(uri)

    @property
    def key(self):
        return self._key

    @abstractmethod
    def job(self):
        pass

    @abstractmethod
    def find(self, *, host: str, port: int):
        pass
