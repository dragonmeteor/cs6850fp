import json
import sys
from sets import Set
from StringIO import StringIO
import time

if len(sys.argv) < 2:
	print "Usage: python remove_forward_in_time_edges.py <input-file> <output-file>"

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

edges = data["edges"]
nodes = data["nodes"]
time_format = "%Y-%m-%d %H:%M:%S %Z"
new_edges = []
for edge in edges:
	v0 = nodes[edge[0]]
	v1 = nodes[edge[1]]
	time0 = time.strptime(v0["uploaded_at"], time_format)
	time1 = time.strptime(v1["uploaded_at"], time_format)
	#print "%s: %s" % (edge[0], time0)
	#print "%s: %s" % (edge[1], time1)
	#exit(0)	
	if time.mktime(time0) > time.mktime(time1):
		new_edges.append(edge)

new_edges.sort()
new_new_edges = []
for i in xrange(len(new_edges)):
	if i == 0:
		new_new_edges.append(new_edges[i])
	elif new_edges[i] != new_edges[i-1]:
		new_new_edges.append(new_edges[i])
data["edges"] = new_new_edges
	
import codecs
fout = codecs.open(sys.argv[2], "w", "utf-8")
json.dump(data, fout, ensure_ascii=False, encoding="utf-8", indent=1)
fout.close()
