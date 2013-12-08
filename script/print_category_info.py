import json
import sys
from sets import Set
from StringIO import StringIO
import time
import random

if len(sys.argv) < 2:
	print "Usage: python print_category_info.py <input-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

nodes = data["nodes"]
multicat_nodes = []
combo_count = {}
cat_count = {"cg":0, "model":0, "motion":0, "tool":0, "editing":0}
single_cat_count = {"cg":0, "model":0, "motion":0, "tool":0, "editing":0}
for node_id in nodes:
	node = nodes[node_id]
	
	combo = ",".join(node["categories"])
	if combo not in combo_count:
		combo_count[combo] = 0
	combo_count[combo] += 1

	for cat in node["categories"]:
		cat_count[cat] += 1

	if len(node["categories"]) > 1:
		multicat_nodes.append(node_id)

	if len(node["categories"]) == 1:
		single_cat_count[node["categories"][0]] += 1

multicat_nodes_set = Set(multicat_nodes)

edge_count = {}
nodes = data["nodes"]
count = 0
multicat_edge_count = 0
inlinks = {"cg": 0, "model":0, "motion":0, "tool":0, "editing":0}
outlinks = {"cg": 0, "model":0, "motion":0, "tool":0, "editing":0}
for edge in data["edges"]:
	v0 = nodes[edge[0]]
	v1 = nodes[edge[1]]
	c0 = ','.join(v0["categories"])
	c1 = ','.join(v1["categories"])
	edge_type = "%s--%s" % (c0,c1)
	if edge_type not in edge_count:
		edge_count[edge_type] = 0
	edge_count[edge_type] += 1
	
	#if edge_type == "cg--cg":
	#	if count < 20 and random.randint(0, 100) > 99:
	#		print v0["nicoid"], v1["nicoid"]
	#		count += 1

	if edge[0] in multicat_nodes_set or edge[1] in multicat_nodes_set:
		multicat_edge_count += 1

	if len(v0["categories"])==1 and len(v1["categories"])==1:
		inlinks[c1] += 1
		outlinks[c0] += 1		


for category in combo_count:
	print "%s: %d" % (category, combo_count[category])
print

for cat in cat_count:
	print "%s: %d" % (cat, cat_count[cat])
print

edge_types = []
for edge_type in edge_count:
	edge_types.append(edge_type)
edge_types.sort()
	
for edge_type in edge_types:
	print "%s: %d" % (edge_type, edge_count[edge_type])

print
print "Multicategory node count =", len(multicat_nodes)
print "Multicategory edge count =", multicat_edge_count

print
print "Per category statistics"
for cat in ["cg", "model", "motion", "tool", "editing"]:
	print cat, single_cat_count[cat], inlinks[cat], inlinks[cat]*1.0 / single_cat_count[cat], outlinks[cat], outlinks[cat]*1.0 / single_cat_count[cat]

print
print "Latex Table"
cat_name = {"cg": "CG Production", "model": "Modeling", "motion": "Choreography", "tool": "Tool Making", "editing": "Summarizing"}
for cat in ["cg", "model", "motion", "tool", "editing"]:
	sys.stdout.write(cat_name[cat]+ " & ")
	sys.stdout.write("{:,}".format(single_cat_count[cat]) + " & ")
	sys.stdout.write("{:,}".format(inlinks[cat]) + " & ")
	sys.stdout.write("%0.2f" % (inlinks[cat]*1.0 / single_cat_count[cat]) + " & ")
	sys.stdout.write("{:,}".format(outlinks[cat]) + " & ")
	sys.stdout.write("%0.2f" % (outlinks[cat]*1.0 / single_cat_count[cat]))
	if cat != "editing":
		sys.stdout.write("\\\\")
	sys.stdout.write("\n")
