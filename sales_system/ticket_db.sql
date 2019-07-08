CREATE TABLE IF NOT EXISTS Event(
    id serial PRIMARY KEY,
    name varchar NOT NULL,
    datetime timestamp without time zone NOT NULL);

CREATE TABLE IF NOT EXISTS Ticket(
    id serial PRIMARY KEY,
    type varchar NOT NULL,
    price real NOT NULL,
    event_id integer NOT NULL REFERENCES Event(id),
    reservation_state varchar NOT NULL DEFAULT 'available');

CREATE TABLE IF NOT EXISTS Reservation(
    id serial PRIMARY KEY,
    ticket_id integer NOT NULL REFERENCES Ticket(id),
    reservation_time timestamp without time zone NOT NULL);
