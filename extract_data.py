import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


def get_comment_info(single_comment):
	authors = []
	for line in single_comment:
		authors.append(line['author']['_account_id'])
	return authors

df = pd.read_json('test_data_with_comments.json')

for line in df['owner']:
	print(line["_account_id"])

file_comment_tuple_list = []

for i in range(0, len(df['owner'])):
	comments = df['comments'][i]
	if isinstance(comments, dict):
		for key in comments.keys():
			print(key)
			authors = get_comment_info(comments[key])
			for author in authors:
				if df['owner'][i]["_account_id"] == author:
					print('author matches')
				else:
					file_comment_tuple = (key, author)
					print(file_comment_tuple)
					file_comment_tuple_list.append(file_comment_tuple)
print(len(file_comment_tuple_list))

# for line in df['comments']:
# 	if isinstance(line,dict):
# 		for key in line.keys():
# 			get_comment_info(line[key])
			
