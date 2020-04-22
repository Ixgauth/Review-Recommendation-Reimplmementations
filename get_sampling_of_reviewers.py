import json
import csv
import os
import pathlib
import requests
import random
import pandas as pd
from datetime import timedelta, date, datetime

def create_user_dictionary(df):
	user_lookup_dictionary = {}
	problems = {}
	for i in range(0, len(df['owner'])):
		comments = df['comments'][i]
		if isinstance(comments, dict):
			for key in comments.keys():
				single_comment = comments[key]
				for line in single_comment:
					name = line['author']['name']
					account_id = line['author']['_account_id']
					if name not in user_lookup_dictionary.keys():
						user_lookup_dictionary[name] = account_id
					else:
						if user_lookup_dictionary[name] != account_id:
							problems[name] = account_id
	return user_lookup_dictionary

def get_reviewer_dictionary(df):
	reviewers_dictionary = {}

	for line in df['reviewers_name_list']:
		if type(line) == float:
			continue
		for reviewer in line:
			if reviewer in reviewers_dictionary.keys():
				reviewers_dictionary[reviewer] += 1
			else:
				reviewers_dictionary[reviewer] = 1

	return reviewers_dictionary

def get_reccomendataion_dictionary(df):
	recommendations = {}

	for line in df['recommendations']:
		i = 0
		if type(line) == float:
			print(line)
			continue
		for reviewer in line:
			if i > 5:
				continue
			if reviewer in recommendations.keys():
				recommendations[reviewer] += 1
			else:
				recommendations[reviewer] = 1
			i+=1
	return recommendations


def get_right_wrong_reviewers(df, reviewers_dict, recommendations_dict):
	overlapping_recs = {}
	non_overlapping_recs = {}
	number_of_reviews_correct = 0
	number_of_reviews_incorrect = 0

	for i in range(0, len(df['recommendations'])):
		if type(df['recommendations'][i]) == float:
			print(df['recommendations'][i])
			continue
		reviewers_names = df['reviewers_name_list'][i]
		recommendations = df['recommendations'][i][:1]

		first_choice = recommendations[0]

		current_line = df.iloc[[i]]
		current_line_dict = current_line.to_dict('r')[0]
		current_change_id = current_line_dict['change_id']
		current_line_dict['recommendations'] = first_choice


		if first_choice in reviewers_names:
			number_of_reviews_correct+=1
			current_line_dict['guess_correct'] = "True"
			if first_choice in overlapping_recs.keys():
				overlapping_recs[first_choice][current_change_id] = current_line_dict
			else:
				overlapping_recs[first_choice] = {}
				overlapping_recs[first_choice][current_change_id] = current_line_dict
		else:
			number_of_reviews_incorrect+=1
			current_line_dict['guess_correct'] = "False"
			if first_choice in non_overlapping_recs.keys():
				non_overlapping_recs[first_choice][current_change_id] = current_line_dict
			else:
				non_overlapping_recs[first_choice] = {}
				non_overlapping_recs[first_choice][current_change_id] = current_line_dict
	print(len(overlapping_recs))
	print(len(non_overlapping_recs))
	print('number_of_reviews_correct', number_of_reviews_correct)
	print('number_of_reviews_incorrect', number_of_reviews_incorrect)
	return overlapping_recs, non_overlapping_recs

def get_latest_change(dict_of_changes):
	first_review_time = datetime.strptime("2012-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
	first_review = []
	for key in dict_of_changes.keys():
		cur_review_str = dict_of_changes[key]['updated']
		cur_review_str = cur_review_str.replace('.000000000', '')
		cur_review_time = datetime.strptime(cur_review_str, '%Y-%m-%d %H:%M:%S')
		if first_review_time < cur_review_time:
			first_review_time = cur_review_time
			first_review.append(dict_of_changes[key])
	return first_review[len(first_review)-1]

	
	
def get_one_change_per_reviewer(overlapping_recs, non_overlapping_recs):
	chosen_changes_correct = {}
	chosen_changes_incorrect = {}

	for key in overlapping_recs:
		if len(overlapping_recs[key]) == 1:
			current_reviewer = overlapping_recs[key]
			for in_key in current_reviewer.keys():
				chosen_changes_correct[key] = current_reviewer[in_key]
		else:
			current_reviewer = overlapping_recs[key]
			change = get_latest_change(current_reviewer)
			chosen_changes_correct[key] = change

	for key in non_overlapping_recs:
		if len(non_overlapping_recs[key]) == 1:
			current_reviewer = non_overlapping_recs[key]
			for in_key in current_reviewer.keys():
				chosen_changes_incorrect[key] = current_reviewer[in_key]
		else:
			current_reviewer = non_overlapping_recs[key]
			change = get_latest_change(current_reviewer)
			chosen_changes_incorrect[key] = change
	
	print(len(chosen_changes_correct.keys()))
	print(len(chosen_changes_incorrect.keys()))
	return chosen_changes_correct, chosen_changes_incorrect


def get_changes_for_correct(correct_recs, incorrect_recs, sample_size_correct, sample_size_incorrect, max_for_reviewer):
	chosen_changes = []
	current_chosen_correct = 0
	overall_dict = {}

	chosen_dict = {}

	removed_authors = []
	all_correct_recs_left = []

	all_incorrect_recs = []

	for key in correct_recs.keys():
		if len(correct_recs[key]) < max_for_reviewer:
			current_user_dict = correct_recs[key]
			for in_key in current_user_dict.keys():
				chosen_changes.append(current_user_dict[in_key])
				current_chosen_correct+=1
				if key in chosen_dict.keys():
					chosen_dict[key] += 1
				else:
					chosen_dict[key] = 1
			removed_authors.append(key)
	
	for author in removed_authors:
		correct_recs.pop(author, None)
	
	left_over = sample_size_correct - current_chosen_correct

	number_per_reviewer_left = int(left_over/(len(correct_recs)))

	all_correct_recs_left = []

	all_revs_left_max = {}

	for key in correct_recs.keys():
		current_user_dict = correct_recs[key]
		all_revs_left_max[key] = number_per_reviewer_left
		for in_key in current_user_dict.keys():
			all_correct_recs_left.append(current_user_dict[in_key])

	while current_chosen_correct < sample_size_correct:
		current_max = len(all_correct_recs_left)
		random_generated = random.randrange(0, current_max)
		change_chosen = all_correct_recs_left[random_generated]
		reviewer = change_chosen['recommendations']
		left = all_revs_left_max[reviewer]
		if left == 0:
			continue
		else:
			chosen_changes.append(change_chosen)
			all_revs_left_max[reviewer] = all_revs_left_max[reviewer]-1
			current_chosen_correct+=1
			if reviewer in chosen_dict.keys():
				chosen_dict[reviewer] += 1
			else:
				chosen_dict[reviewer] = 1
		all_correct_recs_left.remove(change_chosen)
	
	for key in incorrect_recs.keys():
		current_user_dict = incorrect_recs[key]
		for in_key in current_user_dict.keys():
			all_incorrect_recs.append(current_user_dict[in_key])

	current_chosen_incorrect = 0
	i = 0
	while current_chosen_incorrect < sample_size_incorrect:
		current_max = len(all_incorrect_recs)
		random_generated = random.randrange(0, current_max)
		change_chosen = all_incorrect_recs[random_generated]
		reviewer = change_chosen['recommendations']
		if reviewer in chosen_dict.keys():
			number_chosen_reviewer = chosen_dict[reviewer]
		else:
			number_chosen_reviewer = 0
			chosen_dict[reviewer] = 0
		
		if number_chosen_reviewer >= max_for_reviewer:
			continue
		else:
			chosen_changes.append(change_chosen)
			chosen_dict[reviewer] +=1
			current_chosen_incorrect+=1
		all_incorrect_recs.remove(change_chosen)
		i+=1
		if i > 5000:
			break
	print(chosen_dict)

	for change in chosen_changes:
		inner_key = change['change_id']
		overall_dict[inner_key] = change
	return overall_dict


def get_changes_for_all(current_recs, sample_size):
	all_overlapping_list = []
	chosen_changes = []
	current_chosen = 0
	overall_dict = {}
	for key in current_recs.keys():
		current_user_dict = current_recs[key]
		for in_key in current_user_dict.keys():
			all_overlapping_list.append(current_user_dict[in_key])
	while current_chosen < sample_size:
		current_max = len(all_overlapping_list)
		random_generated = random.randrange(0, current_max)
		change_chosen = all_overlapping_list[random_generated]
		chosen_changes.append(change_chosen)
		all_overlapping_list.remove(change_chosen)
		current_chosen+=1

	for change in chosen_changes:
		inner_key = change['change_id']
		overall_dict[inner_key] = change
	return(overall_dict)

def get_all_reviews_clear(correct_recs, incorrect_recs):
	all_overlapping_list = []
	overall_dict = {}
	for key in correct_recs.keys():
		current_user_dict = correct_recs[key]
		for in_key in current_user_dict.keys():
			all_overlapping_list.append(current_user_dict[in_key])
	for key in incorrect_recs.keys():
		current_user_dict = incorrect_recs[key]
		for in_key in current_user_dict.keys():
			all_overlapping_list.append(current_user_dict[in_key])

	for change in all_overlapping_list:
		inner_key = change['change_id']
		overall_dict[inner_key] = change
	return(overall_dict)



df = pd.read_json('data_with_recommendations.json')

second_df = pd.read_json('test_data_without_detail.json')

user_lookup_dict = create_user_dictionary(second_df)

reviewers_dict = get_reviewer_dictionary(df)

recommendations_dict = get_reccomendataion_dictionary(df)

overlapping_recs, non_overlapping_recs = get_right_wrong_reviewers(df, reviewers_dict, recommendations_dict)

overall_changes = get_changes_for_correct(overlapping_recs, non_overlapping_recs, 198, 233, 20)

changes_list = []

columns_out = []

for line in overall_changes.keys():
	columns_out = list(overall_changes[line].keys())
	changes_list.append(list(overall_changes[line].values()))
# for line in chosen_changes_incorrect.keys():
# 	changes_list.append(list(chosen_changes_incorrect[line].values()))

out_df = pd.DataFrame(changes_list, columns = columns_out)
out_df['correct_account_id'] = ''
out_df['correct_email'] = ''
print(len(out_df['recommendations']))
for i in range (0,len(out_df['reviewers_account_id'])):
	correct_name = out_df['recommendations'][i]
	current_reviewers = out_df['reviewers_account_id'][i]
	if str(out_df['guess_correct'][i]) == 'True':
		for rev in current_reviewers:
			baseURL_REST = "https://gerrit-review.googlesource.com/accounts/" + str(rev)
			resp = requests.get(baseURL_REST)
			if resp.status_code == 200:
				loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
				if loaded['name'] == correct_name:
					print(loaded['name'])
					out_df['correct_account_id'][i] = loaded["_account_id"]
					out_df['correct_email'][i] = loaded['email']
			else:
				print(resp.status_code)
	else:
		if correct_name in user_lookup_dict:
			print('found them')
			account_id = user_lookup_dict[correct_name]
			baseURL_REST = "https://gerrit-review.googlesource.com/accounts/" + str(account_id)
			resp = requests.get(baseURL_REST)
			if resp.status_code == 200:
				loaded = json.loads(resp.content.decode("utf-8").replace(")]}'",''))
				if loaded['name'] == correct_name:
					print(loaded['name'])
					out_df['correct_account_id'][i] = loaded["_account_id"]
					out_df['correct_email'][i] = loaded['email']
				else:
					print("name mixup")
			else:
				print(resp.status_code)


del out_df['project']
del out_df["change_id"]
del out_df['hashtags']
del out_df['subject']
del out_df['status']
del out_df['branch']
del out_df['updated']
del out_df['created']
del out_df['submitted']
del out_df['submitter']
del out_df['insertions']
del out_df['deletions']
del out_df['total_comment_count']
del out_df['unresolved_comment_count']
del out_df['has_review_started']
del out_df['submission_id']
del out_df['_number']
del out_df['owner']
del out_df['labels']
del out_df['current_revision']
del out_df['revisions']
del out_df['requirements']
del out_df['comments']
del out_df['work_in_progress']
del out_df['revert_of']
del out_df['topic']
del out_df['assignee']
del out_df['submit_type']
del out_df['reviewers_account_id']
del out_df['reviewers_name_list']

out_df.sort_values('correct_account_id', inplace=True, ascending=False)


out_df.to_csv('changes_for_reviewers.csv', index = False, header = True)