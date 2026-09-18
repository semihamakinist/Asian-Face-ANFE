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


def write_json(file_path, json_data):
    with open(file_path, "w", encoding='utf8') as fp:
        fp.write(json.dumps(json_data, indent=4, sort_keys=True))
    fp.close()
