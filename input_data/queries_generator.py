import datetime
import math
import os
import pickle
import random
from collections import defaultdict

from db.PostgresConnector import PostgresConnector
from db.crud.select_queries import select_ordered_values, select_count, select_column_type
from input_data.temp_input_data import range_columns, n_rows, n_queries, n_predicates_per_query, duplicates_percentage

directory = os.environ['QUERIES_DIRECTORY'] + str(int(duplicates_percentage * 100))


def generate_attributes_distribution(connector):
    """
    This function is used only once to generate 30% - 80% intervals of distribution for each attribute
    """

    # intervals = {}
    # for column in range_columns:
    #     column_values = select_ordered_values(connector, column)
    #     min_value = column_values[math.floor(0.3 * n_rows)][0]
    #     max_value = column_values[math.floor(0.7 * n_rows)][0]
    #     intervals[column] = [min_value, max_value]
    # print(intervals)

    # for column, ranges in range_columns.items():
    #     if isinstance(ranges[0], datetime.date):
    #         start = select_count(connector, [column + ' <= \'' + str(ranges[0]) + '\''])
    #         middle = select_count(connector, [
    #             column + ' > \'' + str(ranges[0]) + '\' AND ' + column + ' < \'' + str(ranges[1]) + '\''])
    #         end = select_count(connector, [column + ' >= \'' + str(ranges[1]) + '\''])
    #     else:
    #         start = select_count(connector, [column + ' <= ' + str(ranges[0])])
    #         middle = select_count(connector,
    #                               [column + ' > ' + str(ranges[0]) + ' AND ' + column + ' < ' + str(ranges[1])])
    #         end = select_count(connector, [column + ' >= ' + str(ranges[1])])
    #     print(start / n_rows, middle / n_rows, end / n_rows)


def generate_queries(connector):
    # step 1: generating simple predicates without repetitions
    predicates_set = defaultdict(list)
    columns_set = list(range_columns.keys())
    unique_predicates_amount = n_queries * n_predicates_per_query - math.floor(n_queries * n_predicates_per_query * duplicates_percentage)
    predicates_counter = 0
    while unique_predicates_amount != predicates_counter:
        column = random.choice(columns_set)
        if isinstance(range_columns[column][0], int):
            bound_value = random.randrange(range_columns[column][0], range_columns[column][1])
        elif isinstance(range_columns[column][0], float):
            bound_value = random.uniform(range_columns[column][0], range_columns[column][1])
        else:
            bound_value = "'" + str(range_columns[column][0] + (range_columns[column][1] - range_columns[column][0]) * random.random()) + "'"
        operator = '<' if random.choice([True, False]) else '>='
        bounds = [predicate[2] for predicate in predicates_set[column]]
        if bound_value in bounds:
            continue
        predicates_counter += 1
        predicates_set[column].append((column, operator, bound_value))
        columns_set.remove(column)
        if not len(columns_set):
            columns_set = list(range_columns.keys())

    # step 2: generate duplicates
    for _ in range(math.floor(n_queries * n_predicates_per_query * duplicates_percentage)):
        column = random.choice(list(predicates_set.keys()))
        predicate = random.choice(predicates_set[column])
        predicates_set[column].append(predicate)

    # step 3: distribution of predicates over the queries:
    queries = [[] for _ in range(n_queries)]
    for column, predicates in predicates_set.items():
        for predicate in predicates:
            min_length = len(min(queries, key=len))
            candidates_queries = [query_idx for query_idx, query in enumerate(queries)
                                  if len(query) == min_length and predicate[0] not in [p[0] for p in query]
                                  ]
            queries[random.choice(candidates_queries)].append(predicate)

    # checks (just to be sure)
    for query in queries:
        columns = [predicate[0] for predicate in query]
        if len(columns) != len(set(columns)):
            assert len(columns) == len(set(columns)), 'there are several predicates on the same column in one query'
            return

    # write to a file
    os.makedirs(directory, exist_ok=True)
    files_in_directory = os.listdir(directory)
    file_to_create = 0
    if files_in_directory:
        file_to_create = max([int(file_name) for file_name in files_in_directory]) + 1
    with open(directory + '/' + str(file_to_create), 'wb') as fp:
        pickle.dump(queries, fp)

if __name__ == "__main__":
    connector = PostgresConnector()
    generate_queries(connector)
