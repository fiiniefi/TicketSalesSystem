import pytest
from mock import Mock


@pytest.fixture(scope='session')
def db_connection_base():
    return Mock(connection=Mock(), cursor=Mock())


@pytest.fixture(scope='session')
def db_connection_commit(db_connection_base):
    db_connection_base.commit = Mock()
    return db_connection_base
