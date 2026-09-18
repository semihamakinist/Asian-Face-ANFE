
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from units.set_log import LOG
import errno
import re
import os


logging = LOG(log_file_name="set_folder")


def path_list(folder_path):
    return [(root_path, file_name)
            for root_path, d, file_names in os.walk(folder_path) for file_name in file_names
            if re.match(r'.*\.(jpg|jpeg|png)', file_name.lower(), flags=re.I)]


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.log_info("{} adlı yeni bir klasör oluşturuldu.".format(folder_path))
        return
    logging.log_info("{} adlı klasör sistemde zaten mevcut.".format(folder_path))


def mkdirP(path):
    assert path is not None

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
