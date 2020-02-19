import requests
import json
import re

baseURL = "https://gerrit-review.googlesource.com/changes/?q=project:gerrit&n=1&o=ALL_FILES&o=LABELS"

resp = requests.get(baseURL)
# resp_parsed = re.sub(r'^jsonp\d+\(|\)\s+$', '', resp.text)

if(resp.status_code == 200):
    print(resp.content)
    print("it worked")
    print(json.loads(resp.content))
else:
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

