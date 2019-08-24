import os
import pickle
from collections import defaultdict

from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector


def test_parameters():
    connector = PostgresConnector()
    print('######### OPTIMUM #########')
    get_optimum(connector)
    input_files = os.listdir('../input_data/queries')
    queries_files = [pickle.load(open('../input_data/queries/' + file, 'rb')) for file in input_files]
    test_linkage_criteria(connector, queries_files)
    test_metrics(connector, queries_files)


def test_linkage_criteria(connector, queries_files):
    print('######### linkage criteria test #########')
    options = ['single_linkage', 'complete_linkage', 'average_linkage', 'centroid_method', 'centroid_method_rows_amount']
    costs = defaultdict(int)
    for option in options:
        for queries in queries_files:
            costs[option] += combined_horizontal_from_db(connector, 'euclidean_distance', option, queries)
    print(costs)


def test_metrics(connector, queries_files):
    print('######### metrics test #########')
    options = ['euclidean_distance', 'squared_euclidean_distance', 'manhattan_distance', 'maximum_distance']
    costs = defaultdict(int)
    for option in options:
        for queries in queries_files:
            costs[option] += combined_horizontal_from_db(connector, option, 'centroid_method_rows_amount', queries)
    print(costs)


def get_optimum(connector):
    pass


if __name__ == "__main__":
    test_parameters()