from tools.GegeneralTools import readFile
from tools.GegeneralTools import ifCondition

import string
import glob
import os
import sys
sys.getfilesystemencoding()


if __name__ == '__main__':
    check_folder_movies = r"dataset\asianwiki\movies_players"
    check_folder_posters = r"dataset\asianwiki\movies_posters"
    check_movie_path = r"../dataset/asianwiki_main_page_links.txt"
    check_movie_error_path = "asianwiki_movie_error_links_yedek.txt"
    movie_links = readFile(check_movie_path)
    # check_movie_error_path = list(set(readFile(check_movie_path)))
    # movie_links = list(set(movie_links).difference(check_movie_error_path))
    # del check_movie_error_path

    folder_movies_list = os.listdir(check_folder_movies)
    folder_movies_list.extend(os.listdir(check_folder_posters))
    movie_folders = list(set(folder_movies_list))
    movie_folders_new = []
    for folder_name in movie_folders:
        movie_name = folder_name \
            .replace("_-_", "_") \
            .replace('_', ' ') \
            .replace('-', ' ') \
            .replace('\n', '') \
            .translate(str.maketrans('', '', string.punctuation))
        movie_name = movie_name.replace(" ", "_")
        movie_folders_new.append(movie_name)
    del movie_folders

    new_links = []
    for href in movie_links:
        if (ifCondition(href, condition_type=0)):
            movie_name = href.split('/')[-1]
            movie_name = movie_name\
                .replace("_-_", "_")\
                .replace('_', ' ')\
                .replace('-', ' ')\
                .replace('\n', '')\
                .translate(str.maketrans('', '', string.punctuation))
            movie_name = movie_name.replace(" ", "_")
            if movie_name not in movie_folders_new:
                new_links.append(href)
                print(href)
