#!python3.7
# -*- coding: utf-8 -*-

import os
import shutil
import random
import time
import config  # Config need to store path to folders to work to

print('Hi there!')


# Look through the whole archives with photos and create a list of all existing files with jpg extension
def get_list_of_photos(archive_path):
    list_of_pictures = []
    for root, subfolders, files in os.walk(archive_path):
        print(f'Checking {root}')
        for file in files:
            # print(f'Checking {file}')
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                list_of_pictures.append(os.path.join(root, file))

    print(f'There are {len(list_of_pictures)} pictures.')
    return list_of_pictures


# TODO Make user to be able to choose number of photos
def choose_random_photos(pictures, number):
    random_pics = random.sample(pictures, 100)
    for pic in random_pics:
        print(pic)
    return random_pics


# Copy chosen photo to a given folder (folder where Windows is set to get pictures for a slideshow)
def copy_photos(photos):
    if os.path.exists(config.SCREENSAVER_FOLDER):
        shutil.rmtree(config.SCREENSAVER_FOLDER)
    os.mkdir(config.SCREENSAVER_FOLDER)
    for photo in photos:
        new_path = os.path.join(config.SCREENSAVER_FOLDER, os.path.basename(photo))
        if not os.path.exists(new_path):
            print(f'Copying {os.path.basename(photo)}...')
            shutil.copy2(photo, new_path)
        else:
            print(f'{os.path.basename(photo)} already exists.')
    print('Done!')


# This chunk of code let user to choose mode of how script will work
# Also it is responsible for rephrashing photos after given amount of time
while True:
    print('Choose one option below:\n1. Copy 5 random photos.\n2. Copy photos that were taken in this day in the past')
    option = int(input('Please type "1" or "2": '))
    if option == 1:
        pics = get_list_of_photos(config.PHOTO_ARCHIVE)
        random_photos = choose_random_photos(pics, config.INITIAL_NUMBER_OF_PHOTOS)
        copy_photos(random_photos)
        while True:
            timer = config.MINUTES_TO_REFRESH
            for minutes in range(timer, 0, -1):
                print(f'{minutes} minutes left before adding another {config.NUMBER_OF_PHOTOS_TO_ADD} photos.')
                time.sleep(timer * 60)
            random_photos = choose_random_photos(pics, config.NUMBER_OF_PHOTOS_TO_ADD)
            copy_photos(random_photos)
            break

    if option == 2:
        print('Ooops! This feature isn\'t available yet.')
        continue
    else:
        print('Input error. You can only type "1" or "2". Try again.')
