from tools.GegeneralTools import normalize_url
from tools.SeleniumTools import (
    wait_load_main_webpage,
    close_driver
)

from tools.MongoDBTools import (
    get_asianwiki_mongo_collections,
    close_db
)

from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime

import sys
sys.getfilesystemencoding()


def movie_update_db(
        col_movies,
        clean_url,
        error_case: bool=False,
        error_message_str: str = ""
):
    now = datetime.now()

    # Bu film/dizi linki tarandı → case = true
    set_data = {
        "case": False,  # web sayfası taranmadı yap
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


if __name__ == '__main__':
    min_s = 0
    max_s = 200
    mongo_client = None

    # headless_bln = True/False
    headless_bln = False
    restart_every = 100

    driver = None
    driver_path = ChromeDriverManager().install()
    try:
        # Mongo bağlantısı
        mongo_client, mongo_db, col_movies, col_players = get_asianwiki_mongo_collections()
        # session = requests.Session()  # main'de 1 kere oluştur, hep kullan

        # START: Get Link on Wensite
        clean_url = normalize_url("https://asianwiki.com/Main_Page")
        driver = wait_load_main_webpage(
            driver,
            clean_url,
            0,
            restart_every,
            driver_path,
            headless_bln,
            by_tag_type=By.ID,
            by_tag_name="mw-content-text"
        )

        div_ids = ["slidorion2", "slidorion"]
        new_links = [
            normalize_url(a_tag.get_attribute('href').replace('%22', ''))
            for div_id in div_ids
                for a_tag in driver.find_element(By.ID, div_id).find_elements(By.TAG_NAME, "a")
                     if (
                            ('%3C/a%3E' not in a_tag.get_attribute('href'))
                            and ('%3Cbr%3E' not in a_tag.get_attribute('href'))
                     )
        ]
        # END: Get Link on Wensite

        save_links = list(set(new_links))
        # save_links = [
        # ]
        for link in save_links:
            print(f"İşlenen URL: {link}")
            movie_update_db(col_movies, link)
            # break

        # print(save_links)
        print("İşlem Bitti")

    except Exception as e:
        print(f"[Error] Ana bağlantıda bir sorun oluştu: {e}")
    finally:
        close_driver(driver)
        close_db(mongo_client)
