import numpy as np
from sklearn.cluster import DBSCAN

from temp_input_data import n_rows, n_queries, n_columns


def precomputed_horizontal(selectivity_list):
    row_selectivities = np.zeros((n_rows, n_queries))
    for query_idx in range(n_queries):
        for row_idx in range(n_rows):
            for column_idx in range(n_columns):
                if selectivity_list[row_idx * n_columns + column_idx][query_idx]:
                    row_selectivities[row_idx][query_idx] = 1
                    break

    print('precomputed horizontal step1')

    row_clusters = DBSCAN(eps=0.1, min_samples=1).fit(row_selectivities)

    print('precomputed horizontal step2')

    return row_clusters.labels_
