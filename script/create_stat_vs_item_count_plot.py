import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys

if len(sys.argv) < 6:
	print "python script/create_stat_vs_item_count_plot.py <json-file-name> <stat-name> <legend> <fit-line> <plot-file-name>"
	exit()

json_data=open(sys.argv[1])
data = json.load(json_data)
json_data.close()

stat_name = sys.argv[2]

count_map = {}
nodes = data["nodes"]
for item_id in nodes:
	item = nodes[item_id]
	if item[stat_name] not in count_map:
		count_map[item[stat_name]] = 0
	count_map[item[stat_name]] += 1

max_item_count = 0
max_count = 0
for count in count_map:
	if max_item_count < count_map[count]:
		max_item_count = count_map[count]
		max_count = count

print "count with maximum item =", max_count
print "associated item count", max_item_count

def save_power_law_graph(the_map, xlabel, ylabel, filename, fitLine=True):
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
	if fitLine:
		plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	if fitLine:
		plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
	plt.savefig(filename)

def save_scatter_graph(the_map, xlabel, ylabel, filename):
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
	
	plt.scatter(np.log(xx), yy)
	plt.plot(lx, ly, 'g')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title("best fit line: %fx + %f" % (coeffs[0], coeffs[1]))
	plt.savefig(filename)

fit_line = bool(sys.argv[4])
print fit_line

save_power_law_graph(count_map, "log(" + sys.argv[3] + ")", "log(number of items)", sys.argv[5], fit_line)