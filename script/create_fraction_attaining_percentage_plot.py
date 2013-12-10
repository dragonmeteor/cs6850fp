import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *
import time
import datetime

if len(sys.argv) < 8:
	print "python script/create_fraction_attaining_percentage_plot.py <json-file-name> <period-in-days> <min-indegree> <max-indegree> <include-self-link> <output-file-name> <percentile-0> <percentile-1> ..."
	exit()

period = int(sys.argv[2])
min_indegree = int(sys.argv[3])
max_indegree = int(sys.argv[4])
include_self_link = False
if sys.argv[5].lower() == "yes":
	include_self_link = True
output_file_name = sys.argv[6]
percentiles = []
for i in xrange(7, len(sys.argv)):
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
in_link_counts = {}
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
		if (not include_self_link) and nodes[source_id]["user"] == nodes[node_id]["user"]:
			continue
		source_node = nodes[source_id]
		source_time = time.mktime(time.strptime(source_node["uploaded_at"], time_format))
		delta = datetime.timedelta(seconds=source_time - node_time)
		if delta.days < period:
			in_link_count[delta.days] += 1
	for i in xrange(1,period):
		in_link_count[i] = in_link_count[i-1] + in_link_count[i]

	if in_link_count[period-1] >= min_indegree and in_link_count[period-1] <= max_indegree and len(node["categories"]) == 1:
		old_enough_nodes[node_id] = in_link_count	
		in_link_counts[node_id] = in_link_count
	else:
		no_link_count += 1
		continue

	indegree = in_link_count[period-1]
	for i in xrange(period):
		in_link_count[i] = in_link_count[i] * 100.0 / indegree

print "There are", len(old_enough_nodes), "that are older than", period, "days and has at least one in-link."
print "There are", no_link_count, "nodes that were disqualified."

xx = np.zeros((period,))
yy = [np.zeros((period,)) for i in xrange(len(percentiles))]
for i in xrange(period):
	xx[i] = i
for node_id in in_link_counts:
	pos = 0
	in_link_count = in_link_counts[node_id]
	for day in xrange(period):
		while pos < len(percentiles) and in_link_count[day] >= percentiles[pos]:
			yy[pos][day] += 1
			pos += 1

for i in xrange(len(percentiles)):
	for day in xrange(1,period):
		yy[i][day] = yy[i][day-1] + yy[i][day]

convex_count = {"all": 0, "cg":0, "model":0, "motion":0, "tool":0, "editing":0}
linear_count = {"all": 0, "cg":0, "model":0, "motion":0, "tool":0, "editing":0}
concave_count = {"all": 0, "cg":0, "model":0, "motion":0, "tool":0, "editing":0}
for node_id in in_link_counts:
	in_link_count = in_link_counts[node_id]
	node = nodes[node_id]
	min_diff = 0
	max_diff = 0
	more_day = 0
	less_day = 0
	area_under_curve = 0
	count = 0
	for j in xrange(period):
		diff = in_link_count[j] - j * 100.0 / (period-1)
		if min_diff > diff:
			min_diff = diff			
		if max_diff < diff:
			max_diff = diff
		if diff > 0:
			less_day += 1
		if diff < 0:
			more_day += 1
		area_under_curve += diff
	if abs(area_under_curve) < period*5:
		linear_count["all"] += 1
		linear_count[node["categories"][0]] += 1
		if False:
			if count == 1:
				pass
			else:
				xx = np.zeros((period,))
				yy = np.zeros((period,))
				zz = np.zeros((period,))
				for k in xrange(period):
					xx[k] = k
					yy[k] = in_link_count[k]
					zz[k] = k * 100.0 / (period-1)
				plt.figure()
				plt.plot(xx, yy)
				plt.plot(xx, zz)
				plt.show()
	elif area_under_curve >= period * 5:
		concave_count["all"] += 1
		concave_count[node["categories"][0]] += 1
	else:
		convex_count["all"] += 1
		convex_count[node["categories"][0]] += 1
	#print "max_diff =", max_diff
	#print "min_diff =", min_diff
	#if min_diff >= -10 and max_diff <= 10:
	#	print "less_day", less_day
	#	print "more_day", more_day
	#	if abs(less_day - more_day) < period / 10:
	#		linear_count += 1
	#	elif less_day - more_day >= period / 10:
	#		concave_count += 1
	#	else:
	#		convex_count += 1
	#elif max_diff > 10:
	#	concave_count += 1
	#else:
	#	convex_count += 1
	#if the_sum > period:
	#	concave_count += 1
	#elif the_sum < -period:
	#	convex_count += 1	
	#else:
	#	linear_count += 1

cat_name = {"cg": "CG Production", "model": "Modeling", "motion":"Choreography", "tool":"Tool Making", "editing": "Summarizing", "all": "All"}
for cat in ["cg", "model", "motion", "tool", "editing", "all"]:
	sys.stdout.write(cat_name[cat] + " & ")
	sys.stdout.write("%d" % convex_count[cat])
	sys.stdout.write(" & ")
	sys.stdout.write("%d" % linear_count[cat])
	sys.stdout.write(" & ")
	sys.stdout.write("%d" % concave_count[cat])
	sys.stdout.write(" & ")
	sys.stdout.write("%d" % (convex_count[cat] + linear_count[cat] + concave_count[cat]))
	sys.stdout.write(" \\\\\n")

plt.figure()
plots = []
legends = []
for i in xrange(len(percentiles)):
	plt.plot(xx, yy[i], label=("%d%%" % percentiles[i]))	
plt.legend(loc=4, borderaxespad=0.)
plt.xlabel("Number of days since uploaded")
plt.ylabel("Number of items the stated fraction of indegree")
#plt.show()
plt.savefig(output_file_name)