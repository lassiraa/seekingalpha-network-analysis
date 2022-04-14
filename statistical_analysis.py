# %%
import json

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

G = nx.read_gexf('SA.gexf')
nodes = G.nodes()
edges = G.edges()
total_deg = edges * 2
max_deg = max(dict(G.degree()).values())
min_deg = min(dict(G.degree()).values())
degrees = list(G.degree())

# %%
total_deg = 0
max_deg = 0
for _, d in degrees:
    if d > max_deg:
        max_deg = d
    total_deg += d

# %%
G_er = nx.erdos_renyi_graph()
G_ba = nx.barabasi_albert_graph()
