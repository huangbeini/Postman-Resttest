#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: testrequest.py

import requests

from .error import RestTestError
from .colortext import ColorText
from .expectation import Expectation
from ..utils import utils


class TestRequest():
    """docstring for TestRequest
          this class is for build a request using url, method, etc
          and then return a response
    """
    REQUEST_KEYS = ('id', 'name', 'description', 'method', 'url', 'data')
    SUPPORTED_HTTP_METHODS = ('get', 'post', 'put', 'delete')

    def __init__(self, doc, context):
        ''' init method
            passing a json to form an objective
        '''
        if not isinstance(doc, dict):
            raise RestTestError('FORMAT_ERROR', correct_type='dict')

        for key in self.REQUEST_KEYS:
            if key not in doc.keys():
                raise RestTestError('KEY_NOT_FOUND',
                                    key=key,
                                    collection='request')

        self.id = doc['id']
        self.name = doc['name']
        self.description = doc['description']
        self.method = str(doc['method']).lower()
        self.context = context
        self.url = self.generate_url(doc['url'])
        self.data = {}
        for item in doc['data']:
            if item['enabled']:
                self.data[item['key']] = \
                    self.replace_context_value(item['value'])
        self.response = None
        self.expectations = None
        if 'expectations' in doc.keys():
            self.expectations = doc['expectations']

    def test(self):
        try:
            self.send_request()
        except:
            utils.print_separator()
            fail_msg = 'request failed on {}, please check your request'
            utils.print_log(
                ColorText(fail_msg.format(self.name),  'warning'))

        if self.response:
            self.print_info()
            self.check_expectations()

    def send_request(self):
        if self.method not in self.SUPPORTED_HTTP_METHODS:
            raise RestTestError('UNSUPPORT_METHOD', self.method)
        mtd = getattr(requests, self.method)
        if self.data:
            self.response = mtd(self.url, self.data)
        else:
            self.response = mtd(self.url)

    def check_expectations(self):
        if not self.response:
            raise RestTestError('NO_RESPONSE')
        if not self.expectations:
            utils.print_log(
                ColorText('no expectation found, passed', 'warning'))
            return

        for expectation in self.expectations:
            ep = Expectation(expectation, self.response, self.name)
            ep.check_expectation()

    def print_info(self):
        utils.print_separator()
        if not self.response:
            raise RestTestError('NO_RESPONSE')
        utils.print_log('##### case:   {}'.format(
            ColorText(self.name, 'keywords')))
        utils.print_log(
            '####### id:   {}'.format(ColorText(self.id, 'keywords')))
        utils.print_log('### remark:   {}'.format(
            ColorText(self.description, 'keywords')))
        r_string = '{} {}'.format(self.method.upper(), self.response.url)
        utils.print_log('## request:   {}'.format(
            ColorText(r_string, 'keywords')))
        if self.data:
            for i, key in enumerate(self.data.keys(), 0):
                if i == 0:
                    utils.print_log('##### data:   {}'.format(
                        ColorText((key + ' = ' + self.data[key]), 'keywords')))
                else:
                    utils.print_log(' '*14 + '{}'.format(
                        ColorText((key + ' = ' + self.data[key]), 'keywords')))
        utils.print_log('# response:   {}'.format(
            ColorText(self.response.status_code, 'keywords')))
        utils.print_log('')

    def generate_url(self, origin_url):
        if not str(origin_url).startswith('http'):
            origin_url = 'http://' + str(origin_url)
        return self.replace_context_value(origin_url)

    def replace_context_value(self, string):
        string = str(string)
        if not ('{' in string and '}' in string):
            return string
        else:
            while '{' in string and '}' in string:
                # 获取context变量名
                pos1 = string.find('{')
                pos2 = string.find('}')
                param = string[pos1+1:pos2]

                # 使用context变量值替换
                if self.context:
                    for c in self.context:
                        if c['name'] == param:
                            if 'value' in c.keys() and c['value']:
                                string = string.replace(
                                    '{' + param + '}', c['value'])
                            elif c['default']:
                                string = string.replace(
                                    '{' + param + '}', c['default'])
                            else:
                                # if can not find a value, give blank
                                string = string.replace(
                                    '{' + param + '}', '')
                else:
                    break
            return string
