from datetime import datetime, timezone
import socket
import struct
from pymongo import UpdateOne
from tqdm import tqdm

from protocols.MasterServer import MasterServer


class Scum(MasterServer):
    # Unknown index = |           index:    0 4    5   6 7 8 | 10 | 12
    __SERVER_INFO_STRUCT = struct.Struct("<4B H 100s x B B B B B 7s 8B")

    def __init__(self) -> None:
        super().__init__('Scum')

    def create_index(self):
        self.collection.create_index({'ip': 1, 'port': 1})

    def job(self):
        # Fetch data until empty
        servers = self._fetch()

        # Perform bulk write (upsert) operation
        self._upsert_bulk_write(servers)

        # Remove old documents (assuming this method exists)
        self._remove_old_documents(minutes=30)

    def find(self, *, host: str, port: int):
        # Define the query to find documents with a specific address and port
        query = {'ip': host, 'port': port}

        # Specify the projection to exclude certain fields
        projection = {'_id': 0, '_created_at': 0, '_last_modified': 0}

        # Retrieve the result
        result = self.collection.find_one(query, projection)

        return result

    def _fetch(self):
        __addresses = [
            ("176.57.138.2", 1040),
            ("172.107.16.215", 1040),
            ("206.189.248.133", 1040),
        ]
        size = self.__SERVER_INFO_STRUCT.size  # 127 bytes for each server

        for address in __addresses:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect(address)
                except Exception as e:
                    print(f"Failed to connect to {address}: {e}")
                    continue

                client_socket.sendall(b"\x04\x03\x00\x00")

                total: int = struct.unpack('<H', client_socket.recv(2))[0]
                total_bytes = total * size

                data = b''

                with tqdm(total=total_bytes, unit='B', unit_scale=True, desc=f'[{self.key}] Receiving data') as pbar:
                    while len(data) < total_bytes:
                        data += client_socket.recv(size)
                        pbar.update(size)

                servers = [self._parse_server(
                    data[(i * size):((i+1) * size)]) for i in range(total)]

                return servers

        raise Exception("All master server addresses are unreachable")

    def _parse_server(self, data: bytes):
        result = self.__SERVER_INFO_STRUCT.unpack(data)

        server = {}
        server['ip'] = '.'.join(map(str, reversed(result[0:4])))
        server['port'] = result[4]
        server['name'] = bytes(result[5]).rstrip(b'\0').decode(errors='ignore')
        server['num_players'] = result[6]
        server['max_players'] = result[7]
        server['time'] = f'{str(result[8]).zfill(2)}:00'
        server['password'] = ((result[10] >> 1) & 1) == 1

        # Convert the result to hexadecimal and pad with zeros
        hex_values = [hex(result[12 + i])[2:].rjust(2, '0') for i in range(8)]

        # Reverse the list
        reversed_hex_values = list(reversed(hex_values))

        # Extract version components
        major = int(reversed_hex_values[0], 16)
        minor = int(reversed_hex_values[1], 16)
        patch = int(reversed_hex_values[2] + reversed_hex_values[3], 16)
        build = int(''.join(reversed_hex_values[4:]), 16)

        # Format the version string
        server['version'] = f"{major}.{minor}.{patch}.{build}"

        return server

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
    scum = Scum()
    # scum.job()
    server = scum.find(host='15.235.181.18', port=7042)
    print(server)
