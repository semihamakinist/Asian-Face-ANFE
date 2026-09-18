import os
import shutil

if __name__ == '__main__':
    folder_mainpath = r"dataset\asianwiki\movies_payers"
    folder_playersmainpath = r"dataset\asianwiki\payers"
    move_folder_mainpath = r"dataset\asianwiki\movies_posters"

    names_of_folders = os.listdir(folder_mainpath)
    count = 0
    for name_of_folder in names_of_folders:
        folder_path = os.path.join(folder_mainpath, name_of_folder)
        move_folder_path = os.path.join(move_folder_mainpath, name_of_folder)
        names_of_subfolder = os.listdir(folder_path)
        sub_file_cont = 0
        if len(names_of_subfolder) is 3:
            if os.path.isfile(os.path.join(folder_path, names_of_subfolder[0])):
                sub_file_cont += 1
            if os.path.isfile(os.path.join(folder_path, names_of_subfolder[1])):
                sub_file_cont += 1
            if os.path.isfile(os.path.join(folder_path, names_of_subfolder[2])):
                sub_file_cont += 1
            if sub_file_cont >= 2:
                print(f"name_of_folder: {name_of_folder} - len: {len(names_of_subfolder)}")
                count += 1

        # if len(names_of_subfolder) is 2:
        #     if (".jp" in names_of_subfolder[0]) and (".jp" in names_of_subfolder[1]):
        #         print(f"name_of_folder: {name_of_folder} - len: {len(names_of_subfolder)}")
        #         count += 1
        # if len(names_of_subfolder) is 1:
        #     print(f"name_of_folder: {name_of_folder} - len: {len(names_of_subfolder)}")
        #     # print(f"name_of_folder: {name_of_folder} - folder_path: {folder_path} "
        #     #       + f"- move_folder_path: {move_folder_path} - len: {len(names_of_subfolder)} "
        #     #         f"")
        #     shutil.move(folder_path, move_folder_path)
        #     # break
        #     count += 1
    print(f"count_movie: {count}")
    # names_of_playerfolders = os.listdir(folder_playersmainpath)
    # count = 0
    # for name_of_playerfolder in names_of_playerfolders:
    #     if '-' in name_of_playerfolder:
    #         if name_of_playerfolder.replace("-", "_") in names_of_playerfolders:
    #             print(f"name_of_folder: {name_of_playerfolder}")
    #             count += 1
    # print(f"count_palyer: {count}")
