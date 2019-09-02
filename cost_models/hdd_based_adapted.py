import collections
from typing import List

import pyeda.inter as pyeda
from pyparsing import Group, oneOf, quotedString
from pyparsing import Keyword, infixNotation, opAssoc
from pyparsing import pyparsing_common, ParserElement

ParserElement.enablePackrat()

column = pyparsing_common.identifier.copy()
and_ = Keyword("and", caseless=True)
or_ = Keyword("or", caseless=True)
not_ = Keyword("not", caseless=True)

operators = ["=", "!=", ">=", ">", "<=", "<", ]
cooperators = ["!=", "=", "<", "<=", ">", ">="]


class Op(object):
    def __init__(self, tokens):
        if len(tokens) == 1 and not isinstance(tokens[0],  (Op, Cond, BoolNot)):
            tokens = tokens[0]
        self.items = list(filter(lambda x: isinstance(x, (Op, Cond, BoolNot)), tokens))

    def __iter__(self):
        return iter(self.items)


class Cond(object):
    def __init__(self, tokens):
        if len(tokens) == 1:
            tokens = tokens[0]
        self.left = tokens[0]
        self.op = tokens[1]
        self.right = tokens[2]

    def __eq__(self, other):
        return (self.left, self.op, self.right) == (other.left, other.op, other.right)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.left, self.op, self.right))

    def __str__(self):
        return "<Cond({} {} {})>".format(self.left, self.op, self.right)

    def __iter__(self):
        return iter(())

    def to_expr(self):
        return pyeda.exprvar(str(self))

    def implies(self, actual, other):
        """
        Check what :param actual value of this condition implies for :param other.
        :return: None if no connection, True or False otherwise.
        """
        real_op = self.op if actual else cooperators[operators.index(self.op)]
        if self.left != other.left:
            return None
        elif real_op == "=":
            if other.op == "=":
                return self.right == other.right
            elif other.op == "!=":
                return False if self.right == other.right else None
            elif other.op == ">":
                return self.right > other.right
            elif other.op == ">=":
                return self.right >= other.right
            elif other.op == "<":
                return self.right < other.right
            elif other.op == "<=":
                return self.right <= other.right
        elif real_op == "!=":
            if other.op == "=":
                return False if self.right == other.right else None
            elif other.op == "!=":
                return True if self.right == other.right else None
            else:
                return None
        elif real_op == ">":
            if other.op == "=":
                return False if self.right >= other.right else None
            elif other.op == "!=":
                return True if self.right >= other.right else None
            elif other.op == ">":
                return True if self.right >= other.right else None
            elif other.op == ">=":
                return True if self.right >= other.right else None
            elif other.op == "<":
                return False if self.right >= other.right else None
            elif other.op == "<=":
                return False if self.right >= other.right else None
        elif real_op == ">=":
            if other.op == "=":
                return False if self.right > other.right else None
            elif other.op == "!=":
                return True if self.right > other.right else None
            elif other.op == ">":
                return True if self.right > other.right else None
            elif other.op == ">=":
                return True if self.right >= other.right else None
            elif other.op == "<":
                return False if self.right >= other.right else None
            elif other.op == "<=":
                return False if self.right > other.right else None
        elif real_op == "<":
            if other.op == "=":
                return False if self.right <= other.right else None
            elif other.op == "!=":
                return True if self.right <= other.right else None
            elif other.op == ">":
                return False if self.right <= other.right else None
            elif other.op == ">=":
                return False if self.right <= other.right else None
            elif other.op == "<":
                return True if self.right <= other.right else None
            elif other.op == "<=":
                return True if self.right <= other.right else None
        elif real_op == "<=":
            if other.op == "=":
                return False if self.right < other.right else None
            elif other.op == "!=":
                return True if self.right < other.right else None
            elif other.op == ">":
                return False if self.right <= other.right else None
            elif other.op == ">=":
                return False if self.right < other.right else None
            elif other.op == "<":
                return True if self.right < other.right else None
            elif other.op == "<=":
                return True if self.right <= other.right else None


class BoolAnd(Op):
    def __str__(self):
        return f"<And({str.join(' and ', self)})>"

    def to_expr(self):
        return pyeda.And(*[it.to_expr() for it in self])


class BoolOr(Op):
    def __str__(self):
        return f"<Or({str.join(' or ', self)})>"

    def to_expr(self):
        return pyeda.Or(*[it.to_expr() for it in self])


class BoolNot(object):
    def __init__(self, tokens):
        if isinstance(tokens, collections.Sequence):
            tokens = tokens[0]
        if isinstance(tokens, collections.Sequence):
            self.val = next(filter(lambda x: isinstance(x, (Op, Cond, BoolNot)), tokens), None)
        else:
            self.val = tokens

    def __str__(self):
        return "<Not({})>".format(self.val)

    def __iter__(self):
        return iter((self.val,))

    def to_expr(self):
        return pyeda.Not(self.val.to_expr())


columnRval = pyparsing_common.number.copy() | quotedString()

condition = Group(column + oneOf(operators, caseless=True) + columnRval)

boolExpr = infixNotation(condition,
                         [
                             (not_, 1, opAssoc.RIGHT, BoolNot,),
                             (and_, 2, opAssoc.LEFT, BoolAnd,),
                             (or_, 2, opAssoc.LEFT, BoolOr,),
                         ])

condition.setParseAction(Cond)


def str_to_query_tokens(query: str):
    return boolExpr.parseString(query).asList()[0]


def str_to_tokens(fragment):
    return boolExpr.parseString(str(fragment)).asList()[0]


def pretokenized_converter(fragment):
    return fragment.tokens


def hdd_based_adapted_cost(query_tokens, fragments, fragments_conventor=pretokenized_converter) -> int:
    """
    Estimate cost of executing the query on given fragmentation. Doesn't check if fragmentation is actually valid (e.g.
    disjoint and complete).
    :param query_tokens: parsed query. use :func:`str_to_query_tokens` or :func:"`ranges_to_query_tokens`.
    :param fragments: a list of predicates, each of which defines one fragment.
    :param fragments_conventor: a function to convert a fragment into tokens, use one of
    :func:`str_to_tokens` or :func:`ranges_to_tokens`
    :return: cost
    """
    conditions = find_conditions(query_tokens)
    expr = query_tokens.to_expr()
    solutions = list(expr.satisfy_all())
    independent_conditions = {}
    for cond in conditions:
        if all(solution[cond.to_expr()] == 1 for solution in solutions):
            independent_conditions[cond] = True
        elif all(solution[cond.to_expr()] == 0 for solution in solutions):
            independent_conditions[cond] = False

    fragment_inclusion = {}
    for fragment in fragments:
        if len(str(fragment)) == 0:
            fragment_inclusion[fragment] = True
            continue
        fragment_tokens = fragments_conventor(fragment)
        fragment_conditions = find_conditions(fragment_tokens)
        fragment_variables_to_conditions = {cond.to_expr(): cond for cond in fragment_conditions}
        fragment_expr = fragment_tokens.to_expr()
        known_conditions = {}
        for var in fragment_expr.inputs:
            for (independent_cond, actual) in independent_conditions.items():
                cond = fragment_variables_to_conditions[var]
                implication = independent_cond.implies(actual, cond)
                if implication is None:
                    continue
                elif implication:
                    assert cond not in known_conditions or known_conditions[cond] is True
                    known_conditions[cond] = True
                else:
                    assert cond not in known_conditions or known_conditions[cond] is False
                    known_conditions[cond] = False
        include_fragment = fragment_expr.compose(
            {known_cond.to_expr(): value for known_cond, value in known_conditions.items()}
        ).simplify()
        if include_fragment:
            fragment_inclusion[fragment] = True
        else:
            fragment_inclusion[fragment] = False
    return sum(fragment.count() for fragment, included in fragment_inclusion.items() if included)


def find_conditions(tokens: Op):
    stack = [tokens]
    conditions = set()
    while len(stack) > 0:
        current_token = stack.pop(0)
        if isinstance(current_token, Cond):
            conditions.add(current_token)
        else:
            for next_token in current_token:
                stack.append(next_token)
    return conditions