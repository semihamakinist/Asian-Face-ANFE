from pymongo import MongoClient
from datetime import datetime

import os

# ----------------- MongoDB Yardımcıları ----------------- #
def ensure_asianwiki_movies_indexes(col_movies):
    try:
        col_movies.create_index("url", unique=True)
        col_movies.create_index("updated_at")
        col_movies.create_index([("url", 1), ("img_scr", 1)], unique=True)
        col_movies.create_index("img_scr")
        col_movies.create_index("case")
        col_movies.create_index("case_poster")
        col_movies.create_index("case_players")

    except Exception as ex:
        print(f"Index warning: {ex}")

def ensure_asianwiki_players_indexes(col_players):
    try:

        col_players.create_index("img_scr")
        col_players.create_index("url")
        col_players.create_index("old_urls")
        col_players.create_index([("url", 1), ("img_scr", 1)], unique=True)
        col_players.create_index("updated_at")
    except Exception as ex:
        print(f"Index warning: {ex}")

def get_asianwiki_mongo_collections():
    """
    MongoDB bağlantısını kurar ve gerekli koleksiyonları döner.
    ENV değişkenleriyle yapılandırılabilir:

      - MONGO_URI    (default: mongodb://localhost:27017)
      - MONGO_DB_NAME (default: myasianwiki_db)

    Collection'lar:
      - asianwiki_movie
      - asianwiki_player_infos
    """
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db_name = os.getenv("MONGO_DB_NAME", "myasianwiki_db")

        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]

        col_movies = db["asianwiki_movie"]
        col_players = db["asianwiki_player_infos"]
        return client, db, col_movies, col_players

    except Exception as e:
        print("Error: Database connection not found. "
              "Please check your .env file or run "
              "'python3 -m run.main' to start the server. "
              "\n{error_str}".format(error_str=e))
        return None

# ----------------- MongoDB Yardımcıları ----------------- #
def get_mydramalist_mongo_collections():
    """
    MongoDB bağlantısını kurar ve gerekli koleksiyonları döner.
    ENV değişkenleriyle yapılandırılabilir:

      - MONGO_URI    (default: mongodb://localhost:27017)
      - MONGO_DB_NAME (default: mydramalist_db)

    Collection'lar:
      - mydramalist_movie
      - mydramalist_player_infos
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db_name = os.getenv("MONGO_DB_NAME", "mydramalist_db")

    client = MongoClient(mongo_uri)
    db = client[mongo_db_name]

    col_movies = db["mydramalist_movie"]
    col_players = db["mydramalist_player_infos"]

    # INDEX’LER
    col_movies.create_index("url", unique=True)
    col_players.create_index("url", unique=True)

    return client, db, col_movies, col_players

def get_asianwiki_mongo_player_collections():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db_name = os.getenv("MONGO_DB_NAME", "myasianwiki_db")

        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]

        col_players = db["asianwiki_player_infos"]
        return client, db, col_players
    except Exception as e:
        print("Error: Database connection not found. "
              "Please check your .env file or run "
              "'python3 -m run.main' to start the server. "
              "\n{error_str}".format(error_str=e))
        return None

def get_asianwiki_mongo_player_logs_collections():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db_name = os.getenv("MONGO_DB_NAME", "myasianwiki_db")

        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]

        col_players = db["asianwiki_player_infos_logs"]
        return client, db, col_players
    except Exception as e:
        print("Error: Database connection not found. "
              "Please check your .env file or run "
              "'python3 -m run.main' to start the server. "
              "\n{error_str}".format(error_str=e))
        return None

def get_asianwiki_mongo_movie_collections():
    try:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        mongo_db_name = os.getenv("MONGO_DB_NAME", "myasianwiki_db")

        client = MongoClient(mongo_uri)
        db = client[mongo_db_name]

        col_movies = db["asianwiki_movie"]
        return client, db, col_movies
    except Exception as e:
        print("Error: Database connection not found. "
              "Please check your .env file or run "
              "'python3 -m run.main' to start the server. "
              "\n{error_str}".format(error_str=e))
        return None

def update_asianwiki_movie_page(
        col_movies,
        target_url: str,
        movie_img_scr: str,
        movie_folder_name: str,
        has_poster: bool,
        has_players: bool,
        error_page: bool = False,
        error_exception: str = "",
):
    now = datetime.now()

    set_data = {
        "img_scr": movie_img_scr,
        "case": True, # Sayfa tarandı
        "case_poster": has_poster, # poster resmi var -> True, yok -> False
        "case_players": has_players, # oyuncu resim listesi var -> True, yok -> False
        "updated_at": now
    }
    if error_page:
        set_data["error"] = {'status': True, 'message': error_exception}

    # oyuncu listesi ya da posteri varsa folder_name sakla
    if has_poster or has_players:
        set_data["movie_folder_name"] = movie_folder_name

    data_temp = {
        "match_data": {"url": target_url},
        "set_data": {
            "$set": set_data,
            "$setOnInsert": {
                "created_at": now
            }
        },
    }
    print(f"set_data: {data_temp}")

    col_movies.update_one(
        {"url": target_url},
        {
            "$set": set_data,
            "$setOnInsert": {
                "created_at": now
            }
        },
        upsert=True
    )

def write_asianwiki_log(
        log_col,
        run_id,
        url,
        action,
        status="success",
        img_scr=None,
        old_url=None,
        new_url=None,
        message=None,
        extra=None):
    doc = {
        "run_id": run_id,
        "url": url,
        "img_scr": img_scr,
        "action": action,
        "status": status,
        "old_url": old_url,
        "new_url": new_url,
        "message": message,
        "created_at": datetime.now()
    }

    if extra and isinstance(extra, dict):
        doc["extra"] = extra

    log_col.insert_one(doc)

def close_db(client):
    if client is not None:
        try:
            client.close()
            print("[INFO] MongoDB bağlantısı kapatıldı.")
        except Exception as e:
            print(f"[UYARI] MongoDB bağlantısı kapatılamadı: {e}")
