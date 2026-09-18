from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from datetime import datetime
import logging
import os


class LOG:
    def __init__(self, log_file_name="logging"):
        now_date = datetime.now()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=os.path.join(os.getcwd(), "logs",
                                                  '{}-{}-{}-pull_{}.txt'.format(now_date.year, now_date.month,
                                                                                now_date.day, log_file_name)),
                            filemode='a'
                            )
    @staticmethod
    def log_info(info_message):
        logging.info(info_message)

    @staticmethod
    def log_error(error_message):
        logging.info(error_message, exc_info=True)
