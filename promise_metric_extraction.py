import json
import csv
import os
import pathlib
import requests
import pandas as pd
import math
from pathlib import Path
import requests
from datetime import timedelta, date, datetime

def get_all_reviewer_candidates(df):
	candidates = []
	for line in df['owner']:
		if '_account_id' not in line.keys():
			continue
		rever = line['_account_id']
		if rever not in candidates:
			candidates.append(rever)
	print(candidates)

def get_files_for_rev(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		files.append(filename)
	return files

def get_all_files_for_commit(commit):
	all_files = {}
	for key in commit.keys():
		all_files[key] = get_files_for_rev(commit[key])
	return all_files

df = pd.read_json('test_data.json')

get_all_reviewer_candidates(df)