from unittest import TestCase

from clustering_implementations.combined_horizontal.linkage_criteria import single_linkage, complete_linkage, \
    average_linkage, centroid_method, centroid_method_rows_amount


class TestLinkage(TestCase):
    def test_single_linkage(self):
        clusters = {
            frozenset({0}): {'coordinate': [0, 0, 0, 0]},
            frozenset({1}): {'coordinate': [0, 0, 1, 0]},
            frozenset({2}): {'coordinate': [0, 0, 1, 1]}
        }
        clusters_to_merge = (frozenset({0}), frozenset({1, 2}))
        metric = 'manhattan_distance'
        self.assertEqual(single_linkage(clusters, clusters_to_merge, metric), 1.0)

    def test_complete_linkage(self):
        clusters = {
            frozenset({0}): {'coordinate': [0, 0, 0, 0]},
            frozenset({1}): {'coordinate': [0, 0, 1, 0]},
            frozenset({2}): {'coordinate': [0, 0, 1, 1]}
        }
        clusters_to_merge = (frozenset({0}), frozenset({1, 2}))
        metric = 'manhattan_distance'
        self.assertEqual(complete_linkage(clusters, clusters_to_merge, metric), 2.0)

    def test_average_linkage(self):
        clusters = {
            frozenset({0}): {'coordinate': [0, 0, 0, 0]},
            frozenset({1}): {'coordinate': [0, 0, 1, 0]},
            frozenset({2}): {'coordinate': [0, 0, 1, 1]}
        }
        clusters_to_merge = (frozenset({0}), frozenset({1, 2}))
        metric = 'manhattan_distance'
        self.assertEqual(average_linkage(clusters, clusters_to_merge, metric), 1.5)

    def test_centroid_linkage(self):
        clusters = {
            frozenset({0}): {'coordinate': [1, 1, 1, 1]},
            frozenset({1}): {'coordinate': [0, 1, 0, 0]},
            frozenset({2}): {'coordinate': [0, 0, 0, 1]}
        }
        clusters_to_merge = (frozenset({0}), frozenset({1, 2}))
        metric = 'manhattan_distance'
        self.assertEqual(centroid_method(clusters, clusters_to_merge, metric), 3.0)

    def test_centroid_rows_amount_linkage(self):
        clusters = {
            frozenset({0}): {'coordinate': [1, 1, 1, 1], 'rows_amount': 21380},
            frozenset({1}): {'coordinate': [0, 1, 0, 1], 'rows_amount': 3},
            frozenset({2}): {'coordinate': [0, 0, 1, 0], 'rows_amount': 2}
        }
        clusters_to_merge = (frozenset({0}), frozenset({1, 2}))
        metric = 'manhattan_distance'
        self.assertEqual(centroid_method_rows_amount(clusters, clusters_to_merge, metric), 2.4)
