import matplotlib.pyplot as plt
import numpy as np
import seaborn
from matplotlib import colors

from input_data.temp_input_data import n_columns, n_rows


# draw(clustering)

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

