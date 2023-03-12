import os
import uuid
import datetime
import random
import shutil
from mutagen.id3 import ID3, ID3NoHeaderError

path = 'F:\\'
file_count = 0

def hello():
	print('Enter 1 for random rename, 2 for tag removing, 3 for file recreation, 4 for everything')
	inp = int(input())
	if inp == 1:
		random_rename()
	elif inp == 2:
		remove_tags()
	elif inp == 3:
		file_recreation()
	elif inp == 4:
		random_rename()
		remove_tags()
		file_recreation()
	else:
		hello()
	
def count_files():
	global file_count
	for root, dirs, files in os.walk(path):
		for file in files:
			if file.endswith('.mp3'):
				file_count += 1

def random_rename():
	global file_count
	curr_count = 0
	for file in os.listdir(path):
		if file.endswith('.mp3'):
			curr_count += 1
			file_extension = os.path.splitext(file)[1]
			new_filename = str(uuid.uuid4()) + file_extension
			print(f'Renaming file {curr_count} out of {file_count}')
			os.rename(os.path.join(path, file), os.path.join(path, new_filename))

def remove_tags():
	global file_count
	curr_count = 0
	for file in os.listdir(path):
		if file.endswith('.mp3'):
			curr_count += 1
			file_path = os.path.join(path, file)
			print(f'Removing tag from file {curr_count} out of {file_count}')
			try:
				audio = ID3(file_path)
				audio.delete()
				audio.save()
			except ID3NoHeaderError:
				continue

def file_recreation():
	global file_count
	curr_count = 0
	for file in os.listdir(path):
		if file.endswith('.mp3'):
			curr_count += 1
			original_file_path = os.path.join(path, file)
			new_file_path = os.path.join(path, file + ".bak")
			print(f'Recreating file {curr_count} out of {file_count}')
			with open(original_file_path, 'rb') as original_file, open(new_file_path, 'wb') as new_file:
				content = original_file.read()
				new_file.write(content)
			os.remove(original_file_path)
			os.rename(new_file_path, original_file_path)


count_files()
hello()

