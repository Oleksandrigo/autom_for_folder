import os
import shutil
import re
import sqlite3
import hashlib
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from send2trash import send2trash

BACKUP_DIR = "backups"

@dataclass
class Config:
    ignore_all: bool = False
    rename_all: bool = False
    ignore_list: List[str] = field(default_factory=list)

    def set_ignore_all(self, value: bool) -> None:
        self.ignore_all = value

    def set_rename_all(self, value: bool) -> None:
        self.rename_all = value


def create_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path)

def ensure_file_exists(path: str):
    if not os.path.exists(path):
        open(path, 'x', encoding="utf-8").close()

def backup_db(db_path: str):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    files = [f for f in os.listdir(BACKUP_DIR) if f != ".gitignore"]
    
    next_num = 1 if not files else int(max(files)[:4]) + 1
    shutil.copyfile(db_path, os.path.join(BACKUP_DIR, f"{next_num:04}_md5s.sqlite"))

def save_to_sqlite(data: Dict[str, str], db_path: str, fake_save: bool = False) -> str:
    if fake_save:
        return "Fake save mode enabled.\nDatabase not updated."
    
    with create_connection(db_path) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM md5s")
        cur.executemany("INSERT INTO md5s (md5, path) VALUES (?, ?)", data.items())
    
    log = f"Database now contains {len(data)} entries\nDatabase update completed."
    backup_db(db_path)
    return log

def is_valid_md5(string: str) -> bool:
    return bool(re.match(r"^[a-fA-F0-9]{32}$", string.split(".")[0]))

def get_md5(file_path: str, force: bool = False) -> str:
    if is_valid_md5(os.path.basename(file_path)) and not force:
        return os.path.basename(file_path).split(".")[0]
    
    with open(file_path, mode="rb") as file_data:
        return hashlib.file_digest(file_data, "md5").hexdigest()

def rename_file(source_file_path: str, new_file_name: str, fake_rename: bool = False) -> Tuple[str, str]:
    new_file_path = os.path.join(os.path.dirname(source_file_path), new_file_name + os.path.splitext(source_file_path)[1])
    log = ""
    
    if os.path.exists(new_file_path):
        log += f"File with MD5 name already exists: \n{new_file_path=}\n{source_file_path=}\nSkipping rename operation."
        return source_file_path, log
    
    try:
        if not fake_rename:
            os.rename(source_file_path, new_file_path)
        log += f"File {source_file_path} renamed to {new_file_path}"
        return new_file_path, log
    except FileExistsError as e:
        if not fake_rename:
            os.remove(source_file_path)
        log += f"Duplicate file {source_file_path} removed"
        return new_file_path, log
    except OSError as e:
        log += f"Error renaming file: {e}"
        return source_file_path, log

def delete_file(file_path: str, fake_delete: bool = False, to_trashcan: bool = True) -> str:
    log = ""
    if os.path.exists(file_path):
        try:
            if not fake_delete:
                if to_trashcan:
                    send2trash(file_path)
                else:
                    os.remove(file_path)
            log = f"Removed file: {file_path}"
        except Exception as e:
            log += f"Error: {e}"
    else:
        log += f"File not found: {file_path}"

    return log
    