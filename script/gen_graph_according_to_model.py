import json
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys
from mmd_graph_lib import *
import math

if len(sys.argv) < 3:
	print "python script/gen_graph_according_to_model.py <spec-file> <output-file>"
	exit()

spec_file_name = sys.argv[1]
output_file_name = sys.argv[2]

fin = open(spec_file_name, "r")
lines = fin.readlines()

num_items = int(lines[0])
num_users = int(lines[1])
user_item_exponent = float(lines[2])
max_user_item_count = float(lines[3])
self_cite_prob = float(lines[4])
no_cite_prob = float(lines[5])

cat_prob = {}
line_index = 6
for cat in ["cg", "model", "motion", "tool", "editing"]:
	cat_prob[cat] = float(lines[line_index])
	line_index += 1

misiden_prob = {}
for cat in ["model", "motion", "tool", "editing"]:
	misiden_prob[cat] = float(lines[line_index])
	line_index += 1

fin.close()

user_count_scale = [0 for i in xrange(max_user_item_count)]
for i in xrange(max_user_item_count):
	user_count_scale[i] = ((i+1)*1.0)**user_item_exponent
user_count_scale_sum = 0
for i in xrange(max_user_item_count):
	user_count_scale_sum += user_count_scale[i]
scale_factor = user_count / user_count_scale_sum
for i in xrange(max_user_item_count):
	user_count_scale[i] *= scale_factor
user_count_by_num_item = [0 for i in xrange(max_user_item_count)]
for i in xrange(max_user_item_count):
	user_count_by_num_item[i] = user_count_scale[i]))

G = nx.DiGraph()
