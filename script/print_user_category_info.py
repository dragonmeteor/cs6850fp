import json
import sys
from sets import Set
from StringIO import StringIO
import time
import sys

if len(sys.argv) < 2:
	print "Usage: python print_user_category_info.py <input-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

nodes = data["nodes"]
cat_count = {"cg":0, "model":0, "motion":0, "tool":0, "editing":0}
item_count = {"cg": 0, "model":0, "motion":0, "tool":0, "editing":0}
for node_id in nodes:
	node = nodes[node_id]
	cat_count[node["category"]] += 1
	item_count[node["category"]] += node["item_count"]

inlinks = {"cg": 0, "model":0, "motion":0, "tool":0, "editing":0}
outlinks = {"cg": 0, "model":0, "motion":0, "tool":0, "editing":0}
edge_count = {}
self_link_count = 0
for edge in data["edges"]:
	if edge[0] == edge[1]:
		self_link_count += edge[2]
		continue
	v0 = nodes[edge[0]]
	v1 = nodes[edge[1]]
	c0 = v0["category"]
	c1 = v1["category"]
	edge_type = "%s--%s" % (c0,c1)
	if edge_type not in edge_count:
		edge_count[edge_type] = 0
	edge_count[edge_type] += edge[2]
	inlinks[c1] += edge[2]
	outlinks[c0] += edge[2]

for cat in ["cg", "model", "motion", "tool", "editing"]:
	print "%s: %d %0.2f" % (cat, cat_count[cat], cat_count[cat]*100.0/len(nodes))
print

edge_types = []
for edge_type in edge_count:
	edge_types.append(edge_type)
edge_types.sort()
	
for edge_type in edge_types:
	print "%s: %d" % (edge_type, edge_count[edge_type])	
print

cat_name = {"cg": "CG Producers", "model": "Modelers", "motion": "Choreographers", "tool": "Tool Makers", "editing": "Summarizers"}
for cat0 in ["cg", "model", "motion", "tool", "editing"]:
	sys.stdout.write(cat_name[cat0])
	for cat1 in ["cg", "model", "motion", "tool", "editing"]:
		edge_type = "%s--%s" % (cat0, cat1)
		sys.stdout.write(" & ")		
		sys.stdout.write("{:,}".format(edge_count[edge_type]))
	print " \\\\"

print 
print "Per category statistics"
for cat in ["cg", "model", "motion", "tool", "editing"]:
	print cat, cat_count[cat], item_count[cat], item_count[cat] * 1.0 / cat_count[cat], inlinks[cat], inlinks[cat]*1.0/item_count[cat], inlinks[cat]*1.0/cat_count[cat], outlinks[cat], outlinks[cat]*1.0/item_count[cat], outlinks[cat]*1.0/cat_count[cat]
print
print "Number of self links =", self_link_count

print
print "Latex Table"
for cat in ["cg", "model", "motion", "tool", "editing"]:
	sys.stdout.write(cat_name[cat]+ " & ")
	sys.stdout.write("{:,}".format(cat_count[cat]) + " & ")
	sys.stdout.write("{:,}".format(item_count[cat]) + " & ")
	sys.stdout.write("%0.2f" % (item_count[cat] * 1.0 / cat_count[cat]) + " & ")
	sys.stdout.write("{:,}".format(inlinks[cat]) + " & ")
	sys.stdout.write("%0.2f" % (inlinks[cat] * 1.0 / item_count[cat]) + " & ")
	sys.stdout.write("{:,}".format(outlinks[cat]) + " & ")
	sys.stdout.write("%0.2f" % (outlinks[cat] * 1.0 / item_count[cat]))
	if cat != "editing":
		sys.stdout.write("\\\\")
	sys.stdout.write("\n")

if False:	
	combo_count = {}	
	for node_id in nodes:
		node = nodes[node_id]

		node["categories"].sort()	
		combo = ",".join(node["categories"])
		if combo not in combo_count:
			combo_count[combo] = 0
		combo_count[combo] += 1

		for cat in node["categories"]:
			cat_count[cat] += 1

	edge_count = {}
	nodes = data["nodes"]
	for edge in data["edges"]:
		v0 = nodes[edge[0]]
		v1 = nodes[edge[1]]
		c0 = ','.join(v0["categories"])
		c1 = ','.join(v1["categories"])
		edge_type = "%s--%s" % (c0,c1)
		if edge_type not in edge_count:
			edge_count[edge_type] = 0
		edge_count[edge_type] += edge[2]

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