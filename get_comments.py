import json
import csv
import pandas as pd
import math
from pathlib import Path


def intake_data_frame(filename):
	with open(filename) as file:
		data = json.load(file)

	df = pd.DataFrame(data["commits"])
	return df

# data = []
# for line in open('test_data.json', 'r'):
# 	# print(line)
# 	data.append(json.loads(line))

# df = pd.DataFrame(data)

with open('test_data.json') as json_file:
	data = json.load(json_file)

print(data[0]['change_id'])