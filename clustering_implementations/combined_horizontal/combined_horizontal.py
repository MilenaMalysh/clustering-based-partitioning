import itertools

from clustering_implementations.combined_horizontal.HierarchicalClustering import HierarchicalClustering
from db.crud.config_queries import add_column, drop_column
from db.crud.partition_queries import update_cluster_id_col
from db.crud.select_queries import select_count
from input_data.queries import queries
from input_data.temp_input_data import n_rows, n_queries, n_columns



# the algorithm consists of the following steps:
# 1) form list of clusters with identical elements inside
# 2) run modified version of hierarchical agglomerative clustering algorithm which uses cost model based on hypoPG
# clustering evaluation in case there are several clusters with the same distances to merge.
def combined_horizontal_from_sel_list(selectivity_list, connector):

    print('combined horizontal algorithm')

    # 1st step
    distinct_clusters = {}
    for row_idx in range(n_rows):
        queries_array = set(range(n_queries))
        for column_idx in range(n_columns):
            for query_idx in set(queries_array):
                if selectivity_list[row_idx * n_columns + column_idx][query_idx]:
                    queries_array.remove(query_idx)
            if not len(queries_array):
                break
        cluster_id = frozenset(queries_array)
        if cluster_id in distinct_clusters:
            distinct_clusters[cluster_id] += 1
        else:
            distinct_clusters[cluster_id] = 1

    distinct_clusters = {frozenset({i}): {'coordinate': queries_to_coordinates(queries_untouched), 'rows_amount': rows_amount}
                         for i, (queries_untouched, rows_amount) in enumerate(distinct_clusters.items())}

    print('combined horizontal step1')

    hc = HierarchicalClustering(distinct_clusters, 2, n_queries, connector, '')

    hc.hierarchical_clustering()

    print('combined horizontal step2 ', hc.clusters)

    return hc.clusters


def queries_to_coordinates(queries_untouched):
    result = [1] * n_queries
    for query in queries_untouched:
        result[query] = 0
    return result


def combined_horizontal_from_db(connector):

    print('combined horizontal algorithm')

    # 1st step
    distinct_clusters = {}
    new_cluster_idx = 0
    cluster_id_col_name = 'cluster_id'

    add_column(connector, cluster_id_col_name)

    for qs in itertools.product([0, 1], repeat=len(queries)):
        selected_queries = [query if qs[idx] else 'NOT ' + query for idx, query in enumerate(queries)]
        rows_amount = select_count(connector, selected_queries)
        if rows_amount:
            update_cluster_id_col(connector, selected_queries, new_cluster_idx, cluster_id_col_name)
            distinct_clusters[frozenset({new_cluster_idx})] = {'coordinate': list(qs), 'rows_amount': rows_amount}
            new_cluster_idx +=1

    print('db setup is finished')

    hc = HierarchicalClustering(distinct_clusters, 5, len(queries), connector, cluster_id_col_name)

    cost = hc.hierarchical_clustering()

    drop_column(connector, cluster_id_col_name)

    print('final results: \n clusters:', hc.clusters, '\n cost:', cost)

    return hc.clusters
