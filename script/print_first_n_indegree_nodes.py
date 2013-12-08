import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *

if len(sys.argv) < 3:
	print "python script/print_n_first_indegree_nodes.py <json-file-name> <count>"
	exit()

count = int(sys.argv[2])

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
	index = nodes_and_indegree[n-i][0]
	print index, data["nodes"][index]["nicoid"], nodes_and_indegree[n-i][1], data["nodes"][index]["categories"], "http://www.nicovideo.jp/watch/%s" % data["nodes"][index]["nicoid"]

print
for i in xrange(1,count+1):
	index = nodes_and_indegree[n-i][0]
	print "%d)" % i
	print "{:,}".format(nodes_and_indegree[n-i][1]), "links"
	print "http://www.nicovideo.jp/watch/%s" % data["nodes"][index]["nicoid"]
	print