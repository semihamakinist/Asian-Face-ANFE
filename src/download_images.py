"""
Download images from metadata URLs to local storage for research purposes.
Protects repository from hosting raw copyrighted materials directly.
"""
import os
import json
import requests
from tqdm import tqdm

from tools.GegeneralTools import (
    set_save_folder,
    set_img_name,
)


def download_dataset_images(
        json_file: str,
        movie_name: str,
        save_dir: str,
        data_mod: int = 1
):
    """
    JSON meta veri dosyasındaki resim URL'lerini okuyarak yerel diske indirir.
    """
    # os.makedirs(save_dir, exist_ok=True)
    if not os.path.exists(json_file):
        print(f"[!] Hata: {json_file} dosyası bulunamadı.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data if isinstance(data, list) else data.get("records", [])

    print(f"[*] {len(records)} kayıt taranıyor...")
    for item in tqdm(records):
        img_url = item.get("img_scr")
        img_name = set_img_name(img_url)
        if img_name is None:
            return False

        folder_name = item.get("folder_name")
        if data_mod == 2:
            movie_name = f'{movie_name}/{item.get("gender")}'

        save_folder_path = set_save_folder(
            main_path=save_dir,
            movie_name=movie_name,
            folder_name=folder_name
        )
        os.makedirs(save_folder_path, exist_ok=True)

        save_img_file_path = os.path.join(save_folder_path, img_name)
        # dowload image
        if img_url and not os.path.exists(save_img_file_path):
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                res = requests.get(img_url, headers=headers, timeout=10)
                if res.status_code == 200:
                    with open(save_img_file_path, "wb") as img_f:
                        img_f.write(res.content)
            except Exception:
                continue


if __name__ == "__main__":
    # Download AsianWiki
    JSON_PATH = r"data/asianwiki/asianwiki_player_infos.json"
    SAVE_DIRECTORY = "dataset/asianwiki"
    MOVIE_NAME = "players"


    print(f"[*] AsianWiki Görselleri indiriliyor: {JSON_PATH} -> {SAVE_DIRECTORY}")
    download_dataset_images(json_file=JSON_PATH, movie_name=MOVIE_NAME, save_dir=SAVE_DIRECTORY, data_mod=1)

    # Download MyDramaList
    # JSON_PATH = r"data/mydramalist/mydramalist_player_infos.json"
    # SAVE_DIRECTORY = "dataset/mydramalist"
    # MOVIE_NAME = "players"
    # print(f"[*] MyDramaList Görselleri indiriliyor: {JSON_PATH} -> {SAVE_DIRECTORY}")
    # download_dataset_images(json_file=JSON_PATH, movie_name=MOVIE_NAME, save_dir=SAVE_DIRECTORY, data_mod=2)