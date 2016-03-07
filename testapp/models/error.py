#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: error.py


class RestTestError(Exception):
    """docstring for RestError
          this class defines Errors on resttest
    """

    # General
    FORMAT_ERROR = (100000,
                    'illegal format, you should pass a {correct_type}')
    KEY_NOT_FOUND = (100001,
                     'key {key} not found in {collection}')
    ILLEGAL_DATA = (100002,
                    'illegal data for {param}:  {value}')
    ILLEGAL_JSON_FILE = (100003,
                         'illegal json file, skipped')
    FILE_NOT_FOUND = (100004,
                      'file not found: {path}')
    DIR_NOT_FOUND = (100005,
                     'directory not found: {dir}')
    SOMETHING_MISSING = (100006,
                         '{sth} not found')
    UNSUPPORT_TYPE = (100007,
                      '{type} is not supported when {whenclause}')
    UNSUPPORT_OPERATOR = (100008,
                          '{operator} is not supported now')

    # HTTP Requests
    UNSUPPORT_METHOD = (200001,
                        'unsupport http method found: {method}')
    NO_RESPONSE = (200002,
                   'no response info, send request first')

    # CONTEXT
    NO_VALUE = (300001,
                'not found value of {param} when update context')

    # OTHER
    UNSUPPORT_COLOR = (900001,
                       'color {color} is not supported')
    OPRANDS_ERROR = (900002,
                     'wrong oprands, pass a list include 2 oprands to compare')
    TEMPLATE_NOT_FOUND = (900003,
                          'template {template} is not supported now')
    UNSUPPORT_TYPE = (900004,
                      'type {type} is not supported')

    def __init__(self, name, **kargs):
        if name not in dir(self):
            raise RuntimeError('Undefined Error: {0}'.format(name))

        self.error = getattr(self, name)
        self.code = self.error[0]
        if kargs:
            self.message = str.format(self.error[1], **kargs)
        else:
            self.message = self.error[1]

    def __str__(self):
        return repr(self.message)
