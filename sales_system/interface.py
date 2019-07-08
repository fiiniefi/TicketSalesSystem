from functools import reduce
from typing import Optional
from sales_system.exceptions import ConnectionNotProvided
from sales_system.connection import Connection  # noqa: F401
from sales_system.events import EventManager
from sales_system.tickets import TicketManager


class TicketSystem:
    def __init__(self, connection, db_path='ticket_db.sql'):
        self.default_connection = connection
        self.default_connection.cursor.execute(open(db_path).read())

    def get_events(self, connection=None, event_name=None, timestamp=None, ticket_type=None):
        # type: (Optional[Connection], Optional[str], Optional[int], Optional[str]) -> list
        """
        If called without arguments, returns all events in current state of database.
        Otherwise, returns all events matching values in specified parameters.

        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :param str event_name: (optional) If given, function returns only events
            matching specified name
        :param int timestamp: (optional) If given, function returns only events
            taking place in specified date and time
        :param str ticket_type: (optional) If given, function returns number of tickets
            of specified type for all matched events
        :rtype: list
        :return: All matched events with data about them (name, date and time, number of
            available tickets of all types)
        """
        connection = self._validate_connection(connection)
        return EventManager(self._generate_condition).\
            get_events(connection, event_name, timestamp, ticket_type)

    def get_available_tickets_info(self, connection=None, event_name=None, ticket_type=None):
        # type: (Optional[Connection], Optional[str], Optional[str]) -> list
        """
        If called without arguments, returns all available tickets in the current state of database.
        Otherwise, returns all available tickets matching values in specified parameters.

        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :param str event_name: (optional) name of the event for which tickets are checked
        :param str ticket_type: (optional) desired type of the ticket
        :rtype: list
        :return: Data about all matched available tickets:
            * Price
            * Name of an event
            * Type
            * Number of tickets of a specified types
        """
        connection = self._validate_connection(connection)
        return TicketManager(self._generate_condition).\
            get_available_tickets_info(connection, event_name, ticket_type)

    def reserve_ticket(self, ticket_id, connection=None, reservation_minutes=15):
        # type: (int, Optional[Connection], float) -> None
        """
        Reserves a ticket indicated by given ticket_id.

        :param int ticket_id: id of a ticket to reserve
        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :param float reservation_minutes: (optional) reservation time in minutes. Defaults to 15
        :raise InvalidTicket: when there is no ticket indicated by ticket_id in current state
            of database
        """
        connection = self._validate_connection(connection)
        TicketManager(self._generate_condition).\
            reserve_ticket(connection, ticket_id, reservation_minutes)

    def buy_ticket(self, ticket_id, connection=None):
        # type: (int, Optional[Connection]) -> None
        """
        Makes purchase of a ticket indicated by ticket_id.

        :param int ticket_id: id of the chosen ticket
        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :raise CardError: when card is declined
        :raise CurrencyError: when chosen currency is not supported
        :raise InvalidTicket: when there is no ticket indicated by ticket_id in current state
            of database
        :raise PaymentError: when something unspecified went wrong with transaction
        """
        connection = self._validate_connection(connection)
        TicketManager(self._generate_condition).buy_ticket(connection, ticket_id)

    def get_reservation_info(self, connection=None, ticket_id=None):
        # type: (Optional[Connection], Optional[int]) -> list
        """
        Returns information about valid reservation

        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :param int ticket_id: (optional) If given, function returns reservation data
            of ticket indicated by ticket_id
        :rtype: list
        :return: Data of matched reservations:
            * reservation ID
            * id of reserved ticket
            * reservation time
            * type of reserved ticket
            * price of reserved ticket
            * name of an event
        """
        connection = self._validate_connection(connection)
        return TicketManager(self._generate_condition).\
            get_reservation_info(connection, ticket_id)

    def get_reservation_statistics(self, connection=None):
        # type: (Optional[Connection]) -> dict
        """
        Generates and returns overall statistics about currently active reservations.

        :param Connection connection: (optional) If not provided, function uses default
            connection defined in constructor
        :rtype: dict
        :return: Returns dict with statistic description as a key and statistic data as a value.
            Currently supported statistics:
            * Summary amount of reserved tickets for each event
            * Summary amount of reserved tickets of a specified type
        """
        connection = self._validate_connection(connection)
        return TicketManager(self._generate_condition).\
            get_reservation_statistics(connection)

    def _validate_connection(self, connection):
        connection = connection if connection is not None else self.default_connection
        if connection is None:
            raise ConnectionNotProvided("Connection should be passed to constructor or to function call")
        return connection

    def _generate_condition(self, **kwargs):
        return reduce(lambda res, pair: res if pair[1] is None else res + f"AND {pair[0]}='{pair[1]}' ",
                      kwargs.items(),
                      "WHERE 1=1 ")
