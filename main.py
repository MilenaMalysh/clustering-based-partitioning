from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal_from_db
from db.PostgresConnector import PostgresConnector


def main():

    connector = PostgresConnector()
    combined_horizontal_from_db(connector, 'euclidean_distance', 'complete_linkage')


# clustering algorithms
# clustering = DBSCAN(eps=0.1, min_samples=3).fit(np.load("selectivity_list"))
# clustering = KMeans(7).fit(np.load("selectivity_list"))
# clustering = sequential_hybrid(np.load("selectivity_list"))
# clustering = precomputed_horizontal(np.load("selectivity_list"))

if __name__ == "__main__":
    main()
