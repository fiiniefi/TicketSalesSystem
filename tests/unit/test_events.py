# noinspection PyUnresolvedReferences
from tests.unit.connections import db_connection
from sales_system.events import EventManager
import sales_system.events
from mock import Mock


def test_GetEvents_PassedCorrectly(db_connection, monkeypatch):
    monkeypatch.setattr(sales_system.events, 'datetime', Mock())
    EventManager(Mock()).get_events(db_connection)
    db_connection.cursor.execute.assert_called_once()
    db_connection.cursor.fetchall.assert_called_once_with()
