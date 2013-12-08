import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys

if len(sys.argv) < 3:
	print "python script/create_item_count_vs_user_plot.py <json-file-name> <graph-file-name>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

count_map = {}
nodes = data["nodes"]
for user_id in nodes:
	user = nodes[user_id]
	if user["item_count"] not in count_map:
		count_map[user["item_count"]] = 0
	count_map[user["item_count"]] += 1

max_count = 0
for count in count_map:
	if max_count < count:
		max_count = count
print "max_count =", max_count
for user_id in nodes:
	user = nodes[user_id]
	if (user["item_count"] == max_count):
		print user_id

#count_dist = [0 for i in xrange(max_count+1)]
#for count in count_map:
#	count_dist[count] = count_map[count]
#for i in xrange(1, max_count+1):
#	count_dist[i] = count_dist[i] + count_dist[i-1]

def show_power_law_graph(the_map, xlabel, ylabel):
	in_degree_map = the_map.copy()

	if 0 in in_degree_map:
		del in_degree_map[0]
	count = len(in_degree_map)
	xx = np.zeros((count,))
	yy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xx[count] = indeg
			yy[count] = in_degree_map[indeg]
			count += 1

	remove_list = []
	for indeg in in_degree_map:
		count = in_degree_map[indeg]
		if count == 1:
			remove_list.append(indeg)
	for indeg in remove_list:
		del in_degree_map[indeg]
	count = len(in_degree_map)
	xxxx = np.zeros((count,))
	yyyy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xxxx[count] = indeg
			yyyy[count] = in_degree_map[indeg]
			count += 1
	coeffs = np.polyfit(np.log(xxxx), np.log(yyyy), 1)
	right = -coeffs[1] / coeffs[0]
	lx = np.linspace(0,right,1000)
	ly = lx*coeffs[0] + coeffs[1]
	
	plt.scatter(np.log(xx), np.log(yy))
	plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
	plt.show()

def save_power_law_graph(the_map, xlabel, ylabel, filename):
	in_degree_map = the_map.copy()

	if 0 in in_degree_map:
		del in_degree_map[0]
	count = len(in_degree_map)
	xx = np.zeros((count,))
	yy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xx[count] = indeg
			yy[count] = in_degree_map[indeg]
			count += 1

	remove_list = []
	for indeg in in_degree_map:
		count = in_degree_map[indeg]
		if count == 1:
			remove_list.append(indeg)
	for indeg in remove_list:
		del in_degree_map[indeg]
	count = len(in_degree_map)
	xxxx = np.zeros((count,))
	yyyy = np.zeros((count,))
	count = 0
	for indeg in in_degree_map:
		if indeg != 0:
			xxxx[count] = indeg
			yyyy[count] = in_degree_map[indeg]
			count += 1
	coeffs = np.polyfit(np.log(xxxx) / np.log(10.0), np.log(yyyy) / np.log(10.0), 1)
	right = -coeffs[1] / coeffs[0]
	lx = np.linspace(0,right,1000)
	ly = lx*coeffs[0] + coeffs[1]
	
	plt.scatter(np.log(xx) / np.log(10.0), np.log(yy) / np.log(10.0))
	plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
	plt.savefig(filename)



save_power_law_graph(count_map, "log(number of items uploaded)", "log(number of creators)", sys.argv[2])

#xx = range(1, max_count+1)
#yy = count_dist[1:]

#plt.scatter(np.log(xx), np.log(yy))
#plt.plot(lx, ly, 'g')
#plt.xlabel(xlabel)
#plt.ylabel(ylabel)
#plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
#plt.show()