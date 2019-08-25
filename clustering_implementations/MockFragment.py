from db.PostgresConnector import PostgresConnector
from db.crud.select_queries import select_count


class MockFragment(object):
    def __init__(self, where_clause, tokens, connector):
        self.connector = connector
        self.where_clause = where_clause
        self.tokens = tokens
        self._count_cache = None

    def count(self) -> int:
        if self._count_cache is None:
            self._count_cache = select_count(self.connector, [self.where_clause])
        return self._count_cache

    def __str__(self):
        return self.where_clause

    def __hash__(self):
        return hash(self.where_clause)

    def __eq__(self, other):
        return self.where_clause == other.where_clause

    def __ne__(self, other):
        return not self == other
