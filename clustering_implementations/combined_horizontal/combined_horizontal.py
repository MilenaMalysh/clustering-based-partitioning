import itertools

from clustering_implementations.combined_horizontal.HierarchicalClustering import HierarchicalClustering
from cost_models.hdd_based_adapted import str_to_query_tokens
from db.crud.config_queries import add_column, drop_column
from db.crud.select_queries import select_count
from input_data.temp_input_data import n_rows, n_queries


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


def combined_horizontal_from_db(connector, metric, linkage_criterion, cost_model_usage, queries):
    distinct_clusters = {}
    new_cluster_idx = 0

    str_queries = ['(' + ' AND '.join([' '.join([str(i) for i in q]) for q in query]) + ')' for query in queries]

    for qs in itertools.product([0, 1], repeat=len(str_queries)):
        selected_queries = [query if qs[idx] else '(NOT ' + query + ')' for idx, query in enumerate(str_queries)]
        rows_amount = select_count(connector, selected_queries)
        if rows_amount:
            distinct_clusters[frozenset({new_cluster_idx})] = {'coordinate': list(qs), 'rows_amount': rows_amount}
            new_cluster_idx += 1

    hc = HierarchicalClustering(
        distinct_clusters,
        str_queries,
        len(queries),
        connector,
        metric,
        linkage_criterion,
        cost_model_usage
    )

    return hc.hierarchical_clustering()
    #
    # print('final results: \n clusters:', hc.clusters, '\n cost:', cost)
    #
    # return {'cost': cost, 'clusters': hc.clusters}
