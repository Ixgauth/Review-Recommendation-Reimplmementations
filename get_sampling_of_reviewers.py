import json
import csv
import os
import pathlib
import requests
import pandas as pd
from datetime import timedelta, date, datetime

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
			if first_choice in overlapping_recs.keys():
				overlapping_recs[first_choice][current_change_id] = current_line_dict
			else:
				overlapping_recs[first_choice] = {}
				overlapping_recs[first_choice][current_change_id] = current_line_dict
		else:
			if first_choice in non_overlapping_recs.keys():
				non_overlapping_recs[first_choice][current_change_id] = current_line_dict
			else:
				non_overlapping_recs[first_choice] = {}
				non_overlapping_recs[first_choice][current_change_id] = current_line_dict


		# for reviewer in reviewers_names:
		# 	first_choice = recommendations[0]
		# 	print(type(first_choice))
		# 	print(type(reviewer))
		# 	if reviewer in recommendations:
		# 		if reviewer in overlapping_recs.keys():
		# 			current_line = df.iloc[[i]]
		# 			current_line_dict = current_line.to_dict('r')[0]
		# 			current_change_id = current_line_dict['change_id']
		# 			overlapping_recs[first_choice][current_change_id] = current_line_dict
		# 		else:
		# 			current_line = df.iloc[[i]]
		# 			current_line_dict = current_line.to_dict('r')[0]
		# 			current_change_id = current_line_dict['change_id']
		# 			overlapping_recs[first_choice] = {}
		# 			overlapping_recs[first_choice][current_change_id] = current_line_dict
		# 	else:
		# 		if reviewer in non_overlapping_recs.keys():
		# 			current_line = df.iloc[[i]]
		# 			current_line_dict = current_line.to_dict('r')[0]
		# 			current_change_id = current_line_dict['change_id']
		# 			non_overlapping_recs[first_choice][current_change_id] = current_line_dict
		# 		else:
		# 			current_line = df.iloc[[i]]
		# 			current_line_dict = current_line.to_dict('r')[0]
		# 			current_change_id = current_line_dict['change_id']
		# 			non_overlapping_recs[first_choice] = {}
		# 			non_overlapping_recs[first_choice][current_change_id] = current_line_dict
	print(len(overlapping_recs))
	print(len(non_overlapping_recs))
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
			


df = pd.read_json('data_with_recommendations.json')



reviewers_dict = get_reviewer_dictionary(df)

recommendations_dict = get_reccomendataion_dictionary(df)

overlapping_recs, non_overlapping_recs = get_right_wrong_reviewers(df, reviewers_dict, recommendations_dict)

chosen_changes_correct, chosen_changes_incorrect = get_one_change_per_reviewer(overlapping_recs, non_overlapping_recs)

changes_list = []

columns_out = []

for line in chosen_changes_correct.keys():
	columns_out = list(chosen_changes_correct[line].keys())
	changes_list.append(list(chosen_changes_correct[line].values()))
for line in chosen_changes_incorrect.keys():
	changes_list.append(list(chosen_changes_incorrect[line].values()))
print(columns_out)

out_df = pd.DataFrame(changes_list, columns = columns_out)
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


print(list(out_df.columns))

out_df.to_csv('changes_for_reviewers.csv', index = False, header = True)