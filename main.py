import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn
from matplotlib import colors
from node2vec import Node2Vec
from sklearn.cluster import DBSCAN, KMeans

n_columns = 6
n_rows = 6
n_queries = 3
n_dimensions = 3


def draw(data):
    data = data.reshape(n_columns, n_rows)

    clusters_amount = len(set(data.flatten())) + 1

    color = seaborn.color_palette("hls", clusters_amount)
    cmap = colors.ListedColormap(color)
    norm = colors.BoundaryNorm(range(clusters_amount), cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, n_columns))
    ax.set_yticks(np.arange(-.5, n_rows))
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show()


def table_to_graph(cells) -> nx.Graph:
    graph = nx.Graph()
    for i_query in range(n_queries):
        graph.add_node("query" + str(i_query))

    for i_row in range(n_rows):
        for i_column in range(n_columns):
            node = "x" + str(i_column) + "y" + str(i_row)
            graph.add_node(node)
            for i_query in range(n_queries):
                if cells[n_columns * i_row + i_column][i_query]:
                    graph.add_edge(node, "query" + str(i_query))
    return graph


def model_to_cells(model) -> np.ndarray:
    result = np.zeros([n_columns, n_rows, n_dimensions])
    for i, node in enumerate(model.wv.index2entity):
        if 'query' not in node:
            i_x = node.find('x')
            i_y = node.find('y')
            i_column = int(node[i_x + 1:i_y])
            i_row = int(node[i_y + 1:])
            result[i_row][i_column] = model.wv.vectors[i]

    return result.reshape(n_columns * n_rows, n_dimensions)


def main():
    cells = np.array([
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
        [1, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [0, 0, 0],
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0]
        ])
    clustering = DBSCAN(eps=0.1, min_samples=3).fit(cells)
    # clustering = KMeans(7).fit(X)
    draw(clustering.labels_)
    print(clustering.labels_)

    graph = table_to_graph(cells)
    nx.draw_networkx(graph, arrows=False)
    node2vec = Node2Vec(graph, dimensions=n_dimensions, walk_length=30, num_walks=200)
    model = node2vec.fit(window=10, min_count=1, batch_words=4)
    restored_cells = model_to_cells(model)
    clustering = DBSCAN(eps=1, min_samples=3).fit(restored_cells)
    draw(clustering.labels_)
    print(clustering.labels_)


if __name__ == "__main__":
    main()
