import pytest
from datetime import datetime
from time import sleep
from sales_system.interface import TicketSystem
from sales_system.connection import DBConnection
from sales_system.metadata.settings import DB_NAME, DB_USERNAME, DB_PASSWORD


@pytest.fixture(scope='session')
def db_connection():
    return DBConnection(DB_NAME, DB_USERNAME, DB_PASSWORD)


@pytest.fixture(scope='session')
def ticket_system(db_connection):
    return TicketSystem(db_connection)


@pytest.fixture(scope='function')
def new_event(db_connection):
    date_and_time = datetime.fromtimestamp(1557475701)
    db_connection.cursor.execute("SELECT max(id) FROM event;")
    max_id = db_connection.cursor.fetchone()[0]
    db_connection.cursor.execute(f"INSERT INTO event VALUES({max_id+1}, 'test_event', '{date_and_time}');")
    yield max_id
    db_connection.cursor.execute(f"DELETE FROM event WHERE id={max_id+1};")


@pytest.fixture(scope='function')
def new_ticket(db_connection, new_event):
    db_connection.cursor.execute("SELECT max(id) FROM ticket;")
    max_id = db_connection.cursor.fetchone()[0]
    db_connection.cursor.execute(f"INSERT INTO ticket VALUES({max_id+1}, 'VIP', 60.0, {new_event}, 'available');")
    yield max_id
    db_connection.cursor.execute(f"DELETE FROM ticket WHERE id={max_id+1};")


def test_BuyTicket(db_connection, ticket_system, new_event):
    db_connection.cursor.execute("SELECT max(id) FROM ticket;")
    max_id = db_connection.cursor.fetchone()[0]
    db_connection.cursor.execute(f"INSERT INTO ticket VALUES({max_id+1}, 'VIP', 60.0, {new_event}, 'available');")
    ticket_system.buy_ticket(max_id+1)
    db_connection.cursor.execute("SELECT max(id) FROM ticket;")
    try:
        assert max_id == db_connection.cursor.fetchone()[0]
    except AssertionError as err:
        db_connection.cursor.execute(f"DELETE FROM ticket WHERE id={max_id+1}")
        raise err


def test_ReserveTicket(db_connection, ticket_system, new_ticket):
    calculation_time = 0.01
    ticket_system.reserve_ticket(new_ticket, reservation_minutes=calculation_time)
    db_connection.cursor.execute(f"SELECT reservation_state FROM ticket WHERE id={new_ticket};")
    assert db_connection.cursor.fetchone()[0] == 'reserved'
    db_connection.cursor.execute("SELECT max(id) FROM reservation;")
    max_reservation_id = db_connection.cursor.fetchone()[0]
    sleep(3)
    db_connection.cursor.execute("SELECT max(id) FROM reservation;")
    assert db_connection.cursor.fetchone()[0] < max_reservation_id
