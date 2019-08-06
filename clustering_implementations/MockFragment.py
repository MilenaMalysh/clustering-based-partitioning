from db.PostgresConnector import PostgresConnector
from db.crud.select_queries import select_count


class MockFragment(object):
    def __init__(self, where_clause, connector):
        self.connector = connector
        self.where_clause = where_clause

    def count(self) -> int:
        return select_count(self.connector, [self.where_clause])

    def __str__(self):
        return self.where_clause

    def __hash__(self):
        return hash(self.where_clause)

    def __eq__(self, other):
        return self.where_clause == other.where_clause

    def __ne__(self, other):
        return not self == other
