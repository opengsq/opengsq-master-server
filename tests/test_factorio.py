import pytest

from protocols import MasterServer, Factorio


@pytest.fixture
def instance():
    return Factorio()


def test_job(instance: MasterServer):
    assert instance.job() is None


def test_find(instance: MasterServer):
    server = instance.collection.find_one()
    host, port = str(server['host_address']).split(':')
    result = instance.find(host=host, port=port)
    assert server['host_address'] == result['host_address']
