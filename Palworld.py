from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
from pymongo import UpdateOne
from tqdm import tqdm
import requests

from MasterServer import MasterServer


class Palworld(MasterServer):
    def __init__(self) -> None:
        super().__init__('Palworld')
        self.collection.create_index('server_id')
        self.collection.create_index({'address': 1, 'port': 1})

    def job(self):
        # Fetch data until empty
        servers = self._fetch_until_empty()

        # Perform bulk write (upsert) operation
        self._upsert_bulk_write(servers)

        # Remove old documents (assuming this method exists)
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
        response = requests.get(url, timeout=15)
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
        return self._bulk_write(updates)

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


if __name__ == "__main__":
    palword = Palworld()
    # palword.job()
    server = palword.find(host='104.192.227.52', port=8211)
    print(server)
