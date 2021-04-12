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

def get_files_commit_old(commit):
	all_files = {}
	for key in commit.keys():
		all_files[key] = get_files_for_rev(commit[key])
	return all_files

def get_files_for_each_change(df):
	files_list = []
	# print(df['owner'][0])

	for line in df['revisions']:
		files = get_all_files_for_commit(line)
		files_list.append(files)

	# print(files_list)
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

def get_reviewers_for_files(df, files_list):
	file_reviewers_dictionary = {}
	for file in files_list:
		cur_file_dictionary = {}
		total_changes = 0
		for i in range(0, len(df['files'])):
			if file in df['files'][i]:
				reviewers = df['reviewers_account_id'][i]
				if type(reviewers) == float:
					continue
				for rever in reviewers: 
					if rever in cur_file_dictionary.keys():
						cur_file_dictionary[rever] = cur_file_dictionary[rever] + 1/len(reviewers)
					else:
						cur_file_dictionary[rever] = 1/len(reviewers)
				total_changes += 1
		for rever in cur_file_dictionary.keys():
			total_for_rever = cur_file_dictionary[rever]
			cur_file_dictionary[rever] = total_for_rever / total_changes
		file_reviewers_dictionary[file] = cur_file_dictionary
	return file_reviewers_dictionary

def get_author_familiarity_dict(df):
	author_familiarity_dict = {}
	for i in range(0, len(df['owner'])):
		current_familiarity_dict = {}
		author = line['_account_id'][i]
		if author in author_familiarity_dict.keys():
			current_familiarity_dict = author_familiarity_dict[author]
		reviewers = df['reviewers_account_id'][i]
		if type(reviewers) == float:
				continue
		for rever in reviewers:
			if rever in current_familiarity_dict:
				current_familiarity_dict[rever] = current_familiarity_dict[rever] + 1
			else:
				current_familiarity_dict[rever] = 1
		author_familiarity_dict[author] = current_familiarity_dict
	return author_familiarity_dict

def find_last_comments(df, number_of_comments):
	number_obtained = 0

	list_of_reviewers = []

	list_of_lines = []

	number_checked = 0

	number_merges = 0

	len_orig_df = len(df['owner'])

	while number_obtained < number_of_comments:
		number_checked +=1
		if number_checked == len_orig_df:
			break
		elif number_checked % 200 == 0:
			print(number_checked, '  ', number_obtained)
		final_line = df.tail(1)
		line_status = final_line['status'].iloc[0]
		description = final_line['subject'].iloc[0]
		owner = final_line['owner'].iloc[0]['_account_id']
		description = description.lower()
		reviewrs = final_line['reviewers_account_id'].iloc[0]
		skip = False
		if 'merge branch' in description:
			skip = True
			number_merges+=1
		if line_status != 'MERGED' and line_status != 'ABANDONED':
			skip = True
		if type(reviewrs) == list and len(reviewrs) == 1:
			if owner == reviewrs[0]:
				skip = True
				print(reviewrs, '  ', owner)
		if skip == False:
			actual_reviewer_list = final_line['reviewers_name_list']
			if not pd.isnull(actual_reviewer_list).all() and len(actual_reviewer_list) > 0:
				if len(final_line['reviewers_name_list']) > 0:
					revisions = final_line['revisions']
					revs_dict = revisions.to_dict()
					found_a_file = False
					for key in revs_dict.keys():
						rev = revs_dict[key]
						files_in_change = get_files_commit_old(rev)
						for kye in files_in_change.keys():
							if len(files_in_change[kye]) != 0:
								found_a_file = True
							else: 
								continue
					if found_a_file == False:
						print('no files')
					else:
						reviewers = final_line['reviewers_name_list'].to_list()[0]
						if not reviewers:
							print(reviewers)
						else:
							number_obtained+=1
							df_line = final_line.values.tolist()
							list_of_lines.append(df_line)
		# 	else:
		# 		print('no reviewers')
		# else:
		# 	print('change ongoing or merge')

		df.drop(df.tail(1).index,inplace=True)
	final_list = []
	for line in list_of_lines:
		final_list.append(line[0])

	df_test = pd.DataFrame(final_list, columns = df.columns)
	return df_test


new_df = pd.read_json('test_data_without_detail.json')

# list_of_lines = []

# for i in range(0, 30):
# 	final_line = new_df.tail(1)
# 	df_line = final_line.values.tolist()
# 	list_of_lines.append(df_line)
# 	new_df.drop(new_df.tail(1).index,inplace=True)


# final_list = []
# for line in list_of_lines:
# 	final_list.append(line[0])

# df = pd.DataFrame(final_list, columns = new_df.columns)

# df.reset_index(inplace = True)


# df = get_files_for_each_change(df)

# files_list = get_all_files(df)

# file_to_author_dictionary = get_authors_for_files(df, files_list)

# file_to_reviewers_dict = get_reviewers_for_files(df, files_list)

# for line in file_to_reviewers_dict.keys():
# 	print(line, '  ', file_to_reviewers_dict[line])

print(len(new_df['owner']))

df_tail = find_last_comments(new_df.copy(), len(new_df['owner']))

print(len(df_tail['owner']))

# df_tail.to_csv('return_trip/test.csv', index = False, header = True)
