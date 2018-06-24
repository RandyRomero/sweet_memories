#!python3
# -*- coding: utf-8 -*-

import os
import shelve
import random

print('Hi there!')


def get_list_of_photos(archive_path):
    list_of_pictures = []
    for root, subfolders, files in os.walk(archive_path):
        print(f'Checking {root}')
        for file in files:
            print(f'Checking {file}')
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                list_of_pictures.append(file)

    print(f'There are {len(list_of_pictures)} pictures.')
    return list_of_pictures


def choose_random_pictures(pictures):
    random_pics = random.sample(pictures, 5)
    for pic in random_pics:
        print(pic)
    return random_pics


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
        photos = get_list_of_photos(path_to_archive)
        random_photos = choose_random_pictures(photos)
        break
    if option == 2:
        print('Ooops! This feature isn\'t available yet.')
        continue
    else:
        print('Input error. You can only type "1" or "2". Try again.')