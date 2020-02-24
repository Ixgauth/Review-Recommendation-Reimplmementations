import requests
import json
import re

S = 1
while True:
	print("S=",S)
	baseURL = f"https://gerrit-review.googlesource.com/changes/?q=project:gerrit&S={S}&n=500&o=ALL_FILES&o=LABELS"
	print(baseURL)
	resp = requests.get(baseURL)
	# resp_parsed = re.sub(r'^jsonp\d+\(|\)\s+$', '', resp.text)

	if(resp.status_code == 200):
	    print("it worked")
	    loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
	    S+=500
	else:
	    break
	if S > 5000:
		break

with open('data.json','w') as outfile:
	outfile.write(resp.content.decode("utf-8").replace(")]}'",'').strip())