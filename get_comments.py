import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


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

for line in data:
	change_id = line["change_id"]
	baseURL = f"https://gerrit-review.googlesource.com/changes/{change_id}/comments"
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		print("it worked")
		line["comments"] = resp.content.decode("utf-8").replace(")]}'",'')

outfile = open("test_data_with_comments.json", "w")
outfile.write(json.dumps(data))