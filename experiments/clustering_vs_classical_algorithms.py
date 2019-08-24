from clustering_implementations.classical_algorithms.zhang import zhang
from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector
from input_data.queries import queries


def test():
    print('-----------------------------------------------------------------------')
    print('CLUSTERING vs CLASSICAL ALGORITHMS TEST')
    print('-----------------------------------------------------------------------')
    connector = PostgresConnector()
    clustering_cost = combined_horizontal_from_db(connector, 'euclidean_distance', 'single_linkage')

    frequencies = [1] * 9
    predicate_usage = [[] for _ in queries]
    predicates = list(set().union(*queries))
    for predicate_idx, predicate in enumerate(predicates):
        for query_idx, query in enumerate(queries):
            if predicate in query:
                predicate_usage[query_idx].append(predicate_idx)
    zhang_cost = zhang(frequencies, predicates, predicate_usage, connector)

    print('***********************************************************************')
    print('RESULT ')
    print('clustering cost: {} zhang_cost {}'.format(clustering_cost, zhang_cost))


if __name__ == "__main__":
    test()
