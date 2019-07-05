import logging
from multiprocessing import Process
from datetime import datetime
from time import sleep
from mock import Mock
from sales_system.payment import PaymentGateway
from sales_system.connection import DBConnection
from sales_system.exceptions import InvalidTicket


class TicketManager:
    def __init__(self, generate_condition):
        self._generate_condition = generate_condition

    def get_available_tickets_info(self, connection, event_name=None, ticket_type=None):
        condition_payload = {'name': event_name, 'type': ticket_type, 'reservation_state': 'available'}
        expr = "SELECT price, name, type, count(type) FROM ticket " \
               "JOIN event ON (event_id=event.id) " \
               f"{self._generate_condition(**condition_payload)} " \
               "GROUP BY name, type, price"
        connection.cursor.execute(expr)
        return connection.cursor.fetchall()

    def reserve_ticket(self, connection, ticket_id, reservation_minutes=15):
        if not self._is_ticket_valid(connection, ticket_id):
            raise InvalidTicket(f"Ticket of given id ({ticket_id}) is invalid (maybe already sold?)")

        now = datetime.now()
        expr = f"UPDATE ticket SET reservation_state='reserved' WHERE id={ticket_id};" \
               f"INSERT INTO reservation (ticket_id, reservation_time) VALUES ({ticket_id}, '{now}');"
        connection.cursor.execute(expr)
        connection.commit()
        logging.debug(f"Ticket of number {ticket_id} has been reserved.")

        self._run_reservation_monitor(ticket_id, reservation_minutes)

    def buy_ticket(self, connection, ticket_id):
        if not self._is_ticket_valid(connection, ticket_id):
            raise InvalidTicket(f"Ticket of given id ({ticket_id}) is invalid (maybe already sold?)")
        expr = f"SELECT * FROM ticket WHERE id={ticket_id};"
        connection.cursor.execute(expr)
        column_names = [column.name for column in connection.cursor.description]
        ticket_data = dict(zip(column_names, connection.cursor.fetchone()))

        self._pay_for_ticket(ticket_data['price'])
        self._remove_ticket(connection, ticket_id)
        logging.debug(f"Ticket of number {ticket_id} has been bought.")
        connection.commit()

    def get_reservation_info(self, connection, ticket_id=None):
        expr = "SELECT reservation.id, ticket_id, reservation_time, type, price, name " \
               "FROM reservation " \
               "JOIN ticket ON (ticket_id=ticket.id) " \
               "JOIN event ON (event_id=event.id) " \
               f"{self._generate_condition(**{'ticket.id': ticket_id})}"
        connection.cursor.execute(expr)
        return connection.cursor.fetchall()

    def get_reservation_statistics(self, connection):
        statistics = {'Amount of reserved tickets for each event': self._reserved_for_event_statistics(connection),
                      'Amount of reserved tickets of a specified type': self._reserved_of_type_statistics(connection),
                      }
        return statistics

    def _reserved_for_event_statistics(self, connection):
        expr = "SELECT name, count(reservation.ticket_id) FROM event " \
               "LEFT JOIN ticket ON (event.id=event_id) " \
               "LEFT JOIN reservation ON (ticket.id=ticket_id) " \
               "GROUP BY event.id"
        connection.cursor.execute(expr)
        return connection.cursor.fetchall()

    def _reserved_of_type_statistics(self, connection):
        expr = "SELECT type, count(reservation.ticket_id) FROM ticket " \
               "LEFT JOIN reservation ON (ticket.id=ticket_id) " \
               "GROUP BY type"
        connection.cursor.execute(expr)
        return connection.cursor.fetchall()

    def _run_reservation_monitor(self, ticket_id, reservation_minutes):
        reservation_runner = Process(target=self._handle_reservation,
                                     args=(
                                         ticket_id, reservation_minutes),
                                     )
        reservation_runner.start()

    def _handle_reservation(self, ticket_id, reservation_minutes):
        start_time = datetime.now()
        connection = DBConnection('ticket_platform', 'ticket_admin', 'qwerty')    # to be improved
        expr = f"SELECT * FROM reservation WHERE ticket_id={ticket_id}"
        while self._result_rowcount(connection, expr):
            sleep(0.1)
            time_is_up = (datetime.now() - start_time).seconds >= reservation_minutes*60
            if time_is_up:
                self._withdraw_reservation(connection, ticket_id)
        connection.commit()
        connection.close()

    def _withdraw_reservation(self, connection, ticket_id):
        logging.debug(f"Reservation of ticket number {ticket_id}  withdrawn.")
        expr = f"UPDATE ticket SET reservation_state='available' WHERE id={ticket_id};" \
               f"DELETE FROM reservation WHERE ticket_id={ticket_id};"
        connection.cursor.execute(expr)

    def _pay_for_ticket(self, price):
        PaymentGateway().charge(price, self._get_payment_token())

    def _get_payment_token(self):
        return Mock(return_value='success')

    def _remove_ticket(self, connection, ticket_id):
        expr = f"DELETE FROM reservation WHERE ticket_id={ticket_id};" \
               f"DELETE FROM ticket WHERE id={ticket_id};"
        connection.cursor.execute(expr)

    def _result_rowcount(self, connection, expr):
        connection.cursor.execute(expr)
        return connection.cursor.rowcount

    def _is_ticket_valid(self, connection, ticket_id):
        expr = f"SELECT * FROM ticket WHERE id={ticket_id} AND reservation_state='available'"
        connection.cursor.execute(expr)
        return connection.cursor.rowcount
