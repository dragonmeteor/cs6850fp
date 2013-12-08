import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *
import time
import datetime

if len(sys.argv) < 3:
	print "python script/create_in_degree_evolution_plot.py <json-file-name> <count> <file-name-prefix>"
	exit()

count = int(sys.argv[2])
file_name_prefix = sys.argv[3]

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

G = nx.DiGraph()
for item_name in data["nodes"]:
	#item_data = data["nodes"][item_name]	
	G.add_node(item_name)
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

n = G.number_of_nodes()
nodes_and_indegree = id_and_indegree_sorted_by_indegree(G)
for i in xrange(1,count+1):
	target_id = nodes_and_indegree[n-i][0]
	plt = get_indegree_evolution_plot(G, data, target_id)	
	filename = ("%s%04d.png" % (file_name_prefix, i))
	print "Saving", filename, "..."
	plt.savefig(filename)
