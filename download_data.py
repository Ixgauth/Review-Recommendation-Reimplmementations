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

for line in json_list:
	change_id = line["change_id"]
	baseURL = f"https://gerrit-review.googlesource.com/changes/{change_id}/comments"
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		line["comments"] = json.loads(resp.content.decode("utf-8").replace(")]}'",''))


# new_df = pd.DataFrame(json_list)
# new_df.to_csv('test_data_with_comments.csv', index = False, header = True)

outfile = open("test_data_with_comments.json", "w")
outfile.write(json.dumps(json_list))

# print(json_list[0]["comments"])
# for line in json_list:
# 	outfile.write(json.dumps(line))


# df = pd.DataFrame(json_list)
# df.to_csv('test_data.json', index = False, header=False)