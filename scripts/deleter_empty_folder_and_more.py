import hashlib
import os
from pprint import pprint
import shutil
from typing import Generator, Set, Dict, List, Tuple
from send2trash import send2trash

BLACKLIST_FILE = "black_list_artist.txt"
MIN_FILE_SIZE = 1024 * 1024
TRASH_MD5_HASHES: Set[str] = {"b325d6ba8efb828686667aa58ab549e8"}
BLACKLIST_KEYWORDS: Set[str] = {"voice_actor", "voiceactor", "voice-actor"}


def save_black_list(data: Dict[str, List[str]]) -> None:
    print(1)
    with open(BLACKLIST_FILE, encoding="utf-8", mode="w") as f:
        for type, _data in data.items():
            f.write(f"#{type}\n")
            for item in sorted(filter(bool, _data)):
                f.write(f"{item}\n")

def delete_from_black_list(category: str, artist: str, fake_delete: bool = True) -> Dict[str, List[str]]:
    list_data = get_bl_artist()
    list_data[category].remove(artist)

    if fake_delete:
        print(artist)
        pprint(list_data)
        return list_data
    
    save_black_list(list_data)

    return list_data

def get_bl_artist(add: str = None) -> Dict[str, List[str]]: 
    data = {"VA": [], "Other": []}
    try:
        with open(BLACKLIST_FILE, encoding="utf-8") as f:
            current_type = None
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    current_type = line[1:]
                elif current_type and line:
                    data[current_type].append(line)
    except FileNotFoundError:
        with open(BLACKLIST_FILE, encoding="utf-8", mode="w") as f:
            f.write("#VA\n#Other\n")
            data = {"VA": [], "Other": []}

    data_black_list = {k: list(map(fix_folder_name, v)) for k, v in data.items()}
    
    if add:
        data_black_list.setdefault("VA", []).append(fix_folder_name(add))
        save_black_list(data_black_list)

    return data_black_list

def fix_folder_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def move_files(source_dir: str, destination_dir: str, **kwargs) -> Tuple[bool, str]:
    fake_delete: bool = kwargs.get("fake_delete", False)

    if not os.path.exists(source_dir):
        return False, f"Source folder does not exist: {source_dir}"

    os.makedirs(destination_dir, exist_ok=True)

    log: str = ""
    for filename in os.listdir(source_dir):
        source_file = os.path.join(source_dir, filename)
        destination_file = os.path.join(destination_dir, filename)
        
        if not fake_delete:
            shutil.move(source_file, destination_file)
        
        log += f"File {filename} moved to {destination_dir}\n"

    return True, log

def rename_folder(original_full_path_folder: str, fix_full_path: str, **kwargs) -> Tuple[bool, str]:
    fake_delete: bool = kwargs.get("fake_delete", False)
    try:
        if not fake_delete:
            os.rename(original_full_path_folder, fix_full_path)
        return True, f"Deleted blacklisted name in folder name from {original_full_path_folder} \n-> to {fix_full_path}"
    except FileExistsError as e:
        result, log = move_files(original_full_path_folder, fix_full_path, fake_delete=fake_delete)
        if not os.listdir(original_full_path_folder):
            if not fake_delete:
                os.rmdir(original_full_path_folder)
            log += f"Folder {original_full_path_folder} deleted because it was empty\n"

        return result, log

def del_bl_from_str(input_str: str, blacklist_set: Set[str]) -> str:
    sub_strs_folder = input_str.split("+")
    if len(sub_strs_folder) <= 1:
        return input_str
    
    result = []
    for sub_str_folder in sub_strs_folder:
        fix_f_name = fix_folder_name(sub_str_folder)
        if fix_f_name not in blacklist_set:
            result.append(sub_str_folder)

    if not result:
        return f"!FBL_{input_str}"
    return "+".join(result)

def get_new_name_folder(path: str) -> Generator:
    def upd_blacklist() -> Set[str]:
        _blacklist_set = set(blacklist.get("VA", []))
        _blacklist_set.update({item for sublist in blacklist.values() if sublist != blacklist.get("VA", []) for item in sublist})
        return _blacklist_set
    
    blacklist: Dict[str, List[str]] = get_bl_artist()
    blacklist_set = upd_blacklist()

    folder_list: List[str] = list(set([
        subfolder
        for _, folders, _ in os.walk(path)
        for folder in folders
        for subfolder in folder.split("+")
    ]))

    for sub_str_folder in folder_list:
        fix_f_name = fix_folder_name(sub_str_folder)
        if any(check in fix_f_name for check in BLACKLIST_KEYWORDS) and fix_f_name not in blacklist_set:
            yield [sub_str_folder, blacklist]
            blacklist_set = upd_blacklist()
    
    for dirpath, folders, _ in os.walk(path, topdown=False):
        for original_folder in folders:
            original_full_path_folder = os.path.normpath(os.path.join(dirpath, original_folder))
            clean_folder = original_folder.replace("++", "+").strip("+")
            
            folder_name_fix_bl = del_bl_from_str(clean_folder, blacklist_set)
            
            if folder_name_fix_bl != original_folder:
                fix_full_path = os.path.normpath(os.path.join(dirpath, folder_name_fix_bl))
                yield (original_folder, folder_name_fix_bl, original_full_path_folder, fix_full_path)

def del_from_path(
    path: str, 
    trashcan: bool = True, 
    auto_delete_empty_folders: bool = False,
    **kwargs
) -> Tuple[bool, List[str]]:
    fake_delete: bool = kwargs.get("fake_delete", False)
    log_message: List[str] = []

    try:
        if trashcan:
            if not fake_delete:
                send2trash(path)
            log_message.append(f"{'File' if os.path.isfile(path) else 'Folder'} \"{path}\" moved to trash")
        else:
            if not fake_delete:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    os.rmdir(path)
            log_message.append(f"{'File' if os.path.isfile(path) else 'Folder'} \"{path}\" deleted permanently")
        
        if auto_delete_empty_folders:
            parent_dir: str = os.path.dirname(path)
            if not os.listdir(parent_dir):
                if not fake_delete:
                    if trashcan:
                        send2trash(parent_dir)
                    else:
                        os.rmdir(parent_dir)
                log_message.append(f"Folder \"{parent_dir}\" deleted permanently because it last file/folder was deleted")

        return True, log_message
    except Exception as e:
        log_message.append(f"[!]  Error while deleting {path=}: {e=}")
        return False, log_message

def find_empty_folders(path: str, del_trash_files: bool = False) -> List[str]:
    to_delete_items: List[str] = []
    
    for dirpath, folders, files in os.walk(path, topdown=False):
        if del_trash_files:
            for file in files:
                full_path_file = os.path.join(dirpath, file)
                if os.path.getsize(full_path_file) >= MIN_FILE_SIZE:
                    continue
                
                with open(full_path_file, "rb") as file_data:
                    md5_check = hashlib.file_digest(file_data, "md5").hexdigest()
                if md5_check in TRASH_MD5_HASHES:
                    to_delete_items.append(os.path.normpath(full_path_file))

        if dirpath == path:
            continue
        
        if not folders and not files:
            to_delete_items.append(os.path.normpath(dirpath))
    
    return to_delete_items