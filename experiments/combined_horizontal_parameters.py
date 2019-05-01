from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector


def test_parameters():
    connector = PostgresConnector()
    test_linkage_criteria(connector)
    test_metrics(connector)


def test_linkage_criteria(connector):
    print('linkage criteria test')
    options = ['single_linkage', 'complete_linkage', 'average_linkage', 'centroid_method', 'centroid_method_rows_amount']
    costs = {}
    for option in options:
        costs[option] = combined_horizontal_from_db(connector, 'euclidean_distance', option)
    print(costs)


def test_metrics(connector):
    print('metrics test')
    options = ['euclidean_distance', 'squared_euclidean_distance', 'manhattan_distance', 'maximum_distance']
    costs = {}
    for option in options:
        costs[option] = combined_horizontal_from_db(connector, option, 'centroid_method_rows_amount')
    print(costs)


if __name__ == "__main__":
    test_parameters()