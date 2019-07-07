from mock import Mock
import pytest
# noinspection PyUnresolvedReferences
from tests.unit.connections import db_connection_base
from sales_system.events import EventManager
import sales_system.events


@pytest.fixture(scope='module')
def event_manager():
    return EventManager(Mock())


def test_GetEvents_PassedCorrectly(db_connection_base, event_manager, monkeypatch):
    monkeypatch.setattr(sales_system.events, 'datetime', Mock())

    event_manager.get_events(db_connection_base)

    db_connection_base.cursor.execute.assert_called_once()
    db_connection_base.cursor.fetchall.assert_called_once_with()
