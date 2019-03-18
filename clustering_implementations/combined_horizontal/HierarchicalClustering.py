import math
import heapq
from itertools import combinations
from copy import deepcopy

from db.crud.evaluation_queries import get_query_cost_on_partitions
from db.crud.partition_queries import create_list_partition, drop_partitions, create_list_partition_column
from input_data.queries import queries


class HierarchicalClustering:
    def __init__(self, points, clusters_amount, dimensions, connector, cluster_id_col_name):
        self.clusters_amount = clusters_amount
        self.dimensions = dimensions
        self.clusters = points
        self.original_dataset = deepcopy(points)
        self.heap = self.build_priority_queue(self.compute_pairwise_distance())
        self.db_connector = connector
        self.cluster_id_col_name = cluster_id_col_name

    def merged_clusters_coordinates(self, coord1, coord2, rows_amount1, rows_amount2):
        new_coord = []
        for i in range(self.dimensions):
            new_coord.append((coord1[i] * rows_amount1 + coord2[i] * rows_amount2) / (rows_amount1 + rows_amount2))
        return new_coord

    def euclidean_distance(self, data_point_one, data_point_two):
        result = 0.0
        for i in range(self.dimensions):
            f1 = float(data_point_one[i])
            f2 = float(data_point_two[i])
            tmp = f1 - f2
            result += pow(tmp, 2)
        result = math.sqrt(result)
        return result

    def compute_pairwise_distance(self):
        result = []
        for (cluster_id1, cluster1_data), (cluster_id2, cluster2_data) in combinations(self.clusters.items(), 2):
            if cluster_id1 != cluster_id2:
                dist = self.euclidean_distance(cluster1_data['coordinate'], cluster2_data['coordinate'])
                result.append((dist, (cluster_id1, cluster_id2)))
        return result

    def build_priority_queue(self, distance_list):
        heapq.heapify(distance_list)
        self.heap = distance_list
        return self.heap

    def clusters_cost(self):
        costs = 0
        for query_idx in range(len(queries)):
            clusters_touched = []
            for cluster, cluster_data in self.original_dataset.items():
                if cluster_data['coordinate'][query_idx]:
                    clusters_touched.append(str(*cluster))
            costs += get_query_cost_on_partitions(self.db_connector, self.cluster_id_col_name, clusters_touched)
        return costs

    def merge_clusters_db_cost(self, merge_clusters):
        create_list_partition_column(self.db_connector, self.cluster_id_col_name)
        for cluster in self.clusters.keys():
            if not merge_clusters or (cluster != merge_clusters[0] and cluster != merge_clusters[1]):
                create_list_partition(self.db_connector, cluster)
        if merge_clusters:
            create_list_partition(self.db_connector, merge_clusters[0].union(merge_clusters[1]))
        costs = self.clusters_cost()
        drop_partitions(self.db_connector)
        return costs

    def hierarchical_clustering(self):

        print('cost before clustering(1 cluster): ', self.clusters_cost())
        print('cost before clustering(all clusters): ', self.merge_clusters_db_cost(()))

        min_cost = 0

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


            min_cost = self.merge_clusters_db_cost(clusters_pairs[0][1])
            min_cost_pair_idx = 0
            # if we use real db
            if self.cluster_id_col_name:
                for idx, (_, pair) in enumerate(clusters_pairs[1:]):
                    cost = self.merge_clusters_db_cost(pair)
                    if cost < min_cost:
                        min_cost = cost
                        min_cost_pair_idx = idx


            # push values back to the heap
            for idx, (cost, pair) in enumerate(clusters_pairs):
                if idx != min_cost_pair_idx:
                    heapq.heappush(self.heap, (cost, pair))

            cluster1 = self.clusters.pop(clusters_pairs[min_cost_pair_idx][1][0])
            cluster2 = self.clusters.pop(clusters_pairs[min_cost_pair_idx][1][1])

            new_cluster_id = clusters_pairs[min_cost_pair_idx][1][0].union(clusters_pairs[min_cost_pair_idx][1][1])
            new_cluster_coordinate = self.merged_clusters_coordinates(cluster1['coordinate'], cluster2['coordinate'],
                                                                      cluster1['rows_amount'], cluster2['rows_amount'])

            for cluster_id, cluster_data in self.clusters.items():
                heapq.heappush(self.heap, (self.euclidean_distance(cluster_data['coordinate'], new_cluster_coordinate),
                                           (cluster_id, new_cluster_id)))

            self.clusters[new_cluster_id] = {
                'coordinate': new_cluster_coordinate,
                'rows_amount': cluster1['rows_amount'] + cluster2['rows_amount']
            }
            print('step', len(self.original_dataset) - len(self.clusters), ' cost: ', min_cost)
        return min_cost

