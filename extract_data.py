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

def get_total_number_of_coments(file):
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

df = pd.read_json('test_data_with_comments.json')

file_comment_tuple_list = []

for i in range(0, len(df['owner'])):
	comments = df['comments'][i]
	if isinstance(comments, dict):
		file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)
			
print(len(file_comment_tuple_list))

# print(file_comment_tuple_list)

file_dictionary = arrange_data(file_comment_tuple_list)

for key in file_dictionary.keys():
	current_file = file_dictionary[key]

	workday = get_most_recent_workday(current_file)
	number_of_comments = get_total_number_of_coments(current_file)
	number_of_workdays = get_total_number_of_workdays(current_file)

	get_number_of_comments_each_author(current_file)

	file_dictionary[key]['most_recent_date'] = workday
	file_dictionary[key]['total_number_of_comments'] = number_of_comments
	file_dictionary[key]['total_number_of_workdays'] = number_of_workdays

	print(file_dictionary[key])

