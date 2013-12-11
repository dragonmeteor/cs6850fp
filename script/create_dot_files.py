import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *

if len(sys.argv) < 6:
	print "python script/create_dot_files.py <json-file-name> <cascade-count-file> <count> <include-self-link> <file-name-prefix>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

sys.stdout.write("Loading JSON ... ")
json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()
print "DONE"

include_self_link = (sys.argv[4].lower() == "yes")
sys.stdout.write("Constructing graph ... ")
G = construct_item_graph(data, exclude_multi_category_nodes=True, exclude_self_links=(not include_self_link))
print "DONE"

cascades = []
fin = open(sys.argv[2], "rt")
for line in fin.readlines():
	if len(line.strip()) == 0:
		continue
	comps = line.strip().split()
	cascades.append(comps)
fin.close()

count = int(sys.argv[3])
file_name_prefix = sys.argv[5]
nodes = data["nodes"]
for i in xrange(count):	
	file_name = file_name_prefix + ("%04d" % (i+1)) + ".gv"
	sys.stdout.write("Saving %s ... " % file_name)
	start = cascades[i][1]
	H = get_cascade(G, nodes, str(start))
	gen_dot_file(H, file_name)	
	print "DONE"