from datetime import datetime


class EventManager:
    def __init__(self, generate_condition):
        self._generate_condition = generate_condition

    def get_events(self, connection, event_name=None, timestamp=None, ticket_type=None):
        date_and_time = datetime.fromtimestamp(timestamp) if timestamp is not None else None
        condition_payload = {'name': event_name, 'datetime': date_and_time, 'type': ticket_type}
        expr = "SELECT event.id, name, datetime, count(ticket.id) FROM event " \
               "LEFT JOIN ticket ON (event.id=event_id) " \
               f"{self._generate_condition(**condition_payload)} " \
               f"GROUP BY event.id"
        connection.cursor.execute(expr)
        return connection.cursor.fetchall()
