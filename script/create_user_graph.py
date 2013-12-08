import json
import sys
from sets import Set
from StringIO import StringIO
import time

if len(sys.argv) < 2:
	print "Usage: python create_user_graph.py <input-file> <output-file>"

json_data=open(sys.argv[1])
item_graph = json.load(json_data)
json_data.close()

user_graph = {"nodes": {}, "edges": []}
#user_items = {}
for item_id in item_graph["nodes"]:
	item = item_graph["nodes"][item_id]
	user = item["user"]
	#if user not in user_items:
	#	user_items[user] = []
	if user not in user_graph["nodes"]:
		user_graph["nodes"][user] = {
			"id": user, "categories": [], "item_count": 0,
			"category_count": {"cg":0, "model":0, "motion":0, "tool":0, "editing":0}}	
	categories = item["categories"]
	for cat in categories:
		if cat not in user_graph["nodes"][user]["categories"]:
			user_graph["nodes"][user]["categories"].append(cat)
		user_graph["nodes"][user]["category_count"][cat] += 1
	#user_items[user].append(item_id)
	user_graph["nodes"][user]["item_count"] += 1

	if item["user"] == "":
		print item["nicoid"]

print "Number of nodes with unidentified user =", user_graph["nodes"][""]["item_count"]
del user_graph["nodes"][""]

for user_id in user_graph["nodes"]:
	user = user_graph["nodes"][user_id]
	cat_count = user["category_count"]

	max_cat = "tool"
	for cat in ["model", "motion", "tool", "editing"]:
		if cat_count[max_cat] < cat_count[cat]:
			max_cat = cat
	if cat_count[max_cat] == 0:
		user["category"] = "cg"
	else:
		user["category"] = max_cat

edge_count = {}
edge_involving_no_user = 0
for edge in item_graph["edges"]:
	v0 = item_graph["nodes"][edge[0]]
	v1 = item_graph["nodes"][edge[1]]
	if v0["user"] == "" or v1["user"] == "":
		edge_involving_no_user += 1
		continue
	edge_id = ",".join([v0["user"], v1["user"]])
	if edge_id not in edge_count:
		edge_count[edge_id] = 0
	edge_count[edge_id] += 1

for edge_id in edge_count:
	edge = edge_id.split(",")
	user_graph["edges"].append(edge + [edge_count[edge_id]])

import codecs
fout = codecs.open(sys.argv[2], "w", "utf-8")
json.dump(user_graph, fout, ensure_ascii=False, encoding="utf-8", indent=1)
fout.close()

print "Number of edges associated with no users =", edge_involving_no_user