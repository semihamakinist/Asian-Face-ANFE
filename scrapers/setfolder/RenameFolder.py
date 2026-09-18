from tools.GegeneralTools import setFamousName
from tools.GegeneralTools import readFile

import string
import glob
import os


def rename_directory(old_name, new_name):
    os.rename(old_name, new_name)


if __name__ == '__main__':
    gender_main_path = r"../dataset/asianwiki/gender"
    str_punctuation_digits = string.punctuation.replace('-', '').replace('_', '') + string.digits

    data_size_after = 1000
    data_size_before = "Test1000"
    data_size = 1000
    gender_folder_keys = [
        {
            "id": "actors",
            "gender": "male",
            "counter": len(glob.glob(os.path.join(gender_main_path, f'{data_size_after}',
                                                  'male', '__KontrolEdilenler', '*', '*.*')))
        },
        # {
        #     "id": "actresses",
        #     "gender": "female",
        #     "counter": len(glob.glob(os.path.join(gender_main_path, f'{data_size_after}',
        #                                           'female', '__KontrolEdilenler', '*', '*.*')))
        # }
    ]

    for data in gender_folder_keys:
        gender_type = data["gender"]
        print(f'START: gender: {gender_type} - counter: {data["counter"]}')
        gender_sub_path = os.path.join(gender_main_path, f'{data_size_after}', gender_type, '__KontrolEdilenler')
        gender_folder_list = os.listdir(gender_sub_path)
        index_count = 0
        for folder_name in gender_folder_list:
            if ('_female' in folder_name) or ('_male' in folder_name):
                src = os.path.join(gender_sub_path, folder_name)
                dest = os.path.join(gender_sub_path, folder_name.replace("_female", "").replace("_male", ""))
                os.rename(src, dest)
                print(f'src: {src} - dest: {dest}')
                # index_count += 1
                # if index_count == 100:
                #     break

    # Example usage
    # rename_directory('old_directory', 'new_directory')
