from input_data.temp_input_data import table_name
#
# # TODO: sort cluster ids for clusters_queries keys in alphabetical order
# def create_partitions(connector, clusters_queries, master_table):
#     clusters_check_conditions = {}
#     for sub_table, cluster_queries in clusters_queries.items():
#         subclusters_check_conditions = []
#         for subcluster_queries in cluster_queries:
#             subcluster_check_conditions = []
#             for idx, query in enumerate(subcluster_queries):
#                 subclusters_check_conditions.append(
#                     queries[idx] if query else 'NOT ' + queries[idx]
#                 )
#             subclusters_check_conditions.append(subcluster_check_conditions)
#         subclusters_check_conditions_str = ' OR '.join(subclusters_check_conditions)
#         connector.query("CREATE TABLE {0} ({1}) INHERITS ({3});".format(
#             master_table + '_' + sub_table, subclusters_check_conditions_str, master_table))
#         connector.commit()
#         clusters_check_conditions[sub_table] = subclusters_check_conditions_str
#     return clusters_check_conditions
#
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
