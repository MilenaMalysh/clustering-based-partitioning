from random import shuffle

import math
import heapq
from itertools import combinations
from copy import deepcopy

from db.crud.config_queries import drop_table
from db.crud.evaluation_queries import get_plan_costs, drop_statistics, get_partitions_cost
from db.crud.partition_queries import create_partitions, merge_two_partitions, split_partition
from input_data.queries import queries
from input_data.temp_input_data import table_name
import clustering_implementations.combined_horizontal.linkage_criteria as linkage_criteria


class HierarchicalClustering:
    def __init__(self, points, clusters_amount, dimensions, connector, metric, linkage_criterion):
        self.clusters_amount = clusters_amount
        self.dimensions = dimensions
        self.clusters = set(points.keys())
        self.original_dataset = deepcopy(points)
        self.metric = metric
        self.linkage_criterion = linkage_criterion
        self.heap = self.build_priority_queue(self.compute_pairwise_distance())
        self.db_connector = connector

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

    @staticmethod
    def build_priority_queue(distance_list):
        heapq.heapify(distance_list)
        return distance_list

    def hierarchical_clustering(self):

        create_partitions(self.db_connector,
                          {k: [v['coordinate']] for k, v in self.original_dataset.items()},
                          table_name + '_copy')

        if len(self.clusters) <= self.clusters_amount:
            raise Exception('Number of input clusters is too small')

        else:
            while len(self.clusters) > self.clusters_amount:
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
                min_cost = 0
                min_cost_pair_idx = 0
                for idx, (_, pair) in enumerate(clusters_pairs):
                    merge_two_partitions(
                        self.db_connector,
                        table_name + '_copy',
                        (
                            (pair[0], [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[0]]),
                            (pair[1], [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[1]])
                        )
                    )
                    drop_statistics(self.db_connector)
                    cost = get_partitions_cost(self.db_connector, table_name + '_copy')
                    if cost < min_cost or not min_cost:
                        min_cost = cost
                        min_cost_pair_idx = idx
                    split_partition(
                        self.db_connector,
                        table_name + '_copy',
                        {
                            pair[0]: [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[0]],
                            pair[1]: [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in pair[1]]
                        })

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

                merge_two_partitions(
                    self.db_connector,
                    table_name + '_copy',
                    (
                        (cluster_to_merge_one, [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in
                                                cluster_to_merge_one]),
                        (cluster_to_merge_two, [self.original_dataset[frozenset({cluster})]['coordinate'] for cluster in
                                                cluster_to_merge_two])
                    )
                )
            plan_cost = get_partitions_cost(self.db_connector, table_name + '_copy')
            drop_table(self.db_connector, table_name + '_copy')
            return plan_cost
