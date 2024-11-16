import os
from typing import List, Dict
import shutil

PATHS: List[str] = [
    r"E:\Video", 
    r"E:\GIFS"
]

SMALL_FILE_COUNT_FOLDER: str = "!SmallFileCount"
EXCLUDE_FOLDERS: List[str] = ["!new", "!SmallFileCount"]


def get_filtered_folders(paths: List[str], min_file_count: int = 5) -> Dict[str, int]:
    filtered_folders: Dict[str, int] = {}
    for path in paths:
        for root, dirs, files in os.walk(path):
            dirs[:] = [dir for dir in dirs if dir not in EXCLUDE_FOLDERS]
            if not dirs:
                file_count: int = len(files)
                if file_count <= min_file_count:
                    filtered_folders[root] = file_count
    return filtered_folders

def move_small_file_count_folders(folder: str, fake_move: bool = False) -> str:
    parent_folder: str = os.path.dirname(folder)
    folder_name: str = os.path.basename(folder)
    new_folder_path: str = os.path.join(parent_folder, SMALL_FILE_COUNT_FOLDER, folder_name)
    if not fake_move:
        os.makedirs(os.path.dirname(new_folder_path), exist_ok=True)
        shutil.move(folder, new_folder_path)
    
    log = f"Moving folder: {folder} to {new_folder_path}"
    return log
