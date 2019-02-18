import random

from sklearn.cluster import DBSCAN, KMeans
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

from cost_models.hdd_based import get_cost_per_query
from temp_input_data import size, selectivity_list


def draw(data):
    data = data.reshape(size, size)

    clusters_amount = len(set(data.flatten())) + 1

    color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(clusters_amount)]

    cmap = colors.ListedColormap(color)
    norm = colors.BoundaryNorm(range(-1, clusters_amount), cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    for y in range(size):
        for x in range(size):
            plt.text(x, y, data.flatten()[y * size + x], color="white", fontsize=20)

    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, size))
    ax.set_yticks(np.arange(-.5, size))
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show()


def main():
    # clustering = DBSCAN(eps=0.1, min_samples=3).fit(np.array(selectivity_list))
    clustering = KMeans(7).fit(np.array(selectivity_list))

    draw(clustering.labels_)
    print(clustering.labels_)
    print(sum([get_cost_per_query(query_idx, clustering.labels_) for query_idx in
               range(len(selectivity_list[0]))]))


if __name__ == "__main__":
    main()