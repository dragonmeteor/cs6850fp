import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
import math

if len(sys.argv) < 2:
	print "Usage: python script/print_popularity_measure_correlation.py <graph-file>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

del data["nodes"]["145167"]

G = nx.DiGraph()
for item_name in data["nodes"]:
	item_data = data["nodes"][item_name]
	G.add_node(item_name)
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

nodes = data["nodes"]
for node_id in nodes:
	indeg = G.in_degree(node_id)
	nodes[node_id]["indegree"] = indeg
	if nodes[node_id]["comment_count"] == 10531164:
		print nodes[node_id]["nicoid"]
		print node_id

measures = ["view_count", "comment_count", "mylist_count", "indegree"]
correlation = {}
n = len(data["nodes"])

view_count_vec = np.zeros((n, 1))
comment_count_vec = np.zeros((n, 1))
mylist_count_vec = np.zeros((n, 1))
indegree_vec = np.zeros((n, 1))

index = 0
for node_id in nodes:
	node = nodes[node_id]
	view_count_vec[index, 0] = node["view_count"]
	comment_count_vec[index, 0] = node["comment_count"]
	mylist_count_vec[index, 0] = node["mylist_count"]
	indegree_vec[index, 0] = node["indegree"]
	index += 1

#plt.scatter(view_count_vec, comment_count_vec)
#plt.show()

print np.max(comment_count_vec)

#if True:
#	exit()

for i in xrange(len(measures)):
	for j in xrange(i+1, len(measures)):
		m0 = measures[i]
		m1 = measures[j]
		key = ("%s--%s" % (m0, m1))
		key0 = ("%s--%s" % (m1, m0))
		print key

		m0sum = 0.0
		m1sum = 0.0		

		for node_id in nodes:
			node = nodes[node_id]
			m0sum += node[m0]
			m1sum += node[m1]

		m0avg = m0sum / n
		m1avg = m1sum / n

		m0var = 0.0
		m1var = 0.0

		for node_id in nodes:
			node = nodes[node_id]
			m0var += (node[m0]-m0avg)**2
			m1var += (node[m1]-m1avg)**2

		m0stdev = math.sqrt(m0var / n)
		m1stdev = math.sqrt(m1var / n)

		xysum = 0
		for node_id in nodes:
			node = nodes[node_id]
			x0 = (node[m0]-m0avg)/m0stdev
			x1 = (node[m1]-m1avg)/m1stdev
			xysum += x0*x1

		corr = xysum / n
		correlation[key] = corr
		correlation[key0] = corr

keys = correlation.keys()
keys.sort()
for key in keys:
	print key, correlation[key]
