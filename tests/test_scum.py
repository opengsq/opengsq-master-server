import pytest

from protocols import MasterServer, Scum


@pytest.fixture
def instance():
    return Scum()


def test_job(instance: MasterServer):
    assert instance.job() is None


def test_find(instance: MasterServer):
    server = instance.collection.find_one()
    host, port = server['ip'], server['port']
    result = instance.find(host=host, port=port)
    assert result['ip'] == host and result['port'] == port
