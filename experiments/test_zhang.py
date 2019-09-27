import os
import pickle
from unittest import TestCase

from clustering_implementations.classical_algorithms.zhang import zhang
from db.PostgresConnector import PostgresConnector
from input_data.queries import queries
#
# """
# example of input data for vertical partitioning from
# Y.Zhang and M.E.Orlowska, On fragmentation approaches for distributed database design, 1994
# """
#
#
# def test_vertical():
#     frequencies = [25, 50, 25, 35, 25, 25, 25, 15]  # vertical fragmentation
#     predicates_amount = 10
#     predicate_usage = [
#         [0, 4, 6],
#         [1, 2, 7, 8],
#         [3, 5, 9],
#         [1, 6, 7],
#         [0, 1, 2, 4, 6, 7, 8],
#         [0, 4],
#         [2, 8],
#         [2, 3, 5, 8, 9]
#     ]
#     zhang(frequencies, predicates_amount, predicate_usage)
#
#
# """
# example of input data for horizontal partitioning from
# Y.Zhang and M.E.Orlowska, On fragmentation approaches for distributed database design, 1994
# """
#
#
# def test_horizontal():
#     frequencies = [25, 50, 25, 35, 25, 25, 25]  # horizontal fragmentation
#     predicates_amount = 9
#     predicate_usage = [
#         [0, 2, 5],
#         [1, 2],
#         [2, 3],
#         [4, 5, 8],
#         [5, 6, 8],
#         [5, 7, 8],
#         [2, 6]
#     ]
#     # intermediate results after aa matrix generation differ from those provided in the paper
#     # predicate_affinity = [
#     #     [0, 0, 25, 0, 0, 25, 0, 0, 0],
#     #     [0, 0, 50, 0, 0, 0, 0, 0, 0],
#     #     [25, 50, 0, 25, 0, 25, 25, 0, 0],
#     #     [0, 0, 25, 0, 0, 0, 0, 0, 0],
#     #     [0, 0, 0, 0, 0, 35, 0, 0, 35],
#     #     [25, 0, 25, 0, 35, 85, 25, 25, 85],
#     #     [0, 0, 25, 0, 0, 25, 0, 0, 25],
#     #     [0, 0, 0, 0, 0, 25, 0, 0, 0],
#     #     [0, 0, 0, 0, 35, 85, 25, 0, 0]
#     # ]
#     zhang(frequencies, predicates_amount, predicate_usage)
#
from input_data.temp_input_data import n_queries, n_predicates_per_query

"""
my example for thesis
"""


def test_my_values():
    print('-----------------------------------------------------------------------')
    print('ZHANG ALGORITHM TESTS')
    print('-----------------------------------------------------------------------')
    predicates_amount = 9
    frequencies = [1] * 9
    predicate_usage = [[] for _ in queries]
    predicates = list(set().union(*queries))
    for predicate_idx, predicate in enumerate(predicates):
        for query_idx, query in enumerate(queries):
            if predicate in query:
                predicate_usage[query_idx].append(predicate_idx)
    zhang(frequencies, predicates, predicate_usage, PostgresConnector())

    # predicates_amount = 9
    # predicate_usage = [
    #     [1, 2, 7],
    #     [0, 5, 7, 8],
    #     [3, 4, 6, 8],
    #     [1, 2, 3, 6],
    #     [0, 8],
    #     [6, 7, 8]
    # ]
    # frequencies = [5, 20, 20, 15, 10, 10]  # my example
    # predicates_amount = 11
    # predicate_usage = [
    #     [1, 2, 9],
    #     [0, 5, 7, 9, 10],
    #     [3, 4, 6, 8, 10],
    #     [1, 2, 4, 8],
    #     [0, 10],
    #     [3, 8, 9, 10]
    # ]

    # print('-----------------------------------------------------------------------')
    # print('EXPERIMENT RESULTS')
    # print('cost ', cost / len(queries_files))
    # print('cost model calls ', cost_model_calls / len(queries_files))
    # print('-----------------------------------------------------------------------')


def test_different_duplicates_percentage():
    print('ZHANG ALGORITHM <DIFFERENT DUPLICATES PERCENTAGE TESTS>')
    percentages = [10, 20, 30, 40, 50, 60, 70]
    results = {}
    for percentage in percentages:
        print("DUPLICATES PERCENTAGE = " + str(percentage))
        directory = '../input_data/queries/zhang/' + str(percentage)
        input_files = os.listdir(directory)
        queries_files = [pickle.load(open(directory + '/' + file, 'rb')) for file in input_files]
        cost_model_calls = 0
        cost = 0
        for queries_file in queries_files:
            predicate_usage = [[] for _ in queries_file]
            predicates = list(set().union(*queries_file))
            for predicate_idx, predicate in enumerate(predicates):
                for query_idx, query in enumerate(queries_file):
                    if predicate in query:
                        predicate_usage[query_idx].append(predicate_idx)
            result = zhang([1] * len(queries_file), predicates, predicate_usage, queries_file, PostgresConnector())
            cost_model_calls += result['cost_model_calls']
            cost += result['cost']
        results[percentage] = {
            'cost model calls': cost_model_calls,
            'cost': cost
        }
        with open(directory + '\../result_' + str(percentage) + '.txt', 'w') as f:
            print(results, file=f)
    print('ZHANG ALGORITHM <DIFFERENT DUPLICATES PERCENTAGE TESTS> RESULTS: ', results)


if __name__ == "__main__":
    print('-----------------------------------------------------------------------')
    print('ZHANG ALGORITHM TESTS')
    print('-----------------------------------------------------------------------')
    test_different_duplicates_percentage()