import psycopg2
from abc import ABC


class Connection(ABC):
    pass


class DBConnection(Connection):
    def __init__(self, db_name, username, password, host='localhost'):
        self.connection = psycopg2.connect(database=db_name, user=username,
                                           password=password, host=host)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def __getattr__(self, item):
        return getattr(self.connection, item)
