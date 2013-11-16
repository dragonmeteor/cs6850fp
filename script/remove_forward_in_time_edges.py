import json
import sys
from sets import Set
from StringIO import StringIO

if len(sys.argv) < 2:
	print "Usage: python classify_item.py <input-file> <output-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

nodes = data["nodes"]
for node_name in nodes:
	node = nodes[node_name]
	node["categories"] = []	
	tags = node["tags"]

	# Classify model.
	is_model = False
	for tag in tags:
		tag = tag.lower()
		if tag in model_tag_set:
			is_model = True
	if is_model:
		node["categories"].append("model")

	is_motion = False
	for tag in tags:
		tag = tag.lower()
		if tag in motion_tag_set:
			is_motion = True
	if is_motion:
		node["categories"].append("motion")

	is_tool = False
	for tag in tags:
		tag = tag.lower()
		if tag in tool_tag_set:
			is_motion = True
	if is_tool:
		node["categories"].append("tool")

	is_editing = False
	for tag in tags:
		tag = tag.lower()
		if tag in editing_tag_set:
			is_editing = True
	if is_editing:
		node["categories"].append("editing")

	if len(node["categories"]) == 0:
		node["categories"].append("cg")

	#print

import codecs
fout = codecs.open(sys.argv[2], "w", "utf-8")
json.dump(data, fout, ensure_ascii=False, encoding="utf-8", indent=1)
fout.close()
