from functools import reduce

from db.crud.config_queries import copy_table_structure, copy_table_data, drop_table, create_table, \
    create_insertion_rule, drop_insertion_rule, insert_data_from_table
from input_data.queries import queries
from input_data.temp_input_data import table_name
from helpers.minimize import minimize


def generate_clusters_rules(clusters_queries):
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
        clusters_check_conditions['_'.join(str(x) for x in sorted(list(sub_table)))] = subclusters_check_conditions_str
    return clusters_check_conditions


def create_tables_hierarchy(connector, master_table, check_conditions):
    for sub_table, check_condition in check_conditions.items():
        create_table(connector, master_table + '_' + sub_table, check_condition, master_table)


def create_insertion_rules(connector, master_table, check_conditions):
    for sub_table, check_condition in check_conditions.items():
        create_insertion_rule(connector, master_table + '_' + sub_table, check_condition, master_table)


def create_partitions(connector, clusters_queries, master_table):
    # copy structure from original table to the new <master_table>
    copy_table_structure(connector, master_table)
    # generate clusters' conditions which will be used for subtables hierarchy and insertion rules
    clusters_conditions = generate_clusters_rules(clusters_queries)
    # create hierarchy of subtables
    create_tables_hierarchy(connector, master_table, clusters_conditions)
    # set up insertion rules
    create_insertion_rules(connector, master_table, clusters_conditions)
    # insert data from the original table to the new <master_table>
    insert_data_from_table(connector, master_table, table_name)


def merge_two_partitions(connector, master_table, clusters_to_merge):
    """
    Args:
    clusters_to_merge: example value ((frozenset({1, 2, 3}), [[0, 0, 0], [1, 0, 1]]), (frozenset({4}), [[0, 0, 1]]))
    """

    # generate new check condition for merger clusters
    sub_table, check_condition = list(generate_clusters_rules({
        clusters_to_merge[0][0].union(clusters_to_merge[1][0]): clusters_to_merge[0][1] + clusters_to_merge[1][1]
    }).items())[0]
    # add new subtable
    create_table(connector, master_table + '_' + sub_table, check_condition, master_table)
    for cluster_to_merge in clusters_to_merge:
        table_to_drop = master_table + '_' + '_'.join(str(x) for x in sorted(list(cluster_to_merge[0])))
        drop_insertion_rule(connector, table_to_drop, master_table)
        drop_table(connector, table_to_drop)

    create_insertion_rule(connector, master_table + '_' + sub_table, check_condition, master_table)

    insert_data_from_table(connector, master_table + '_' + sub_table, table_name, check_condition)


def split_partition(connector, master_table, clusters_to_create):
    """
    Args:
    clusters_to_split: example value {frozenset({1, 2, 3}): [[0, 0, 0], [1, 0, 1]]), frozenset({4}), [[0, 0, 1]]}
    """

    table_to_split = master_table + '_' + '_'.join(str(x) for x in sorted(list(frozenset().union(*clusters_to_create.keys()))))
    where_clause = generate_clusters_rules(
        {frozenset({'table_to_split'}): reduce(lambda x, y: x + y, clusters_to_create.values())}
    )

    drop_insertion_rule(connector, table_to_split, master_table)
    drop_table(connector, table_to_split)

    # generate new check condition for merged clusters
    check_conditions = generate_clusters_rules(clusters_to_create)

    for table_to_create, cluster_conditions in check_conditions.items():
        # add new subtable
        create_table(connector, master_table + '_' + table_to_create, cluster_conditions, master_table)
        create_insertion_rule(connector, master_table + '_' + table_to_create, cluster_conditions, master_table)

    insert_data_from_table(connector, master_table, table_name, where_clause['table_to_split'])


# def create_insert_trigger(connector, clusters_check_conditions, master_table):
#     trigger_conditions = []
#     for cluster_table, cluster_conditions in clusters_check_conditions.items():
#         if not trigger_conditions:
#             trigger_conditions.append("IF ({0}) THEN INSERT INTO {1} VALUES (NEW.*);"
#                                       .format(cluster_conditions.replace("l_", "NEW.l_"), cluster_table))
#         else:
#             trigger_conditions.append("ELSIF ({0}) THEN INSERT INTO {1} VALUES (NEW.*);"
#                                       .format(cluster_conditions.replace("l_", "NEW.l_"), cluster_table))
#
#     trigger_function = """
#     CREATE OR REPLACE FUNCTION {0}_insert_trigger()
#     RETURNS TRIGGER AS $$
#     BEGIN
#         {1}
#         ELSE
#             RAISE EXCEPTION 'Date out of range.  Fix the {0}_insert_trigger() function!';
#         END IF;
#         RETURN NULL;
#     END;
#     $$
#     LANGUAGE plpgsql;
#     """.format(master_table, ''.join(trigger_conditions))
#
#     connector.query(trigger_function)
#     connector.commit()
#     connector.query("""
#     CREATE TRIGGER insert_{0}_trigger
#     BEFORE INSERT ON {0}
#     FOR EACH ROW EXECUTE PROCEDURE {0}_insert_trigger();
#     """.format(master_table))
#     connector.commit()

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
