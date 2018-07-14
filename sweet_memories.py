#!python3.7
# -*- coding: utf-8 -*-

import os
import shutil
import random
import time
import config  # Config need to store path to folders to work to

print('Hi there!')

all_copied_files = []  # Keep track of copied photos in order to delete them in order they were copied
total_photo_size = 0  # Keep track of size of photos that were copied in order to remove some when there are to much
# of them


# Delete first photos that were copied to clean up a bit
def delete_photos():
    print('Start cleaning folder...')
    global total_photo_size
    global all_copied_files

    for index, photo in enumerate(all_copied_files):
        total_photo_size -= os.path.getsize(photo)
        print(f'Removing {photo}...')

        # remove no more pictures than it is set in config file
        if index > config.NUMBER_OF_PHOTOS_TO_DELETE - 1:
            break
        os.remove(photo)

    print('before')
    all_copied_files[:config.NUMBER_OF_PHOTOS_TO_DELETE] = []  # delete first N values
    print('after')
    print(f'Done cleaning screensaver folder. There are {(total_photo_size / 1024**2):.0f} MB of photos ready to show.')
    return


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


# Choose several photos in random order
def choose_random_photos(pictures, number):
    random_pics = random.sample(pictures, number)
    # for pic in random_pics:
    #     print(pic)
    print(f'{number} random photos have been chosen.')
    return random_pics


# Copy chosen photo to a given folder (folder where Windows is set to get pictures for a slideshow)
def copy_photos(photos):
    print('Adding new photos...')
    global total_photo_size
    for photo in photos:
        new_path = os.path.join(config.SCREENSAVER_FOLDER, os.path.basename(photo))
        if not os.path.exists(new_path):
            print(f'Copying {os.path.basename(photo)}...')
            shutil.copy2(photo, new_path)
            all_copied_files.append(new_path)
            total_photo_size += os.path.getsize(photo)
        else:
            print(f'{os.path.basename(photo)} already exists.')

    print(f'Done! There are {(total_photo_size / 1024**2):.0f} MB of photos ready to show.')


# This chunk of code let user to choose mode of how script will work
# Also it is responsible for adding photos after given amount of time
while True:
    print('Choose one option below:\n1. Copy 5 random photos.\n2. Copy photos that were taken in this day in the past')
    option = int(input('Please type "1" or "2": '))
    if option == 1:
        pics = get_list_of_photos(config.PHOTO_ARCHIVE)

        if os.path.exists(config.SCREENSAVER_FOLDER):
            shutil.rmtree(config.SCREENSAVER_FOLDER)
        for i in range(5):
            try:
                os.mkdir(config.SCREENSAVER_FOLDER)
                break
            except PermissionError:
                time.sleep(1)
                continue
        else:
            print('Can\'t create folder for photos')

        random_photos = choose_random_photos(pics, config.INITIAL_NUMBER_OF_PHOTOS)
        copy_photos(random_photos)

        while True:
            time.sleep(60)
            if total_photo_size > config.MAX_TOTAL_SIZE:
                delete_photos()
            random_photos = choose_random_photos(pics, config.NUMBER_OF_PHOTOS_TO_ADD)
            copy_photos(random_photos)

    if option == 2:
        print('Ooops! This feature isn\'t available yet.')
        continue
    else:
        print('Input error. You can only type "1" or "2". Try again.')
