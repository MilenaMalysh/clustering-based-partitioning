# selectivity_list = [
#     [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
#     [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
#     [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
#     [1, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [0, 0, 0],
#     [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
#     [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0]
# ]

# n_queries = 3
# n_columns = 6
# n_rows = 6
# n_dimensions = 3
import datetime
import os

n_columns = 16
# n_rows = 104857
n_rows = 1048575
n_queries = 6
n_predicates_per_query = 3
n_clusters = 4
# n_queries > (1 + duplicates_percentage) * math.ceil(n_queries * n_predicates_per_query / len(range_columns))
# + min number of unique predicates in number of predicates per query => in our case max duplicates_percentage = 1 - 3 / 3 * 6 = 5/6 = 0.83
duplicates_percentage = 0.1
range_columns = {'l_orderkey': [314691, 733478],
                 'l_partkey': [59994, 140010],
                 'l_suppkey': [3007, 7005],
                 'l_linenumber': [2, 4],
                 'l_quantity': [16.00, 36.00],
                 'l_extendedprice': [22421.56, 51223.75],
                 'l_discount': [0.03, 0.07],
                 'l_tax': [0.02, 0.06],
                 'l_shipdate': [datetime.date(1994, 2, 25), datetime.date(1996, 10, 12)],
                 'l_commitdate': [datetime.date(1994, 2, 25), datetime.date(1996, 10, 11)],
                 'l_receiptdate': [datetime.date(1994, 3, 13), datetime.date(1996, 10, 27)]
                 }

table_name = os.environ['TABLENAME']