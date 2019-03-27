# -*- coding: utf-8 -*-
# from here https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyeda
from itertools import repeat
from unittest import TestCase

from pyeda.boolalg.expr import Complement, One
from pyeda.inter import *
from typing import List, Tuple, Union


def minimize(cluster_features: List[Union[Tuple, List]]) -> List[Tuple]:
    """Minimizes features for cluster

    Example:

        >> minimize([[0, 1], [1, 1]])
    [[-1, 1]]

    :param cluster_features: list of features; 0 means exclude query predicates, 1 means include.
    :return: minimized cluster features, -1 means ignore query predicates,
    0 means exclude query predicates, 1 means include.
    """
    num_queries = len(cluster_features[0])
    variables = exprvars("x", num_queries)
    predicate = False
    for feature in cluster_features:
        feature_predicate = And(*[variables[i] if x else ~variables[i] for i, x in enumerate(feature)])
        predicate = Or(predicate, feature_predicate)
    minimized, = espresso_exprs(predicate.to_dnf())
    if minimized != One:
        result = []
        for and_expr in minimized.to_dnf().cover:
            feature = list(repeat(-1, len(variables)))
            for var in and_expr:
                if type(var) is Complement:
                    feature[var.top.indices[0]] = 0
                else:
                    feature[var.indices[0]] = 1
            result.append(tuple(feature))
        return result
    else:
        return []


class TestMinimize(TestCase):
    def test_minimize(self):
        self.assertSetEqual(set(minimize([[0, 1], [1, 1]])), {(-1, 1)})
        self.assertSetEqual(set(minimize([[0, 0], [1, 0]])), {(-1, 0)})
        self.assertSetEqual(set(minimize([[0, 1], [1, 0]])), {(0, 1), (1, 0)})
        self.assertSetEqual(set(minimize([[0, 1], [1, 0], [0, 0], [1, 1]])), set())
