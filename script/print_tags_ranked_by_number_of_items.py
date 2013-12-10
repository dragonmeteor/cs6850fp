import json
import sys
from sets import Set
from StringIO import StringIO
import time
import sys

if len(sys.argv) < 2:
	print "Usage: python print_tag_ranked_by_number_of_items.py <input-file> <output-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

nodes = data["nodes"]
tag_count = {}
for node_id in nodes:
	node = nodes[node_id]
	for tag in node["tags"]:
		tag = tag.lower()
		if tag not in tag_count:
			tag_count[tag] = 0
		tag_count[tag] += 1

import codecs
fout = codecs.open(sys.argv[2], "w", "utf-8")
tags = tag_count.keys()
tags = sorted(tags, key=lambda x: tag_count[x], reverse=True)
count = 0
for tag in tags:	
	fout.write(tag)
	fout.write(" ") 
	fout.write(str(tag_count[tag]))
	fout.write("\n")
	count += 1
	if count == 300:
		break
fout.close()

