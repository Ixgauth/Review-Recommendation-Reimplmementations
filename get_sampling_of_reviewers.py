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
		recommendations = df['recommendations'][i][:5]

		for reviewer in reviewers_names:
			if reviewer in recommendations:
				if reviewer in overlapping_recs.keys():
					overlapping_recs[reviewer] += 1
				else:
					overlapping_recs[reviewer] = 1
			else:
				if reviewer in non_overlapping_recs.keys():
					non_overlapping_recs[reviewer] += 1
				else:
					non_overlapping_recs[reviewer] = 1
	print(overlapping_recs)
	print(non_overlapping_recs)
	print(len(overlapping_recs))
	print(len(non_overlapping_recs))
	


df = pd.read_json('data_with_recommendations.json')



reviewers_dict = get_reviewer_dictionary(df)

# print(len(reviewers_dict.keys()))

recommendations_dict = get_reccomendataion_dictionary(df)

# print(len(recommendations_dict.keys()))

get_right_wrong_reviewers(df, reviewers_dict, recommendations_dict)