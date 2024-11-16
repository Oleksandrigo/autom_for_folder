import os
import re
import shutil
from pprint import pprint
from typing import Generator, List, Dict, Set, Tuple
from dataclasses import dataclass

from fuzzywuzzy import fuzz

PATHS = [
    "E:\\Video",
    "E:\\GIFS"
]
BL_WL_LIST_FILE = "GSAF_bl_wl_lists.txt"
EXCLUDED_DIRS = ["!Htai", "!new"]
NEW_DIR = "E:\\Video\\!new"
KNOW_NAMES_DIR = "!KNOW_NAMES"
OTHERS_DIR = ["!Others", "!Other"]
CENSORED_TAG = "[Censored]"
SIMILARITY_THRESHOLD = 80


@dataclass
class Match:
    original_folder_name: str 
    artist_name: str
    folder_name: str
    similarity: int



def get_folders_list(path: str) -> List[str]:
    """
    Получает список всех папок в директории уже существующих папок, исключая EXCLUDED_DIRS.
    """
    result = []
    first_level_folders = [
        item
        for item in os.listdir(path)
        if os.path.isdir(os.path.join(path, item)) and item not in EXCLUDED_DIRS
    ]

    for folder in first_level_folders:
        folder_path = os.path.join(path, folder)
        result.extend(
            [
                (sub_item, folder_path)
                for sub_item in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, sub_item))
                and sub_item not in OTHERS_DIR
            ]
        )

    return result


def clean_folders_list(folder: str) -> Tuple[str, str]:
    """
    Очищаем название папки от CENSORED_TAG и приводим к нижнему регистру.
    Возвращаем кортеж с оригинальным и очищенным названием папки.
    """
    cleaned = re.sub(re.escape(CENSORED_TAG), "", folder, flags=re.IGNORECASE).strip()
    return (folder, cleaned.lower())


def get_new_folders_list(path: str) -> List[Tuple[str, str]]:
    """
    Получаем список всех папок в директории новых папок.
    """
    new_path = os.path.join(path, NEW_DIR)
    for root, dirs, _ in os.walk(new_path):
        if root == new_path:
            return [(item, new_path) for item in dirs]
    return []


def create_folders_dict(folders_list: List[str]) -> Dict[str, List[Tuple[str, str]]]:
    """
    Создает словарь, где ключами являются отдельные слова из названий папок,
    а значениями - списки кортежей (оригинальное_название, ключевое_слово).

    Функция разбивает каждое название папки на отдельные слова (разделитель '+'),
    и для каждого слова создает запись в словаре. Если слово уже есть в словаре,
    добавляет новый кортеж в список значений.

    Args:
        folders_list (List[str]): Список названий папок.

    Returns:
        Dict[str, List[Tuple[str, str]]]: Словарь, где ключи - отдельные слова,
        а значения - списки кортежей с оригинальными названиями папок и ключевыми словами.
    """
    folders_dict = {}
    for folder, _ in folders_list:
        for key in folder.split("+"):
            key = key.strip()
            if key:
                folders_dict.setdefault(key, []).append((folder, key))
    return folders_dict


def remove_artist_keyword(folder_name: str) -> str:
    res = folder_name.strip().lower().replace("artist", "")
    if res.find("_()") != -1:
        res = res.replace("_()", "")
    elif res.find("()") != -1:
        res = res.replace("()", "")
    return res



def load_list(file_path: str) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    if not os.path.exists(file_path):
        return set(), set()
    
    whitelist = set()
    blacklist = set()
    current_list = None

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("##"):
                if "blacklist" in line:
                    current_list = 'blacklist'
                elif "whitelist" in line:
                    current_list = 'whitelist'
            elif line:
                item = tuple(line.split(","))
                if current_list == 'blacklist':
                    blacklist.add(item)
                elif current_list == 'whitelist':
                    whitelist.add(item)

    return whitelist, blacklist


def save_to_list(file_path: str, folder: str, key: str, is_whitelist: bool) -> None:
    whitelist, blacklist = load_list(file_path)

    if is_whitelist:
        whitelist.add((folder, key))
        print(f"Added to whitelist: {folder} - {key}")
    else:
        blacklist.add((folder, key))
        print(f"Added to blacklist: {folder} - {key}")

    with open(file_path, "w") as f:
        f.write("## blacklist\n")
        for item in blacklist:
            f.write(f"{item[0]},{item[1]}\n")
        f.write("\n## whitelist\n")
        for item in whitelist:
            f.write(f"{item[0]},{item[1]}\n")


def compare_folders(
    sorted_folders_list: List[Tuple[Tuple[str, str], str]],
    folders_dict: Dict[str, List[Tuple[str, str]]],
    whitelist: Set[Tuple[str, str]],
    blacklist: Set[Tuple[str, str]],
) -> Generator[Tuple[str, str, int, Tuple[str, str]], bool, List[Match]]:
    def add_to_matches(match: Match) -> None:
        if match not in matches:
            matches.append(match)

    
    matches: List[Match] = []

    for (original_folder, cleaned_folder), _ in sorted_folders_list:
        for artist_name, folder_list in folders_dict.items():
            cleaned_artist_name: str = remove_artist_keyword(artist_name)
            similarity: int = fuzz.token_set_ratio(cleaned_folder, cleaned_artist_name)

            for folder_name, _ in folder_list:
                match: Match = Match(original_folder, cleaned_artist_name, folder_name, similarity)
                pair: Tuple[str, str] = (cleaned_folder, cleaned_artist_name)
                reverse_pair: Tuple[str, str] = (cleaned_artist_name, cleaned_folder)

                if pair in whitelist or reverse_pair in whitelist:
                    add_to_matches(match)
                elif pair in blacklist or reverse_pair in blacklist:
                    continue
                elif SIMILARITY_THRESHOLD <= similarity < 100:
                    res: bool = yield original_folder, artist_name, similarity, pair
                    if res:
                        add_to_matches(match)
                elif similarity == 100:
                    add_to_matches(match)
      
    return matches


def move_matched_folders(matches: List[Match], fake_move: bool = False) -> List[str]:
    matched_folders = {os.path.join(NEW_DIR, match.folder_name) for match in matches}
    know_names_path = os.path.join(NEW_DIR, KNOW_NAMES_DIR)
    if not fake_move:
        os.makedirs(know_names_path, exist_ok=True)

    log_text = []
    for folder in matched_folders:
        if os.path.exists(folder):
            new_location = os.path.join(know_names_path, os.path.basename(folder))
            if not fake_move:
                shutil.move(folder, new_location)
            log_text.append(f"Folder {folder} moved to: {new_location}")
        else:
            log_text.append(f"Folder does not exist: {folder}")

    return log_text
