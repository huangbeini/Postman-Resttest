#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: testfile.py

import json
import os

import arrow

from .error import RestTestError
from .colortext import ColorText
from .testrequest import TestRequest
from ..utils import utils


class TestFile():
    """docstring for TestFile"""

    REQUEST_KEYS = ('id', 'name', 'description', 'order', 'requests',)

    def __init__(self, filename):
            # search files
            if os.path.exists(filename) and os.path.isfile(filename):
                with open(filename, encoding='utf-8') as f:
                    try:
                        t_json = json.loads(f.read())
                        for key in self.REQUEST_KEYS:
                            if key not in t_json.keys():
                                raise RestTestError('KEY_NOT_FOUND',
                                                    key=key,
                                                    collection=t_json)
                        self.filename = filename
                        self.id = t_json['id']
                        self.name = t_json['name']
                        self.description = t_json['description']
                        if not self.description:
                            self.description = '-'
                        self.order = t_json['order']
                        self.requests = t_json['requests']
                        self.context = None
                        if 'context' in t_json.keys():
                            self.context = t_json['context']
                    except json.decoder.JSONDecodeError:
                        raise RestTestError('ILLEGAL_JSON_FILE')
            else:
                raise RestTestError('FILE_NOT_FOUND', path=filename)

    def print_file_info(self):
        utils.print_log('description: {0}'.format(
            ColorText(self.description, 'keywords')))
        utils.print_log('starting test')

    def update_context(self, request_id, response):
        if self.context:
            for c in self.context:
                for req in c['request']:
                    if req['id'] == request_id:
                        try:
                            c['value'] = utils.get_json_with_path(
                                response.json(), req['path'])
                            c['timestamp'] = arrow.now('Asia/Shanghai')
                        except:
                            utils.print_log(
                                'try to get context value {} failed'
                                ''.format(c['name']))

    def test_requests(self):
        for t_id in self.order:
            for request in self.requests:
                if t_id == request['id']:
                    tr = TestRequest(request, self.context)
                    # print general info and request info
                    tr.test()

                    # if tr's output is a context's value, update it
                    if tr.response:
                        self.update_context(t_id, tr.response)
