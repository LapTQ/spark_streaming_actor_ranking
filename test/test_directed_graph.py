# 0.Import required modules
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import time

# def directed_k_shell(G):
#     # Initialize the k-shell decomposition
#     k_shell = {}

#     # Initialize the list of nodes in the k-shell
#     nodes = list(G.nodes())

#     # Initialize the list of nodes with zero degree
#     zero_degree_nodes = []

#     # Compute the in-degree and out-degree for each node
#     in_degrees = {}
#     out_degrees = {}
#     for node in nodes:
#         in_degrees[node] = sum([G[p][node].get('weight', 1) for p in list(G.predecessors(node))])
#         out_degrees[node] = sum([G[node][s].get('weight', 1) for s in list(G.successors(node))])
    
#     # Compute the minimum degree in the graph
#     min_degree = min(list(in_degrees.values()) + list(out_degrees.values()))

#     # Repeat the k-shell decomposition until all nodes have been assigned to a shell
#     shell_num = 0
#     print("acd")
#     while nodes:
#         # Find the nodes with degree less than or equal to the current shell number
#         shell_nodes = [n for n in nodes if in_degrees[n] + out_degrees[n] <= shell_num]

#         # If there are no more shell nodes, increment the shell number and continue
#         if not shell_nodes:
#             shell_num += 1
#             continue

#         # Assign the shell number to the shell nodes
#         for n in shell_nodes:
#             k_shell[n] = shell_num

#             # Remove the node from the list of nodes and its in- and out-edges from the graph
#             nodes.remove(n)
#             zero_degree_nodes.append(n)
#             for neighbor in list(G.neighbors(n)):
#                 if neighbor not in zero_degree_nodes:
#                     in_degrees[neighbor] -= G[n][neighbor].get('weight', 1)
#                     out_degrees[neighbor] -= G[n][neighbor].get('weight', 1)

#     return k_shell

def directed_k_shell(G):
    result = []
    
    # create a copy of the graph
    G_copy = G.copy()

    # calculate the in-degree and out-degree of each node
    in_degrees = dict(G_copy.in_degree())


    k = 1
    while True:
        if not in_degrees:
            break
        # identify the nodes with the smallest in-degree
        min_in_degree = min(in_degrees.values())
        shell_nodes = [n for n in in_degrees if in_degrees[n] == min_in_degree]

        if not shell_nodes:
            # no nodes left in the graph
            break
        
        for i in range(k,min_in_degree):
            result.append([])
        
        result.append(shell_nodes)
        k = min_in_degree
        
        # remove the shell nodes and their associated edges from the graph
        G_copy.remove_nodes_from(shell_nodes)

        # recalculate the in-degree and out-degree of the remaining nodes
        in_degrees = dict(G_copy.in_degree())

        k += 1

    return result

def process_the_data():
    
    def extract_from_file(file_path):

        buf = []

        with open(file_path, 'r') as f:
            while True:
                line = f.readline()

                if line == '':
                    break

                if line.startswith('ASIN: '):
                    buf.append({'ASIN': line.strip().split()[1]})
                elif line.strip().startswith('salesrank'):
                    buf[-1]['salesrank'] = int(line.strip().split()[-1])
                elif line.strip().startswith('similar'):
                    buf[-1]['similar'] = line.strip().split()[2:]

        return buf

    df = pd.DataFrame(extract_from_file('./data/amazon-meta.txt'))
    
    df = df[["ASIN", "similar"]]
    df = df[df['similar'].notna()]

    pairs = [[row.ASIN, node2] for row in df.itertuples() for node2 in row.similar]

    return pairs

# Create a directed graph
G = nx.DiGraph()
# edges = [("Lập", "Nhật"), ("Lập", "Trường"), ("Trường", "Hưng"), ("Trường", "Khánh"),
#     ("Tùng", "Khánh"), ("Huy", "Khánh"), ("Huy", "Tâm"), ("Tuấn", "Trường"), ("Tuấn", "Khánh"),
#     ("Rosé", "Trường"), ("Rosé", "Khánh")]
# edges = [(1, 2), (1, 3), (2, 1), (2, 3), (2, 4), (3, 2), (3, 4), (4, 1), (4,5), (1,5), (5,2)]
G.add_edges_from(process_the_data())
# Compute the k-shell decomposition
k_shell = directed_k_shell(G)
print(k_shell)

# Visualize the graph with k-shell colors
# pos = nx.circular_layout(G)
# # node_colors = [k_shell[node] for node in G.nodes()]
# # node_sizes = [100 * (k_shell[node] + 1) for node in G.nodes()]
# nx.draw_networkx(G, pos, cmap=plt.cm.Blues)
# plt.axis('off')
# plt.show()
