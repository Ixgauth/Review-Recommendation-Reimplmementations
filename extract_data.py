import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


def get_comment_info(single_comment):
	info = []
	for line in single_comment:
		info_tuple = line['author']['_account_id'], line['updated']
		info.append(info_tuple)
	return info

# def get_comment_times(comment):


def get_comment_tuples(owner, comments):
	tuple_list = []
	for key in comments.keys():
		comment_info = get_comment_info(comments[key])

		for author in comment_info:
			if owner == author[0]:
				continue
			else:
				file_comment_tuple = (key, author[0],author[1])
				tuple_list.append(file_comment_tuple)
	return tuple_list

df = pd.read_json('test_data_with_comments.json')

file_comment_tuple_list = []

for i in range(0, len(df['owner'])):
	comments = df['comments'][i]
	if isinstance(comments, dict):
		file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)
			
print(len(file_comment_tuple_list))
