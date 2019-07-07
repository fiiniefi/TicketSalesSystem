import pytest
from mock import Mock, patch, ANY
from sales_system import TicketSystem
# noinspection PyUnresolvedReferences
from tests.unit.connections import db_connection_base
import sales_system.interface


@pytest.fixture(scope='module')
def ticket_system(db_connection_base):
    with patch('sales_system.interface.open'):
        yield TicketSystem(db_connection_base, Mock())


@pytest.mark.parametrize('module, function_name, additional_argc, keyword_argv',
                         [(sales_system.interface.EventManager, 'get_events', 3, []),
                          (sales_system.interface.TicketManager, 'get_available_tickets_info', 2, []),
                          (sales_system.interface.TicketManager, 'reserve_ticket', 2, [Mock()]),
                          (sales_system.interface.TicketManager, 'buy_ticket', 1, [Mock()]),
                          (sales_system.interface.TicketManager, 'get_reservation_info', 1, []),
                          (sales_system.interface.TicketManager, 'get_reservation_statistics', 0, []),
                          ])
def test_InterfaceKeywords_PassedCorrectly(db_connection_base, ticket_system, monkeypatch,
                                           module, function_name, additional_argc, keyword_argv):
    function_mock = Mock()
    monkeypatch.setattr(module, function_name, function_mock)

    getattr(ticket_system, function_name)(*keyword_argv)

    function_mock.assert_called_once_with(db_connection_base, *([ANY] * additional_argc))
