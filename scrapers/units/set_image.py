from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from units.set_log import LOG
import numpy as np
import base64
import cv2
import os


logging = LOG(log_file_name="set_image")


def hex2bgr2rgb(hex_code):
    hex = hex_code.lstrip('#')
    hlen = len(hex)
    b, g, r = tuple(int(hex[i:i + int(hlen / 3)], 16) for i in range(0, hlen, int(hlen / 3)))
    return r, g, b


def base_2_image(jpg_as_str):
    img = base64.b64decode(jpg_as_str)
    npimg = np.fromstring(img, dtype=np.uint8)
    # BGR formatinda resim doner
    # return cv2.cvtColor(cv2.imdecode(npimg, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    return cv2.imdecode(npimg, cv2.IMREAD_COLOR)


def resize_frame(img, w, h, scale_percent):
    # calculate the 50 percent of original dimensions
    # width = int(frame.shape[1] * scale_percent / 100)
    # height = int(frame.shape[0] * scale_percent / 100)
    width = int(w * scale_percent / 100)
    height = int(h * scale_percent / 100)
    return cv2.resize(img, (width, height))


def read_image_rgb_bgr(image_path):
    try:
        rgb_img = cv2.imread(image_path)
        bgr_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)
        return rgb_img, bgr_img
    except Exception as e:
        logging.log_error("read_image_rgb_bgr Failed: {}, image_path: {}".format(e, image_path))
        return None, None


def read_image_rgb(image_path):
    try:
        return cv2.imread(image_path)
    except Exception as e:
        logging.log_error("read_image_rgb Failed: {}, image_path: {}".format(e, image_path))
        return None


def convert_rgb_bgr(image_data):
    try:
        if image_data.size > 0:
            return cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logging.error("convert_rgb_bgr Failed: {}".format(e))
        return None


def write_image_cv(image_path, image_arr):
    # convert BGR to RGB
    # img = cv2.cvtColor(image_arr, cv2.COLOR_RGB2BGR)
    try:
        if not os.path.exists(image_path):
            # cv2.imwrite(image_path, cv2.cvtColor(image_arr, cv2.COLOR_RGB2BGR))
            cv2.imwrite(image_path, image_arr)
        return True
    except Exception as e:
        logging.error("write_image_cv Failed: {}".format(e))
        return False
