import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys

if len(sys.argv) < 3:
	print "Usage: python script/create_item_count_vs_indegree_plot.py <graph-file> <output-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

G = nx.DiGraph()
for item_name in data["nodes"]:
	item_data = data["nodes"][item_name]
	G.add_node(item_name)
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

in_degree_map = {}
for node in G.nodes_iter():
	indeg = G.in_degree(node)
	if indeg in in_degree_map:
		in_degree_map[indeg] = in_degree_map[indeg]+1
	else:
		in_degree_map[indeg] = 1

def save_power_law_graph(the_map, xlabel, ylabel, filename, fitLine=True):
	in_degree_map = the_map.copy()

	if 0 in in_degree_map:
		del in_degree_map[0]
	count = len(in_degree_map)
	xx = np.zeros((count,))
	yy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xx[count] = indeg
			yy[count] = in_degree_map[indeg]
			count += 1

	remove_list = []
	for indeg in in_degree_map:
		count = in_degree_map[indeg]
		if count == 1:
			remove_list.append(indeg)
	for indeg in remove_list:
		del in_degree_map[indeg]
	count = len(in_degree_map)
	xxxx = np.zeros((count,))
	yyyy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xxxx[count] = indeg
			yyyy[count] = in_degree_map[indeg]
			count += 1
	coeffs = np.polyfit(np.log(xxxx) / np.log(10.0), np.log(yyyy) / np.log(10.0), 1)
	right = -coeffs[1] / coeffs[0]
	lx = np.linspace(0,right,1000)
	ly = lx*coeffs[0] + coeffs[1]
	
	plt.scatter(np.log(xx) / np.log(10.0), np.log(yy) / np.log(10.0))
	if fitLine:
		plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	if fitLine:
		plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))	
	plt.savefig(filename)

save_power_law_graph(in_degree_map, "log(number of items)", "log(indegree)", sys.argv[2])