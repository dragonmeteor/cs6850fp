import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

json_data=open('data/mmd_10_11_2013.json')
data = json.load(json_data)
json_data.close()

G = nx.DiGraph()
for item_name in data["nodes"]:
	item_data = data["nodes"][item_name]
	G.add_node(item_name, 
		nicoid=item_data["nicoid"],
		user=item_data["user"],
		view_count=item_data["view_count"],
		comment_count=item_data["comment_count"],
		mylist_count=item_data["mylist_count"],
		tags=item_data["tags"])
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

in_degree_map = {}
for node in G.nodes_iter():
	indeg = G.in_degree(node)
	if indeg in in_degree_map:
		in_degree_map[indeg] = in_degree_map[indeg]+1
	else:
		in_degree_map[indeg] = 1

out_degree_map = {}
for node in G.nodes_iter():
	indeg = G.out_degree(node)
	if indeg in out_degree_map:
		out_degree_map[indeg] = out_degree_map[indeg]+1
	else:
		out_degree_map[indeg] = 1

def plot_power_law_graph(the_map, xlabel, ylabel):
	in_degree_map = the_map.copy()

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
	coeffs = np.polyfit(np.log(xxxx), np.log(yyyy), 1)		
	lx = np.linspace(0,6,1000)
	ly = lx*coeffs[0] + coeffs[1]
	
	plt.scatter(np.log(xx), np.log(yy))
	plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
	plt.show()

def plot_log_scatter(the_map, xlabel, ylabel):
	in_degree_map = the_map.copy()

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

	plt.scatter(np.log(xx), np.log(yy))
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)	
	plt.show()

#plot_power_law_graph(in_degree_map, "log(in-degree)", "log(node count)")
plot_log_scatter(out_degree_map, "log(out-degree)", "log(node count)")


#print nx.connected_components(G.to_undirected())
#nx.draw(G)