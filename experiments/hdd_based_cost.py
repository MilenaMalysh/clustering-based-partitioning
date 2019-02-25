import numpy as np
from sklearn.cluster import DBSCAN

from clustering_implementations.sequential_hybrid import sequential_hybrid
from cost_models.hdd_based import get_cost_for_queries


def sqnt_hybr_vs_hybr():
    selectivity_list = np.load("selectivity_list")
    clustering = DBSCAN(eps=0.1, min_samples=1).fit(selectivity_list).labels_
    print('DBSCAN algorithm finish')

    print('DBSCAN algorithm result cost: ', get_cost_for_queries(selectivity_list, clustering))

    clustering = sequential_hybrid(selectivity_list)

    print('sequential hybrid algorithm finish')

    print('sequential hybrid algorithm result cost: ', get_cost_for_queries(selectivity_list, clustering))
