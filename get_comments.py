import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests

with open('smaller_test_data.json') as json_file:
	data = json.load(json_file)

problem_lines = []
print(len(data))

i = 0
for line in data:
	if i % 50 == 0:
		print(i)
	i+=1
	change_id = line["change_id"]
	baseURL = f"https://gerrit-review.googlesource.com/changes/{change_id}/detail"
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		line['details'] = json.loads(resp.content.decode("utf-8").replace(")]}'",''))

		reviewers_qued = line['details']['reviewers']
		if 'REVIEWER' in reviewers_qued.keys():
			reviewers_list = reviewers_qued['REVIEWER']
			account_id_list = []
			reviewer_name_list = []
			owner_id = line['details']['owner']['_account_id']

			for lne in reviewers_list:
				if '_account_id' in lne.keys() and 'name' in lne.keys():
					if lne['_account_id'] == owner_id:
						continue
					if lne['_account_id'] == 1022687:
						continue

					account_id_list.append(lne['_account_id'])
					reviewer_name_list.append(lne['name'])
				else:
					print('problem line', i)
					problem_lines.append(line)

			line['reviewers_account_id'] = account_id_list
			line['reviewers_name_list'] = reviewer_name_list
		else:
			print('problem line', i)
			problem_lines.append(line)

print(len(problem_lines))
for line in problem_lines:
	data.remove(line)
print(len(data))

outfile = open("smaller_test_data_with_reviewers.json", "w")
outfile.write(json.dumps(data))	