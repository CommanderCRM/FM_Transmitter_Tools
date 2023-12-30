import os
import uuid
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from mutagen.id3 import ID3, ID3NoHeaderError
from tqdm import tqdm
from argparsing import parser


def start(path: str) -> None:
    """Choosing a function based on command line arguments."""
    multithread = "MT" in arg_list if arg_list else False
    for arg in arg_list:
        if arg == "rename":
            random_rename(path, multithread)
        elif arg == "remove_tags":
            remove_tags(path, multithread)
        elif arg == "recreate":
            file_recreation(path, multithread)
        elif arg == "all":
            random_rename(path, multithread)
            remove_tags(path, multithread)
            file_recreation(path, multithread)
    if not arg_list:
        parser.print_help()
        return


def format_drive(drive_letter, new_name):
    """Formatting drive to FAT32 (Windows-only)"""
    command = f'format {drive_letter}: /FS:FAT32 /V:{new_name} /Q /Y'
    subprocess.run(command, shell=True, check=True)


def create_folder(src_folder: str, new_folder_name: str) -> str:
    """Create folder in the same place as the existing one, return its path"""
    parent_dir = os.path.dirname(src_folder)
    new_folder_path = os.path.join(parent_dir, new_folder_name)

    os.makedirs(new_folder_path, exist_ok=True)

    return new_folder_path


def copy_folder(src_folder: str, dest_folder: str):
    """Copy all .mp3 files from source to destination"""
    for src_dir, dirs, files in os.walk(src_folder):
        files = [file for file in files if file.endswith(".mp3")]
        for file in tqdm(files, desc=f"Copying files to {dest_folder}", dynamic_ncols=True, ascii=" ="):
            src_file = os.path.join(src_dir, file)
            dst_file = os.path.join(dest_folder, file)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.copy(src_file, dest_folder)


def get_file_info(path: str) -> list:
    """Getting .mp3 file info (path, file)"""
    return [(path, file) for file in os.listdir(path) if file.endswith(".mp3")]


def rename_file(file_info: tuple, pbar: tqdm) -> None:
    """Renaming files using UUID4"""
    path, file = file_info
    file_extension = os.path.splitext(file)[1]
    new_filename = str(uuid.uuid4()) + file_extension

    os.rename(os.path.join(path, file), os.path.join(path, new_filename))

    pbar.update()


def remove_tags_file(file_info: tuple, pbar: tqdm) -> None:
    """Removing all possible MP3 tags"""
    path, file = file_info
    file_path = os.path.join(path, file)

    try:
        audio = ID3(file_path)
        audio.delete()
        audio.save()
    except ID3NoHeaderError:
        pass
    finally:
        pbar.update()


def file_recreation_file(file_info: tuple, pbar: tqdm, processed_files: set, lock: Lock) -> None:
    """Modifying date properties by recreating files"""
    path, file = file_info

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


def process_files(files_to_process: list, process_file_func: callable, description: str, multithread: bool, *args, **kwargs) -> None:
    """Function to handle processing multiple files (either with multithreading or not)"""
    pbar = tqdm(total=len(files_to_process), desc=description, dynamic_ncols=True, ascii=" =")

    if multithread:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_file_func, file_info, pbar, *args, **kwargs) for file_info in files_to_process]
            for future in futures:
                future.result()
    else:
        for file_info in files_to_process:
            process_file_func(file_info, pbar, *args, **kwargs)

    pbar.close()


def random_rename(path: str, multithread: bool) -> None:
    """Call renaming function"""
    files_to_process = get_file_info(path)
    process_files(files_to_process, rename_file, "Renaming files", multithread)


def remove_tags(path: str, multithread: bool) -> None:
    """Call removing tags function"""
    files_to_process = get_file_info(path)
    process_files(files_to_process, remove_tags_file, "Removing tags from files", multithread)


def file_recreation(path: str, multithread: bool) -> None:
    """Call recreate files function"""
    files_to_process = get_file_info(path)
    processed_files = set()
    lock = Lock()
    process_files(files_to_process, file_recreation_file, "Recreating files", multithread,
                   processed_files=processed_files, lock=lock)


args = parser.parse_args()
arg_list = args.actions if args.actions else []
arg_dict = vars(args)

PATH = arg_dict["src"]

if args.drive and args.new_name:
    format_drive(args.drive, args.new_name)
    new_folder_path = create_folder(PATH, args.new_name)
    copy_folder(PATH, new_folder_path)
    start(new_folder_path)
    copy_folder(new_folder_path, args.drive + ":\\")
    shutil.rmtree(new_folder_path)
else:
    print("Drive letter and new name must be provided")
    parser.print_help()
