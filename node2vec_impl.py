import networkx as nx
import numpy as np

from temp_input_data import n_queries, n_rows, n_columns, n_dimensions


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
