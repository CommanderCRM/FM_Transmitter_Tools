import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from mutagen.id3 import ID3, ID3NoHeaderError
from tqdm import tqdm
from argparsing import parser

args = parser.parse_args()
arg_list = args.actions if args.actions else []
arg_dict = vars(args)

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


def rename_file(file_info: tuple, pbar: tqdm) -> None:
    """Renaming files using UUID4"""
    path, file, _, __ = file_info
    file_extension = os.path.splitext(file)[1]
    new_filename = str(uuid.uuid4()) + file_extension

    os.rename(os.path.join(path, file), os.path.join(path, new_filename))

    pbar.update()


def random_rename(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for file renaming"""
    files_to_rename = [
        (path, file, idx + 1, file_count)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]

    pbar = tqdm(total=len(files_to_rename), desc="Renaming files", dynamic_ncols=True)

    if multithread:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(rename_file, file_info, pbar) for file_info in files_to_rename]
            for future in futures:
                future.result()
    else:
        for file_info in files_to_rename:
            rename_file(file_info, pbar)

    pbar.close()


def remove_tags_file(file_info: tuple, pbar: tqdm) -> None:
    """Removing all possible MP3 tags"""
    file_path, _, __ = file_info

    try:
        audio = ID3(file_path)
        audio.delete()
        audio.save()
    except ID3NoHeaderError:
        pass
    finally:
        pbar.update()


def remove_tags(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for tag removing"""
    files_to_process = [
        (os.path.join(path, file), idx + 1, file_count)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]

    pbar = tqdm(total=len(files_to_process), desc="Removing tags from files", dynamic_ncols=True)

    if multithread:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(remove_tags_file, file_info, pbar) for file_info in files_to_process]
            for future in futures:
                future.result()
    else:
        for file_info in files_to_process:
            rename_file(file_info, pbar)

    pbar.close()


def file_recreation_file(file_info: tuple, processed_files: set, lock: Lock, pbar: tqdm) -> None:
    """Modifying date properties by recreating files"""
    path, _, __, file = file_info

    with lock:
        if file in processed_files:
            return
        processed_files.add(file)

    if file.endswith(".mp3"):
        original_file_path = os.path.join(path, file)
        new_file_path = os.path.join(path, file + ".bak")

        with open(original_file_path, "rb") as original_file, open(
            new_file_path, "wb"
        ) as new_file:
            content = original_file.read()
            new_file.write(content)
        os.remove(original_file_path)
        os.rename(new_file_path, original_file_path)

        pbar.update()


def file_recreation(path: str, file_count: int, multithread: bool = False) -> None:
    """Multithreading logic for file recreation"""
    files_to_process = [
        (path, file_count, idx + 1, file)
        for idx, file in enumerate(os.listdir(path))
        if file.endswith(".mp3")
    ]
    processed_files = set()
    lock = Lock()

    pbar = tqdm(total=len(files_to_process), desc="Recreating files", dynamic_ncols=True)

    if multithread:
        with ThreadPoolExecutor() as executor:
            for file_info in files_to_process:
                executor.submit(file_recreation_file, file_info, processed_files, lock, pbar)
    else:
        for file_info in files_to_process:
            file_recreation_file(file_info, processed_files, lock, pbar)

    pbar.close()


PATH = arg_dict["src"]
FILE_COUNT = count_files(PATH)
start()
