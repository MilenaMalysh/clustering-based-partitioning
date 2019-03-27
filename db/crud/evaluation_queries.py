import os

from input_data.temp_input_data import table_name


def get_plan_costs(connector, query):
    return explain_query(connector, query)[0][0]['Plan']['Total Cost']


def explain_query(connector, query):
    return connector.query("EXPLAIN (FORMAT json) " + query).fetchone()


def get_execution_time(connector, query):
    return explain_analyze_query(connector, query)[0][0]['Execution Time']


def explain_analyze_query(connector, query):
    result = connector.query("EXPLAIN (ANALYZE, FORMAT json) " + query).fetchone()
    connector.commit()
    return result


def get_query_cost_on_partitions(connector, cluster_id_col_name, cluster_ids):
    return get_plan_costs(connector, "SELECT * from {0} WHERE {1} IN ({2})".format(
        table_name,
        cluster_id_col_name,
        ', '.join(cluster_ids)
    ))


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
