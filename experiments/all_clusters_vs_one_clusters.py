import itertools

from db.PostgresConnector import PostgresConnector
from db.crud.partition_queries import create_partitions
from db.crud.select_queries import select_count
from input_data.queries import queries
from input_data.temp_input_data import table_name


def compare_running_time():
    pass


def compare_creation_time():
    connector = PostgresConnector()

    print('test: compare creation times')

    distinct_clusters = {}
    new_cluster_idx = 0
    for qs in itertools.product([0, 1], repeat=len(queries)):
        selected_queries = [query if qs[idx] else 'NOT ' + query for idx, query in enumerate(queries)]
        rows_amount = select_count(connector, selected_queries)
        if rows_amount:
            distinct_clusters[str(new_cluster_idx)] = [qs]
            new_cluster_idx += 1
    cost = create_partitions(connector, distinct_clusters, table_name+'_copy')
    print(distinct_clusters)
    print('all clusters costs: ', cost)

    # cost = create_partitions(connector,
    #                          {'1': [qs for qs in itertools.product([0, 1], repeat=len(queries))]},
    #                          table_name+'_copy')
    # print('original predicates', [qs for qs in itertools.product([0, 1], repeat=len(queries))])
    # print('one cluster costs: ', cost)
    #
    # distinct_clusters = {}
    # small_clusters = []
    # new_cluster_idx = 0
    # for qs in itertools.product([0, 1], repeat=len(queries)):
    #     selected_queries = [query if qs[idx] else 'NOT ' + query for idx, query in enumerate(queries)]
    #     rows_amount = select_count(connector, selected_queries)
    #     if rows_amount > 30000:
    #         distinct_clusters[str(new_cluster_idx)] = [qs]
    #         new_cluster_idx += 1
    #     else:
    #         small_clusters.append(qs)
    # if small_clusters:
    #     distinct_clusters[str(new_cluster_idx)] = small_clusters
    # else:
    #     print('there are no small clusters')
    # print('original predicates', distinct_clusters)
    # cost = create_partitions(connector, distinct_clusters, table_name+'_copy')
    # print('big clusters costs: ', cost)


if __name__ == "__main__":
    compare_creation_time()

