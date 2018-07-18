#!python3
# -*- coding: utf-8 -*-

PHOTO_ARCHIVE = r'F:\AllPhoto'  # Place where to pick up photos from
# PHOTO_ARCHIVE = r'C:\ya.disk\YandexDisk\Фотокамера'  # Place where to pick up photos from
SCREENSAVER_FOLDER = r'C:\screensaver'  # Place where to put chosen photos
INITIAL_NUMBER_OF_PHOTOS = 100  # Number of photos to pick initially
NUMBER_OF_PHOTOS_TO_ADD = 5  # Number of photo to add after some time
MINUTES_TO_REFRESH = 1  # Minutes to wait before adding new photos
MAX_TOTAL_SIZE = 1024 * 1024 ** 2  # Maximum size of folder with chosen photos
# (remove some photos after exceeding this value)
NUMBER_OF_PHOTOS_TO_DELETE = 20  # How many photos to delete it order to clean screensaver photo
