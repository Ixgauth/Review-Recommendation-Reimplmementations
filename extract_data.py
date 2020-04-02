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
		date_time_str = line['updated']
		date_time_str = date_time_str.replace('.000000000', '')
		date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
		date_obj = date_time_obj.date()
		info_tuple = line['author']['name'], str(date_obj)
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

def arrange_data_for_package(file_comment_tuple_list):
	file_dictionary = {}

	for line in file_comment_tuple_list:
		file = line[0]
		file = pathlib.Path(file)
		new_file = str(file.parent)
		if new_file in file_dictionary.keys():
			file_dict_entry = file_dictionary[new_file]
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
			file_dictionary[new_file] = author_dict
	return(file_dictionary)

def arrange_data_system(file_comment_tuple_list):
	file_dictionary = {}

	for line in file_comment_tuple_list:
		file = line[0]
		topdir = file.split('/')[0]
		if topdir in file_dictionary.keys():
			file_dict_entry = file_dictionary[topdir]
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
			file_dictionary[topdir] = author_dict
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

def get_files_for_rev_package(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		file = pathlib.Path(filename)
		new_file = file.parent
		files.append(str(new_file))
	return files

def get_files_for_rev_system(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		topdir = filename.split('/')[0]
		files.append(topdir)
	return files

def merge_dictionaries(dict1, dict2): 
    return(dict2.update(dict1))

def get_all_files_for_commit(commit):
	all_files = {}
	for key in commit.keys():
		all_files[key] = get_files_for_rev(commit[key])
	return all_files

def get_all_files_for_commit_package(commit):
	all_files = {}
	for key in commit.keys():
		all_files[key] = get_files_for_rev_package(commit[key])
	return all_files

def get_all_files_for_commit_system(commit):
	all_files = {}
	for key in commit.keys():
		all_files[key] = get_files_for_rev_system(commit[key])
	return all_files

def find_best_reviewer(revision, file_dictionary, owner):
	reviewer_dict = {}
	for file in revision:
		if file in file_dictionary.keys():
			cur_file = file_dictionary[file]
			for reviewer in cur_file.keys():
				if reviewer == 'most_recent_date' or reviewer == 'total_number_of_comments' or reviewer == 'total_number_of_workdays':
					continue
				if reviewer in reviewer_dict.keys():
					prior_X = reviewer_dict[reviewer]
					new_X = prior_X + cur_file[reviewer][7]
					reviewer_dict[reviewer] = new_X
				else:
					X_Score = cur_file[reviewer][7]
					reviewer_dict[reviewer] = X_Score
	reviewer_list = []
	for reviewer in reviewer_dict.keys():
		if reviewer == owner:
			print("found owner")
			continue
		reviewer_list.append([reviewer_dict[reviewer], reviewer])

	reviewer_list.sort(reverse=True)
	return reviewer_list

def find_power_users(file_dictionary):
	print(len(file_dictionary.keys()))
	user_dictiorary = {}
	for key in file_dictionary.keys():
		file = file_dictionary[key]
		for reviewer_key in file.keys():
			reviewer = file[reviewer_key]
			if reviewer_key == 'most_recent_date' or reviewer_key == 'total_number_of_comments' or reviewer_key == 'total_number_of_workdays':
					continue
			if reviewer_key in user_dictiorary.keys():
				current_score = user_dictiorary[reviewer_key]
				file_score = reviewer[7]
				current_score+= file_score
				user_dictiorary[reviewer_key] = current_score
			else:
				file_score = reviewer[7]
				user_dictiorary[reviewer_key] = file_score
	reviewer_list = []
	for reviewer in user_dictiorary.keys():
		reviewer_list.append([user_dictiorary[reviewer], reviewer])
	reviewer_list.sort(reverse=True)
	for i in range(0, 10):
		print(reviewer_list[i])

def find_best_reviewer_always(df, file_comment_tuple_list):
	file_dictionary = arrange_data(file_comment_tuple_list)

	file_dictionary = obtain_all_metrics(file_dictionary)

	file_dictionary = obtain_X_factor(file_dictionary)

	file_dictionary_package = arrange_data_for_package(file_comment_tuple_list)

	file_dictionary_package = obtain_all_metrics(file_dictionary_package)

	file_dictionary_package = obtain_X_factor(file_dictionary_package)

	file_dictionary_system = arrange_data_system(file_comment_tuple_list)

	file_dictionary_system = obtain_all_metrics(file_dictionary_system)

	file_dictionary_system = obtain_X_factor(file_dictionary_system)

	files_for_each_rev = []
	files_for_each_rev_package = []
	files_for_each_rev_system = []
	for line in df['revisions']:
		files_for_each_rev.append(get_all_files_for_commit(line))
		files_for_each_rev_package.append(get_all_files_for_commit_package(line))
		files_for_each_rev_system.append(get_all_files_for_commit_system(line))
	
	revs_with_files_dict = {}
	revs_with_files_dict_package = {}
	revs_with_files_dict_system = {}

	for line in files_for_each_rev:
		revs_with_files_dict.update(line)

	for line in files_for_each_rev_package:
		revs_with_files_dict_package.update(line)

	for line in files_for_each_rev_system:
		revs_with_files_dict_system.update(line)


	total_empty = 0
	total_score = 0

	top_rev_rec = {}
	top_rev_rec_package = {}

	for key in revs_with_files_dict.keys():
		owner = df['owner'][i]
		rev_recs = find_best_reviewer(revs_with_files_dict[key], file_dictionary, owner)
		if len(rev_recs) == 0:
			rev_recs = find_best_reviewer(revs_with_files_dict_package[key], file_dictionary_package, owner)
			if len(rev_recs) == 0:
				rev_recs = find_best_reviewer(revs_with_files_dict_system[key], file_dictionary_system, owner)
				if len(rev_recs) == 0:
					total_empty+=1
				else:
					top_rev_rec[key] = rev_recs[0]
					best_rec = rev_recs[0]
					score = best_rec[0]
					total_score += score
			else:
				top_rev_rec[key] = rev_recs[0]
				best_rec = rev_recs[0]
				score = best_rec[0]
				total_score += score
		else:
			top_rev_rec[key] = rev_recs[0]
			best_rec = rev_recs[0]
			score = best_rec[0]
			total_score += score
	print(total_empty)
	total_filled =len(revs_with_files_dict) - total_empty
	avg_score = total_score/total_filled
	print(total_filled)
	print(avg_score)

def find_last_comments(df, number_of_comments):
	number_obtained = 0
	while number_obtained < number_of_comments:
		final_line = df.tail(1)
		line_labels = final_line['labels']
		for line in line_labels:
			reviewer = line['Code-Review']
			if len(reviewer) > 0:
				if 'approved' in reviewer.keys():
					account_id = reviewer['approved']['_account_id']
					baseURL = "https://gerrit-review.googlesource.com/accounts/" + str(account_id)
					print(baseURL)
					resp = requests.get(baseURL)
					print(resp.status_code)
					if resp.status_code == 200:
						print("it worked")
						loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
						print(loaded)
				number_obtained+=1

		df.drop(df.tail(1).index,inplace=True)

df = pd.read_json('test_data_with_comments.json')

# file_comment_tuple_list = []

# for i in range(0, len(df['owner'])):
# 	comments = df['comments'][i]
# 	if isinstance(comments, dict):
# 		file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)
			
# find_best_reviewer_always(df, file_comment_tuple_list)


df_tail = find_last_comments(df, 20)