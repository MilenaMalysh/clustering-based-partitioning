import matplotlib.pyplot as plt
import numpy as np
import seaborn
from matplotlib import colors

from clustering_implementations.combined_horizontal.combined_horizontal import combined_horizontal

from temp_input_data import n_columns, n_rows


def draw(data):
    data = data.reshape(n_rows, n_columns).astype(int)

    clusters_amount = len(set(data.flatten())) + 1

    color = seaborn.color_palette("hls", clusters_amount)
    print(color)
    cmap = colors.ListedColormap(color)
    norm = colors.BoundaryNorm(range(-1, clusters_amount + 1), cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    for y in range(n_rows):
        for x in range(n_columns):
            plt.text(x, y, data.flatten()[y * n_columns + x], color="black", fontsize=20)

    ax.grid(which='major', axis='both', linestyle='-', color='k')
    ax.set_xticks(np.arange(-.5, n_columns))
    ax.set_yticks(np.arange(-.5, n_rows))
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show(format='eps')
    fig.savefig('filename.svg', format='svg')


def main():


    # input data
    selectivity_list = [[1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
     [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
     [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
     [1, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [0, 0, 0],
     [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
     [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0]]
    # selectivity_list = generate_selectivity_list(n_columns, n_rows, n_queries)


    # clustering algorithms
    # clustering = DBSCAN(eps=0.1, min_samples=3).fit(np.load("selectivity_list"))
    # clustering = KMeans(7).fit(np.load("selectivity_list"))
    # clustering = sequential_hybrid(np.load("selectivity_list"))
    # clustering = precomputed_horizontal(np.load("selectivity_list"))

    # draw(clustering)


    # node2vec
    # graph = table_to_graph(np.array(selectivity_list))
    # nx.draw_networkx(graph, arrows=False)
    # node2vec = Node2Vec(graph, dimensions=n_dimensions, walk_length=30, num_walks=200)
    # model = node2vec.fit(window=10, min_count=1, batch_words=4)
    # restored_cells = model_to_cells(model)
    # clustering = DBSCAN(eps=1, min_samples=3).fit(restored_cells)



    # tests
    # precomp_horiz_vs_hybr()

    combined_horizontal(selectivity_list)


if __name__ == "__main__":
    main()
