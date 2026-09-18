
from selenium.webdriver.common.by import By

from tools.SeleniumTools import (
    get_or_download_chromedriver,
    wait_load_main_webpage,
    close_driver
)

from tools.MongoDBTools import (
    get_mydramalist_mongo_collections,
    close_db
)

from datetime import datetime


def get_a_tag_info(web_driver, a_tag_xpath):
    links = []
    a_tags = web_driver.find_elements(By.XPATH, a_tag_xpath)
    for a_tag in a_tags:
        href = a_tag.get_attribute("href")
        if href:
            print("page_name: {text} - url: {url}".format(text=a_tag.text, url=href))
            links.append({"person_name": a_tag.text, "url": href})
    return links

def movies_set_save(col_movies, links):
    # movie url
    urls = [
        f'{raw["url"]}/cast'.replace(" ", "")
        for raw in links
        if raw["url"] is not None
    ]
    movie_match = list(col_movies.find({"url": {"$in": urls}}))
    movie_match_db_urls = [raw["url"] for raw in movie_match]
    diff_url_lists = list(set(urls).difference(set(movie_match_db_urls)))
    print(f"No_DB_links: {diff_url_lists}")

    now = datetime.now()
    # insert data
    if diff_url_lists:
        bulk_docs = []
        for url in diff_url_lists:
            clean = url.strip()
            if not clean:
                continue
            bulk_docs.append({
                "url": clean,
                "case": False,  # tarama henüz yapılmadı
                "created_at": now,
                "updated_at": now
            })
        if bulk_docs:
            try:
                col_movies.insert_many(bulk_docs, ordered=False)
                print(f"[init] {len(bulk_docs)} adet film/dizi linkleri DB'ye insert edildi.")
            except Exception as e:
                print(f"[init] col_movies insert_many hata: {e}")
        else:
            print("[init] Yüklenecek film/dizi verisi bulunamadı.")
    else:
        print("[init] Yüklenecek film/dizi verisi yok.")
    # # update data
    # if movie_match_db_urls:
    #     try:
    #         update_doc = {
    #             "$set": {
    #                 "case": False,
    #                 "updated_at": now
    #             }
    #         }
    #         col_movies.update_many(
    #             {"url": {"$in": movie_match_db_urls}, "case": True},
    #             update_doc
    #         )
    #     except Exception as e:
    #         print(f"[init] col_movies update_doc hata: {e}")


def players_set_save(col_players, links):
    # players url
    urls = [raw["url"] for raw in links if raw["url"] is not None]
    players_match = list(col_players.find({"url": {"$in": urls}}))
    players_match_db_urls = [raw["url"] for raw in players_match]
    diff_url_lists = list(set(urls).difference(set(players_match_db_urls)))

    no_save_players = []
    for url in diff_url_lists:
        for raw in links:
            if (raw["url"] is not None) and (raw["url"] == url):
                no_save_players.append(raw)

    print(f"save_player_datas:\n {no_save_players}")

if __name__ == "__main__":
    headless_bln = False
    driver_path = get_or_download_chromedriver()

    driver = None
    try:
        mongo_client, mongo_db, col_movies, col_players = get_mydramalist_mongo_collections()
        try:
            # "search_type": 1 -> players
            # "search_type": 2 -> movie
            # "pages" -> taranacak sayfa araligini belirtir
            search_urls = [
                {"url": "https://mydramalist.com/reviews/shows", "pages": range(201, 1001), "search_type": 2},
                # {"url": "", "pages": range(1, 2), "search_type": 1},
            ]

            # web_idx = 0
            restart_every = 200
            # for raw in search_urls:
            for web_idx, raw in enumerate(search_urls, start=1):
                links = []
                for page in raw["pages"]:  # örneğin iki sayfan varsa
                    # if page == 101:
                    #     break
                    # web_idx += 1
                    url = f"{raw['url']}?page={page}".replace(" ", "")
                    if not url:
                        continue
                    print(f"\n\n🔍==*  WEB PAGE URL: {url} *==")

                    # class_name = "box-body"
                    # class_name = "container-fluid"
                    class_name = "box"

                    driver = wait_load_main_webpage(
                        driver,
                        url,
                        web_idx - 1,
                        restart_every,
                        driver_path,
                        headless_bln,
                        by_tag_type=By.CLASS_NAME,
                        by_tag_name=class_name
                    )
                    # get ul list
                    ul_xpath = '//*[@id="collection-lists"]/div/div[2]/div[2]/ul/li/div[1]/div[2]/h2/a'
                    links_temp = get_a_tag_info(driver, ul_xpath)
                    if len(links_temp) > 0:
                        links.extend(links_temp)
                        continue

                    ul_xpath = '//*[@id="collection-lists"]/div/div[2]/div[2]/ul/li/div/div[2]/div[1]/div[1]/h2/a'
                    links_temp = get_a_tag_info(driver, ul_xpath)
                    if len(links_temp) > 0:
                        links.extend(links_temp)
                        continue

                    ul_xpath = '//*[@id="collection-lists"]/div/div[2]/div[2]/ul/li/div/div[2]/h2/a'
                    links_temp = get_a_tag_info(driver, ul_xpath)
                    if len(links_temp) > 0:
                        links.extend(links_temp)
                        continue

                    ul_xpath = '//*[@id="content"]/div/div[2]/div/div[1]/div/div/div/div/div[2]/h6/a[1]'
                    links_temp = get_a_tag_info(driver, ul_xpath)
                    if len(links_temp) > 0:
                        links.extend(links_temp)
                        continue

                    ul_xpath = '//*[@class="review"]/div[1]/div/div[1]/div[2]/b/a'
                    links_temp = get_a_tag_info(driver, ul_xpath)
                    if len(links_temp) > 0:
                        links.extend(links_temp)
                        continue

                # print(f"size: {len(links)} - data:{links}")
                print(f"size: {len(links)}")
                if links:
                    if raw["search_type"] == 1:
                        players_set_save(col_players, links)
                    elif raw["search_type"] == 2:
                        movies_set_save(col_movies, links)
        except Exception as ex:
            print(ex)
        finally:
            close_driver(driver)
            close_db(mongo_client)
    except Exception as e:
        print(f"Main_Error: {e}")
