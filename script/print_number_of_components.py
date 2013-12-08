import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys

if len(sys.argv) < 2:
	print "python script/print_number_of_components.py <json-file-name>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

G = nx.DiGraph()
for item_name in data["nodes"]:
	item_data = data["nodes"][item_name]
	G.add_node(item_name)
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

print nx.number_connected_components(G.to_undirected())
#nx.draw(G)