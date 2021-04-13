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

def get_author_familiarity_dict(df, author):
	author_familiarity_dict = {}
	total = 0
	for i in range(0, len(df['owner'])):
		cur_author =  df['owner'][i]['_account_id']
		if cur_author == author:
			reviewers = df['reviewers_account_id'][i]
			if type(reviewers) == float:
					continue
			for rever in reviewers:
				if rever == author:
					continue
				if rever in author_familiarity_dict.keys():
					author_familiarity_dict[rever] = author_familiarity_dict[rever] + 1
					total +=1
				else:
					author_familiarity_dict[rever] = 1
					total +=1
	for key in author_familiarity_dict.keys():
		author_familiarity_dict[key] = author_familiarity_dict[key] / total
	return author_familiarity_dict

def get_participation_rate(df, candidate):
	total_requested = 0
	total_participated = 0

	for i in range(0, len(df['owner'])):
		actual_revs = df['reviewers_account_id'][i]
		assigned_revs = df['assigned_reviewer_account_id'][i]
		if candidate in actual_revs or candidate in assigned_revs:
			total_requested += 1
		if candidate in actual_revs:
			total_participated += 1
	if total_requested == 0:
		return 0
	particpation_rate = total_participated / total_requested
	return particpation_rate


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
			actual_reviewer_list = final_line['reviewers_account_id']
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
						reviewers = final_line['reviewers_account_id'].to_list()[0]
						if not reviewers:
							print(reviewers)
						else:
							number_obtained+=1
							df_line = final_line.values.tolist()
							list_of_lines.append(df_line)

		df.drop(df.tail(1).index,inplace=True)
	final_list = []
	for line in list_of_lines:
		final_list.append(line[0])

	df_test = pd.DataFrame(final_list, columns = df.columns)
	return df_test


def compute_metrics(df, change_df):
	files_list = get_all_files(change_df)

	file_author_dict = get_authors_for_files(df, files_list)

	metrics_reached_dictionary = {}

	code_ownership_metric_dict = {}
	total_number_files = len(file_author_dict.keys())
	for key in file_author_dict.keys():
		response = file_author_dict[key]
		for kye in response.keys():
			if kye in code_ownership_metric_dict:
				code_ownership_metric_dict[kye] = code_ownership_metric_dict[kye] + response[kye] / total_number_files
			else:
				code_ownership_metric_dict[kye] = response[kye] / total_number_files
				if kye not in metrics_reached_dictionary.keys():
					metrics_reached_dictionary[kye] = 1
				else:
					metrics_reached_dictionary[kye] = metrics_reached_dictionary[kye] + 1

	reviewer_author_dictionary = get_reviewers_for_files(df, files_list)

	reviewing_experience_metric = {}
	for key in reviewer_author_dictionary.keys():
		response = reviewer_author_dictionary[key]
		for kye in response.keys():
			if kye in reviewing_experience_metric.keys():
				reviewing_experience_metric[kye] = reviewing_experience_metric[kye] + response[kye] / total_number_files
			else:
				reviewing_experience_metric[kye] = response[kye] / total_number_files
				if kye not in metrics_reached_dictionary.keys():
					metrics_reached_dictionary[kye] = 1
				else:
					metrics_reached_dictionary[kye] = metrics_reached_dictionary[kye] + 1


	# print(change_df['owner'][0]['_account_id'])
	reviewer_familiarity_matric = get_author_familiarity_dict(df, change_df['owner'][0]['_account_id'])


	for key in reviewer_familiarity_matric.keys():
		if key not in metrics_reached_dictionary.keys():
			metrics_reached_dictionary[key] = 1
		else:
			metrics_reached_dictionary[key] = metrics_reached_dictionary[key] + 1
	
	participation_rate_dictionary = {}

	for key in metrics_reached_dictionary:
		p_rate = get_participation_rate(df, key)
		if p_rate == 0:
			participation_rate_dictionary[key] = 0
		else:
			participation_rate_dictionary[key] = p_rate
			metrics_reached_dictionary[key] = metrics_reached_dictionary[key] + 1
	# print(participation_rate_dictionary)
	# print(metrics_reached_dictionary)



df = pd.read_json('return_trip/data_cleaned_for_promise.json')

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


# new_df = find_last_comments(df.copy(), len(df['owner']))

# with open('return_trip/data_cleaned_for_promise.json', 'w') as f:
#     f.write(new_df.to_json())


get_files_for_each_change(df)

for i in range(0,30):
	df_tail = find_last_comments(df, 1)

	print(len(df))

	compute_metrics(df, df_tail)

