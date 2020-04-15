import json
import csv
import os
import pathlib
import requests
import pandas as pd

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
	
def get_one_change_per_reviewer(overlapping_recs, non_overlapping_recs):
	chosen_changes_correct = {}
	chosen_changes_incorrect = {}

	used_keys = []



	for key in overlapping_recs:
		print(key, len(overlapping_recs[key]))
		if len(overlapping_recs[key]) == 1:
			current_reviewer = overlapping_recs[key]
			for in_key in current_reviewer.keys():
				chosen_changes_correct[key] = current_reviewer[in_key]
				print(current_reviewer[in_key]['recommendations'][0])
				print(current_reviewer[in_key]["reviewers_name_list"])
				print()
				if in_key in used_keys:
					print("found twice")
				used_keys.append(in_key)


	for key in non_overlapping_recs:
		print(key, len(non_overlapping_recs[key]))
		if len(non_overlapping_recs[key]) == 1:
			current_reviewer = non_overlapping_recs[key]
			for in_key in current_reviewer.keys():
				chosen_changes_incorrect[key] = current_reviewer[in_key]
				print(current_reviewer[in_key]['recommendations'][0])
				print(current_reviewer[in_key]["reviewers_name_list"])
				print()
				if in_key in used_keys:
					print("found twice")
				used_keys.append(in_key)
	# print(used_keys)


df = pd.read_json('data_with_recommendations.json')



reviewers_dict = get_reviewer_dictionary(df)

recommendations_dict = get_reccomendataion_dictionary(df)

overlapping_recs, non_overlapping_recs = get_right_wrong_reviewers(df, reviewers_dict, recommendations_dict)

get_one_change_per_reviewer(overlapping_recs, non_overlapping_recs)
