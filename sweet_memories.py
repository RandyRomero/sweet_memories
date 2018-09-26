#!python3
# -*- coding: utf-8 -*-

import os
import shutil
import random
import time
import config  # Config need to store path to folders to work to
import exifread
import shelve
import re
from handle_logs import logger
import datetime as dt

print('Hi there!')


all_copied_files = []  # Keep track of copied photos in order to delete them in order they were copied
total_photo_size = 0  # Keep track of size of photos that were copied in order to remove some when there are to much
# of them


# Read EXIF from file to find date when photo was taken
def get_date_from_exif(root, file):
    with open(os.path.join(root, file), 'rb') as f:
        exif_info = exifread.process_file(f, details=False)
        return (str(exif_info.get('EXIF DateTimeOriginal', '')) or str(exif_info.get('EXIF DateTimeDigitized', '')) or
                str(exif_info.get('Image DateTime', '')) or 'no data')


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


def make_snaphot_with_dates(archive_path):
    list_of_pictures = []
    files_without_date_in_name = 0
    for root, subfolders, files in os.walk(archive_path):
        print(f'Checking {root}')
        # Get regex with any year and today's date like \d{4}-07-16

        regex = re.compile(r'\d{4}-\d{2}-\d{2}')
        for file in files:
            if not file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                continue

            # Use regex to look for photos with specific date: first check if there is date in filename,
            # if not check the date in EXIF data within photo
            date_from_filename = re.match(regex, file)
            if date_from_filename:
                list_of_pictures.append([os.path.join(root, file), date_from_filename[0]])

            else:
                print(f'Checking {file}...')
                date_from_exif = get_date_from_exif(root, file)
                if date_from_exif == 'no data':
                    print('There is no exif in', os.path.join(root, file))
                    continue

                date_from_exif = date_from_exif.replace(':', '-')
                list_of_pictures.append([os.path.join(root, file), date_from_exif])
            continue

    print(f'There are {len(list_of_pictures)} pictures.')
    print(f'There are {files_without_date_in_name} pictures were found by examining of EXIF.')

    if not os.path.exists('snapshots'):
        os.mkdir('snapshots')

    name = input('Please enter a name for a snapshot: ')
    name = name if name else dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%d %H-%M-%S')
    logger.info(f'name: {name}')
    db = shelve.open('snapshots/sweet_dreams_db')

    db[name] = list_of_pictures
    db.close()
    print(f'Snapshot "{name}" has been saved.')

    return list_of_pictures


# Copy chosen photo to a given folder (folder where Windows is set to get pictures for a slideshow)
def copy_photos(photos):
    if isinstance(photos, str):
        photos = [photos]
    print('Adding new photos...')
    global total_photo_size
    for photo in photos:
        new_path = os.path.join(config.SCREENSAVER_FOLDER, os.path.basename(photo))
        if not os.path.exists(new_path):
            print(f'Copying {os.path.basename(photo)}...')
            try:
                shutil.copy2(photo, new_path)
                all_copied_files.append(new_path)
                total_photo_size += os.path.getsize(photo)
            except FileNotFoundError:
                logger.warning(f"Can't find {photo}.")
        else:
            print(f'{os.path.basename(photo)} already exists.')

    print(f'Done! There are {(total_photo_size / 1024**2):.0f} MB of photos ready to show.')


def select_photos_of_the_day(list_of_photos):
    today = dt.datetime.strftime(dt.datetime.now(), '%m-%d')
    regex = re.compile(r'\d{4}-' + today)
    return [x[0] for x in list_of_photos if re.match(regex, x[1])]


def ask_path():
    while True:
        path = input('Please type path to your photos: ')
        if os.path.isdir(path):
            print('Got it')
            return path
        else:
            print('Path is invalid. Try again.')
            continue


def get_photo_of_the_day():
    while True:
        cmd = input('Please, press L if you want to [l]oad a snapshot or P if you want to choose a [p]ath to '
                    'your folder with photos: ').lower()
        if cmd == 'l':
            try:
                db = shelve.open('snapshots/sweet_dreams_db')
                print('Open database - ok')
            except FileNotFoundError:
                print('There are no snapshots yet.')
                continue
            print('There are these snapshots. Please, choose one and type its number:')
            keys = list(db.keys())
            if not keys:
                print('There are no snapshots yet.')
                continue
            roach = dict(zip(range(1, len(keys) + 1), keys))
            for i, k in roach.items():
                print(f'{i}. {k}')
            while True:
                choice = int(input('Your choice (one number): '))
                if choice in roach.keys():
                    snapshot = db[roach[choice]]
                    return select_photos_of_the_day(snapshot)

        if cmd == 'p':
            # list_of_photos_with_dates = make_snaphot_with_dates(ask_path())
            return select_photos_of_the_day(make_snaphot_with_dates(ask_path()))


# Look through the whole archives with photos and create a list of all existing files with jpg extension
def get_list_of_photos(archive_path):
    size_to_copy = 0
    list_of_pictures = []
    for root, subfolders, files in os.walk(archive_path):
        print(f'Checking {root}')
        for file in files:
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                list_of_pictures.append(os.path.join(root, file))

    print(f'There are {len(list_of_pictures)} pictures in total.')

    photos = []
    while size_to_copy < config.MAX_TOTAL_SIZE:
        random_pic = random.choice(list_of_pictures)
        size_to_copy += os.path.getsize(random_pic)
        photos.append(random_pic)
    return photos


def create_folder():
    if os.path.exists(config.SCREENSAVER_FOLDER):
        shutil.rmtree(config.SCREENSAVER_FOLDER)
    for attempt in range(5):
        try:
            os.mkdir(config.SCREENSAVER_FOLDER)
            return True
        except PermissionError:
            time.sleep(1)
            continue
    else:
        print('Can\'t create folder for photos')
        return False


# This chunk of code let user to choose mode of how script will work
# Also it is responsible for adding photos after given amount of time
while True:
    print('Choose one option below:\n'
          f'1. Copy {config.INITIAL_NUMBER_OF_PHOTOS} random photos.\n'
          '2. Copy photos that were taken in this day in the past.\n')

    option = int(input('Please type "1" or "2": '))

    if option == 1:
        if not create_folder():
            exit()

        # for pic in get_list_of_photos(ask_path()):
        #     print(pic)
        copy_photos(get_list_of_photos(ask_path()))
        exit()

    elif option == 2:
        pics = get_photo_of_the_day()

        # Close script if it can't create a folder 5 times straight
        if not create_folder():
            exit()

        # If there less than, for example, 100 photos, copy them and stop the script
        if len(pics) < config.INITIAL_NUMBER_OF_PHOTOS:
            copy_photos(pics)
            print('All photos from this day in the past were copied. Bye!')
            exit()

        print(f'Now copy {len(pics[:config.INITIAL_NUMBER_OF_PHOTOS])} photos.')
        copy_photos(pics[:config.INITIAL_NUMBER_OF_PHOTOS])
        while True:
            pics[:config.INITIAL_NUMBER_OF_PHOTOS] = []
            time.sleep(60)
            if not pics:
                exit()
            if total_photo_size > config.MAX_TOTAL_SIZE:
                delete_photos()
            if len(pics) >= 100:
                print(f'Now copy other {len(pics[:config.INITIAL_NUMBER_OF_PHOTOS])} photos. '
                      f'{len(pics) - config.NUMBER_OF_PHOTOS_TO_ADD} left.')
            elif len(pics) < 100:
                print(f'Now copy last {len(pics)} photos')
            copy_photos(pics[:config.INITIAL_NUMBER_OF_PHOTOS])

    else:
        print('Input error. You can only type "1", "2" or "3". Try again.')


# TODO ClI interface to delete snapshots