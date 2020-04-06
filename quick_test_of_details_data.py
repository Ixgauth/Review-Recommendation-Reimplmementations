import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


with open('test_data_with_reviewers.json') as json_file:
	data = json.load(json_file)

print(data[0].keys())
i = 0
x = 0
for line in data:
	if 'details' in line.keys():
		del line['details']
	else:
		x+=1
	if i % 1000 == 0:
		print(i)
	i+=1

outfile = open("test_data_without_detail.json", "w")
outfile.write(json.dumps(data))	