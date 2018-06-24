#!python3
# -*- coding: utf-8 -*-

import os
import shutil
import random
import sys

print('Hi there!')


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


def choose_random_photos(pictures):
    random_pics = random.sample(pictures, 5)
    for pic in random_pics:
        print(pic)
    return random_pics


def copy_photos(photos):
    if os.path.exists('your_photos'):
        shutil.rmtree('your_photos')
    os.mkdir('your_photos')
    for photo in photos:
        new_path = os.path.join('your_photos', os.path.basename(photo))
        if not os.path.exists(new_path):
            print(f'Copying {os.path.basename(photo)}...')
            shutil.copy2(photo, new_path)
        else:
            print(f'{os.path.basename(photo)} already exists.')
    print('Done!')


def choose_and_copy(photos):
    random_photos = choose_random_photos(photos)
    copy_photos(random_photos)
    repeat = input('Do you want other 5 pics from this folder? y/n: ')
    if repeat == 'y':
        choose_and_copy(photos)
    if repeat == 'n':
        print('Goobye!')
        sys.exit()
    else:
        print('Wrong input! Try again.')
        choose_and_copy(photos)


while True:
    path_to_archive = input('Please, type in path to you photo archive:\n')
    if not os.path.exists(path_to_archive):
        print('This path doesn\'t exist. Try another one.')
        continue
    if not os.path.isdir(path_to_archive):
        print('Path has to be to directory, not to a specific file. Try again.')
        continue
    print('Path is correct!')
    break

while True:
    print('Choose one option below:\n1. Copy 5 random photos.\n2. Copy photos that were taken in this day in the past')
    option = int(input('Please type "1" or "2": '))
    if option == 1:
        pics = get_list_of_photos(path_to_archive)
        choose_and_copy(pics)

    if option == 2:
        print('Ooops! This feature isn\'t available yet.')
        continue
    else:
        print('Input error. You can only type "1" or "2". Try again.')
