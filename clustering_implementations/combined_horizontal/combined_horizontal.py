import itertools

from clustering_implementations.combined_horizontal.HierarchicalClustering import HierarchicalClustering
from db.crud.config_queries import add_column, drop_column
from db.crud.select_queries import select_count
from input_data.queries import queries
from input_data.temp_input_data import n_rows, n_queries, n_columns


def queries_to_coordinates(queries_untouched):
    result = [1] * n_queries
    for query in queries_untouched:
        result[query] = 0
    return result


''' the algorithm consists of the following steps:
# 1) form list of clusters with identical elements inside
# 2) run modified version of hierarchical agglomerative clustering algorithm which uses cost model based on hypoPG
# clustering evaluation in case there are several clusters with the same distances to merge.
'''


def combined_horizontal_from_db(connector, metric, linkage_criterion):
    print('combined horizontal algorithm')

    # 1st step
    distinct_clusters = {}
    new_cluster_idx = 0

    for qs in itertools.product([0, 1], repeat=len(queries)):
        selected_queries = [query if qs[idx] else 'NOT ' + query for idx, query in enumerate(queries)]
        rows_amount = select_count(connector, selected_queries)
        if rows_amount:
            distinct_clusters[frozenset({new_cluster_idx})] = {'coordinate': list(qs), 'rows_amount': rows_amount}
            new_cluster_idx += 1

    print('input data is generated')

    hc = HierarchicalClustering(
        distinct_clusters,
        5,
        len(queries),
        connector,
        metric,
        linkage_criterion
    )

    cost = hc.hierarchical_clustering()

    print('final results: \n clusters:', hc.clusters, '\n cost:', cost)

    return {'cost': cost, 'clusters': hc.clusters}
