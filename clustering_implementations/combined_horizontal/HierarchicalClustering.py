import random
from random import shuffle

import math
import heapq
from itertools import combinations
from copy import deepcopy

from clustering_implementations.MockFragment import MockFragment
from cost_models.hdd_based_adapted import str_to_query_tokens, hdd_based_adapted_cost, BoolNot, BoolAnd, BoolOr, \
    pretokenized_converter
from db.crud.config_queries import drop_table
from db.crud.evaluation_queries import get_plan_costs, drop_statistics, get_partitions_cost
from db.crud.partition_queries import create_partitions, merge_two_partitions, split_partition
from helpers.minimize import minimize
from input_data.queries import queries
from input_data.temp_input_data import table_name, n_clusters
import clustering_implementations.combined_horizontal.linkage_criteria as linkage_criteria


class HierarchicalClustering:
    def __init__(self, points, queries, dimensions, connector, metric, linkage_criterion, cost_model_usage):
        self.dimensions = dimensions
        self.clusters = set(points.keys())
        self.original_dataset = deepcopy(points)
        self.metric = metric
        self.linkage_criterion = linkage_criterion
        self.heap = self.build_priority_queue(self.compute_pairwise_distance())
        self.db_connector = connector
        self.queries = queries
        self.tokenized_queries = [str_to_query_tokens(query) for query in queries]
        self.mock_fragments = {
            cluster: self.create_mock_fragment([self.original_dataset[frozenset({c})]['coordinate'] for c in cluster]) for cluster in self.clusters
        }
        self.cost_model_usage = cost_model_usage

    def create_mock_fragment(self, coordinate):
        subclusters_check_conditions = []
        subclusters_tokens = []
        cluster_queries = minimize(coordinate)
        for subcluster_queries in cluster_queries:
            subcluster_check_conditions = []
            subcluster_tokens = []
            for idx, query in enumerate(subcluster_queries):
                if query != -1:
                    subcluster_tokens.append(
                        self.tokenized_queries[idx] if query else BoolNot(self.tokenized_queries[idx])
                    )
                    subcluster_check_conditions.append(
                        self.queries[idx] if query else '(NOT ' + self.queries[idx] + ')'
                    )
            subclusters_tokens.append(BoolAnd(subcluster_tokens))
            subclusters_check_conditions.append('(' + ' AND '.join(subcluster_check_conditions) + ')')
        subclusters_check_conditions_str = ' OR '.join(subclusters_check_conditions)
        subclusters_check_conditions_tokens = BoolOr(subclusters_tokens)

        return MockFragment(subclusters_check_conditions_str, subclusters_check_conditions_tokens,
                            self.db_connector)

    def get_distance(self, cluster_one, cluster_two):
        linkage_function = getattr(linkage_criteria, self.linkage_criterion)
        return linkage_function(self.original_dataset, (cluster_one, cluster_two), self.metric)

    def compute_pairwise_distance(self):
        result = []
        for cluster1, cluster2 in combinations(self.clusters, 2):
            if cluster1 != cluster2:
                dist = self.get_distance(cluster1, cluster2)
                result.append((dist, (cluster1, cluster2)))
        return result

    def partitioning_scheme_cost(self, fragments):
        cost = 0
        for query in self.tokenized_queries:
            cost += hdd_based_adapted_cost(
                query,
                fragments,
                pretokenized_converter
            )
        return cost

    @staticmethod
    def build_priority_queue(distance_list):
        heapq.heapify(distance_list)
        return distance_list

    def hierarchical_clustering(self):

        print('-----------------------------------------------------------------------')
        print('HIERARCHICAL CLUSTERING ALGORITHM')
        print('-----------------------------------------------------------------------')

        cost_function_calls = 0  # additional measure


        # create_partitions(self.db_connector,
        #                   {k: [v['coordinate']] for k, v in self.original_dataset.items()},
        #                   table_name + '_copy')

        if len(self.clusters) <= n_clusters:
            raise Exception('Number of input clusters is too small')

        else:
            while len(self.clusters) > n_clusters:
                print('***********************************************************************')
                print('STEP ', len(self.original_dataset.items()) - len(self.clusters) + 1)
                clusters_pairs = []

                while not clusters_pairs:
                    min_dist, _ = heapq.nsmallest(1, self.heap)[0]

                    while len(self.heap):
                        new_dist, new_dist_clusters = heapq.heappop(self.heap)
                        if new_dist == min_dist:
                            if new_dist_clusters[0] in self.clusters and new_dist_clusters[1] in self.clusters:
                                clusters_pairs.append((new_dist, new_dist_clusters))
                        else:
                            heapq.heappush(self.heap, (new_dist, new_dist_clusters))
                            break
                if self.cost_model_usage:
                    min_cost = 0
                    min_cost_pair_idx = 0
                    for idx, (_, pair) in enumerate(clusters_pairs):
                        # merge_two_partitions(
                        #     self.db_connector,
                        #     table_name + '_copy',
                        #     (
                        #         (pair[0], [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[0]]),
                        #         (pair[1], [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[1]])
                        #     )
                        # )
                        # drop_statistics(self.db_connector)
                        # cost = get_partitions_cost(self.db_connector, table_name + '_copy')
                        fragment_to_merge_one = self.mock_fragments.pop(pair[0])
                        fragment_to_merge_two = self.mock_fragments.pop(pair[1])
                        # mock_fragmets = []
                        # for cluster in self.clusters:
                        #     if not (cluster == pair[0] or cluster == pair[1]):
                        #         mock_fragmets.append(self.create_mock_fragment([self.original_dataset[frozenset({c})]['coordinate'] for c in cluster]))
                        new_fragment = self.create_mock_fragment(
                            [self.original_dataset[frozenset({c})]['coordinate'] for c in pair[0].union(pair[1])])
                        cost = self.partitioning_scheme_cost(list(self.mock_fragments.values()) + [new_fragment])
                        cost_function_calls += len(self.tokenized_queries)

                        if cost < min_cost or not min_cost:
                            min_cost = cost
                            min_cost_pair_idx = idx

                        self.mock_fragments[pair[0]] = fragment_to_merge_one
                        self.mock_fragments[pair[1]] = fragment_to_merge_two
                        # split_partition(
                        #     self.db_connector,
                        #     table_name + '_copy',
                        #     {
                        #         pair[0]: [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[0]],
                        #         pair[1]: [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[1]]
                        #     })
                else:
                    min_cost_pair_idx = random.randrange(0, len(clusters_pairs))
                cluster_to_merge_one = clusters_pairs[min_cost_pair_idx][1][0]
                cluster_to_merge_two = clusters_pairs[min_cost_pair_idx][1][1]

                # push values back to the heap
                for idx, (cost, pair) in enumerate(clusters_pairs):
                    if idx != min_cost_pair_idx:
                        heapq.heappush(self.heap, (cost, pair))

                self.clusters.remove(cluster_to_merge_one)
                self.clusters.remove(cluster_to_merge_two)

                new_cluster_id = cluster_to_merge_one.union(cluster_to_merge_two)

                for cluster in self.clusters:
                    heapq.heappush(self.heap, (self.get_distance(cluster, new_cluster_id),
                                               (cluster, new_cluster_id)))

                self.clusters.add(new_cluster_id)

                del self.mock_fragments[cluster_to_merge_one]
                del self.mock_fragments[cluster_to_merge_two]
                self.mock_fragments[new_cluster_id] = self.create_mock_fragment(
                        [
                            self.original_dataset[frozenset({c})]['coordinate']
                            for c in cluster_to_merge_one.union(cluster_to_merge_two)
                        ]
                )

                # merge_two_partitions(
                #     self.db_connector,
                #     table_name + '_copy',
                #     (
                #         (cluster_to_merge_one, [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in
                #                                 cluster_to_merge_one]),
                #         (cluster_to_merge_two, [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in
                #                                 cluster_to_merge_two])
                #     )
                # )
                print('new clusters ', self.clusters)
                new_cost = self.partitioning_scheme_cost(list(self.mock_fragments.values()))
                print('new cost ', new_cost)
            # plan_cost = get_partitions_cost(self.db_connector, table_name + '_copy')
            # drop_table(self.db_connector, table_name + '_copy')
            print('***********************************************************************')
            print('RESULT ')
            mock_fragmets = []
            for cluster in self.clusters:
                mock_fragmet = self.create_mock_fragment(
                        [self.original_dataset[frozenset({c})]['coordinate'] for c in cluster])
                print(mock_fragmet.where_clause)
                mock_fragmets.append(mock_fragmet)
            return {'cost': new_cost, 'cost_function_calls': cost_function_calls}
