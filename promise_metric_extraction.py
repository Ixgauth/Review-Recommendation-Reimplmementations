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


def get_comment_info(single_comment):
	info = []
	for line in single_comment:
		author = line['author']['_account_id']
		info.append(author)
	return info

def get_comment_writers(comments):
	tuple_list = []
	for key in comments.keys():
		if key == "/COMMIT_MSG":
			continue

		comment_info = get_comment_info(comments[key])

		for author in comment_info:
			tuple_list.append(author)
	return tuple_list

def get_all_reviewer_candidates(df):
	candidates = []
	for line in df['owner']:
		if '_account_id' not in line.keys():
			continue
		rever = line['_account_id']
		if rever not in candidates:
			candidates.append(rever)
	for line in df['comments']:
		if isinstance(line, dict):
			new_candidates = get_comment_writers(line)
			for cand in new_candidates:
				if cand not in candidates:
					candidates.append(cand)
	return(candidates)

def get_files_for_rev(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		files.append(filename)
	return files

def get_all_files_for_commit(commit):
	all_files = []
	for key in commit.keys():
		all_files.extend(get_files_for_rev(commit[key]))
	return all_files

def get_files_for_each_change(df):
	files_list = []

	for line in df['revisions']:
		files = get_all_files_for_commit(line)
		files_list.append(files)

	df['files'] = files_list

	return df

def get_all_files(df):
	files_list = []
	for line in df['files']:
		for file in line:
			if file not in files_list:
				files_list.append(file)
	return files_list

def get_authors_for_files(df, files_list):
	file_author_dictionary = {}
	for file in files_list:
		cur_file_dictionary = {}
		total_changes = 0
		for i in range(0, len(df['files'])):
			if file in df['files'][i]:
				owner = df['owner'][i]['_account_id']
				if owner in cur_file_dictionary.keys():
					cur_file_dictionary[owner] = cur_file_dictionary[owner] + 1
				else:
					cur_file_dictionary[owner] = 1
				total_changes += 1
		for author in cur_file_dictionary.keys():
			total_for_author = cur_file_dictionary[author]
			cur_file_dictionary[author] = total_for_author / total_changes
		file_author_dictionary[file] = cur_file_dictionary
	return file_author_dictionary




df = pd.read_json('test_data.json')

df = get_files_for_each_change(df)

files_list = get_all_files(df)

file_to_author_dictionary = get_authors_for_files(df, files_list)