#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: resttest.py

import argparse
from configparser import ConfigParser
import os
import traceback

from testapp.utils import utils
from testapp.models.error import RestTestError
from testapp.models.testfile import TestFile
from testapp.models.expectation import Expectation
from testapp.models.colortext import ColorText

TEST_DIR = os.path.abspath(os.path.dirname(__file__)) \
        + '/testfiles'
CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) \
        + '/settings.conf'


def read_config():
    # default settings
    config = {}
    config['debug_mode'] = False

    # read config settings from config file
    try:
        cp = ConfigParser()
        print(CONFIG_FILE)
        cp.read(CONFIG_FILE)
        if cp.has_section('GENERAL'):
            config['debug_mode'] = \
                'true' == cp.get('GENERAL', 'Debug_mode').lower()
    except TypeError:
        msg = ColorText('get config failed, using default settings', 'warning')
        utils.print_log(msg)

    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug',
                        help='debug mode turned on', action='store_true')
    args = parser.parse_args()

    try:
        if not os.path.isdir(TEST_DIR):
            raise RestTestError('DIR_NOT_FOUND', dir=TEST_DIR)

        utils.print_log('resttest now begin work!')
        config = read_config()
        if args.debug:
            config['debug_mode'] = True
        utils.print_log('scaning folder {}'.format(
                TEST_DIR))

        for tfile in os.listdir(TEST_DIR):
            if tfile[0] != '.' and tfile[-1] != '~':
                utils.print_separator()
                msg = ColorText('trying to read file {}'.format(
                    tfile), 'keywords')
                utils.print_log(msg)
                filename = '{0}/{1}'.format(TEST_DIR, tfile)
                try:
                    tf = TestFile(filename)
                    tf.print_file_info()
                    tf.test_requests()
                except RestTestError as e:
                    if e.code == 100003:
                        msg = ColorText(e.message, 'warning')
                        utils.print_log(e.message)
                    else:
                        raise e
                except Exception as e:
                    raise e

        Expectation.print_summary(config['debug_mode'])
    except RestTestError as e:
        traceback.print_exc()
        utils.print_log(e.message)
    except:
        traceback.print_exc()
