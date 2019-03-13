# where clauses
queries = [
    "l_shipdate >= date '1993-01-01'",
    "l_shipdate >= date '1994-01-01'",
    "l_discount between 0.07 and 0.09",
    "l_quantity < 24",
    "l_commitdate < l_receiptdate",
    "l_orderkey = 1"
]

# queries = [
#     {'column': 'l_shipdate', 'from': "'1993-01-01'", 'to': "'1994-01-01'"},
#     {'column': 'l_discount', 'from': '0.07', 'to': '0.09'},
#     {'column': 'l_quantity', 'from': '7', 'to': '24'},
#     {'column': 'l_orderkey', 'from': '1', 'to': '2540'},
#     {'column': 'l_suppkey', 'from': '2000', 'to': '10000'},
# ]
