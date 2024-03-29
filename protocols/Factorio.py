import json
import os
from datetime import datetime, timezone
from pymongo import UpdateOne

from protocols.MasterServer import MasterServer


class Factorio(MasterServer):
    def __init__(self) -> None:
        super().__init__('Factorio')

    def create_index(self):
        self.collection.create_index('host_address')

    def job(self):
        # Fetch data until empty
        servers = self._fetch()

        # Perform bulk write (upsert) operation
        self._upsert_bulk_write(servers)

        # Remove old documents (assuming this method exists)
        self._remove_old_documents(minutes=30)

    def find(self, *, host: str, port: int):
        # Define the query to find documents with a specific address and port
        query = {'host_address': f'{host}:{port}'}

        # Specify the projection to exclude certain fields
        projection = {'_id': 0, '_created_at': 0, '_last_modified': 0}

        # Retrieve the result
        result = self.collection.find_one(query, projection)

        return result

    def _fetch(self) -> list:
        username = os.getenv("FACTORIO_USERNAME")
        token = os.getenv("FACTORIO_TOKEN")

        # Check if username or token is None or empty string
        if not username or not token:
            print("Warning: FACTORIO_USERNAME or FACTORIO_TOKEN is not set or empty.")
            return []

        url = f"https://multiplayer.factorio.com/get-games?username={username}&token={token}"
        data = self._fetch_url(url)

        # Convert string to JSON
        res = json.loads(data)

        if "message" in res:
            # Possible error messages
            # 1. User not found.        -> Invalid FACTORIO_USERNAME
            # 2. Token doesn't match.   -> Invalid FACTORIO_TOKEN
            raise LookupError(res["message"])

        return res

    def _upsert_bulk_write(self, server_list: list):
        # Prepare the updates
        updates = [
            UpdateOne(
                {'host_address': server['host_address']},
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


if __name__ == "__main__":
    factorio = Factorio()
    # factorio.job()
    server = factorio.find(host='176.93.252.86', port=24609)
    print(server)
