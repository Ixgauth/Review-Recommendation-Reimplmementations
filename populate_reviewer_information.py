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

def get_single_rec_dictionary(df):
	single_recs = {}
	for line in df['recommendations']:
		if type(line) == float:
			print(line)
			continue
		reviewer = line[0]
		if reviewer in single_recs.keys():
				single_recs[reviewer] += 1
		else:
				single_recs[reviewer] = 1
	return single_recs

df = pd.read_json('data_with_recommendations.json')

second_df = pd.read_json('test_data_without_detail.json')

user_lookup_dict = create_user_dictionary(second_df)

reviewers_dict = get_reviewer_dictionary(df)

recommendations_dict = get_reccomendataion_dictionary(df)

single_recs = get_single_rec_dictionary(df)

output_df = pd.read_csv('Final_List_Of_Changes.csv')

number_recs_list = []

number_found = 0

for i in range(0, len(output_df['id'])):
	cur_reviewer = output_df['recommendations'][i]
	if cur_reviewer in single_recs.keys():
		number_recs_list.append(single_recs[cur_reviewer])
		number_found+=1
	else:
		print('not found')

reviews_dict = {}
i = 0
for line in second_df['reviewers_name_list']:
	if i > 5:
		break
	if type(line) == float:
			continue
	for rev in line:
		if rev in reviews_dict.keys():
			reviews_dict[rev] += 1
		else:
			reviews_dict[rev] = 1

new_reviews_dict = {}

for line in reviews_dict.keys():
	current = reviews_dict[line]
	if line in user_lookup_dict.keys():
		account_id_found = user_lookup_dict[line]
		new_reviews_dict[account_id_found] = current

total = 0
for line in reviews_dict.keys():
	cur = reviews_dict[line]
	total+=cur
print(total)

total_reviews_list = []
number_found = 0
for i in range(0, len(output_df['id'])):
	cur_reviewer = output_df['recommendations'][i]
	if cur_reviewer in reviews_dict.keys():
		total_reviews_list.append(reviews_dict[cur_reviewer])
		number_found+=1
	else:
		print('not found')
		print(cur_reviewer)
		cur_reviewer_id = output_df['correct_account_id'][i]
		if cur_reviewer_id in new_reviews_dict.keys():
			print("found it !")
			total_reviews_list.append(new_reviews_dict[cur_reviewer_id])
		else:
			print("still not found")
			total_reviews_list.append(0)
		

print(number_found)

output_df['total number of reviews performed'] = total_reviews_list
# output_df['number of times recommended'] = number_recs_list
output_df.to_csv('Final_List_Of_Changes_out.csv', index = False, header = True)