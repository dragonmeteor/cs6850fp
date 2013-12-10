import networkx as nx

def id_and_indegree_sorted_by_indegree(G):
	nodes = G.nodes()	
	nodes_and_indegrees = [[x,G.in_degree(x)] for x in nodes]
	return sorted(nodes_and_indegrees, key=lambda x: x[1])

def get_indegree_evolution_plot(G, data, target_id):
	import time
	import datetime
	import matplotlib.pyplot as plt
	import numpy as np

	n = G.number_of_nodes()
	time_format = "%Y-%m-%d %H:%M:%S %Z"
	target_node = data["nodes"][target_id]
	target_time = time.mktime(time.strptime(target_node["uploaded_at"], time_format))
	in_edges = G.in_edges_iter(target_id)
	day_map = {}
	max_day = 0
	for edge in in_edges:
		source_id = edge[0]
		source_node = data["nodes"][source_id]
		source_time = time.mktime(time.strptime(source_node["uploaded_at"], time_format))
		delta = datetime.timedelta(seconds=source_time - target_time)
		if delta.days not in day_map:
			day_map[delta.days] = 0
		day_map[delta.days] += 1
		if max_day < delta.days:
			max_day = delta.days

	xx = np.zeros((max_day+1,))
	yy = np.zeros((max_day+1,))
	for day_count in day_map:		
		yy[day_count] = day_map[day_count]
	for i in xrange(max_day+1):
		xx[i] = i
	for i in xrange(1, max_day+1):
		yy[i] = yy[i] + yy[i-1]
	plt.figure()
	plt.plot(xx, yy)
	plt.title("In-degree evolution of %s" % target_node["nicoid"])
	plt.xlabel("Days since uploaded")
	plt.ylabel("Number of in-links")
	return plt

def save_power_law_graph(the_map, xlabel, ylabel, filename, fitLine=True, fit_exclude_threshold=1):
	import numpy as np
	import matplotlib.pyplot as plt

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
		if count <= fit_exclude_threshold:
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

