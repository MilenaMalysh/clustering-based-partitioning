import numpy as np

from clustering_implementations.combined_horizontal.HierarchicalClustering import HierarchicalClustering
from temp_input_data import n_rows, n_queries, n_columns


# the algorithm consists of the following steps:
# 1) form list of clusters with identical elements inside
# 2) run modified version of hierarchical agglomerative clustering algorithm which uses cost model based on hypoPG
# clustering evaluation in case there are several clusters with the same distances to merge.
def combined_horizontal(selectivity_list):

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


    hc = HierarchicalClustering(distinct_clusters, 2, n_queries)

    hc.hierarchical_clustering()

    return distinct_clusters


def queries_to_coordinates(queries_untouched):
    result = [1] * n_queries
    for query in queries_untouched:
        result[query] = 0
    return result
