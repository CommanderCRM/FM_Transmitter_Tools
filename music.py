import os
import uuid
from mutagen.id3 import ID3, ID3NoHeaderError


def hello() -> None:
    '''Greeting the user and prompting them to choose a function.'''
    print('Enter 1 for random rename, 2 for tag removing, 3 for file recreation, 4 for everything')
    inp = int(input())
    if inp == 1:
        random_rename(PATH, FILE_COUNT)
    elif inp == 2:
        remove_tags(PATH, FILE_COUNT)
    elif inp == 3:
        file_recreation(PATH, FILE_COUNT)
    elif inp == 4:
        random_rename(PATH, FILE_COUNT)
        remove_tags(PATH, FILE_COUNT)
        file_recreation(PATH, FILE_COUNT)
    else:
        hello()


def count_files(path: str) -> int:
    '''Counting files in folder for future global use'''
    file_count = 0
    for files in os.walk(path):
        for file in files[2]:
            if file.endswith('.mp3'):
                file_count += 1
    return file_count


def random_rename(path: str, file_count: int) -> None:
    '''Renaming files using UUID4'''
    curr_count = 0
    for file in os.listdir(path):
        if file.endswith('.mp3'):
            curr_count += 1
            file_extension = os.path.splitext(file)[1]
            new_filename = str(uuid.uuid4()) + file_extension
            print(f'Renaming file {curr_count} out of {file_count}')
            os.rename(os.path.join(path, file),
                      os.path.join(path, new_filename))


def remove_tags(path: str, file_count: int) -> None:
    '''Removing all possible MP3 tags'''
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


def file_recreation(path: str, file_count: int) -> None:
    '''Modifying date properties by recreating files'''
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


PATH = 'G:\\music3'
FILE_COUNT = count_files(PATH)
hello()
