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
