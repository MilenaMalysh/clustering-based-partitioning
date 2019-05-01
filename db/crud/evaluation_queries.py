import os

from input_data.temp_input_data import table_name


def get_plan_costs(connector, query):
    return explain_query(connector, query)[0][0]['Plan']['Total Cost']


def explain_query(connector, query):
    return connector.query("EXPLAIN (FORMAT json) " + query).fetchone()


def get_execution_time(connector, query):
    return explain_analyze_query(connector, query)[0][0]['Execution Time']


def get_actual_time(connector, query):
    plan_cost = explain_analyze_query(connector, query)[0][0]['Plan']
    return plan_cost['Actual Total Time'] + plan_cost['Actual Startup Time']


def explain_analyze_query(connector, query):
    result = connector.query("EXPLAIN (ANALYZE, FORMAT json) " + query).fetchone()
    connector.commit()
    return result

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


def drop_statistics(connector):
    connector.query("select pg_stat_reset();")
    connector.commit()
    return
