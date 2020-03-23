import json
import csv
import pandas as pd
import math
from pathlib import Path
import requests
from datetime import timedelta, date, datetime

def get_comment_info(single_comment):
	info = []
	for line in single_comment:
		date_time_str = line['updated']
		date_time_str = date_time_str.replace('.000000000', '')
		date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
		date_obj = date_time_obj.date()
		info_tuple = line['author']['_account_id'], str(date_obj)
		info.append(info_tuple)
	return info

def get_comment_tuples(owner, comments):
	tuple_list = []
	for key in comments.keys():
		if key == "/COMMIT_MSG":
			continue
		comment_info = get_comment_info(comments[key])

		for author in comment_info:
			if owner == author[0]:
				continue
			else:
				file_comment_tuple = (key, author[0],author[1])
				tuple_list.append(file_comment_tuple)
	return tuple_list

def get_most_recent_workday(file):
	most_recent_date = date(2000,1,1)
	for author in file.keys():
		current_date = datetime.strptime(file[author][1], '%Y-%m-%d').date()
		if current_date > most_recent_date:
			most_recent_date = current_date
	return str(most_recent_date)

def get_total_number_of_comments(file):
	number_of_comments = 0
	for key in file.keys():
		author = file[key]
		cur_coms = author[0]
		number_of_comments += len(cur_coms)
	return number_of_comments

def get_total_number_of_workdays(file):
	workdays = []
	for key in file.keys():
		author = file[key]
		cur_coms = author[0]
		for comment in cur_coms:
			if comment in workdays:
				continue
			else:
				workdays.append(comment)
	return(len(workdays))

def get_number_of_comments_each_author(file):
	for key in file.keys():
		author = file[key]
		number_of_comments = len(author[0])
		author.append(number_of_comments)

def get_number_of_workdays_each_author(file):
	for key in file.keys():
		workdays = []
		author = file[key]
		cur_coms = author[0]
		for comment in cur_coms:
			if comment in workdays:
				continue
			else:
				workdays.append(comment)
		author.append(len(workdays))

def arrange_data(file_comment_tuple_list):
	file_dictionary = {}

	for line in file_comment_tuple_list:
		file = line[0]
		if file in file_dictionary.keys():
			file_dict_entry = file_dictionary[file]
			if line[1] in file_dict_entry:
				current_author = file_dict_entry[line[1]]
				current_author[0].append(line[2])
				if line[2] > current_author[1]:
					current_author[1] = line[2]
			else:
				file_dict_entry[line[1]] = [[line[2]], line[2]]
		else:
			author_dict = {}
			author_dict[line[1]] = [[line[2]], line[2]]
			file_dictionary[file] = author_dict
	return(file_dictionary)

def obtain_all_metrics(file_dictionary):
	for key in file_dictionary.keys():
		current_file = file_dictionary[key]

		workday = get_most_recent_workday(current_file)
		number_of_comments = get_total_number_of_comments(current_file)
		number_of_workdays = get_total_number_of_workdays(current_file)

		get_number_of_comments_each_author(current_file)
		get_number_of_workdays_each_author(current_file)

		file_dictionary[key]['most_recent_date'] = workday
		file_dictionary[key]['total_number_of_comments'] = number_of_comments
		file_dictionary[key]['total_number_of_workdays'] = number_of_workdays

		# print(file_dictionary[key])
	return file_dictionary

def obtain_C_score(author, total_number_of_comments):
	comments = author[0]
	C_score = len(comments)/total_number_of_comments
	author.append(C_score)
	return C_score


def obtain_W_score(author, total_number_of_workdays):
	workdays = author[3]
	W_score = workdays/total_number_of_workdays
	author.append(W_score)
	return W_score

def obtain_T_score(author, most_recent_date):
	last_date_str = author[1]
	last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
	most_recent = datetime.strptime(most_recent_date, '%Y-%m-%d').date()
	delta = last_date - most_recent
	difference = abs(delta.days)
	if difference == 0:
		author.append(1)
		return 1
	else:
		T_score = 1/difference
		author.append(T_score)
		return T_score


def obtain_X_factor(file_dictionary):
	for key in file_dictionary.keys():
		current_file = file_dictionary[key]
		total_comments = current_file['total_number_of_comments']
		total_workdays = current_file['total_number_of_workdays']
		most_recent = current_file['most_recent_date']
		for a_key in current_file.keys():
			if a_key == 'most_recent_date' or a_key == 'total_number_of_comments' or a_key == 'total_number_of_workdays':
				continue
			author = current_file[a_key]
			C_score = obtain_C_score(author, total_comments)
			W_score = obtain_W_score(author, total_workdays)
			T_score = obtain_T_score(author, most_recent)
			X_factor = C_score + W_score + T_score
			author.append(X_factor)
	return file_dictionary

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

def find_best_reviewer(revision, file_dictionary):
	reviewer_dict = {}
	for file in revision:
		if file in file_dictionary.keys():
			cur_file = file_dictionary[file]
			print(cur_file)
			for reviewer in cur_file.keys():
				if reviewer == 'most_recent_date' or reviewer == 'total_number_of_comments' or reviewer == 'total_number_of_workdays':
					continue
				print(reviewer)
				if reviewer in reviewer_dict.keys():
					prior_X = reviewer_dict[reviewer]
					new_X = prior_X + cur_file[reviewer][7]
					reviewer_dict[reviewer] = new_X
					print(new_X)
				else:
					X_Score = cur_file[reviewer][7]
					reviewer_dict[reviewer] = X_Score
					print(X_Score)

df = pd.read_json('test_data_with_comments.json')

file_comment_tuple_list = []

for i in range(0, len(df['owner'])):
	comments = df['comments'][i]
	if isinstance(comments, dict):
		file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)
			
print(len(file_comment_tuple_list))


file_dictionary = arrange_data(file_comment_tuple_list)

file_dictionary = obtain_all_metrics(file_dictionary)

file_dictionary = obtain_X_factor(file_dictionary)

# for key in file_dictionary.keys():
# 	print(key, "  ", file_dictionary[key])

files_for_each_rev = []
for line in df['revisions']:
	files = get_all_files_for_commit(line)
	files_for_each_rev.append(files)

for line in files_for_each_rev:
	find_best_reviewer(line, file_dictionary)