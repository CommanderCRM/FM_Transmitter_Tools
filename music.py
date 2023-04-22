import os
import uuid
from mutagen.id3 import ID3, ID3NoHeaderError

PATH = 'F:\\'
FILE_COUNT = 0


def hello() -> None:
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


def count_files() -> None:
    global FILE_COUNT
    for files in os.walk(PATH):
        for file in files:
            if file.endswith('.mp3'):
                FILE_COUNT += 1


def random_rename() -> None:
    global FILE_COUNT
    curr_count = 0
    for file in os.listdir(PATH):
        if file.endswith('.mp3'):
            curr_count += 1
            file_extension = os.path.splitext(file)[1]
            new_filename = str(uuid.uuid4()) + file_extension
            print(f'Renaming file {curr_count} out of {FILE_COUNT}')
            os.rename(os.path.join(PATH, file),
                      os.path.join(PATH, new_filename))


def remove_tags() -> None:
    global FILE_COUNT
    curr_count = 0
    for file in os.listdir(PATH):
        if file.endswith('.mp3'):
            curr_count += 1
            file_path = os.path.join(PATH, file)
            print(f'Removing tag from file {curr_count} out of {FILE_COUNT}')
            try:
                audio = ID3(file_path)
                audio.delete()
                audio.save()
            except ID3NoHeaderError:
                continue


def file_recreation() -> None:
    global FILE_COUNT
    curr_count = 0
    for file in os.listdir(PATH):
        if file.endswith('.mp3'):
            curr_count += 1
            original_file_path = os.path.join(PATH, file)
            new_file_path = os.path.join(PATH, file + ".bak")
            print(f'Recreating file {curr_count} out of {FILE_COUNT}')
            with open(original_file_path, 'rb') as original_file, open(new_file_path, 'wb') as new_file:
                content = original_file.read()
                new_file.write(content)
            os.remove(original_file_path)
            os.rename(new_file_path, original_file_path)


count_files()
hello()
