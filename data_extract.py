import pandas as pd


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

def get_comment_files(commit):
	files = []
	for line in commit.keys():
		files.append(line)
	return(files)


df = pd.read_json('test_data_with_comments.json')

for line in df['revisions']:
	files = get_all_files_for_commit(line)
	print(files)


for line in df['comments']:
	print(get_comment_files(line))
	print(line)