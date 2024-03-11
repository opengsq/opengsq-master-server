import os
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timedelta, timezone
from pymongo import UpdateOne
from tqdm import tqdm
import requests

from MasterServer import MasterServer


class Palworld(MasterServer):
    def __init__(self) -> None:
        super().__init__()
        self._key = 'Palworld'
        self.db = self.client['MasterServer']
        self.collection = self.db['PalWorld']
        self.collection.create_index('server_id')
        self.collection.create_index({'address': 1, 'port': 1})

    def job(self):
        servers = self._fetch_until_empty()
        self._upsert_bulk_write(servers)
        self._remove_old_documents(minutes=30)

    def find(self, *, host: str, port: int):
        # Define the query to find documents with a specific address and port
        query = {'address': host, 'port': port}

        # Specify the projection to exclude certain fields
        projection = {'_id': 0, '_created_at': 0, '_last_modified': 0}

        # Retrieve the result
        result = self.collection.find_one(query, projection)

        return result

    def _fetch_page(self, page: int) -> list:
        url = f"https://api.palworldgame.com/server/list?page={page}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['server_list']

    def _upsert_bulk_write(self, server_list: list):
        # Prepare the updates
        updates = [
            UpdateOne(
                {'server_id': server['server_id']},
                {
                    '$set': server,
                    '$currentDate': {'_last_modified': True},
                    '$setOnInsert': {'_created_at': datetime.now(timezone.utc)}
                },
                upsert=True
            )
            for server in server_list
        ]

        # Chunk size for bulk write
        max_workers = min(32, os.cpu_count() + 4)
        chunk_size = -(-len(updates) // max_workers)

        # Split the updates into chunks
        update_chunks = [updates[i:i + chunk_size]
                         for i in range(0, len(updates), chunk_size)]

        def perform_bulk_write(i: int):
            self.collection.bulk_write(update_chunks[i], ordered=False)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(tqdm(executor.map(perform_bulk_write, range(
                max_workers)), total=len(update_chunks), desc="Bulk Write"))

        return results

    def _fetch_until_empty(self):
        servers = []
        stop = False
        pbar = tqdm(total=0)

        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(self._fetch_page, pbar.total + 1)}

            while futures:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)

                for future in done:
                    server_list = future.result()

                    if server_list:
                        servers.extend(server_list)
                        pbar.update(1)
                    else:
                        stop = True

                    if not stop:
                        pbar.set_description(f'Page {pbar.total + 1}')
                        pbar.total += 1
                        pbar.refresh()
                        futures.add(executor.submit(
                            self._fetch_page, pbar.total + 1))

        return servers

    def _remove_old_documents(self, minutes: int):
        # Calculate the time 'minutes' ago
        time_ago = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        # Remove documents that haven't been updated for 'minutes'
        result = self.collection.delete_many(
            {'_last_modified': {'$lt': time_ago}})

        return result


if __name__ == "__main__":
    palword = Palworld()
    palword.run()
    server = palword.find(host='104.192.227.52', port=8211)
    print(server)
