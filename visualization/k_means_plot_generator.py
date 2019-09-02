import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans

if __name__ == "__main__":
    X, y_true = make_blobs(n_samples=300, centers=3,
                           cluster_std=0.95, random_state=4)
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(X)
    y_kmeans = kmeans.predict(X)
    # plt.annotate("", xy=(0.5, 0.5), xytext=(0, 0), arrowprops=dict(arrowstyle="->"))

    # plt.xlabel('x', fontsize=18)
    # plt.ylabel('y', fontsize=16)

    plt.grid(False)

    plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='winter')
    # plt.show()
    plt.savefig("test.svg")
