import os
import pprint
from typing import List, Tuple

EXCLUDES: List[str] = ["!new"]
PATHS: List[str] = [
    r"E:\Video", 
    r"E:\GIFS"
]


def check_excludes(dirpath: str, excludes: List[str]) -> bool:
    return any(exclude in dirpath for exclude in excludes)


def find_folder_name(folder_name: str, excludes: List[str]) -> List[str]:
    query: List[str] = []
    for path in PATHS:
        for dirpath, folders, _ in os.walk(path):
            if check_excludes(dirpath, excludes):
                continue
            
            if dirpath != path:
                query.extend(
                    os.path.join(dirpath, folder)
                    for folder in folders
                    if folder_name.lower() in folder.lower()
                )
    return query


def find_and_open_folder(folder_name: str) -> Tuple[str, List[str]]:
    folder_name = os.path.basename(folder_name)
    folders: List[str] = []
    for sub_folder_name in folder_name.split("+"):
        folders.extend(find_folder_name(sub_folder_name, EXCLUDES))
    
    
    return (folder_name, list(set(folders)))

