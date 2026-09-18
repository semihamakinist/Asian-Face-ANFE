from datetime import datetime
import argparse
import requests
import string
import json
import os

from selenium.webdriver.common.by import By

from tools.SeleniumTools import (
    get_or_download_chromedriver,
    wait_load_main_webpage,
    close_driver,
)

from tools.GegeneralTools import (
    extract_base64_from_xpath,
    build_person_folder_name,
    load_profile_data_fast,
    saveSRCImage_faster,
    get_element_xpath,
    build_folder_name,
    collectLinksList,
    save_image_smart,
    exists_in_image,
    sleep_if_needed,
    normalize_url,
    safe_old_urls,
)
from tools.MongoDBTools import (
    get_asianwiki_mongo_collections,
    update_asianwiki_movie_page,
    close_db
)

import sys
sys.getfilesystemencoding()

NO_IMAGE = "No_image_available"

def build_clean_movie_name(raw_name: str) -> str:
    tmp = build_folder_name(raw_name)
    if not tmp:
        return raw_name
    return build_folder_name(
        tmp.replace("-", " ").translate(str.maketrans("", "", string.punctuation))
    ).replace(" ", "_")

def normalize_person_url_from_item(item):
    try:
        return normalize_url(item[2])
    except Exception:
        return None

def preload_existing_profile_urls(col_players, target_urls):
    """Tek tek find_one yerine batch kontrol. Büyük hız kazancı sağlar."""
    urls = sorted({u for u in target_urls if u})
    if not urls:
        return set()

    existing = set()
    cursor = col_players.find(
        {"$or": [{"url": {"$in": urls}}, {"old_urls": {"$in": urls}}]},
        {"url": 1, "old_urls": 1},
    )
    url_set = set(urls)
    for doc in cursor:
        u = normalize_url(doc.get("url"))
        if u in url_set:
            existing.add(u)
        for old_u in safe_old_urls(doc.get("old_urls", [])):
            old_u = normalize_url(old_u)
            if old_u in url_set:
                existing.add(old_u)
    return existing


def movie_already_done(col_movies, target_url):
    """Koleksiyon alan adları eski/yeni farklı olabileceği için toleranslı kontrol."""
    doc = col_movies.find_one(
        {"url": target_url},
        {"_id": 1, "case": 1, "case_players": 1, "has_players": 1, "error_page": 1},
    )
    if not doc:
        return False
    if doc.get("error_page") is True:
        return False
    return bool(doc.get("case") or doc.get("case_players") or doc.get("has_players"))


def process_movie_page(driver,
                       target_url: str,
                       wind:int,
                       restart_every:int,
                       driver_path:str,
                       headless:bool,
                       session: requests.Session,
                       headers,
                       main_data_path,
                       col_movies):
    movie_name = target_url.split("/")[-1]
    has_players = False
    has_poster = False
    movie_img_scr = NO_IMAGE
    all_people = []

    try:
        # driver.get(target_url)
        driver = wait_load_main_webpage(
            driver,
            target_url,
            wind,
            restart_every,
            driver_path,
            headless,
            by_tag_type=By.ID,
            by_tag_name="mw-content-text"
        )
        if driver is None:
            raise RuntimeError("Driver yüklenemedi")

        try:
            # WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.ID, "mw-content-text")))
            movie_name = driver.find_element(By.XPATH, "/html/body/div[2]/article/h1").text.strip()
        except Exception:
            pass

        movie_name = build_clean_movie_name(movie_name)

        a_tags = driver.find_elements(By.XPATH, '//*[@id="mw-content-text"]/table/tbody/tr[3]/td/a')
        img_scrs = driver.find_elements(By.XPATH, '//*[@id="mw-content-text"]/table/tbody/tr[2]/td/a/img')
        has_players = len(a_tags) > 0

        try:
            container = driver.find_element(By.ID, "mw-content-text")
        except Exception:
            container = None

        all_people.extend(collectLinksList(movie_name, a_tags, img_scrs, driver, container))

        # Oyuncu küçük görselleri: mevcut akışı koruyoruz ama driver artık yeniden açılmıyor.
        for a_tag, img_tag in zip(a_tags, img_scrs):
            try:
                person_name = a_tag.text
                if not person_name:
                    continue
                img_url = img_tag.get_attribute("src")
                if not img_url or NO_IMAGE in img_url:
                    continue

                img_folder_name = build_person_folder_name(person_name)
                img_xpath = get_element_xpath(driver, img_tag)
                _ = save_image_smart(
                    img_url=img_url,
                    headers=headers,
                    main_path=main_data_path,
                    movie_name=f"movies_players/{movie_name}",
                    folder_name=img_folder_name,
                    session=session,
                    base64_fetcher=lambda: extract_base64_from_xpath(driver, img_xpath)
                    # sadece 403 olursa çağrılır
                )

            except Exception as ex_img:
                print(f"movie player image save error: {ex_img}")

        try:
            mv_img_xpath = '//*[@id="mw-content-text"]/div/div/a/img'
            movie_img = driver.find_element(By.XPATH, mv_img_xpath).get_attribute("src")
            if movie_img and NO_IMAGE not in movie_img:
                check_save_img = save_image_smart(
                    img_url=movie_img,
                    headers=headers,
                    main_path=main_data_path,
                    movie_name=f"movies_posters/{movie_name}",
                    folder_name=None,
                    session=session,
                    base64_fetcher=lambda: extract_base64_from_xpath(driver, img_xpath)
                    # sadece 403 olursa çağrılır
                )
                # has_poster = True
                has_poster = check_save_img
                movie_img_scr = movie_img
        except Exception as movie_ex:
            print(f"movie_link: {target_url}\nPoster save error: {movie_ex}")

        update_asianwiki_movie_page(
            col_movies=col_movies,
            target_url=target_url,
            movie_img_scr=movie_img_scr,
            movie_folder_name=movie_name,
            has_poster=has_poster,
            has_players=has_players,
        )
        print(f"#**# movie_done | has_players={has_players} | has_poster={has_poster} | players_count={len(a_tags)} | {target_url}")
        # return driver, all_people
    except Exception as ex:
        print(f"movie page error: {target_url} -> {ex}")
        update_asianwiki_movie_page(
            col_movies=col_movies,
            target_url=target_url,
            movie_img_scr=NO_IMAGE,
            movie_folder_name="",
            has_poster=False,
            has_players=False,
            error_page=True,
            error_exception=str(ex),
        )
        # return driver, all_people
    return driver, all_people


def process_player_page_fast(driver,
                             target_url,
                             wind: int,
                             restart_every: int,
                             driver_path: str,
                             headless: bool,
                             session: requests.Session,
                             headers,
                             main_data_path,
                             col_players):
    try:
        driver, profile_data = load_profile_data_fast(
            driver, target_url,
            wind, restart_every,
            driver_path, headless,
        )

        person_folder_name = profile_data["person_folder_name"]
        img_scr = profile_data["img_scr"]
        gender = profile_data["gender"]
        person_img_xpath = profile_data["person_img_xpath"]
        now = datetime.now()

        doc_data = {
            "personel_name": person_folder_name,
            "img_scr": img_scr,
            "url": target_url,
            "gender": gender,
            "updated_at": now,
        }

        if NO_IMAGE in img_scr:
            col_players.update_one(
                {"url": target_url, "img_scr": NO_IMAGE},
                {
                    "$set": {**doc_data, "gender": "None", "case": False},
                    "$setOnInsert": {"created_at": now},
                },
                upsert=True,
            )
            return driver, "no_image"

        existing_by_img = list(
            col_players.find(
                {"img_scr": img_scr},
                {
                    "_id": 1,
                    "url": 1,
                    "old_urls": 1,
                    "img_scr": 1,
                    "personel_name": 1,
                    "folder_name": 1,
                    "old_personel_names": 1,
                },
            )
        )

        if not existing_by_img:
            check_save_img = save_image_smart(
                img_url=img_scr,
                headers=headers,
                main_path=main_data_path,
                movie_name=f"players",
                folder_name=person_folder_name,
                session=session,
                base64_fetcher=lambda: extract_base64_from_xpath(driver, person_img_xpath)
                # sadece 403 olursa çağrılır
            )
            doc_data.update({
                "folder_name": person_folder_name,
                "old_personel_names": [],
                # "case": True,
                "case": check_save_img,
                "created_at": now,
            })
            col_players.insert_one(doc_data)
            return driver, "inserted"

        same_url_exists = any(normalize_url(d.get("url")) == target_url for d in existing_by_img)
        if same_url_exists:
            return driver, "already_exists"

        existing_folder_names = [d.get("folder_name") for d in existing_by_img if d.get("folder_name")]
        target_folder_name = existing_folder_names[0] if existing_folder_names else person_folder_name

        # Sadece URL değişiminde ve dosya yoksa indir. Gereksiz disk taraması minimuma indirildi.
        image_exists = any(
            exists_in_image(
                img_url=img_scr,
                main_path=main_data_path,
                movi_name="players",
                folder_name=folder_name,
            ) == 1
            for folder_name in existing_folder_names
        )
        if not image_exists:
            saveSRCImage_faster(
                img_url=img_scr,
                movi_name="players",
                folder_name=target_folder_name,
                header=headers,
                main_path=main_data_path,
                driver=driver,
                img_xpath=person_img_xpath,
            )

        existing_current_urls = set()
        existing_old_urls = set()
        existing_personel_names = set()
        existing_old_personel_names = set()

        for d in existing_by_img:
            current_url = normalize_url(d.get("url"))
            if current_url:
                existing_current_urls.add(current_url)
            for old_u in safe_old_urls(d.get("old_urls", [])):
                old_u = normalize_url(old_u)
                if old_u:
                    existing_old_urls.add(old_u)

            old_name = d.get("personel_name")
            if old_name:
                existing_personel_names.add(old_name)
            for old_pn in d.get("old_personel_names", []):
                if old_pn:
                    existing_old_personel_names.add(old_pn)

        old_urls_to_add = sorted(
            u for u in existing_current_urls if u and u != target_url and u not in existing_old_urls
        )
        old_personel_names_to_add = sorted(
            n for n in existing_personel_names if n and n != person_folder_name and n not in existing_old_personel_names
        )

        update_doc = {
            "$set": {
                "url": target_url,
                "personel_name": person_folder_name,
                "gender": gender,
                "updated_at": now,
            }
        }
        add_to_set = {}
        if old_urls_to_add:
            add_to_set["old_urls"] = {"$each": old_urls_to_add}
        if old_personel_names_to_add:
            add_to_set["old_personel_names"] = {"$each": old_personel_names_to_add}
        if add_to_set:
            update_doc["$addToSet"] = add_to_set

        col_players.update_many({"img_scr": img_scr}, update_doc)
        print(json.dumps({"changed_img_scr": img_scr, "update": update_doc}, default=str, ensure_ascii=False))
        return driver, "updated"

    except Exception as ex:
        print(f"Hata: {target_url} -> {ex}")
        now = datetime.now()
        error_doc = {
            "personel_name": "",
            "img_scr": NO_IMAGE,
            "url": target_url,
            "case": False,
            "error": str(ex),
            "updated_at": now,
        }
        col_players.update_one(
            {"url": target_url, "img_scr": NO_IMAGE},
            {"$set": error_doc, "$setOnInsert": {"created_at": now}},
            upsert=True,
        )
        return driver, "error"


def main():
    # intalling 1*10 movies:
    # #**-- headless: False --**#
    #   python asianwiki_crawler.py -re 100 -smin 1 -smax 2 -st 1 -cb 1 -si 0 -fi 10
    #   python asianwiki_crawler.py -re 100 -smin 1.5 -smax 3.5 -st 1 -cb 1 -si 0 -fi 10
    # #**-- headless: True --**#
    #   python asianwiki_crawler.py --headless -re 100 -smin 1 -smax 2 -st 1 -cb 1 -si 0 -fi 10

    # intalling 10*10 movies:
    # #**-- headless: False --**#
    #   python asianwiki_crawler.py -re 100 -smin 1 -smax 2 -st 10 -cb 1 -si 0 -fi 10
    # #**-- headless: True --**#
    #   python asianwiki_crawler.py --headless -re 100 -smin 1 -smax 2 -st 10 -cb 1 -si 0 -fi 10

    parser = argparse.ArgumentParser()
    parser.add_argument("-cb", "--choose_browser_id", type=int, default=1, help="Choose Browser: 1-Chrome, 2-Opera")
    parser.add_argument("-si", "--start_index", type=int, default=0,  help="Start Index: 0-500")
    parser.add_argument("-fi", "--finish_index", type=int, default=2, help="Finish Index: batch size")
    parser.add_argument("-st", "--step_index", type=int, default=1, help="Step count (kaç batch)")

    parser.add_argument("-hd", "--headless", action="store_true", help="Chrome/Opera görünmeden çalışır. Hız ve stabilite için önerilir.")
    parser.add_argument("-re", "--restart-every", type=int, default=40, help="Driver kaç sayfada bir yenilensin. 0 = hiç yenileme.")
    parser.add_argument("-smin", "--sleep-min", type=float, default=0.0, help="İstekler arası minimum bekleme.")
    parser.add_argument("-smax", "--sleep-max", type=float, default=0.0, help="İstekler arası maksimum bekleme. 0 = bekleme yok.")
    # parser.add_argument("--skip-existing-movies", action="store_true",
    #                     help="DB'de işlenmiş görünen film/dizi sayfalarını atlar.")
    args = parser.parse_args()

    main_data_path = os.path.join(os.getcwd(), "dataset", "asianwiki")
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

    }
    min_s = args.sleep_min
    max_s = args.sleep_max
    # headless_bln = True/False
    headless_bln = args.headless
    restart_every = args.restart_every
    mongo_client = None

    print(f"min_s:{min_s} - max_s: {max_s} - headless_bln: {headless_bln} - restart_every: {restart_every}")
    # aktif chrome browser path
    driver_path = get_or_download_chromedriver()

    # print(f"driver_path: {driver_path}")
    driver = None
    start_index = args.start_index
    finish_index = start_index + args.finish_index

    try:
        mongo_client, mongo_db, col_movies, col_players = get_asianwiki_mongo_collections()
        session = requests.Session()  # main'de 1 kere oluştur, hep kullan

        for s_index in range(args.step_index):
            print(
                f"\n=== STEP {s_index + 1}/{args.step_index} | start={start_index} | finish={finish_index} ==="
            )
            all_list = []

            print("################################# Starting Movie Collection #################################")
            movie_cursor = (
                col_movies
                .find({"case": False})
                # .find({
                #     "case": True,
                #     "error": {"$exists": False},
                #     # "updated_at": {"$gt": start_date,"$lt": end_date},
                #     # "updated_at": {"$gt": start_date},
                #     "updated_at": {"$lt":start_date}
                # })
                # .skip(start_index)
                .limit(args.finish_index)
            )
            movie_batch = list(movie_cursor)
            if not movie_batch:
                print("İşlenecek yeni film/dizi linki kalmadı (case=false yok).")
                break
            rest_drive_idx = 1
            for web_idx, movie_data in enumerate(movie_batch, start=1):
                step_idx = int(finish_index / (args.finish_index if args.finish_index != 0 else 1))
                target_url = normalize_url(movie_data.get("url"))
                if not target_url:
                    continue
                # if args.skip_existing_movies and movie_already_done(col_movies, target_url):
                #     print(f"movie_skip_existing: {target_url}")
                #     continue
                print("****************************************************************************************")

                # print(f"movie_process: {web_idx}/{len(movie_batch)} | {target_url}")
                print(
                    f"\n🔍==* Web STEP {step_idx}: {web_idx}/{args.finish_index} - Rest Drive Index: {rest_drive_idx} *== "
                    f"Web Sayfası İşleniyor: {target_url}"
                )
                driver, people = process_movie_page(
                    driver, target_url, rest_drive_idx - 1,
                    restart_every, driver_path, headless_bln,
                    session, headers, main_data_path, col_movies
                )
                rest_drive_idx +=1

                all_list.extend(people)
                # bir filmden sonrası kısa bekleme
                sleep_if_needed(min_s=min_s, max_s=max_s)
            print(
                f"#################################"
                f" Ending Movie Collection | people_links={len(all_list)} "
                f"#################################"
            )

            # all_list = [
            #   {
            #       'The Bait Part 2',
            #       'Jang Keun-Suk',
            #       'https://asianwiki.com/Jang_Keun-Suk',
            #       'The Bait-Pt2-Jang Keun-Suk.jpg',
            #       'https://asianwiki.com/images/0/06/The_Bait-Pt2-Jang_Keun-Suk.jpg',
            #   }
            # ]

            # Aynı step içinde duplicate profil linklerini temizle.
            unique_people = []
            seen_urls = set()
            for item in all_list:
                url = normalize_person_url_from_item(item)
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_people.append(item)

            existing_urls = preload_existing_profile_urls(col_players, seen_urls)
            print(f"players_total={len(unique_people)} | already_in_db={len(existing_urls)}")

            print("################################# Starting Players Collection #################################")
            stats = {"inserted": 0, "updated": 0, "already_exists": 0, "no_image": 0, "error": 0, "skipped": 0}

            total_people = len(unique_people)
            for player_web_idx, item in enumerate(unique_people, start=1):
                target_url = normalize_person_url_from_item(item)
                if not target_url:
                    continue
                if target_url in existing_urls:
                    stats["skipped"] += 1
                    continue

                print(
                    f"\n🔍==* Player player_process: {player_web_idx}/{total_people} - Rest Drive Index: {rest_drive_idx}"
                    f" | {target_url} *=="
                )
                driver, status = process_player_page_fast(
                    driver, target_url, rest_drive_idx - 1,
                    restart_every, driver_path, headless_bln,
                    session, headers, main_data_path, col_players
                )
                rest_drive_idx += 1

                stats[status] = stats.get(status, 0) + 1
                # her bir oyuncudan sonrası kısa bekleme
                sleep_if_needed(min_s=min_s, max_s=max_s)
            print(
                f"*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*\nstats={stats}\n*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*")
            print(f"################################# Ending Players Collection #################################")


            start_index = finish_index
            finish_index += args.finish_index

    finally:
        close_driver(driver)
        close_db(mongo_client)


if __name__ == "__main__":
    main()
