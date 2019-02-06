import random

from sklearn.cluster import DBSCAN, KMeans
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

size = 6


def draw(data):
    data = data.reshape(size, size)

    clusters_amount = len(set(data.flatten())) + 1

    color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
             for i in range(clusters_amount)]

    cmap = colors.ListedColormap(color)
    norm = colors.BoundaryNorm(range(clusters_amount), cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, size))
    ax.set_yticks(np.arange(-.5, size))
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    plt.show()


def main():
    X = np.array([
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0],
        [1, 0, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
        [1, 1, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [0, 0, 0],
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0],
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 1], [0, 0, 0]
        ])
    clustering = DBSCAN(eps=0.1, min_samples=3).fit(X)
    # clustering = KMeans(7).fit(X)

    draw(clustering.labels_)
    print(clustering.labels_)


if __name__ == "__main__":
    main()