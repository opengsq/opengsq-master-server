import pytest

from protocols import MasterServer, TheFront


@pytest.fixture
def instance():
    return TheFront()


def test_job(instance: MasterServer):
    assert instance.job() is None


def test_find(instance: MasterServer):
    server = instance.collection.find_one()
    host, port = server['addr'], server['port']
    result = instance.find(host=host, port=port)
    assert result['addr'] == host and result['port'] == port
