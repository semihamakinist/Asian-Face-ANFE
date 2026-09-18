from tools.GegeneralTools import (
    extract_base64_from_xpath,
    load_profile_data_fast,
    saveSRCImage_faster,
    save_image_smart,
    exists_in_image,
    normalize_url,
    safe_old_urls,
    wait_load_img,
    readFile
)

from datetime import datetime
import requests
import json
import os

from tools.MongoDBTools import (
    get_asianwiki_mongo_collections,
    close_db
)

from tools.SeleniumTools import (
    find_cached_chromedriver,
    wait_load_main_webpage,
    close_driver,
)

def del_veriable(veriable_data):
    try:
        del veriable_data
    except Exception:
        pass


if __name__ == '__main__':
    main_data_path = os.path.join(os.getcwd(), 'dataset')
    image_main_data_path = os.path.join(main_data_path, 'asianwiki')

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
    }

    search_data = readFile(os.path.join(main_data_path, "search_player.json"))
    search_data = [json.loads(data.replace("},", "}").strip()) for data in search_data]

    # MongoDB bağlantısı
    client, db, col = get_asianwiki_mongo_collections()

    # headless_bln = True
    headless_bln = False
    session = requests.Session()  # main'de 1 kere oluştur, hep kullan

    driver_path = find_cached_chromedriver()
    driver = None
    restart_every = 50

    try:
        # for raw_data in search_data:
        for idx, raw_data in enumerate(search_data, start=1):
            target_url = normalize_url(raw_data.get("url"))
            if not target_url:
                continue

            # gereksiz browser bağlantısını önlemek için yapılan kontrol
            # Eski URL listesinde de varsa tekrar gitme
            query_match_data = {
                "$or": [
                    {"url": target_url},
                    {"old_urls": target_url}
                ]
            }
            existing_profile_url = col.find_one(
                query_match_data,
                {"_id": 1}
            )
            if existing_profile_url is not None:
                print(f"existing_profile_url: {target_url} zaten kayıtlı.")
                continue

            print(f"-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-**-\n")
            print(f"target_profile_url: {target_url}")
            try:
                driver, profile_data = load_profile_data_fast(
                    driver,
                    target_url,
                    idx-1,
                    restart_every,
                    driver_path,
                    headless_bln,
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
                    "updated_at": now
                }

                print(json.dumps(doc_data, default=str, ensure_ascii=False))
                # 1) No image ise ayrı mantık
                if "No_image_available" in img_scr:
                    existing_noimg = col.find_one(
                        {"url": target_url, "img_scr": "No_image_available"},
                        {"_id": 1}
                    )

                    if existing_noimg is None:
                        doc_data["folder_name"] = person_folder_name
                        doc_data["old_personel_names"] = []
                        doc_data["case"] = False
                        doc_data["created_at"] = now
                        col.insert_one(doc_data)

                # 2) Görsel varsa önce img_scr ile ara
                else:
                    existing_by_img = list(
                        col.find(
                            {"img_scr": img_scr},
                            {
                                "_id": 1,
                                "url": 1,
                                "old_urls": 1,
                                "img_scr": 1,
                                "personel_name": 1,
                                "folder_name": 1,
                                "old_personel_names": 1
                            }
                        )
                    )

                    # 2.a) img_scr hiç yoksa -> yeni kayıt + görsel kaydet
                    # if not existing_by_img veya len(all_player_urls) == 0 kontrol et
                    # if len(existing_by_img) == 0:
                    if not existing_by_img:
                        print(f"--------------------\n")
                        wait_load_img(driver, person_img_xpath)
                        check_save_img = save_image_smart(
                            img_url=img_scr,
                            headers=headers,
                            main_path=image_main_data_path,
                            movie_name=f"players",
                            folder_name=person_folder_name,
                            session=session,
                            base64_fetcher=lambda: extract_base64_from_xpath(driver, person_img_xpath)
                            # sadece 403 olursa çağrılır
                        )

                        doc_data["folder_name"] = person_folder_name
                        doc_data["old_personel_names"] = []
                        doc_data["case"] = check_save_img
                        doc_data["created_at"] = now
                        col.insert_one(doc_data)
                        print(f"## Image_Saved-(DB and Local): {doc_data}\n--------------------")

                    # 2.b) img_scr varsa -> url kontrol et
                    else:
                        print(f"--------------------\n")
                        # gelen liste tum "folder_name" klasorlerini kontrol et.
                        # Eger herhangi birinde varsa yani 1 donmus resmi ekleme
                        # Ama eger yoksa ve herhangi "folder_name" klasorde resim bulunmadıysa goruntuyu indir
                        existing_folder_names = []
                        exists_img_filename = []
                        for data in existing_by_img:
                            current_folder_name = data.get("folder_name")
                            existing_folder_names.append(current_folder_name)
                            exists_img_filename.append(
                                exists_in_image(
                                    img_url=img_scr,
                                    main_path=image_main_data_path,
                                    movi_name="players",
                                    folder_name=current_folder_name
                                )
                            )

                        target_folder_name = existing_folder_names[0] if existing_folder_names else person_folder_name
                        # resim indirilmemişse indir
                        if (1 not in exists_img_filename) and (0 in exists_img_filename):
                            wait_load_img(driver, person_img_xpath)
                            saveSRCImage_faster(
                                img_url=img_scr,
                                movi_name="players",
                                folder_name=target_folder_name,
                                header=headers,
                                main_path=image_main_data_path,
                                driver=driver,
                                img_xpath=person_img_xpath,
                            )
                        same_url_exists = any(normalize_url(d.get("url")) == target_url for d in existing_by_img)

                        # Aynı img_scr + aynı url zaten varsa hiçbir şey yapma yeni veriye gec
                        if same_url_exists:
                            # "url, img_scr" -> bu veri kaydi var, hic bir sey yapma
                            continue

                        existing_current_urls = set()
                        existing_old_urls = set()
                        existing_personel_names = set()
                        existing_old_personel_names = set()

                        for d in existing_by_img:
                            current_url = normalize_url(d.get("url"))
                            if current_url:
                                existing_current_urls.add(current_url)
                            for old_u in safe_old_urls(d.get("old_urls", [])):
                                if old_u:
                                    existing_old_urls.add(old_u)

                            old_name = d.get("personel_name")
                            if old_name:
                                existing_personel_names.add(old_name)
                            for old_pn in d.get("old_personel_names", []):
                                if old_pn:
                                    existing_old_personel_names.add(old_pn)

                        # eklenecek eski url:
                        # - boş olmamalı
                        # - yeni url ile aynı olmamalı
                        # - old_urls içinde zaten bulunmamalı
                        old_urls_to_add = sorted(
                            u for u in existing_current_urls
                            if u and u != target_url and u not in existing_old_urls
                        )
                        old_personel_names_to_add = sorted(
                            n for n in existing_personel_names
                            if n and n != person_folder_name and n not in existing_old_personel_names
                        )

                        # Aynı img_scr var ama url farklıysa tüm ilgili kayıtları güncelle
                        update_doc = {
                            "$set": {
                                "url": target_url,
                                "personel_name": person_folder_name,
                                "gender": gender,
                                "updated_at": now
                            }
                        }

                        add_to_set_data = {}
                        if old_urls_to_add:
                            add_to_set_data["old_urls"] = {"$each": list(set(old_urls_to_add))}

                        if old_personel_names_to_add:
                            add_to_set_data["old_personel_names"] = {"$each": list(set(old_personel_names_to_add))}

                        if add_to_set_data:
                            update_doc["$addToSet"] = add_to_set_data

                        print(f"#** UpdateData ** # {update_doc}")
                        col.update_many(
                            {"img_scr": img_scr},
                            update_doc
                        )

            except Exception as ex:
                print(f"Hata: {target_url} -> {ex}")

                error_doc = {
                    "personel_name": "",
                    "img_scr": "No_image_available",
                    "url": target_url,
                    "case": False,
                    "error": str(ex),
                    "updated_at": datetime.now()
                }

                # Aynı hata kaydını tekrar tekrar basmamak için
                col.update_one(
                    {"url": target_url, "img_scr": "No_image_available"},
                    {
                        "$set": error_doc,
                        # sadece ilk kez veri eklendiginde asagidaki adim calisir.
                        "$setOnInsert": {"created_at": datetime.now()}
                    },
                    upsert=True
                )
            # finally:
            #     pass
    finally:
        try:
            close_driver(driver)
            del_veriable(driver)
        except:
            pass

        close_db(client=client)
        del_veriable(client)
        del_veriable(db)
        del_veriable(col)
