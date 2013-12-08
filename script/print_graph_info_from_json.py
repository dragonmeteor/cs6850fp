import json
import sys
from sets import Set
from StringIO import StringIO
import time
import networkx as nx

if len(sys.argv) < 2:
	print "Usage: python print_graph_info.py <input-file>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

print "There are %d nodes." % len(data["nodes"])
print "There are %d edges." % len(data["edges"])

if False:
	G = nx.DiGraph()
	for item_name in data["nodes"]:
		#item_data = data["nodes"][item_name]	
		G.add_node(item_name)	
	for edge in data["edges"]:	
		G.add_edge(edge[0], edge[1])

	print "However, according to networkx:"
	print "There are %d nodes." % G.number_of_nodes()
	print "There are %d edges." % G.number_of_edges()

	data["edges"].sort()
	duplicate_count = 0
	for i in xrange(1,len(data["edges"])):
		if data["edges"][i] == data["edges"][i-1]:
			duplicate_count += 1
	print "There are %d duplicated edges" % duplicate_count