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
	print "python script/count_cascade_patterns.py <json-file-name> <output-file-name> <distribution-graph-file-name>"
	exit()

output_file_name = sys.argv[2]
distribution_graph_file_name = sys.argv[3]

sys.stdout.write("Loading JSON ... ")
json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()
print "DONE"

sys.stdout.write("Constructing graph ... ")
G = nx.DiGraph()
nodes = data["nodes"]
for item_name in data["nodes"]:	
	if len(nodes[item_name]["categories"]) == 1:
		G.add_node(item_name)
for edge in data["edges"]:	
	node0 = nodes[edge[0]]
	node1 = nodes[edge[1]]
	if len(node0["categories"]) != 1:
		continue
	if len(node1["categories"]) != 1:
		continue
	if node0["user"] != node1["user"]:
		G.add_edge(edge[0], edge[1])
print "DONE"

def dictionary_to_array(d):
	a = []
	for key in d:
		a.append((key, d[key]))
	a.sort(key=lambda x: x[0])
	return a

def signature(H):
	sig = []
	sig.append(H.number_of_nodes())
	sig.append(H.number_of_edges())
	
	cat_count = {"cg":0, "model":0, "motion":0, "tool":0, "editing":0}
	indeg_map = {}
	outdeg_map = {}
	for node_id in H.nodes_iter():
		cat_count[H.node[node_id]["category"]] += 1
		
		indeg = H.in_degree(node_id)
		if indeg not in indeg_map:
			indeg_map[indeg] = 0
		indeg_map[indeg] += 1
		
		outdeg = H.out_degree(node_id)
		if outdeg not in outdeg_map:
			outdeg_map[outdeg] = 0
		outdeg_map[outdeg] += 1
		
	sig.append(dictionary_to_array(cat_count))
	sig.append(dictionary_to_array(indeg_map))
	sig.append(dictionary_to_array(outdeg_map))

	if H.number_of_nodes() < 100:
		L = networkx.linalg.laplacian_matrix(H.to_undirected())
		U, s, V = numpy.linalg.svd(L)
		ss = []
		for i in xrange(H.number_of_nodes()):
			ss.append("%0.4f" % s[i])
		sig.append(ss)

	return pprint.pformat(sig)

def get_cascade(G, nodes, node_id):
	H = nx.DiGraph()
	node_list = [node_id]			
	explored_set = set()
	while len(node_list) > 0:
		node_id = node_list[-1]
		H.add_node(node_id, category=nodes[node_id]["categories"][0])
		del node_list[-1]
		explored_set.add(node_id)
		for edge in G.in_edges_iter(node_id):
			H.add_edge(edge[0], node_id)
			if edge[0] not in explored_set:	
				explored_set.add(edge[0])
				node_list.append(edge[0])
	return H

nodes = data["nodes"]
starter_count = 0
trivial_cascade_count = 0
size_count = {}
sig_hash = {}
processed_count = 0
for node_id in nodes:
	root_id = node_id
	if G.out_degree(node_id) == 0:
		starter_count += 1
		if G.in_degree(node_id) == 0:
			trivial_cascade_count += 1
		else:
			H = get_cascade(G, nodes, node_id)
			if H.number_of_nodes() not in size_count:
				size_count[H.number_of_nodes()] = 0
			size_count[H.number_of_nodes()] += 1

			sig = signature(H)
			if sig not in sig_hash:
				sig_hash[sig] = []
			graph_lists = sig_hash[sig]
			found = False
			for graph_class in graph_lists:
				if graph_class["example"] == None:
					break
				F = graph_class["example"]				
				if nx.is_isomorphic(F, H, node_match=lambda d0, d1: d0["category"] == d1["category"]):
					found = True
					graph_class["count"] += 1
			if not found:
				if H.number_of_nodes() < 10:
					graph_lists.append({"example": H, "count":1, "root": root_id, "size": H.number_of_nodes()})
				else:
					graph_lists.append({"example": None, "count":1, "root": root_id, "size": H.number_of_nodes()})
			
			processed_count += 1
			if processed_count % 100 == 0:
				print "Processed", processed_count, "graphs"

max_size = 0
for size in size_count:
	if max_size < size:
		max_size = size

print "Found", starter_count, "nodes that can be root of cascades."
print "Found", trivial_cascade_count, "trivial cascades"
print "Maximum cascade size =", max_size

#one_list = []
#for size in size_count:
#	if size_count[size] == 1:
#		one_list.append(size)
#for size in one_list:
#	del size_count[size]

save_power_law_graph(size_count, "log(number of vertices in cascades)", "log(number of cascades)", distribution_graph_file_name, True, 3)

distrib = []
for sig in sig_hash:
	distrib += sig_hash[sig]
distrib.sort(key=lambda x:x["count"], reverse=True)
fout = open(output_file_name, "wt")
for cascade in distrib:
	fout.write("%d %s %d" % (cascade["size"], cascade["root"], cascade["count"]))
	fout.write("\n")
fout.close()