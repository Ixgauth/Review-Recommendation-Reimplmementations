import requests
import json
import re
from datetime import timedelta, date
import pandas as pd

def get_dates(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

start_date = date(2018, 1, 1)
end_date = date(2020, 1, 1)
json_list = []
for single_date in get_dates(start_date, end_date):
	print(single_date.strftime("%Y-%m-%d"))
	day_start = '{' + str(single_date) + ' 00:00:00.000}'
	day_end =  '{' + str(single_date) + ' 23:59:99.999}'
	baseURL = f"https://gerrit-review.googlesource.com/changes/?q=project:gerrit AND after:{day_start} AND before:{day_end}&o=ALL_REVISIONS&o=ALL_FILES&o=LABELS"
	print(baseURL)
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		print("it worked")
		loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
		for row in loaded:
			json_list.append(row)
	else:
		print(resp.status_code)

# df = pd.DataFrame(json_list)
# df.to_csv('test_data.csv', index = False, header=True)

# outfile = open("some_crap.json", "w")

i = 0
for line in json_list:
	if i % 100 == 0:
		print(i)
	i+=1
	change_id = line["change_id"]
	strng = "CHANGE ID: " + change_id
	baseURL = f"https://gerrit-review.googlesource.com/changes/{change_id}/comments"
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		line["comments"] = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
		reviewers_qued = line['reviewers']
		reviewers_list = reviewers_qued['REVIEWER']
		account_id_list = []
		assigned_account_id_list = []
		reviewer_name_list = []
		assigned_reviewer_name_list = []
		owner_id = line['owner']['_account_id']

		for key in line['comments'].keys():
			for comment in line['comments'][key]:
				if comment['author']['_account_id'] not in account_id_list:
					if comment['author']['_account_id'] == owner_id:
						continue
					account_id_list.append(comment['author']['_account_id'])
				if comment['author']['name'] not in reviewer_name_list:
					reviewer_name_list.append(comment['author']['name'])
		for key in line['labels'].keys():
			for kye in line['labels'][key].keys():
				if type(line['labels'][key][kye]) == dict:
					if line['labels'][key][kye]['_account_id'] not in account_id_list:
						if line['labels'][key][kye]['_account_id'] == owner_id:
							continue
						account_id_list.append(line['labels'][key][kye]['_account_id'])


		for lne in reviewers_list:
			if lne['_account_id'] == owner_id:
				continue
			if lne['_account_id'] == 1022687:
				continue

			assigned_account_id_list.append(lne['_account_id'])
		if 'CC' in reviewers_qued.keys():
			reviewers_list = reviewers_qued['CC']
			for lne in reviewers_list:
				if '_account_id' not in lne.keys():
					continue
				if lne['_account_id'] == owner_id:
					continue
				if lne['_account_id'] == 1022687:
					continue
				if lne['_account_id'] in assigned_account_id_list:
					continue
				assigned_account_id_list.append(lne['_account_id'])
		line['reviewers_account_id'] = account_id_list
		line['reviewers_name_list'] = reviewer_name_list
		line['assigned_reviewer_account_id'] = assigned_account_id_list


# new_df = pd.DataFrame(json_list)
# new_df.to_csv('test_data_with_comments.csv', index = False, header = True)

outfile = open("promise_data_unclean.json", "w")
outfile.write(json.dumps(json_list))

# print(json_list[0]["comments"])
# for line in json_list:
# 	outfile.write(json.dumps(line))


# df = pd.DataFrame(json_list)
# df.to_csv('test_data.json', index = False, header=False)