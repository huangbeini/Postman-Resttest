#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: colortext.py

from .error import RestTestError


class ColorText():
    """docstring for ColorText"""

    COLORS = {
        'BLACK':          '\033[0;30m',
        'DARK_GRAY':      '\033[1;30m',
        'LIGHT_GRAY':     '\033[0;37m',
        'BLUE':           '\033[0;34m',
        'LIGHT_BLUE':     '\033[1;34m',
        'GREEN':          '\033[0;32m',
        'LIGHT_GREEN':    '\033[1;32m',
        'CYAN':           '\033[0;36m',
        'LIGHT_CYAN':     '\033[1;36m',
        'RED':            '\033[0;31m',
        'LIGHT_RED':      '\033[1;31m',
        'PURPLE':         '\033[0;35m',
        'LIGHT_PURPLE':   '\033[1;35m',
        'BROWN':          '\033[0;33m',
        'YELLOW':         '\033[1;33m',
        'WHITE':          '\033[1;37m',
        'DEFAULT_COLOR':  '\033[00m',
        'RED_BOLD':       '\033[01;31m',
        'ENDC':           '\033[0m',
    }

    DARK_TYPES = {
        'info':                     'LIGHT_GRAY',
        'keywords':         'GREEN',
        'success':              'CYAN',
        'fail':                         'RED',
        'warning':              'BROWN',
        'seperator':            'BLUE'
    }

    # def __init__(self, text, color):
    #     if not isinstance(color, str):
    #         raise RestTestError('FORMAT_ERROR', correct_type='string')
    #     if str(color).upper() not in self.COLORS.keys():
    #         raise RestTestError('UNSUPPORT_COLOR', color=color)

    #     self.text = str(text)
    #     self.color = str(color).upper()

    def __init__(self, text, message_type, template='dark'):
        if not isinstance(template, str):
            raise RestTestError('FORMAT_ERROR', correct_type='string')
        template_name = '{}_TYPES'.format(str(template).upper())

        if template_name not in dir(self):
            raise RestTestError('TEMPLATE_NOT_FOUND', template=template)
        else:
            self.template = getattr(self, template_name)

        message_type = str(message_type).lower()
        if not isinstance(message_type, str):
            raise RestTestError('FORMAT_ERROR', correct_type='string')
        if message_type not in self.template.keys():
            raise RestTestError('UNSUPPORT_TYPE', type=message_type)

        self.text = str(text)
        self.color = self.template[message_type]

    def __str__(self):
        if self.COLORS['ENDC'] in self.text:
            self.text = self.text.replace(
                self.COLORS['ENDC'], self.COLORS[self.color])
        return self.COLORS[self.color] + self.text + self.COLORS['ENDC']
