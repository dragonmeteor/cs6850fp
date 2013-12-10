import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *
import time
import datetime

if len(sys.argv) < 4:
	print "python script/create_percentage_indegree_graph.py <json-file-name> <period-in-days> <output-file-name> <percentile-0> <percentile-1> ..."
	exit()

period = int(sys.argv[2])
output_file_name = sys.argv[3]
percentiles = []
for i in xrange(4, len(sys.argv)):
	percentiles.append(int(sys.argv[i]))
percentiles.sort()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

G = nx.DiGraph()
for item_name in data["nodes"]:
	#item_data = data["nodes"][item_name]	
	G.add_node(item_name)
for edge in data["edges"]:	
	G.add_edge(edge[0], edge[1])

nodes = data["nodes"]
n = G.number_of_nodes()
old_enough_nodes = {}
in_link_counts = []
time_format = "%Y-%m-%d %H:%M:%S %Z"
first_crawl_date = "2013-10-01 00:00:00 UTC"
first_crawl_time = time.mktime(time.strptime(first_crawl_date, time_format))
no_link_count = 0
for node_id in nodes:
	node = nodes[node_id]
	node_time = time.mktime(time.strptime(node["uploaded_at"], time_format))
	delta = datetime.timedelta(seconds=first_crawl_time-node_time)
	if delta.days <= period:
		continue
	if G.in_degree(node_id) < 1:
		continue	
	
	in_link_count = [0 for x in xrange(period)]
	in_edges = G.in_edges_iter(node_id)
	for edge in in_edges:
		source_id = edge[0]
		if nodes[source_id]["user"] == nodes[node_id]["user"]:
			continue
		source_node = nodes[source_id]
		source_time = time.mktime(time.strptime(source_node["uploaded_at"], time_format))
		delta = datetime.timedelta(seconds=source_time - node_time)
		if delta.days < period:
			in_link_count[delta.days] += 1
	for i in xrange(1,period):
		in_link_count[i] = in_link_count[i-1] + in_link_count[i]

	if in_link_count[period-1] > 0:
		old_enough_nodes[node_id] = in_link_count	
		in_link_counts.append(in_link_count)
	else:
		no_link_count += 1
		continue

	indegree = in_link_count[period-1]
	for i in xrange(period):
		in_link_count[i] = in_link_count[i] * 1.0 / indegree

print "There are", len(old_enough_nodes), "that are older than", period, "days and has at least one in-link."
print "There are", no_link_count, "nodes that were disqualified."

xx = np.zeros((period,))
yy = [np.zeros((period,)) for i in xrange(len(percentiles))]
for i in xrange(period):
	xx[i] = i
for day in xrange(period):
	in_link_counts.sort(key=lambda x: x[day])
	values = [in_link_counts[0][day]]
	for i in xrange(1, len(in_link_counts)):
		if in_link_counts[i][day] == values[-1]:
			continue
		else:
			values.append(in_link_counts[i][day])
	for i in xrange(len(percentiles)):
		pos = int(percentiles[i]/100.0*len(values))
		yy[i][day] = values[pos]

plt.figure()
for i in xrange(len(percentiles)):
	plt.plot(xx, yy[i])
plt.show()