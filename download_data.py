import requests
import json
import re
from datetime import timedelta, date

def get_dates(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

start_date = date(2019, 1, 1)
end_date = date(2019, 12, 31)
total_string = ''
for single_date in get_dates(start_date, end_date):
	print(single_date.strftime("%Y-%m-%d"))
	day_start = '{' + str(single_date) + ' 00:00:00.000}'
	day_end =  '{' + str(single_date) + ' 23:59:99.999}'
	baseURL = f"https://gerrit-review.googlesource.com/changes/?q=project:gerrit AND after:{day_start} AND before:{day_end}&o=LABELS"
	print(baseURL)
	resp = requests.get(baseURL)
	if(resp.status_code == 200):
		print("it worked")
		loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
		total_string = total_string + resp.content.decode("utf-8").replace(")]}'",'').strip()
	else:
		print(resp.status_code)

# print(total_string)
with open('data.json','w') as outfile:
	outfile.write(total_string)