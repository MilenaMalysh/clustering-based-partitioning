import random

import numpy as np


def generate_selectivity_list(n_columns, n_rows, n_queries):
    selectivity_list = np.zeros((n_columns * n_rows, n_queries))
    columns_referenced = []
    rows_referenced = []

    print('generator step 1')

    for q in range(n_queries):
        n_columns_referenced = random.randint(2, n_columns // 4)
        n_rows_referenced = random.randint(n_rows // 8, n_rows // 4)
        columns_referenced.append(np.random.randint(n_columns, size=n_columns_referenced))
        rows_referenced.append(np.random.randint(n_rows, size=n_rows_referenced))

    print('generator step 2')

    for q in range(n_queries):
        for row in rows_referenced[q]:
            for column in columns_referenced[q]:
                selectivity_list[row * n_columns + column][q] = 1

    selectivity_list.dump('selectivity_list')

    print('selectivity list is generated')
    return selectivity_list
