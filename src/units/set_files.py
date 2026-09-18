from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import json


def read_json(file_path):
    json_data = None
    with open(file_path, "r", encoding='utf8') as fp:
        json_data = json.load(fp)
    fp.close()
    return json.loads(json.dumps(json_data, ensure_ascii=False))


def ReadJsonData(file_path):
    datas = []
    try:
        with open(file_path, 'r') as f:
            datas = json.load(f)
        f.close()
    except Exception as ex:
        print(f"readJsonData Error: {ex}")
    return datas


def write_json(file_path, json_data):
    with open(file_path, "w", encoding='utf8') as fp:
        fp.write(json.dumps(json_data, indent=4, sort_keys=True))
    fp.close()


def WriteJsonData(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        f.close()
    except Exception as ex:
        print(f"writeJsonData Error: {ex}")