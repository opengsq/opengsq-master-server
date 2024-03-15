import json
from datetime import datetime, timezone
from pymongo import UpdateOne

from protocols.MasterServer import MasterServer


class Front(MasterServer):
    def __init__(self) -> None:
        super().__init__('Front')

    def create_index(self):
        self.collection.create_index({'addr': 1, 'port': 1})

    def job(self):
        # Fetch data until empty
        servers = self._fetch()

        # Perform bulk write (upsert) operation
        self._upsert_bulk_write(servers)

        # Remove old documents (assuming this method exists)
        self._remove_old_documents(minutes=30)

    def find(self, *, host: str, port: int):
        # Define the query to find documents with a specific address and port
        query = {'addr': host, 'port': port}

        # Specify the projection to exclude certain fields
        projection = {'_id': 0, '_created_at': 0, '_last_modified': 0}

        # Retrieve the result
        result = self.collection.find_one(query, projection)

        return result

    def _fetch(self) -> list:
        url = f'https://privatelist.playthefront.com/private_list'
        data = self._fetch_url(url)

        # Convert string to JSON
        res = json.loads(data)

        if res['msg'] != 'ok':
            raise LookupError(res['msg'])

        server_list = list(res['server_list'])

        for item in server_list:
            if isinstance(item['info'], str):
                try:
                    item['info'] = json.loads(item['info'])
                except json.JSONDecodeError:
                    print("Error: item['info'] is not valid JSON")
            else:
                print("Warning: item['info'] is not a string")

        return server_list

    def _upsert_bulk_write(self, server_list: list):
        # Prepare the updates
        updates = [
            UpdateOne(
                {'addr': server['addr'], 'port': server['port']},
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
    front = Front()
    # front.job()
    server = front.find(host='45.137.244.52', port=28100)
    print(server)
