from sklearn.cluster import DBSCAN

from temp_input_data import n_columns, n_rows, n_queries
import numpy as np


def sequential_hybrid(selecivities_list):
    column_selectivities = np.zeros((n_columns, n_queries))
    for query_idx in range(n_queries):
        for column_idx in range(n_columns):
            column_selectivities[column_idx][query_idx] =\
                sum(selecivities_list[i * n_columns + column_idx][query_idx] for i in range(n_rows))

    column_clusters = DBSCAN(eps=0.1, min_samples=1).fit(column_selectivities)

    result = np.zeros(len(selecivities_list))
    cluster_idx = 0
    for cluster_label in set(column_clusters.labels_):
        columns_labeled = [i for i, e in enumerate(column_clusters.labels_) if e == cluster_label]
        cells_clusters = DBSCAN(eps=0.1, min_samples=1).fit(
            np.array([selecivities_list[i * n_columns + columns_labeled[0]] for i in range(n_rows)]))

        for column in columns_labeled:
            for row_idx, cluster in enumerate(cells_clusters.labels_):
                result[row_idx * n_columns + column] = cluster_idx + cluster
        cluster_idx += len(set(cells_clusters.labels_))

    return result
