from sklearn.cluster import DBSCAN

from input_data.temp_input_data import n_columns, n_rows, n_queries
import numpy as np


def sequential_hybrid(selectivity_list):
    print('sequential hybrid clustering')

    column_selectivities = np.zeros((n_columns, n_queries))
    for query_idx in range(n_queries):
        for column_idx in range(n_columns):
            column_selectivities[column_idx][query_idx] =\
                sum(selectivity_list[i * n_columns + column_idx][query_idx] for i in range(n_rows))

    print('sequential hybrid step1')

    column_clusters = DBSCAN(eps=0.1, min_samples=1).fit(column_selectivities)

    result = np.zeros(len(selectivity_list))
    cluster_idx = 0
    print('vert clusters amount', len(set(column_clusters.labels_)))
    for cluster_label in set(column_clusters.labels_):
        print('cluster label', cluster_label)
        columns_labeled = [i for i, e in enumerate(column_clusters.labels_) if e == cluster_label]
        # print('cells', np.array([selecivities_list[i * n_columns + columns_labeled[0]] for i in range(n_rows)]))
        cells_clusters = DBSCAN(eps=0.1, min_samples=1, algorithm='ball_tree').fit(
            np.array([selectivity_list[i * n_columns + columns_labeled[0]] for i in range(n_rows)]))
        print('cell cluster amount for vert cluster', cluster_label, ' = ', len(set(cells_clusters.labels_)))
        for column in columns_labeled:
            for row_idx, cluster in enumerate(cells_clusters.labels_):
                result[row_idx * n_columns + column] = cluster_idx + cluster
        cluster_idx += len(set(cells_clusters.labels_))
    print('sequential hybrid step2')

    return result
