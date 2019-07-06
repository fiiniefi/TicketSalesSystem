import pytest
from mock import Mock


@pytest.fixture(scope='session')
def db_connection():
    return Mock(connection=Mock(), cursor=Mock())
