# TicketSalesSystem

Prerequisities:
PostgreSQL >= 10.0<br>
Database: ticket_system<br>
User: ticket_admin<br>
With password: qwerty


Logic part of backend of Ticket Sales System.
Repository contains following layers of abstraction:
* SQL dump of System's database (ticket_db.sql)
* Python classes corresponding to SQL tables (in tickets.py, events.py)
* Interface for end-users (in interface.py)
Documentation of system's keywords is placed inside docstrings in format recognized by autogeneration tools eg. Sphinx.

Program uses environment variables defined in impossible to discover top secret place.
But, to simplify the case, I am going to unmask it right now:


#### db_data.env<br>
DB_NAME="ticket_system"<br>
DB_USERNAME="ticket_admin"<br>
DB_PASSWORD="qwerty"
