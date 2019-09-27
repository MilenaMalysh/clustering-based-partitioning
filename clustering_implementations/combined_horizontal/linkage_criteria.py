import clustering_implementations.combined_horizontal.metrics as metrics
from input_data.temp_input_data import n_queries


def single_linkage(clusters, clusters_to_merge, metric):
    min_dist = 0.0
    for cluster_id1 in clusters_to_merge[0]:
        for cluster_id2 in clusters_to_merge[1]:
            metric_function = getattr(metrics, metric)
            dist = metric_function(clusters[frozenset({cluster_id1})]['coordinate'],
                                   clusters[frozenset({cluster_id2})]['coordinate'])
            if dist < min_dist or not min_dist:
                min_dist = dist
    return min_dist


def complete_linkage(clusters, clusters_to_merge, metric):
    max_dist = 0.0
    for cluster_id1 in clusters_to_merge[0]:
        for cluster_id2 in clusters_to_merge[1]:
            metric_function = getattr(metrics, metric)
            dist = metric_function(clusters[frozenset({cluster_id1})]['coordinate'],
                                   clusters[frozenset({cluster_id2})]['coordinate'])
            if dist > max_dist:
                max_dist = dist
    return max_dist


def average_linkage(clusters, clusters_to_merge, metric):
    dist_sum = 0.0
    for cluster_id1 in clusters_to_merge[0]:
        for cluster_id2 in clusters_to_merge[1]:
            metric_function = getattr(metrics, metric)
            dist = metric_function(clusters[frozenset({cluster_id1})]['coordinate'],
                                   clusters[frozenset({cluster_id2})]['coordinate'])
            dist_sum += dist
    return dist_sum * 1 / (len(clusters_to_merge[0]) * len(clusters_to_merge[1]))


def centroid_method(clusters, clusters_to_merge, metric):
    dimensionality = len(list(clusters.values())[0]['coordinate'])
    cluster1_centroid = []
    cluster2_centroid = []

    for dimension in range(dimensionality):
        coord_sum = 0.0
        for cluster_id in clusters_to_merge[0]:
            coord_sum += clusters[frozenset({cluster_id})]['coordinate'][dimension]
        cluster1_centroid.append(coord_sum / len(clusters_to_merge[0]))

        coord_sum = 0.0
        for cluster_id in clusters_to_merge[1]:
            coord_sum += clusters[frozenset({cluster_id})]['coordinate'][dimension]
        cluster2_centroid.append(coord_sum / len(clusters_to_merge[1]))
    metric_function = getattr(metrics, metric)
    dist = metric_function(cluster1_centroid, cluster2_centroid)
    return dist


def centroid_method_rows_amount(clusters, clusters_to_merge, metric):
    dimensionality = len(list(clusters.values())[0]['coordinate'])
    cluster1_centroid = []
    cluster2_centroid = []

    for dimension in range(dimensionality):
        coord_sum = 0.0
        rows_sum = 0
        for cluster_id in clusters_to_merge[0]:
            coord_sum += clusters[frozenset({cluster_id})]['coordinate'][dimension] *\
                         clusters[frozenset({cluster_id})]['rows_amount']
            rows_sum += clusters[frozenset({cluster_id})]['rows_amount']
        cluster1_centroid.append(coord_sum / rows_sum)

        coord_sum = 0.0
        rows_sum = 0
        for cluster_id in clusters_to_merge[1]:
            coord_sum += clusters[frozenset({cluster_id})]['coordinate'][dimension] *\
                         clusters[frozenset({cluster_id})]['rows_amount']
            rows_sum += clusters[frozenset({cluster_id})]['rows_amount']
        cluster2_centroid.append(coord_sum / rows_sum)
    metric_function = getattr(metrics, metric)
    dist = metric_function(cluster1_centroid, cluster2_centroid)
    return dist


def difference_based(clusters, clusters_to_merge, metric):
    difference_count = 0
    total_rows = 0

    for cluster_id in clusters_to_merge[0].union(clusters_to_merge[1]):
        total_rows += clusters[frozenset({cluster_id})]['rows_amount']

    for dimension in range(n_queries):
        coord = clusters[frozenset({list(clusters_to_merge[0])[0]})]['coordinate'][dimension]
        for cluster_id in clusters_to_merge[0].union(clusters_to_merge[1]):
            if clusters[frozenset({cluster_id})]['coordinate'][dimension] != coord:
                difference_count += 1
                break
    return difference_count * total_rows


def penalty_based(clusters, clusters_to_merge, metric):
    penalty = 0
    new_atomic_fragments = clusters_to_merge[0].union(clusters_to_merge[1])
    for dimension in range(n_queries):
        dimension_coordinates = [clusters[frozenset({cluster_id})]['coordinate'][dimension] for cluster_id in new_atomic_fragments]
        if len(set(dimension_coordinates)) == 2:
            for cluster_id in new_atomic_fragments:
                if not clusters[frozenset({cluster_id})]['coordinate'][dimension]:
                    penalty += clusters[frozenset({cluster_id})]['rows_amount']
    return penalty
