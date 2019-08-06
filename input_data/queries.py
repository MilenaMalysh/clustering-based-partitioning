# where clauses
queries = [
    [('l_orderkey', '<', '200000'), ('l_quantity', '<', '24'), ('l_extendedprice', '>', '50000')],
    [('l_orderkey', '>', '500000'), ('l_suppkey', '>', '3000'), ('l_extendedprice', '>', '50000'), ('l_quantity', '>', '10')],
    [('l_suppkey', '>', '6000'), ('l_linenumber', '<', '4'), ('l_partkey', '>', '160000'), ('l_quantity', '>', '10')],
    [('l_orderkey', '<', '200000'), ('l_quantity', '<', '24'), ('l_suppkey', '>', '6000'), ('l_partkey', '>', '160000')],
    [('l_orderkey', '>', '500000'), ('l_quantity', '>', '10')],
    [('l_partkey', '>', '160000'), ('l_extendedprice', '>', '50000'), ('l_quantity', '>', '10')]
    # 'l_orderkey > 500000',
    # 'l_quantity < 24',
    # 'l_suppkey > 3000',
    # 'l_linenumber < 4',
    # 'l_quantity > 10',
    # 'l_extendedprice > 50000',
    # 'l_partkey > 160000',
    # 'l_orderkey < 200000',
    # 'l_suppkey > 6000'



    # "l_shipdate >= date '1993-01-01'",
    # # "l_shipdate >= date '1994-01-01'",
    # "l_discount < 0.07",
    # "l_quantity < 24",
    # "l_commitdate < l_receiptdate",

    # "l_orderkey = 1",
    # "l_returnflag = 'A'",
    # "l_returnflag = 'N'",
    # "l_returnflag = 'R'",
    # "l_linestatus = 'F'",
    # "l_commitdate > date '1992-09-09'",
    # "l_shipmode in ('AIR', 'MAIL', 'REG AIR', 'TRUCK')"
]

# select count(*) from lineitem where (not l_shipdate >= date '1993-01-01') and (not l_discount between 0.07 and 0.09) and (not l_quantity < 24) and (l_commitdate < l_receiptdate) and not (l_orderkey = 1);

# queries = [
#     {'column': 'l_shipdate', 'from': "'1993-01-01'", 'to': "'1994-01-01'"},
#     {'column': 'l_discount', 'from': '0.07', 'to': '0.09'},
#     {'column': 'l_quantity', 'from': '7', 'to': '24'},
#     {'column': 'l_orderkey', 'from': '1', 'to': '2540'},
#     {'column': 'l_suppkey', 'from': '2000', 'to': '10000'},
# ]
