# where clauses
queries = [
    "l_shipdate >= date '1993-01-01'",
    "l_shipdate >= date '1994-01-01'",
    "l_discount between 0.07 and 0.09",
    "l_quantity < 24",
    "l_commitdate < l_receiptdate",
    "l_orderkey = 1"
]