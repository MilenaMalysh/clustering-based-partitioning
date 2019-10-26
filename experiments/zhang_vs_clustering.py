import os
import pickle

from clustering_implementations.classical_algorithms.zhang import zhang
from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector


def zhang_vs_clustering():
    connector = PostgresConnector()
    percentages = [10, 20, 30, 40, 50, 60, 70]
    settings = [
        # 'zhang',
                ('penalty_based', 'penalty_based')
                # ('single_linkage', 'euclidean_distance'),
                # ('complete_linkage', 'maximum_distance')
                ]
    tests_count = 0
    results = {percentage: {setting: {'cost': 0, 'cost_function_calls': 0} for setting in settings} for percentage in percentages}
    for percentage in percentages:
        print("DUPLICATES PERCENTAGE = " + str(percentage))
        directory = '../input_data/queries/zhang/' + str(percentage)
        input_files = os.listdir(directory)
        queries_files = [pickle.load(open(directory + '/' + file, 'rb')) for file in input_files]
        for idx, queries_file in enumerate(queries_files):
            print("INPUT FILE = " + directory + '/' + str(idx))
            # zhang
            predicate_usage = [[] for _ in queries_file]
            predicates = list(set().union(*queries_file))
            for predicate_idx, predicate in enumerate(predicates):
                for query_idx, query in enumerate(queries_file):
                    if predicate in query:
                        predicate_usage[query_idx].append(predicate_idx)
            zhang_result = zhang([1] * len(queries_file), predicates, predicate_usage, queries_file, PostgresConnector())
            results[percentage]['zhang']['cost'] += zhang_result['cost']
            results[percentage]['zhang']['cost_function_calls'] += zhang_result['cost_model_calls']
            tests_count +=1

            # clustering
            for setting in settings:
                if setting == 'zhang':
                    continue
                clustering_results = combined_horizontal_from_db(connector, setting[1], setting[0], True, queries_file, False)
                tests_count += 1
                print("TEST COUNT = " + str(tests_count))
                results[percentage][setting]['cost'] += clustering_results['cost']
                results[percentage][setting]['cost_function_calls'] += clustering_results['cost_function_calls']
        with open(directory + '\../result_' + str(percentage) + '.txt', 'w') as f:
            print(results[percentage], file=f)
    print('ZHANG ALGORITHM <DIFFERENT DUPLICATES PERCENTAGE TESTS> RESULTS: ', results)


if __name__ == "__main__":
    print('-----------------------------------------------------------------------')
    print('CLUSTERING VS ZHANG TESTS')
    print('-----------------------------------------------------------------------')
    zhang_vs_clustering()