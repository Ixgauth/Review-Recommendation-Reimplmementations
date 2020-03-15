import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests


with open('test_data_with_comments.json') as json_file:
	data = json.load(json_file)


data_items = data[0].items()
data_list = list(data_items)

columns = []
first_row = []

for line in data_list:
	columns.append(line[0])
	first_row.append(line[1])

# for line in first_row:
# 	print(line)

df = pd.DataFrame([first_row], columns = columns)

i =0

for line in data:
	if i == 0:
		i+=1
		continue
	if(len(line)!= len(columns)):
		print("problem")
		continue
	print("gothere")
	data_items_loop = line.items()
	data_list_loop = list(data_items_loop)
	row = []
	for line_loop in data_list_loop:
		row.append(line_loop[1])
	df2 = pd.DataFrame([row], columns = columns)
	df.append(df2)
print(df)