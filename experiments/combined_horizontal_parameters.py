import os
import pickle
from collections import defaultdict

from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector


def test_parameters():
    connector = PostgresConnector()
    print('######### HAC TEST PARAMETERS #########')
    get_optimum(connector)
    directory = '../input_data/queries/zhang/10'
    input_files = os.listdir(directory)
    queries_files = [pickle.load(open(directory + '/' + file, 'rb')) for file in input_files]
    linkage_criteria = [
        'single_linkage',
        'complete_linkage',
        'average_linkage',
        'centroid_method',
        'penalty_based'
    ]
    similarity_measures = [
        'euclidean_distance',
        'squared_euclidean_distance',
        'manhattan_distance',
        'maximum_distance',
        'penalty_based'
    ]
    cost_based_results = {}
    random_based_results = {}
    for idx, queries in enumerate(queries_files):
        for linkage_criterion in linkage_criteria:
            for similarity_measure in similarity_measures:
                if linkage_criterion == 'centroid_method' and similarity_measure != 'euclidean_distance':
                    continue
                if (similarity_measure == 'penalty_based') != (linkage_criterion == 'penalty_based'):
                    continue
                print("INPUTS: {}/{}, {}, {}".format(directory, input_files[idx], linkage_criterion, similarity_measure))
                if not (linkage_criterion + ' + ' + similarity_measure in cost_based_results):
                    cost_based_results[linkage_criterion + ' + ' + similarity_measure] = {
                        'cost': 0,
                        'cost_function_calls': 0
                    }
                    random_based_results[linkage_criterion + ' + ' + similarity_measure] = {
                        'cost': 0
                    }
                cost_based_result = combined_horizontal_from_db(connector, similarity_measure, linkage_criterion, True, queries, False)
                cost_based_results[linkage_criterion + ' + ' + similarity_measure]['cost'] += cost_based_result['cost']
                cost_based_results[linkage_criterion + ' + ' + similarity_measure]['cost_function_calls'] +=\
                    cost_based_result['cost_function_calls']
                # random_based_result = combined_horizontal_from_db(connector, similarity_measure, linkage_criterion, False, queries, False)
                # random_based_results[linkage_criterion + ' + ' + similarity_measure]['cost'] +=random_based_result['cost']
        with open(directory + '/result_' + str(idx) + '.txt', 'w') as f:
            print('COST BASED RESULTS', file=f)
            print(cost_based_results, file=f)
            print('RANDOM BASED RESULTS', file=f)
            print(random_based_results, file=f)

    print('#######################################')
    print('COST BASED RESULTS')
    print(cost_based_results)
    print('RANDOM BASED RESULTS')
    print(random_based_results)
    print('#######################################')


def test_my_similarity():
    connector = PostgresConnector()
    print('######### HAC TEST MY LINKAGE CRITERIA #########')
    get_optimum(connector)
    directory = '../input_data/queries/zhang/10'
    input_files = os.listdir(directory)
    queries_files = [pickle.load(open(directory + '/' + file, 'rb')) for file in input_files]
    cost_based_results = {}
    random_based_results = {}
    for idx, queries in enumerate(queries_files):
        print("INPUTS: {}/{}".format(directory, input_files[idx]))
        if not ('penalty_based' in cost_based_results):
            cost_based_results['penalty_based'] = {
                'cost': 0,
                'cost_function_calls': 0
            }
            random_based_results['penalty_based'] = 0
        cost_based_result = combined_horizontal_from_db(connector, '', 'penalty_based', True, queries, False)
        cost_based_results['penalty_based']['cost'] += cost_based_result['cost']
        cost_based_results['penalty_based']['cost_function_calls'] += \
            cost_based_result['cost_function_calls']
        random_based_results['penalty_based'] += \
            combined_horizontal_from_db(connector, '', 'penalty_based', False, queries, False)['cost']

    print('#######################################')
    print('COST BASED RESULTS')
    print(cost_based_results)
    print('RANDOM BASED RESULTS')
    print(random_based_results)
    print('#######################################')


def test_profiler():
    connector = PostgresConnector()
    print('######### HAC TEST PROFILER SINGLE LINKAGE & EUCLIDEAN DISTANCE #########')
    get_optimum(connector)
    directory = '../input_data/queries/zhang/10'
    input_files = os.listdir(directory)
    queries = pickle.load(open(directory + '/' + input_files[0], 'rb'))
    combined_horizontal_from_db(connector, 'euclidean_distance', 'single_linkage', True, queries, False)


def amount_of_atomic_fragments():
    connector = PostgresConnector()
    percentages = [10, 20, 30, 40, 50, 60, 70]
    results = {percentage: 0 for percentage in percentages}
    for percentage in percentages:
        print("DUPLICATES PERCENTAGE = " + str(percentage))
        directory = '../input_data/queries/zhang/' + str(percentage)
        input_files = os.listdir(directory)
        queries_files = [pickle.load(open(directory + '/' + file, 'rb')) for file in input_files]
        for idx, queries_file in enumerate(queries_files):
            results[percentage] += combined_horizontal_from_db(connector, None, None, True, queries_file, True)
    print(results)

# def test_linkage_criteria(connector, queries_files):
#     print('######### linkage criteria test #########')
#     options = ['single_linkage', 'complete_linkage', 'average_linkage', 'centroid_method', 'centroid_method_rows_amount']
#     results = {}
#     for option in options:
#         results[option] = {
#             'cost': 0,
#             'cost_function_calls': 0
#         }
#         for queries in queries_files:
#             result = combined_horizontal_from_db(connector, 'euclidean_distance', option, queries)
#             results[option]['cost'] += result['cost']
#             results[option]['cost_function_calls'] += result['cost_function_calls']
#     print(results)
#
#
# def test_metrics(connector, queries_files):
#     print('######### metrics test #########')
#     options = ['euclidean_distance', 'squared_euclidean_distance', 'manhattan_distance', 'maximum_distance']
#     results = {}
#     for option in options:
#         results[option] = {
#             'cost': 0,
#             'cost_function_calls': 0
#         }
#         for queries in queries_files:
#             result = combined_horizontal_from_db(connector, option, 'centroid_method_rows_amount', queries)
#             results[option]['cost'] += result['cost']
#             results[option]['cost_function_calls'] += result['cost_function_calls']
#     print(results)


def get_optimum(connector):
    pass


if __name__ == "__main__":
    test_profiler()
