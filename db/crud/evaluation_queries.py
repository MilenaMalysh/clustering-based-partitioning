import os

from input_data.temp_input_data import table_name


def get_execution_time(connector, query):
    return explain_analyze_query(connector, query)[0][0]['Execution Time']


def explain_analyze_query(connector, query):
    return connector.query("EXPLAIN (ANALYZE true, FORMAT json) " + query).fetchone()


def count_partition_query(connector, partition):
    if partition:
        query = []
        for column, ranges in partition.items():
            range_predicates = []
            for r in ranges:
                range_predicates.append(column + ' BETWEEN ' + str(r[0]) + ' AND ' + str(r[1]))
            query.append('(' + ' OR '.join(range_predicates) + ')')
        return connector.query("SELECT COUNT(*) FROM " + table_name + ' WHERE ' + ' AND '.join(query)).fetchone()
    else:
        return 0
