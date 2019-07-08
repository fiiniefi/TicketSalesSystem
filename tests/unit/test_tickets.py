import pytest
from mock import Mock, ANY
import sales_system.tickets
from sales_system.tickets import TicketManager
from sales_system.exceptions import InvalidTicket
# noinspection PyUnresolvedReferences
from tests.unit.connections import db_connection_base, db_connection_commit


@pytest.fixture(scope='module')
def ticket_manager():
    condition_mock = Mock()
    condition_mock.return_value = ("", None)
    return TicketManager(condition_mock)


def test_GetAvailableTicketsInfo_PassedCorrectly(db_connection_base, ticket_manager):
    ticket_manager.get_available_tickets_info(db_connection_base)

    db_connection_base.cursor.execute.assert_called_once()
    db_connection_base.cursor.fetchall.assert_called_once_with()


def test_ReserveTicket_PassedCorrectly(monkeypatch, db_connection_commit, ticket_manager):
    db_connection_commit.cursor.rowcount.return_value = True
    monkeypatch.setattr(sales_system.tickets, 'datetime', Mock())
    monkeypatch.setattr(sales_system.tickets, 'logging', Mock())
    start_mock = Mock()
    process_mock = Mock(return_value=start_mock)
    monkeypatch.setattr(sales_system.tickets, 'Process', process_mock)

    ticket_manager.reserve_ticket(db_connection_commit, ANY)

    assert db_connection_commit.cursor.execute.call_count == 2
    db_connection_commit.commit.assert_called_once_with()
    process_mock.assert_called_once()
    start_mock.start.assert_called_once()


def test_BuyTicket_PassedCorrectly(monkeypatch, db_connection_commit, ticket_manager):
    price_mock = Mock()
    price_mock.name = 'price'
    db_connection_commit.cursor.description = [price_mock]
    db_connection_commit.cursor.fetchone.return_value = [10]
    charge_mock = Mock()
    payment_mock = Mock(return_value=charge_mock)
    monkeypatch.setattr(sales_system.tickets, 'PaymentGateway', payment_mock)
    monkeypatch.setattr(sales_system.tickets, 'logging', Mock())

    ticket_manager.buy_ticket(db_connection_commit, ANY)

    assert db_connection_commit.cursor.execute.call_count == 3
    db_connection_commit.commit.assert_called_once_with()
    payment_mock.assert_called_once()
    charge_mock.charge.assert_called_once_with(10, ANY)


@pytest.mark.parametrize('function_name', ['reserve_ticket', 'buy_ticket'])
def test_TicketFunction_RaisesInvalidTicket(db_connection_base, ticket_manager, function_name):
    db_connection_base.cursor.rowcount = False
    with pytest.raises(InvalidTicket):
        getattr(ticket_manager, function_name)(db_connection_base, ANY)


def test_GetReservationInfo_PassedCorrectly(db_connection_base, ticket_manager):
    ticket_manager.get_reservation_info(db_connection_base)

    db_connection_base.cursor.execute.assert_called_once()
    db_connection_base.cursor.fetchall.assert_called_once_with()


def test_GetReservationStatistics_PassedCorrectly(db_connection_base, ticket_manager):
    statistics_number = 2  # please increment this value after each addition of new statistic

    ticket_manager.get_reservation_statistics(db_connection_base)

    assert db_connection_base.cursor.execute.call_count == statistics_number
    assert db_connection_base.cursor.fetchall.call_count == statistics_number
