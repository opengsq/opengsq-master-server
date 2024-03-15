import pytest

from protocols import MasterServer, Front


@pytest.fixture
def instance():
    return Front()


def test_job(instance: MasterServer):
    assert instance.job() is None


def test_find(instance: MasterServer):
    server = instance.collection.find_one()
    host, port = server['addr'], server['port']
    result = instance.find(host=host, port=port)
    assert result['addr'] == host and result['port'] == port
