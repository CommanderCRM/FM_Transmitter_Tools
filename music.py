import os
import uuid
import argparse
from mutagen.id3 import ID3, ID3NoHeaderError

parser = argparse.ArgumentParser(
    description="MP3 management for FM transmitters",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "-n",
    "--rename",
    dest="actions",
    action="append_const",
    const="rename",
    help="random rename",
)
parser.add_argument(
    "-t",
    "--remove-tags",
    dest="actions",
    action="append_const",
    const="remove_tags",
    help="ID3 tag removing",
)
parser.add_argument(
    "-c",
    "--recreate",
    dest="actions",
    action="append_const",
    const="recreate",
    help="file recreation",
)
parser.add_argument(
    "-a",
    "--all",
    dest="actions",
    action="append_const",
    const="all",
    help="all options",
)
parser.add_argument("src", help="Source location")

args = parser.parse_args()
arg_list = args.actions if args.actions else []
arg_dict = vars(args)


def start() -> None:
    """Choosing a function based on command line arguments."""
    for arg in arg_list:
        if arg == "rename":
            random_rename(PATH, FILE_COUNT)
        elif arg == "remove_tags":
            remove_tags(PATH, FILE_COUNT)
        elif arg == "recreate":
            file_recreation(PATH, FILE_COUNT)
        elif arg == "all":
            random_rename(PATH, FILE_COUNT)
            remove_tags(PATH, FILE_COUNT)
            file_recreation(PATH, FILE_COUNT)
    if not arg_list:
        parser.print_help()


def count_files(path: str) -> int:
    """Counting files in folder for future global use"""
    file_count = 0
    for files in os.walk(path):
        for file in files[2]:
            if file.endswith(".mp3"):
                file_count += 1
    return file_count


def random_rename(path: str, file_count: int) -> None:
    """Renaming files using UUID4"""
    curr_count = 0
    for file in os.listdir(path):
        if file.endswith(".mp3"):
            curr_count += 1
            file_extension = os.path.splitext(file)[1]
            new_filename = str(uuid.uuid4()) + file_extension
            print(f"Renaming file {curr_count} out of {file_count}")
            os.rename(os.path.join(path, file), os.path.join(path, new_filename))


def remove_tags(path: str, file_count: int) -> None:
    """Removing all possible MP3 tags"""
    curr_count = 0
    for file in os.listdir(path):
        if file.endswith(".mp3"):
            curr_count += 1
            file_path = os.path.join(path, file)
            print(f"Removing tag from file {curr_count} out of {file_count}")
            try:
                audio = ID3(file_path)
                audio.delete()
                audio.save()
            except ID3NoHeaderError:
                continue


def file_recreation(path: str, file_count: int) -> None:
    """Modifying date properties by recreating files"""
    curr_count = 0
    for file in os.listdir(path):
        if file.endswith(".mp3"):
            curr_count += 1
            original_file_path = os.path.join(path, file)
            new_file_path = os.path.join(path, file + ".bak")
            print(f"Recreating file {curr_count} out of {file_count}")
            with open(original_file_path, "rb") as original_file, open(
                new_file_path, "wb"
            ) as new_file:
                content = original_file.read()
                new_file.write(content)
            os.remove(original_file_path)
            os.rename(new_file_path, original_file_path)


PATH = arg_dict["src"]
FILE_COUNT = count_files(PATH)
start()
