import itertools
from collections import defaultdict

from clustering_implementations.MockFragment import MockFragment
from cost_models.hdd_based_adapted import hdd_based_adapted_cost, str_to_query_tokens
from input_data.queries import queries
from input_data.temp_input_data import n_clusters


def print_matrix(matrix):
    for row in matrix:
        for elem in row:
            print('{0: < 4}'.format(elem), end=' ')
        print()


def form_fragment(predicates, input_predicates, connector):
    unique_columns = defaultdict(list)
    for predicate in predicates:
        unique_columns[input_predicates[predicate][0]].append('{} {} {}'.format(*input_predicates[predicate]))

    # [
    #     MockFragment("l_linenumber > 5"),
    #     MockFragment("l_linenumber <= 5")
    # ]
    # )

    return MockFragment(' AND '.join(['(' + ' OR '.join(column) + ')' for column in unique_columns.values()]), connector)


def form_negation_fragment(fragments, connector):
    return MockFragment('NOT (' + ' OR '.join('(' + str(fragment) + ')' for fragment in fragments) + ')', connector)


def zhang(frequencies, input_predicates, predicate_usage, connector):
    print('-----------------------------------------------------------------------')
    print('ZHANG ALGORITHM')
    print('-----------------------------------------------------------------------')
    print('input data')
    print('frequencies: ', frequencies)
    print('predicates usage: ')
    print_matrix(predicate_usage)

    print('***********************************************************************')
    print('STEP 1: predicates usage matrix generation')
    predicate_affinity = [[0] * len(input_predicates) for _ in input_predicates]
    for t_idx, transaction in enumerate(predicate_usage):
        # combinations - if we don't want to have values along the diagonal
        # combinations_with_replacement - otherwise
        for i, j in itertools.combinations_with_replacement(transaction, 2):
            predicate_affinity[i][j] += frequencies[t_idx]
            predicate_affinity[j][i] = predicate_affinity[i][j]

    print('result: ')
    print_matrix(predicate_affinity)

    print('***********************************************************************')
    print('STEP 2: permutation of columns')
    ordered_predicates = [0]
    unordered_predicates = list(range(1, len(input_predicates)))

    # mccormic
    # ordered_predicates = [0]
    # unordered_predicates = list(range(1, predicates_amount))
    #
    # while unordered_predicates:
    #     best_global_affinity_measure = -1
    #     best_position = 0
    #     for predicate in unordered_predicates:
    #         for place in range(len(ordered_predicates) + 1):
    #             modified_ordered_predicates = ordered_predicates[:]
    #             modified_ordered_predicates.insert(place, predicate)
    #             global_affinity_measure = 0
    #             for column_idx, column in enumerate(modified_ordered_predicates):
    #                 for row in range(predicates_amount):
    #                     prev_in_row = 0 if column_idx == 0 else predicate_affinity[row][
    #                         modified_ordered_predicates[column_idx - 1]]
    #                     next_in_row = 0 if column_idx == len(ordered_predicates) else predicate_affinity[row][
    #                         modified_ordered_predicates[column_idx - 1]]
    #                     global_affinity_measure += predicate_affinity[row][column] * (
    #                                 prev_in_row + next_in_row)
    #             if global_affinity_measure >= best_global_affinity_measure:
    #                 best_global_affinity_measure = global_affinity_measure
    #                 best_position = (place, predicate)
    #     ordered_predicates.insert(best_position[0], best_position[1])
    #     unordered_predicates.remove(best_position[1])
    #
    # print("best", ordered_predicates)
    # print_matrix([[predicate_affinity[i][j] for j in ordered_predicates] for i in ordered_predicates])

    # oszu presentation full summ
    for predicate in range(1, len(input_predicates)):
        best_global_affinity_measure = 0
        best_position = 0
        for place in range(len(ordered_predicates) + 1):
            modified_ordered_predicates = ordered_predicates[:]
            modified_ordered_predicates.insert(place, predicate)
            global_affinity_measure = 0
            for column_idx, column in enumerate(modified_ordered_predicates):
                for row in range(len(input_predicates)):
                    prev_in_row = 0 if column_idx == 0 else predicate_affinity[row][
                        modified_ordered_predicates[column_idx - 1]]
                    next_in_row = 0 if column_idx == len(ordered_predicates) else predicate_affinity[row][
                        modified_ordered_predicates[column_idx - 1]]
                    global_affinity_measure += predicate_affinity[row][column] * (
                                prev_in_row + next_in_row)
            if global_affinity_measure >= best_global_affinity_measure:
                best_global_affinity_measure = global_affinity_measure
                best_position = place
        ordered_predicates.insert(best_position, predicate)
    # oszu presentation local sum
    # for column in range(predicates_amount):
    #     best_global_affinity_measure = 0
    #     best_position = 0
    #     for place in range(len(ordered_predicates) + 1):
    #         global_affinity_measure = 0
    #         for row in range(predicates_amount):
    #             prev_in_row = 0 if place == 0 else predicate_affinity[row][ordered_predicates[place - 1]]
    #             next_in_row = 0 if place == len(ordered_predicates) else predicate_affinity[row][
    #                 ordered_predicates[place]]
    #             global_affinity_measure += predicate_affinity[row][column] * (
    #                         prev_in_row + next_in_row)
    #         if global_affinity_measure > best_global_affinity_measure:
    #             best_global_affinity_measure = global_affinity_measure
    #             best_position = place
    #     ordered_predicates.insert(best_position, column)

    # exhaustive search
    # for permutation in itertools.permutations(range(predicates_amount)):
    #     global_affinity_measure = 0
    #     for row_predicate in permutation:
    #         for column_idx, column_predicate in enumerate(permutation):
    #             prev_in_row = 0 if column_idx == 0 else predicate_affinity[row_predicate][permutation[column_idx - 1]]
    #             next_in_row = 0 if column_idx == len(permutation) - 1 else predicate_affinity[row_predicate][
    #                 permutation[column_idx + 1]]
    #             global_affinity_measure += predicate_affinity[row_predicate][column_predicate] * (
    #                     prev_in_row + next_in_row)
    #     if global_affinity_measure > best_global_affinity_measure:
    #         best_global_affinity_measure = global_affinity_measure
    #         best_permutation = permutation

    print('results: ')
    print('1) ordered predicates', ordered_predicates)
    print('2) permuted matrix')
    print_matrix([[predicate_affinity[i][j] for j in ordered_predicates] for i in ordered_predicates])

    print('***********************************************************************')
    print('STEP 3: slip - non - overlap')
    # # slip - non - overlap by navathe / binary partitioning
    # best_split = []
    # best_cost = None
    # for order in range(len(ordered_predicates)):
    #     ordered_predicates += [ordered_predicates.pop(0)]
    #     for split_point in range(1, len(ordered_predicates)):
    #         cu = 0
    #         cl = 0
    #         ci = 0
    #         for i, predicates in enumerate(predicate_usage):
    #             ut_flag = False
    #             lt_flag = False
    #             for u in predicates:
    #                 if u in ordered_predicates[:split_point]:
    #                     ut_flag = True
    #                 if u in ordered_predicates[split_point:]:
    #                     lt_flag = True
    #             if ut_flag and lt_flag:
    #                 ci += frequencies[i]
    #             elif ut_flag:
    #                 cu += frequencies[i]
    #             else:
    #                 cl += frequencies[i]
    #         cost = cl * cu - ci * ci
    #         if best_cost is None or cost > best_cost:
    #             best_cost = cost
    #             best_split = [ordered_predicates[:split_point], ordered_predicates[split_point:]]

    # # slip - non - overlap with custom cost function & m-random points
    # best_split = []
    # best_cost = None
    # for order in range(len(ordered_predicates)):
    #     ordered_predicates += [ordered_predicates.pop(0)]
    #     print('ordered_predicates', ordered_predicates)
    #     for split_points in itertools.combinations(range(1, len(input_predicates)), n_clusters - 2):
    #         sets = [form_fragment(ordered_predicates[(split_points[idx - 1] if idx else 0): split_points[idx]],
    #                               input_predicates, connector) for idx in range(len(split_points))] + [
    #             form_fragment(ordered_predicates[split_points[-1]:], input_predicates, connector)
    #         ]
    #         # negation of conjunction of fragment predicates
    #         sets += [form_negation_fragment(sets, connector)]
    #         cost = 0
    #         for query in queries:
    #             cost += hdd_based_adapted_cost(str_to_query_tokens(' AND '.join([' '.join(i) for i in query])), sets)
    #         if best_cost is None or cost < best_cost:
    #             print('local best', cost, split_points, ordered_predicates, [str(fragment) for fragment in sets])
    #             best_cost = cost
    #             best_split = sets
    #
    # print('results: ')
    # print('best cost', best_cost)
    # print('best split', [str(fragment) for fragment in best_split])

    # return best_cost
