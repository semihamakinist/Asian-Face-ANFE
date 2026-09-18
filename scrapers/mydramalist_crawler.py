from tools.GegeneralTools import (
    build_person_record_from_blob,
    extract_base64_from_xpath,
    extract_profile_blob_fast_v3,
    extract_people_db_fast_v3,
    save_image_smart,
    safe_folder_name,
    sleep_if_needed,
    normalize_url,
    get_dbperson
)

from pymongo import UpdateOne
from tools.MongoDBTools import (
    get_mydramalist_mongo_collections,
    close_db
)

from tools.SeleniumTools import (
    get_or_download_chromedriver,
    wait_load_main_webpage,
    close_driver,
)

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from datetime import datetime
import requests
import argparse
import json
import os

import sys

sys.getfilesystemencoding()


def movie_insert_many_db(col_movies, movie_url_list):
    now = datetime.now()
    # normalize + boşları at + aynı batch içindeki duplicate'leri temizle
    urls = list(set(filter(None, map(normalize_url, movie_url_list))))

    if not urls:
        return 0

    operations = [
        UpdateOne(
            {"url": url},
            {
                "$setOnInsert": {
                    "url": url,
                    "case": False,
                    "updated_at": now,
                    "created_at": now
                }
            },
            upsert=True
        )
        for url in urls
    ]
    try:
        result = col_movies.bulk_write(operations, ordered=False)
        if result.upserted_count > 0:
            print(f"💾 [Info] New Movie Insert Count: {result.upserted_count}")
        if result.matched_count > 0:
            print(f"ℹ️ [Info] Existing/Matched Count: {result.matched_count}")
    except Exception as e:
        print(f"movie_insert_many_db Error: {e}")

def movie_insert_db(col_movies, url):
    now = datetime.now()
    result = col_movies.update_one(
        {"url": url},
        {
            "$setOnInsert": {
                "url": url,
                "case": False,  # ilk kez ekleniyorsa "taransın" durumunda
                "updated_at": now,
                "created_at": now
            }
        },
        upsert=True
    )
    if result.upserted_id is not None:
        print(f"💾 [Info] Insert New Movie URL: {url}")

def movie_update_db(col_movies, clean_url, error_case: bool=False, error_message_str: str = ""):
    now = datetime.now()

    # Bu film/dizi linki tarandı → case = true
    set_data = {
        "case": True,  # CAST sayfası tarandı
        "updated_at": now
    }
    if error_case:
        set_data["error"] = error_message_str

    col_movies.update_one(
        {"url": clean_url},
        {
            "$set": set_data,
            "$setOnInsert": {
                "created_at": now
            }
        },
        upsert=True
    )

def player_insert_db(col_players, person_url, ordered_data, check_save_img):
    now = datetime.now()
    # mydramalist_player_infos collection yapısı:
    # case = true  -> resmi var
    # case = false -> resmi yok
    doc = {
        "case": check_save_img,
        **ordered_data,
        "updated_at": now
    }

    # created_at sadece ilk seferde set edilsin
    col_players.update_one(
        {"url": person_url},
        {
            "$set": doc,
            "$setOnInsert": {"created_at": now}
        },
        upsert=True
    )

    # ✅, 💾, 📥, 📝
    print("📝 save_data: {person} ".format(
        person=json.dumps(doc, indent=4, ensure_ascii=False, default=str))
    )

# ----------------- Ana Script ----------------- #
if __name__ == '__main__':
    # intalling 1*10 movies:
    # #**-- headless: False --**#
    #   python mydramalist_crawler.py -re 100 -smin 1 -smax 2 -st 1 -cb 1 -si 0 -fi 10
    # #**-- headless: True --**#
    #   python mydramalist_crawler.py --headless -re 100 -smin 1 -smax 2 -st 1 -cb 1 -si 0 -fi 10

    # intalling 10*10 movies:
    # #**-- headless: False --**#
    #   python mydramalist_crawler.py -re 100 -smin 1 -smax 2 -st 10 -cb 1 -si 0 -fi 10
    # #**-- headless: True --**#
    #   python mydramalist_crawler.py --headless -re 100 -smin 1 -smax 2 -st 10 -cb 1 -si 0 -fi 10
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("-cb", "--choose_browser_id", type=int, default=2, help="Choose Browser: 1-Chrome, 2-Opera")
    parser.add_argument("-si", "--start_index", type=int, default=0, help="Start Index: 0-500")
    parser.add_argument("-fi", "--finish_index", type=int, default=2, help="Finish Index: batch size")
    parser.add_argument("-st", "--step_index", type=int, default=1, help="Step count (kaç batch)")

    parser.add_argument("-hd", "--headless", action="store_true", help="Chrome/Opera görünmeden çalışır. Hız ve stabilite için önerilir.")
    parser.add_argument("-re", "--restart-every", type=int, default=40, help="Driver kaç sayfada bir yenilensin. 0 = hiç yenileme.")
    parser.add_argument("-smin", "--sleep-min", type=float, default=0.0, help="İstekler arası minimum bekleme.")
    parser.add_argument("-smax", "--sleep-max", type=float, default=0.0, help="İstekler arası maksimum bekleme. 0 = bekleme yok.")
    # parser.add_argument("--skip-existing-movies", action="store_true", help="DB'de işlenmiş görünen film/dizi sayfalarını atlar.")

    # Read arguments from command line
    args = parser.parse_args()

    file_root_path = os.path.join(os.getcwd(), 'dataset')
    main_data_path = os.path.join(file_root_path, 'mydramalist')

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
    }

    start_index = args.start_index
    finish_index = start_index + args.finish_index

    save_root = main_data_path
    os.makedirs(save_root, exist_ok=True)

    min_s = args.sleep_min
    max_s = args.sleep_max
    mongo_client = None
    # headless_bln = True/False
    headless_bln = args.headless
    restart_every = args.restart_every

    print(f"min_s:{min_s} - max_s: {max_s} - headless_bln: {headless_bln} - restart_every: {restart_every}")
    driver = None
    driver_path = get_or_download_chromedriver()

    try:
        # Mongo bağlantısı
        mongo_client, mongo_db, col_movies, col_players = get_mydramalist_mongo_collections()

        # Ünlü profilleri için alan sırası
        ordered_keys = [
            "born", "display_name", "family_name", "first_name",
            "folder_name", "gender", "img_scr", "nationality",
            "person_name", "url"
        ]
        session = requests.Session()  # main'de 1 kere oluştur, hep kullan

        for s_index in range(args.step_index):
            print(
                f"\n=== STEP {s_index + 1} / {args.step_index} | "
                f"start_index: {start_index} - finish_index: {finish_index} ===")

            # Mongo üzerinden case=false olan (taranmamış) film/dizi linklerini çek
            # start_date = datetime.now().replace(
            #     hour=0,
            #     minute=0,
            #     second=0,
            #     microsecond=0
            # )
            # end_date = start_date + timedelta(days=1)
            # start_date = datetime.strptime(
            #     "2026-06-01T00:00:00.000Z",
            #     "%Y-%m-%dT%H:%M:%S.%fZ"
            # )
            # print(f"start_date: {start_date}")
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
            # print(f"movie_batch_size: {len(movie_batch)}")

            if not movie_batch:
                print("İşlenecek yeni film/dizi linki kalmadı (case=false yok).")
                break
            # web_idx = 0
            # movie_batch = [{"url": "https://mydramalist.com/13239-signal/cast"}]
            for web_idx, movie_data in enumerate(movie_batch, start=1):
                # web_idx += 1
                step_idx = int(finish_index / (args.finish_index if args.finish_index != 0 else 1))
                clean_url = normalize_url(movie_data["url"])

                if not clean_url:
                    continue
                print("****************************************************************************************")
                print(
                    f"\n🔍==* Web STEP {step_idx}: {web_idx}/{args.finish_index} *== "
                    f"Web Sayfası İşleniyor: {clean_url}"
                )

                # driver = None
                profile_infos = []

                # 1) CAST sayfasından ünlü profillerin URL listesini çek
                try:
                    # driver = setup_driver(headless=headless_bln, drive_path=driver_path)
                    driver = wait_load_main_webpage(
                        driver,
                        clean_url,
                        web_idx - 1,
                        restart_every,
                        driver_path,
                        headless_bln,
                        by_tag_type=By.CLASS_NAME,
                        by_tag_name="box-body"
                    )

                    # Oyuncu Listesi yüklendi mi?
                    try:
                        CAST_CONTAINER = '//*[@id="content"]/div/div[2]/div/div[1]/div/div[3]'
                        WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, CAST_CONTAINER))
                        )
                        # container içi gerçekten dolsun:
                        container = driver.find_element(By.XPATH, CAST_CONTAINER)
                        WebDriverWait(driver, 5).until(
                            lambda d: len(container.find_elements(By.CSS_SELECTOR, "ul li")) > 0)

                    except Exception as e:
                        print(f"Movie_WebDriverWait_Error: {str(e)} - movie_url: {clean_url}")
                        movie_update_db(
                            col_movies,
                            clean_url,
                            error_case=True,
                            error_message_str=f"Movie_WebDriverWait_Error: {str(e)}".strip()
                        )
                        continue

                    # A tag'lerini çek ve href linkleri ile kişi isimlerini al
                    # Artık profile_infos_noimage state'ini Mongo tuttuğu için buraya boş liste verebiliriz
                    profile_infos = extract_people_db_fast_v3(driver, col_players)
                    movie_update_db(col_movies, clean_url)

                except TimeoutException as e:
                    print("❌ TimeoutException: ", e)
                except Exception as e:
                    print("❌ Movie sayfası işlenirken beklenmeyen hata: ", e)
                sleep_if_needed(min_s=min_s, max_s=max_s)

                # 2) Ünlü profil sayfalarını tek tek gez ve player_infos collection'a yaz
                try:
                    # Bu profiller daha önce işlenmiş mi? (resimli veya resimsiz fark etmez)
                    profile_info_urls, existed_urls = get_dbperson(profile_infos, col_players)
                    profile_info_counter = len(profile_info_urls) - len(existed_urls)

                    print(
                        f"🔗 Toplam {len(profile_info_urls)} profil bulundu.\n"
                        f"💾 Bunlardan {profile_info_counter} tane profilin kaydı yapılacak."
                    )
                    if profile_info_counter == 0:
                        continue

                    for idx, person in enumerate(profile_infos, start=1):
                        person_url = normalize_url(person.get('url'))
                        if person_url in existed_urls:
                            # print(f"person_url: {person_url} zaten var.")
                            continue

                        print("##########################################################################")
                        person_name = person.get('person_name')
                        print(f"🔍 Profil İşleniyor: {person_name} - {person_url}")

                        try:
                            driver = wait_load_main_webpage(
                                driver,
                                person_url,
                                idx - 1,
                                restart_every,
                                driver_path,
                                headless_bln,
                                by_tag_type=By.CLASS_NAME,
                                by_tag_name="box-body"
                            )

                            # profil bilgilerini toplamaya basla
                            left_slide_xpath = '//*[@id="content"]/div/div[2]/div/div[2]/div'
                            img_xpath = '//*[@id="content"]/div/div[2]/div/div[2]/div/div[1]/div[2]/img'
                            display_name_xpath = '//*[@id="content"]/div/div[2]/div/div[2]/div/div[1]/div[1]/h1'
                            movie_xpath = '//*[@id="content"]/div/div[2]/div/div[1]/div[1]/div[5]/table/tbody/tr/td[2]/b/a'

                            try:
                                WebDriverWait(driver, 5).until(
                                    EC.visibility_of_element_located((By.XPATH, left_slide_xpath))
                                )
                                WebDriverWait(driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, display_name_xpath))
                                )
                            except Exception as e:
                                print(f"Profile_WebDriverWait_Error: {e} - person_url: {person_url}")
                                continue

                            blob = extract_profile_blob_fast_v3(driver)
                            # Kişinin oynadığı diğer dizi/filmleri al → yeni movie linkleri ekle
                            try:
                                movie_url_list_temp = blob.get("movie_urls", [])
                                movie_insert_many_db(col_movies, movie_url_list_temp)

                            except Exception as e:
                                print("get_movie_list Error: ", e)

                            person = build_person_record_from_blob(
                                person_url=person_url,
                                blob=blob,
                                safe_folder_name_fn=safe_folder_name
                            )

                            check_save_img = save_image_smart(
                                person["img_scr"],
                                headers,
                                main_path=save_root,
                                movie_name=f"players/{person['gender']}",
                                folder_name=person["folder_name"],
                                session=session,
                                base64_fetcher=lambda: extract_base64_from_xpath(driver, img_xpath)
                                # sadece 403 olursa çağrılır
                            )

                            # Ordered dict (var olan key yoksa None ile doldur)
                            ordered_data = {k: person.get(k, None) for k in ordered_keys}
                            player_insert_db(col_players, person_url, ordered_data, check_save_img)

                        except Exception as ex:
                            print(f"❌ Profil işlenirken hata: {ex}")

                except Exception as e:
                    print("❌ Beklenmedik Hata (People Info bloğu): ", e)

                # bir film sonrası kısa bekleme
                sleep_if_needed(min_s=min_s, max_s=max_s)

            # bir step bittikten sonra indeksleri güncelle
            start_index = finish_index
            finish_index += args.finish_index
    except Exception as e:
        print(f"[HATA] Ana akışta beklenmeyen hata: {e}")

    finally:
        close_driver(driver)
        close_db(mongo_client)
