import pandas as pd


def get_files_for_rev(revision):
	file_dictionary = revision['files']
	files = []
	for filename in file_dictionary.keys():
		files.append(filename)
	return files

df = pd.read_json('test_data_with_comments.json')

for line in df['revisions']:
	for key in line.keys():
		files = get_files_for_rev(line[key])
		print(files)