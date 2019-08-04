from unittest import TestCase

from clustering_implementations.combined_horizontal.metrics import euclidean_distance, squared_euclidean_distance, \
    manhattan_distance, maximum_distance


class TestMetrics(TestCase):
    def test_euclidean_distance(self):
        self.assertAlmostEqual(euclidean_distance([0, 0, 1, 1], [1, 0, 1, 0]), 1.4142, 4)

    def test_squared_euclidean_distance(self):
        self.assertAlmostEqual(squared_euclidean_distance([0, 0, 0.25, 1], [1, 0, 1, 0]), 2.5625)

    def test_manhattan_distance(self):
        self.assertEqual(manhattan_distance([0, 0, 0.25, 1], [1, 0, 1, 0]), 2.75)

    def test_maximum_distance(self):
        self.assertEqual(maximum_distance([0, 0, 0.25, 0.5], [0.5, 0, 1, 0]), 0.75)
