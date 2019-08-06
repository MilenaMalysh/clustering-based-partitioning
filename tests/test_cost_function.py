import unittest

from clustering_implementations.MockFragment import MockFragment
from cost_models.hdd_based_adapted import hdd_based_adapted_cost, str_to_query_tokens


class MyTestCase(unittest.TestCase):
    def test_cost(self):
        self.assertEqual(1,
                         hdd_based_adapted_cost(str_to_query_tokens("l_linenumber > 6"),
                              [
                                  MockFragment("l_linenumber > 5"),
                                  MockFragment("l_linenumber <= 5")
                              ]
                              ))
