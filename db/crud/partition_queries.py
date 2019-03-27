from db.crud.config_queries import copy_table_structure, copy_table_data, drop_table
from db.crud.evaluation_queries import get_execution_time, get_plan_costs
from input_data.queries import queries
from input_data.temp_input_data import table_name
from helpers.minimize import minimize


def create_partitions(connector, clusters_queries, master_table):
    copy_table_structure(connector, master_table)
    if len(clusters_queries.keys()) != 1:
        clusters_check_conditions = create_tables_inheritance(connector, clusters_queries, master_table)
        create_insert_trigger(connector, clusters_check_conditions, master_table)

    creation_cost = get_execution_time(connector, "INSERT INTO {0} SELECT * FROM {1};".format(master_table, table_name))
    execution_cost = 0
    for query in queries:
        execution_cost += get_execution_time(connector, "SELECT * FROM {0} WHERE {1}".format(master_table, query))

    drop_table(connector, master_table)
    return {
        'creation cost': creation_cost,
        'execution cost': execution_cost
    }


def create_tables_inheritance(connector, clusters_queries, master_table):
    clusters_check_conditions = {}
    for sub_table, cluster_queries_original in clusters_queries.items():
        subclusters_check_conditions = []
        cluster_queries = minimize(cluster_queries_original)
        for subcluster_queries in cluster_queries:
            subcluster_check_conditions = []
            for idx, query in enumerate(subcluster_queries):
                if query != -1:
                    subcluster_check_conditions.append(
                        queries[idx] if query else '(NOT ' + queries[idx] + ')'
                    )
            subclusters_check_conditions.append('(' + ' AND '.join(subcluster_check_conditions) + ')')
        subclusters_check_conditions_str = ' OR '.join(subclusters_check_conditions)
        connector.query("CREATE TABLE {0} (CHECK ({1})) INHERITS ({2});".format(
            master_table + '_' + sub_table, subclusters_check_conditions_str, master_table))
        connector.commit()
        clusters_check_conditions[master_table + '_' + sub_table] = subclusters_check_conditions_str
    return clusters_check_conditions


def create_insert_trigger(connector, clusters_check_conditions, master_table):
    trigger_conditions = []
    for cluster_table, cluster_conditions in clusters_check_conditions.items():
        if not trigger_conditions:
            trigger_conditions.append("IF ({0}) THEN INSERT INTO {1} VALUES (NEW.*);"
                                      .format(cluster_conditions.replace("l_", "NEW.l_"), cluster_table))
        else:
            trigger_conditions.append("ELSIF ({0}) THEN INSERT INTO {1} VALUES (NEW.*);"
                                      .format(cluster_conditions.replace("l_", "NEW.l_"), cluster_table))

    trigger_function = """
    CREATE OR REPLACE FUNCTION {0}_insert_trigger()
    RETURNS TRIGGER AS $$
    BEGIN
        {1}
        ELSE
            RAISE EXCEPTION 'Date out of range.  Fix the {0}_insert_trigger() function!';
        END IF;
        RETURN NULL;
    END;
    $$
    LANGUAGE plpgsql;
    """.format(master_table, ''.join(trigger_conditions))

    connector.query(trigger_function)
    connector.commit()
    connector.query("""
    CREATE TRIGGER insert_{0}_trigger
    BEFORE INSERT ON {0}
    FOR EACH ROW EXECUTE PROCEDURE {0}_insert_trigger();
    """.format(master_table))
    connector.commit()

# # TODO: clusters_to_merge is tuple, put on the first place cluster with larger amount of rows
# def merge_two_clusters(connector, clusters_check_conditions, clusters_to_merge, master_table):
#     # step 1: create trigger
#     clusters_check_conditions[clusters_to_merge[0]] = clusters_check_conditions[clusters_to_merge[0]] + ' OR ' +\
#                                                       clusters_check_conditions[clusters_to_merge[1]]
#     del clusters_check_conditions[clusters_to_merge[1]]
#
#     trigger_conditions = []
#     for cluster_table, cluster_conditions in clusters_check_conditions.items():
#         if not trigger_conditions:
#             trigger_conditions.append("IF ({0}) THEN INSERT INTO {1} "
#                                       .format(clusters_check_conditions, cluster_table))
#         else:
#             trigger_conditions.append("ELSIF ({0}) THEN INSERT INTO {1} "
#                                       .format(clusters_check_conditions, cluster_table))
#
#     trigger_function = """
#     CREATE OR REPLACE FUNCTION {0}_insert_trigger()\n
#     RETURNS TRIGGER AS $$
#     BEGIN
#         {1}VALUES (NEW.*);
#         ELSE
#             RAISE EXCEPTION 'Date out of range.  Fix the {0}_insert_trigger() function!';
#         END IF;
#         RETURN NULL;
#     END;
#     $$
#     LANGUAGE plpgsql;
#     """.format(master_table, 'VALUES (NEW.*);\n'.join(trigger_conditions))
#
#     connector.query(trigger_function)
#     connector.commit()
#
#     # step 2: copy data from the second cluster to merge to the first one
#
#     # step 3: delete old table and add new one
#     # TODO: recreate clusters table back


def update_cluster_id_col(connector, where_clauses, cluster_id, cluster_id_col_name):
    connector.query(
        "UPDATE {0} SET {1} = {2} WHERE {3};".format(table_name, cluster_id_col_name, cluster_id,
                                                     ' AND '.join(where_clauses))
    )
    connector.commit()


def create_list_partition_column(connector, cluster_id_col_name):
    connector.query(
        "SELECT hypopg_partition_table('{0}', 'PARTITION BY LIST({1})');".format(table_name, cluster_id_col_name)
    )
    connector.commit()


def drop_partitions(connector):
    connector.query("SELECT hypopg_reset_table()")
    connector.commit()


def create_list_partition(connector, cluster_ids):
    connector.query(
        "SELECT tablename FROM hypopg_add_partition('{0}_{1}', 'PARTITION OF {0} FOR VALUES IN ({2})');".format(
            table_name,
            '_'.join(str(cluster_id) for cluster_id in cluster_ids),
            ', '.join(str(cluster_id) for cluster_id in cluster_ids)
        )
    )
    connector.commit()
