import os
import uuid
from concurrent.futures import ThreadPoolExecutor
import logging
from threading import Lock
from mutagen.id3 import ID3, ID3NoHeaderError
from argparsing import parser

args = parser.parse_args()
arg_list = args.actions if args.actions else []
arg_dict = vars(args)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] (%(threadName)-9s) %(message)s",
)


def start() -> None:
    """Choosing a function based on command line arguments."""
    multithread = "MT" in arg_list if arg_list else False
    for arg in arg_list:
        if arg == "rename":
            random_rename(PATH, FILE_COUNT, multithread)
        elif arg == "remove_tags":
            remove_tags(PATH, FILE_COUNT, multithread)
        elif arg == "recreate":
            file_recreation(PATH, FILE_COUNT, multithread)
        elif arg == "all":
            random_rename(PATH, FILE_COUNT, multithread)
            remove_tags(PATH, FILE_COUNT, multithread)
            file_recreation(PATH, FILE_COUNT, multithread)
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


def rename_file(file_info: tuple) -> None:
    """Renaming files using UUID4"""
    path, file, curr_count, file_count = file_info
    file_extension = os.path.splitext(file)[1]
    new_filename = str(uuid.uuid4()) + file_extension
    logging.info("Renaming file %d out of %d", curr_count, file_count)
    os.rename(os.path.join(path, file), os.path.join(path, new_filename))


def random_rename(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for file renaming"""
    files_to_rename = [
        (path, file, idx + 1, file_count)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]

    if multithread:
        with ThreadPoolExecutor() as executor:
            executor.map(rename_file, files_to_rename)
    else:
        for file_info in files_to_rename:
            rename_file(file_info)


def remove_tags_file(file_info: tuple) -> None:
    """Removing all possible MP3 tags"""
    file_path, curr_count, file_count = file_info
    logging.info("Removing tag from file %d out of %d", curr_count, file_count)
    try:
        audio = ID3(file_path)
        audio.delete()
        audio.save()
    except ID3NoHeaderError:
        pass


def remove_tags(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for tag removing"""
    files_to_process = [
        (os.path.join(path, file), idx + 1, file_count)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]
    if multithread:
        with ThreadPoolExecutor() as executor:
            executor.map(remove_tags_file, files_to_process)
    else:
        for file_info in files_to_process:
            remove_tags_file(file_info)


def file_recreation_file(file_info: tuple, processed_files: set, lock: Lock) -> None:
    """Modifying date properties by recreating files"""
    path, file_count, curr_count, file = file_info

    with lock:
        if file in processed_files:
            return
        processed_files.add(file)

    if file.endswith(".mp3"):
        original_file_path = os.path.join(path, file)
        new_file_path = os.path.join(path, file + ".bak")
        logging.info("Recreating file %d out of %d", curr_count, file_count)
        with open(original_file_path, "rb") as original_file, open(
            new_file_path, "wb"
        ) as new_file:
            content = original_file.read()
            new_file.write(content)
        os.remove(original_file_path)
        os.rename(new_file_path, original_file_path)


def file_recreation(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for file recreation"""
    files_to_process = [
        (path, file_count, idx + 1, file)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]
    processed_files = set()
    lock = Lock()

    if multithread:
        with ThreadPoolExecutor() as executor:
            for file_info in files_to_process:
                executor.submit(file_recreation_file, file_info, processed_files, lock)
    else:
        for file_info in files_to_process:
            file_recreation_file(file_info, processed_files, lock)


PATH = arg_dict["src"]
FILE_COUNT = count_files(PATH)
start()
