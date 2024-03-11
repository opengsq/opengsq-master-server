from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class MasterServer(ABC):
    def __init__(self, key: str) -> None:
        self._key = key
        uri = os.getenv('DATABASE_URL')
        self.client = MongoClient(uri)
        self.db = self.client['MasterServer']
        self.collection = self.db[key]

    @property
    def key(self):
        return self._key

    @abstractmethod
    def job(self):
        pass

    @abstractmethod
    def find(self, *, host: str, port: int):
        pass

    def run(self):
        # Record the start time
        start_time = time.time()
        print(f"Running job: {self.key}")

        # Run job
        self.job()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        print(f"Job done: {self.key}. Time elapsed: {elapsed_time:.2f} seconds")

    def _bulk_write(self, updates: list):
        # Chunk size for bulk write
        max_workers = min(32, os.cpu_count() + 4)
        chunk_size = -(-len(updates) // max_workers)

        # Split the updates into chunks
        update_chunks = [updates[i:i + chunk_size]
                         for i in range(0, len(updates), chunk_size)]

        pbar = tqdm(total=len(updates), desc="Bulk Write")

        def perform_bulk_write(i: int):
            self.collection.bulk_write(update_chunks[i], ordered=False)
            pbar.update(len(update_chunks[i]))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(perform_bulk_write, range(max_workers))

        return results

    def _remove_old_documents(self, minutes: int):
        # Calculate the time 'minutes' ago
        time_ago = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        # Remove documents that haven't been updated for 'minutes'
        result = self.collection.delete_many(
            {'_last_modified': {'$lt': time_ago}})

        # Print the count of deleted documents
        print(f"Deleted {result.deleted_count} documents that haven't been updated for {minutes} minutes.")

        return result
