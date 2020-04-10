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

#intake a single comment and return the date when it was written as long as the name of the author
#this will be returned as a tuple for each line in a given comment
def get_comment_info(single_comment,owner ):
	info = []
	for line in single_comment:
		date_time_str = line['updated']
		date_time_str = date_time_str.replace('.000000000', '')
		date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
		date_obj = date_time_obj.date()
		if line['author']['_account_id'] == owner:
			continue
		info_tuple = line['author']['name'], str(date_obj)
		info.append(info_tuple)
	return info

#shoul
def get_comment_tuples(owner, comments):
	tuple_list = []
	for key in comments.keys():
		if key == "/COMMIT_MSG":
			continue
		comment_info = get_comment_info(comments[key], owner)

		for author in comment_info:
			if owner == author[0]:
				continue
			else:
				file_comment_tuple = (key, author[0],author[1])
				tuple_list.append(file_comment_tuple)
	return tuple_list

def get_comment_tuples_all_files(owner, comments, list_of_files):
	tuple_list = []
	for key in comments.keys():
		comment_info = get_comment_info(comments[key], owner)
		for author in comment_info:
			if owner == author[0]:
				continue
			else:
				for file in list_of_files:
					file_comment_tuple = (file, author[0],author[1])
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

def find_overlap(best_rec_line, actuals_line):

	overlap = list(set(best_rec_line) & set(actuals_line))

	number_overlap = len(overlap)

	return(number_overlap)

def find_precision_value(list_of_best_recs, list_of_actuals, m_value):
	total_number_overlap = 0
	total_number_recommended = 0
	for i in range(0, len(list_of_best_recs)):
		b_r_a_l = list_of_best_recs[i]
		best_rec_trimmed = b_r_a_l[:m_value]
		number_overlap = find_overlap(best_rec_trimmed, list_of_actuals[i])
		total_number_overlap+= number_overlap
		total_number_recommended += len(best_rec_trimmed)
	precision = total_number_overlap / total_number_recommended
	return precision

def find_recall_value(list_of_best_recs, list_of_actuals, m_value):
	total_number_overlap = 0
	total_number_actuals = 0
	for i in range(0, len(list_of_best_recs)):
		b_r_a_l = list_of_best_recs[i]
		best_rec_trimmed = b_r_a_l[:m_value]
		number_overlap = find_overlap(best_rec_trimmed, list_of_actuals[i])
		total_number_overlap+= number_overlap
		total_number_actuals += len(list_of_actuals[i])
	recall = total_number_overlap/total_number_actuals
	return recall

def find_f_score_value(precision, recall):
	f_score = 2*precision*recall/(precision+recall)
	return f_score

def find_mean_reciprocal_rank(list_of_best_recs, list_of_actuals):
	total_reciprocal_value = 0
	number_of_changes = len(list_of_best_recs)
	for i in range(0, len(list_of_best_recs)):
		best_rank_in_line = 0
		best_recs_for_line = list_of_best_recs[i]
		for j in range(0, len(best_recs_for_line)):
			rec = best_recs_for_line[j]
			if find_overlap([rec], list_of_actuals[i]) > 0:
				best_rank_in_line = j+1
				break
		if best_rank_in_line != 0:
			reciprocal_value = 1/best_rank_in_line
		else:
			reciprocal_value = 0
		total_reciprocal_value+= reciprocal_value
	mean_reciprocal_value = total_reciprocal_value/number_of_changes
	return mean_reciprocal_value
		


def get_all_performance_metrics(list_of_best_recs, list_of_actuals):
	precision_1 = find_precision_value(list_of_best_recs, list_of_actuals, 1)
	precision_2 = find_precision_value(list_of_best_recs, list_of_actuals, 2)
	precision_3 = find_precision_value(list_of_best_recs, list_of_actuals, 3)
	precision_5 = find_precision_value(list_of_best_recs, list_of_actuals, 5)

	recall_1 = find_recall_value(list_of_best_recs, list_of_actuals, 1)
	recall_2 = find_recall_value(list_of_best_recs, list_of_actuals, 2)
	recall_3 = find_recall_value(list_of_best_recs, list_of_actuals, 3)
	recall_5 = find_recall_value(list_of_best_recs, list_of_actuals, 5)

	f_score_1 = find_f_score_value(precision_1, recall_1)
	f_score_2 = find_f_score_value(precision_2, recall_2)
	f_score_3 = find_f_score_value(precision_3, recall_3)
	f_score_5 = find_f_score_value(precision_5, recall_5)

	print(f_score_1, "  ", f_score_2, "  ", f_score_3, "  ", f_score_5)

	mean_reciprocal_value = find_mean_reciprocal_rank(list_of_best_recs, list_of_actuals)
	print(mean_reciprocal_value)

	outfile = open("results_file.txt", "w")
	outstring = "Precision_1: " + str(precision_1)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Precision_2: "+ str(precision_2)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Precision_3: "+ str(precision_3)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Precision_5: "+ str(precision_5)
	outfile.write(outstring)
	outfile.write('\n')
	outfile.write('\n')

	outstring = "Recall_1: "+ str(recall_1)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Recall_2: "+ str(recall_2)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Recall_3: "+ str(recall_3)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "Recall_5: "+ str(recall_5)
	outfile.write(outstring)
	outfile.write('\n')
	outfile.write('\n')

	outstring = "F_Score_1: "+ str(f_score_1)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "F_Score_2: "+ str(f_score_2)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "F_Score_3: "+ str(f_score_3)
	outfile.write(outstring)
	outfile.write('\n')
	outstring = "F_Score_5: "+ str(f_score_5)
	outfile.write(outstring)
	outfile.write('\n')
	outfile.write('\n')

	outstring = "Mean Reciprocal Value: " + str(mean_reciprocal_value)
	outfile.write(outstring)


def find_best_reviewer_always(df, file_comment_tuple_list):
	file_dictionary = arrange_data(file_comment_tuple_list)

	file_dictionary = obtain_all_metrics(file_dictionary)

	file_dictionary = obtain_X_factor(file_dictionary)

	print(len(file_dictionary))

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


def find_final_change_time(test_df):
	first_str = test_df['created'][0]
	first_str = first_str.replace('.000000000', '')
	earliest_time = datetime.strptime(first_str, '%Y-%m-%d %H:%M:%S')
	for line in test_df['created']:
		change_time = line
		change_time = change_time.replace('.000000000', '')
		change_time_obj = datetime.strptime(change_time, '%Y-%m-%d %H:%M:%S')
		if earliest_time > change_time_obj:
			earliest_time = change_time_obj
	return(earliest_time)

def get_base_tuple_list(df, earliest_time):
	file_comment_tuple_list = []

	changes_after_base = []

	for i in range(0, len(df['owner'])):
		if i % 100 == 0:
			print(i)
		change_time = df['created'][i]
		change_time = change_time.replace('.000000000', '')
		change_time_obj = datetime.strptime(change_time, '%Y-%m-%d %H:%M:%S')
		if earliest_time > change_time_obj:
			rev_files = get_all_files_for_commit(df['revisions'][i])
			files = []
			for change in rev_files.keys():
				files = files + rev_files[change]
			comments = df['comments'][i]
			if isinstance(comments, dict):
				file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)
		else:
			current_row = df.iloc[[i]]
			df_line = current_row.values.tolist()
			changes_after_base.append(df_line)

	final_list = []
	for line in changes_after_base:
		final_list.append(line[0])

	df_extra = pd.DataFrame(final_list, columns = df.columns)

	return file_comment_tuple_list, df_extra 

def find_best_for_specific_change(file_comment_tuple_list, df_extra, change):
	time_created = change['created']
	time_created = time_created.replace('.000000000', '')
	date_time_obj = datetime.strptime(time_created, '%Y-%m-%d %H:%M:%S')

	print(date_time_obj)

	for i in range(0, len(df_extra['owner'])):
		change_time = df_extra['created'][i]
		change_time = change_time.replace('.000000000', '')
		change_time_obj = datetime.strptime(change_time, '%Y-%m-%d %H:%M:%S')
		if date_time_obj > change_time_obj:
			rev_files = get_all_files_for_commit(df['revisions'][i])
			files = []
			for rev in rev_files.keys():
				files = files + rev_files[rev]
			comments = df_extra['comments'][i]
			if isinstance(comments, dict):
				file_comment_tuple_list = file_comment_tuple_list + get_comment_tuples(df['owner'][i]["_account_id"], comments)

	print(len(file_comment_tuple_list))
	file_dictionary = arrange_data(file_comment_tuple_list)

	file_dictionary = obtain_all_metrics(file_dictionary)

	file_dictionary = obtain_X_factor(file_dictionary)

	list_of_files = []
	files_in_change = get_all_files_for_commit(change['revisions'])

	for key in files_in_change.keys():
		list_of_files = list_of_files + files_in_change[key]

	owner = change['owner']

	baseURL_REST = "https://gerrit-review.googlesource.com/accounts/" + str(owner["_account_id"])
	resp = requests.get(baseURL_REST)
	owner_name = ''
	if resp.status_code == 200:
		loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
		owner_name = loaded['name']

	best_rec = []

	rev_recs = find_best_reviewer(list_of_files, file_dictionary, owner)
	if len(rev_recs) == 0:
		print('nothing found at review level')
		file_dictionary_package = arrange_data_for_package(file_comment_tuple_list)

		file_dictionary_package = obtain_all_metrics(file_dictionary_package)

		file_dictionary_package = obtain_X_factor(file_dictionary_package)

		files_in_change_package = get_all_files_for_commit_package(change['revisions'])

		list_of_files_package = []

		for package_key in files_in_change_package.keys():
			list_of_files_package = list_of_files_package + files_in_change_package[package_key]

		rev_recs = find_best_reviewer(list_of_files_package, file_dictionary_package, owner)

		if len(rev_recs) == 0:
			print(owner)
			print('nothing found at package')
			file_dictionary_system = arrange_data_system(file_comment_tuple_list)

			file_dictionary_system = obtain_all_metrics(file_dictionary_system)

			file_dictionary_system = obtain_X_factor(file_dictionary_system)

			files_in_change_system = get_all_files_for_commit_system(change['revisions'])


			list_of_files_system = []

			for system_key in files_in_change_system.keys():
				list_of_files_system = list_of_files_system + files_in_change_system[system_key]

			rev_recs = find_best_reviewer(list_of_files_system, file_dictionary_system, owner)

			if len(rev_recs) == 0:
				print("nothing found")
				print(files_in_change)

			else:
				best_rec = rev_recs

		else:
			best_rec = rev_recs
	else:
		owner_found = []
		for rec in rev_recs:
			if owner_name in rec:
				print("FOUND THE OWNER")
				print(len(rev_recs))
				owner_found.append(rec)

		if len(owner_found) > 0:
			for line in owner_found:
				rev_recs.remove(line)
			print(len(rev_recs))
		best_rec = rev_recs

	best_rec_no_value = []
	for rec in best_rec:
		best_rec_no_value.append(rec[1])
	actual_reviewer_list = change['reviewers_name_list']
	return(best_rec_no_value, actual_reviewer_list)
	
def find_last_comments(df, number_of_comments):
	number_obtained = 0

	list_of_reviewers = []

	list_of_lines = []

	while number_obtained < number_of_comments:
		final_line = df.tail(1)
		actual_reviewer_list = final_line['reviewers_name_list']
		if not pd.isnull(actual_reviewer_list).all() and len(actual_reviewer_list) > 0:
			if len(final_line['reviewers_name_list']) > 0:
				revisions = final_line['revisions']
				revs_dict = revisions.to_dict()
				found_a_file = False
				for key in revs_dict.keys():
					rev = revs_dict[key]
					files_in_change = get_all_files_for_commit(rev)
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

		df.drop(df.tail(1).index,inplace=True)
	final_list = []
	for line in list_of_lines:
		final_list.append(line[0])

	df_test = pd.DataFrame(final_list, columns = df.columns)

	return(df_test)


df = pd.read_json('test_data_without_detail.json')

file_comment_tuple_list = []


df_tail = find_last_comments(df.copy(), 50)

earliest_change = find_final_change_time(df_tail)

base_tuple_list, df_extra = get_base_tuple_list(df, earliest_change)

print(len(base_tuple_list))

list_of_best_recs = []
list_of_actuals = []

for i, j in df_tail.iterrows(): 

	best_recs, actuals = find_best_for_specific_change(base_tuple_list, df_extra, j)
	list_of_best_recs.append(best_recs)
	list_of_actuals.append(actuals)
    
get_all_performance_metrics(list_of_best_recs, list_of_actuals)


# df = pd.read_json('smaller_test_data_with_reviewers.json')

# final_time = date_time_obj = datetime.strptime("2020-01-01 18:12:52", '%Y-%m-%d %H:%M:%S')

# print(len(get_base_tuple_list(df, final_time)[0]))