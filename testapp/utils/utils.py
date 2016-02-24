#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow

from ..models.error import RestTestError
from ..models.colortext import ColorText


def print_log(log_words):
    prefix = '[ {0} ]'.format(arrow.now('Asia/Shanghai')
                                   .format('YYYY-MM-DD HH:mm:ss:SSS'))
    print(ColorText('{0} {1}'.format(prefix, log_words), 'info'))


def print_separator():
    print_log('')
    print_log(ColorText('.' * 30, 'seperator'))
    print_log('')


def get_json_with_path(json_pos, path):
    if not str(path).startswith('.'):
        raise RestTestError('FORMAT_ERROR',
                            correct_type='string start with "."')

    if path == '.':
        return json_pos

    elements = path[1:].split('.')
    try:
        for element in elements:
            json_pos = json_pos[element]
    except:
        return None
        # raise RestTestError('KEY_NOT_FOUND',
        #                     key=element,
        #                     collection=json_pos)
    return json_pos
