import pytest

from protocols import MasterServer, Palworld


@pytest.fixture
def instance():
    return Palworld()


def test_job(instance: MasterServer):
    assert instance.job() is None


def test_find(instance: MasterServer):
    server = instance.collection.find_one()
    host, port = server['address'], server['port']
    result = instance.find(host=host, port=port)
    assert result['address'] == host and result['port'] == port
