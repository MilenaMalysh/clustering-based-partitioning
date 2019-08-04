from unittest import TestCase

from experiments.utils.generate_clusters import generate_clusters


class TestGenerateClusters(TestCase):
    def test_generate_clusters(self):
        print(len(generate_clusters(list(range(16)), 3)))
