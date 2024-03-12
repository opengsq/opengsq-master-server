from datetime import datetime, timezone
from pymongo import UpdateOne

from protocols.MasterServer import MasterServer


class BeamMP(MasterServer):
    def __init__(self) -> None:
        super().__init__('BeamMP')
        self.collection.create_index({'ip': 1, 'port': 1})

    def job(self):
        # Fetch data until empty
        servers = self._fetch_url('https://backend.beammp.com/servers-info')

        # Perform bulk write (upsert) operation
        self._upsert_bulk_write(servers)

        # Remove old documents (assuming this method exists)
        self._remove_old_documents(minutes=30)

    def find(self, *, host: str, port: int):
        # Define the query to find documents with a specific address and port
        query = {'ip': host, 'port': str(port)}

        # Specify the projection to exclude certain fields
        projection = {'_id': 0, '_created_at': 0, '_last_modified': 0}

        # Retrieve the result
        result = self.collection.find_one(query, projection)

        return result

    def _upsert_bulk_write(self, server_list: list):
        # Prepare the updates
        updates = [
            UpdateOne(
                {'ip': server['ip'], 'port': server['port']},
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
    beamMP = BeamMP()
    # beamMP.job()
    server = beamMP.find(host='91.233.187.44', port=30815)
    print(server)
