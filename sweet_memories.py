#!python3
# -*- coding: utf-8 -*-

import os
import shutil
import random
import time
import config
import exifread
import shelve
import re
from handle_logs import logger
import datetime as dt


def get_date_from_exif(root, photo):
    """
    Read EXIF from photo to find date when it was taken

    :param root: root folder of the photo which exif we want to get
    :param photo: filename of photo which exif we want to get
    :return: string with date in format 2017-09-27 02-53-54 or 'no data' string
    """
    with open(os.path.join(root, photo), 'rb') as f:
        exif_info = exifread.process_file(f, details=False)
        return (str(exif_info.get('EXIF DateTimeOriginal', '')) or str(exif_info.get('EXIF DateTimeDigitized', '')) or
                str(exif_info.get('Image DateTime', '')) or 'no data')


def make_snapshot_with_dates(archive_path):
    """
    Function to scan chosen directory (with subdirectories), find any photo, save directory tree (where are only
    photos and folders) with dates where each photo was taken in a db, return this list of photos with dates

    :param archive_path: path to directory to scan
    :return: list where every item is another list where 1st item is full path to photo, 2nd - date where this photo
    was taken
    """
    i = 0
    list_of_pictures = []
    files_without_date_in_name = 0
    for root, subfolders, files in os.walk(archive_path):
        print(f'Checking {root}')

        # Make regex to look for photos with date like 2018-02-27
        regex = re.compile(r'\d{4}-\d{2}-\d{2}')
        for file in files:
            i = i + 1
            if not file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                continue
            date_from_filename = re.search(regex, file)
            if date_from_filename:
                list_of_pictures.append([os.path.join(root, file), date_from_filename[0]])
            else:
                print(f'{i+1}. Checking {file}...')
                date_from_exif = get_date_from_exif(root, file)
                if date_from_exif == 'no data':
                    print('There is no exif in', os.path.join(root, file))
                    continue

                files_without_date_in_name += 1
                date_from_exif = date_from_exif.replace(':', '-')
                list_of_pictures.append([os.path.join(root, file), date_from_exif])
            continue

    print(f'There are {len(list_of_pictures)} pictures.')
    print(f'There are {files_without_date_in_name} pictures were found by examining of EXIF.')

    # Make snapshot in order not to scan disk every time
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


def copy_photos(photos):
    """
    Copy given photos to a given folder (e.g. folder where Windows is set to get pictures for a slideshow)

    :param photos: list of photos with dates
    :return: None
    """
    total_photo_size = 0
    print('Adding new photos...')
    for i, photo in enumerate(photos):
        photo = photo[0]
        if total_photo_size > config.MAX_TOTAL_SIZE:
            print(f'There are already {(total_photo_size / 1024**2):.0f} MB of photos, stop copying new ones.')
            print('Bye!')
            exit()
        new_path = os.path.join(config.SCREENSAVER_FOLDER, os.path.basename(photo))
        if not os.path.exists(new_path):
            print(f'{i+1}. Copying {os.path.basename(photo)}...')
            try:
                shutil.copy2(photo, new_path)
                total_photo_size += os.path.getsize(photo)
            except FileNotFoundError:
                logger.warning(f"Can't find {photo}.")
        else:
            print(f'{os.path.basename(photo)} already exists.')

    print(f'Done! There are {(total_photo_size / 1024**2):.0f} MB of photos ready to show.')


def select_photos_of_the_day(list_of_photos):
    """
    Make list of photos that were taken in that day in previous years
    :param list_of_photos: list of photos with dates [[path to photo, date when photo was taken], [...], ...]
    :return: list of photos that were taken in that day in previous years
    """
    today = dt.datetime.strftime(dt.datetime.now(), '%m-%d')
    regex = re.compile(r'\d{4}-' + today)
    # return [x[0] for x in list_of_photos if re.match(regex, x[1])]
    return [x for x in list_of_photos if re.match(regex, x[1])]


def ask_path():
    """
    Ask user path to anything and validate it
    :return: existing path to folder
    """
    while True:
        path = input('Please type path to your photos: ')
        if os.path.isdir(path):
            print('Got it')
            return path
        else:
            print('Path is invalid. Try again.')
            continue


def manage_snapshots(cmd):
    """
     Function to make an ordered list of keys of database and let user to choose one key by its number

    :param cmd: it's string with either 'get' list of photos or 'del' snapshot from a db
    :return: tuple where first arg is boolean depending of was operation successful or not, second arg is either
    error message or list with photos from db
    """

    try:
        db = shelve.open('snapshots/sweet_dreams_db')
        print('Open database - ok')
    except FileNotFoundError:
        return False, 'There is no database.'
    keys = list(db.keys())
    if not keys:
        db.close()
        return False, 'There are no snapshots yet.\n'
    print('There are these snapshots. Please, choose one and type its number:')
    roach = dict(zip(range(1, len(keys) + 1), keys))
    for i, k in roach.items():
        print(f'{i}. {k}')
    while True:
        choice = int(input('Your choice (one number): '))
        if choice in roach.keys():
            if cmd == 'del':
                key = roach[choice]
                del db[roach[choice]]
                db.close()
                return True, f'{key} was successfully removed'
            if cmd == 'get':
                return True, db[roach[choice]]
            else:
                return False, 'Unknown command'


def get_list_of_photos(mode):
    """
    Ask user whether he wants to scan disk for photos or use one of previous scans stored in database
    :param mode: one of two modes - choose random photos or photos from this day in the past
    :return: list of paths to photos
    """
    while True:
        cmd = input('Please, press L if you want to [l]oad a snapshot or P if you want to choose a [p]ath to '
                    'your folder with photos: ').lower()
        if cmd == 'l':
            # Get paths to photos from database
            response = manage_snapshots('get')
            if response[0]:
                if mode == 'all':
                    # From all paths to photos choose given number of them randomly
                    return random.choices([x for x in response[1]], k=config.NUMBER_OF_PHOTOS)
                elif mode == 'of the day':
                    # From all paths to photos choose that were taken in this day in the past
                    return select_photos_of_the_day(response[1])
            else:
                print(response[1])  # print error message

        if cmd == 'p':
            if mode == 'all':
                # scan given directory then return list of paths to photos chosen randomly
                return random.choices(make_snapshot_with_dates(ask_path()), k=config.NUMBER_OF_PHOTOS)
            elif mode == 'of the day':
                # scan given directory then return list of paths to photos that were taken in this day in the past
                return select_photos_of_the_day(make_snapshot_with_dates(ask_path()))


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


def main():

    print('Hi there!')

    while True:
        print('Choose one option below:\n'
              f'1. Copy {config.NUMBER_OF_PHOTOS} random photos.\n'
              '2. Copy photos that were taken in this day in the past.\n'
              '3. Delete a snapshot.\n'
              '4. Quit.')

        option = int(input('Please type "1", "2", "3" or "4": '))

        if option == 1:
            # Create folder to copy snapshots to
            if not create_folder():
                continue

            copy_photos(get_list_of_photos('all'))
            continue

        elif option == 2:
            pics = get_list_of_photos('of the day')

            # Close script if it can't create a folder 5 times straight
            if not create_folder():
                continue

            # If there less than, for example, 100 photos, copy them and stop the script
            if len(pics) < config.NUMBER_OF_PHOTOS:
                copy_photos(pics)
                print('All photos from this day in the past were copied. Bye!')
                continue

            copy_photos(random.choices(pics, k=config.NUMBER_OF_PHOTOS))

        elif option == 3:
            response = manage_snapshots('del')
            if not response[0]:
                print(response[1])
            continue

        elif option == 4:
            print('Tschuss!')
            exit()
        else:
            print('Input error. You can only type "1", "2" or "3". Try again.')


if __name__ == '__main__':
    main()
