import pandas as pd
import os
import math


def get_files_for_rev(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		files.append(filename)
	return files

def get_all_files_for_commit(commit):
	all_files = []
	for key in commit.keys():
		all_files = all_files + get_files_for_rev(line[key])
	return all_files
def get_files_for_rev_system(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		topdir = filename.split('/')[0]
		files.append(topdir)
	return files

def get_comment_files(commit):
	files = []
	for line in commit.keys():
		files.append(line)
	return(files)
def get_system_level_dir(commit):
	all_files = []
	for key in commit.keys():
		all_files = all_files + get_files_for_rev_system(commit[key])
	return all_files

def get_all_reviewers(df):
	number_of_lines_with_revs = 0
	list_of_reviewers = []
	for line in df['reviewers_name_list']:
		if type(line) == list and len(line) > 0:
			number_of_lines_with_revs += 1
			for reviewer in line:
				if reviewer in list_of_reviewers:
					continue
				else:
					list_of_reviewers.append(reviewer)
		else:
			print("nothing")
	return list_of_reviewers, number_of_lines_with_revs

df = pd.read_json('test_data_without_detail.json')

list_of_reviewers, number_of_lines_with_revs = get_all_reviewers(df)
print(list_of_reviewers)
print(len(list_of_reviewers))
print(len(df))
print(number_of_lines_with_revs)