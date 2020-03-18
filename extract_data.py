import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


def get_comment_info(single_comment):
	for line in single_comment:
		if 'line' in line.keys():
			print(line['line'])
		else:
			print('nope')

df = pd.read_json('test_data_with_comments.json')

for line in df['comments']:
	if isinstance(line,dict):
		for key in line.keys():
			get_comment_info(line[key])
