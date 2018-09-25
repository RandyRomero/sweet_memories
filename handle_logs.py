# -*- coding: utf-8 -*-

import logging


def set_logger():
    new_logger = logging.getLogger(__name__)
    new_logger.setLevel(logging.DEBUG)

    # create console_handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s line %(lineno)d: %(message)s...',
                                  datefmt='%H:%M:%S')
    ch.setFormatter(formatter)

    new_logger.addHandler(ch)

    return new_logger


logger = set_logger()

