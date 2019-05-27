#!/usr/bin/python
# -*-coding:utf-8-*-

import json
import os
import sys


# Print the tree recursively with given path prefix
def check_tree(tree, prefix, f_write):
	if isinstance(tree, dict):
		for k, v in tree.items():
			prefix_path = prefix + "." + k
			if isinstance(v, dict) or isinstance(v, list):  # continue sub-tree
				check_tree(v, prefix_path, f_write)
			else:  # leaf
				f_write.write("{}={}\n".format(prefix_path, v))
	elif isinstance(tree, list):
		for i, v in enumerate(tree):
			prefix_path = "{}[{}]".format(prefix, i)
			if isinstance(v, dict) or isinstance(v, list):  # continue sub-tree
				check_tree(v, prefix_path, f_write)
			else:  # leaf
				f_write.write("{}={}\n".format(prefix_path, v))
	else:  # json only allow dict or list structure
		print("Wrong format of json tree")


# Process all json files under the path
def process(directory):
	for f in os.listdir(directory):
		if f.endswith(".block.json"):
			file_name = os.path.join(json_dir, f)
			f_read = open(file=file_name, mode="r", encoding='utf-8')
			f_write = open(file=file_name+"-flat.json", mode="w", encoding='utf-8')
			check_tree(json.load(f_read), "", f_write)
			f_read.close()
			f_write.close()
		else:
			print("Ignore non-json file {}".format(f))


# Usage python json_flatter.py [path_containing_json_files]
# Print all json elements in flat structure
# e.g.,
# {
#	"a": {
#       	"b": ["c", "d"]
#		 }
#  }
# ==>
# a.b[0]=c
# a.b[1]=d
if __name__ == '__main__':
	json_dir = "../raft/channel-artifacts/"
	if len(sys.argv) > 1:
		json_dir = sys.argv[1]

	print("Will process json files under {}".format(json_dir))
	process(json_dir)
