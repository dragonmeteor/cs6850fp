import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *
import time
import datetime
import pprint
import networkx.linalg
import numpy.linalg


if len(sys.argv) < 4:
	print "python script/create_rooted_subgraph_dot.py <json-file-name> <nicoid> <output-file-name> [indegree-lowerbound]"
	exit()

nicoid = sys.argv[2]

sys.stdout.write("Loading JSON ... ")
json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()
print "DONE"

sys.stdout.write("Constructing graph ... ")
G = construct_item_graph(data, exclude_multi_category_nodes=False, exclude_self_links=True)
print "DONE"

root_id = None
nodes = data["nodes"]
for node_id in nodes:
	node = nodes[node_id]
	if node["nicoid"] == nicoid:
		root_id = node_id
		break

indegree_lower_bound = 0
if len(sys.argv) >= 5:
	indegree_lower_bound = int(sys.argv[4])

def get_terminal_node_sig(H, node):
	target_list = []
	for edge in H.out_edges_iter(node):
		target_list.append(edge[1])
	target_list.sort()
	return pprint.pformat([target_list, H.node[node]["category"]])

if root_id is None:
	print "Node with ID", nicoid, "not found."
else:
	H = get_cascade(G, nodes, root_id, indegree_lower_bound)
	
	print "There are", H.number_of_nodes(), "nodes in the rooted subgraph."
	terminals = 0
	for node in H.nodes_iter():
		if H.in_degree(node) == 0:
			terminals += 1
	print "There are", terminals, "terminal nodes"

	if True:
		F = nx.DiGraph()
		terminal_map = {}
		for node in H.nodes_iter():
			if H.in_degree(node) > 0:
				F.add_node(node, category=H.node[node]["category"], count=1)
			else:
				sig = get_terminal_node_sig(H, node)
				if sig not in terminal_map:
					terminal_map[sig] = 0
				terminal_map[sig] += 1
		for node in H.nodes_iter():
			if H.in_degree(node) > 0:
				for edge in H.out_edges_iter(node):					
					F.add_edge(edge[0], edge[1])
		terminal_count = 0
		for sig in terminal_map:
			node_name = "t%d" % terminal_count
			sigobj = eval(sig)
			F.add_node(node_name, category=sigobj[1], count=terminal_map[sig])
			terminal_count += 1
			for target in sigobj[0]:
				F.add_edge(node_name, target)

		gen_dot_file_with_count(F, sys.argv[3])
	else:
		gen_dot_file(H, sys.argv[3])