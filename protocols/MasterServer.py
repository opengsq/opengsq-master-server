from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
import requests
from tqdm import tqdm

load_dotenv()

uri = os.getenv('DATABASE_URL')
client = MongoClient(uri)


class MasterServer(ABC):
    def __init__(self, key: str) -> None:
        self._key = key
        self.db = self.get_db()
        self.collection = self.db[key]

    @staticmethod
    def get_db():
        db = client['MasterServer']
        return db

    @property
    def key(self):
        return self._key

    @abstractmethod
    def create_index(self):
        pass

    @abstractmethod
    def job(self):
        pass

    @abstractmethod
    def find(self, *, host: str, port: int) -> dict:
        pass

    def run(self):
        # Record the start time
        start_time = time.time()

        # Run job
        self.job()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        print(f"[{self.key}] Job done. Time elapsed: {elapsed_time:.2f} seconds")

    def _fetch_url(self, url: str):
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()

        # Get the total content length (in bytes) from the response headers
        total_size = int(response.headers.get("content-length", 0))

        # Initialize an empty data buffer
        data = b''

        # Create a progress bar
        desc = f"[{self.key}] Fetching data from url"
        with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024, desc=desc) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    data += bytes(chunk)
                    pbar.update(len(chunk))

        # Convert bytes to string
        str_data = data.decode('utf-8')

        return str_data

    def _bulk_write(self, updates: list):
        # Check if there are any updates to perform
        if len(updates) == 0:
            print("No updates to perform.")
            return

        # Determine the number of workers for parallel processing
        # The number of workers is the minimum of 32 and the number of CPUs plus 4
        max_workers = min(32, os.cpu_count() + 4)

        # Calculate the chunk size for each worker
        # The chunk size is the ceiling of the division of the number of updates by the number of workers
        chunk_size = -(-len(updates) // max_workers)

        # Split the updates into chunks for each worker
        update_chunks = [updates[i:i + chunk_size]
                        for i in range(0, len(updates), chunk_size)]

        # Initialize a progress bar for tracking the progress of the bulk write
        pbar = tqdm(total=len(updates), desc=f"[{self.key}] Bulk Write")

        # Define a function for performing the bulk write for a chunk of updates
        def perform_bulk_write(i: int):
            # Perform the bulk write for the chunk
            self.collection.bulk_write(update_chunks[i], ordered=False)
            # Update the progress bar
            pbar.update(len(update_chunks[i]))

        # Create a ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map the function to perform the bulk write for each chunk of updates
            results = executor.map(perform_bulk_write, range(max_workers))

        # Return the results of the bulk write
        return results

    def _remove_old_documents(self, minutes: int):
        # Calculate the time 'minutes' ago
        time_ago = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        # Remove documents that haven't been updated for 'minutes'
        result = self.collection.delete_many(
            {'_last_modified': {'$lt': time_ago}})

        # Print the count of deleted documents
        print(f"[{self.key}] Deleted {result.deleted_count} servers that haven't been updated for {minutes} minutes.")

        return result
