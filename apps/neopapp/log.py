"""Initializes the logger with a custom name"""

import logging
import datetime
import os
import sys

def init_logger():
    """Set up the log file"""
    if not os.path.exists('logs/'):
        os.makedirs('logs/')
    filename = 'logs/stocktickerv2 ' + str(datetime.datetime.now()) + '.txt'
    if sys.version_info[:2] > (3, 7):
        logging.basicConfig(filename=filename, encoding='utf=8', level=logging.DEBUG)
    else:
        logging.basicConfig(filename=filename, level=logging.DEBUG)

    get_logger().info('Running with Python %s.%s', sys.version_info[0], sys.version_info[1])

def get_logger():
    """Get the logger for this application"""
    return logging.getLogger('stocktickerv2')