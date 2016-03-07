#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename: expectation.py

import json

from .error import RestTestError
from .colortext import ColorText
from ..utils import utils


class Expectation():
    """docstring for Expectation"""

    SUPPORTED_TYPE = \
        ('status_code', 'include_keys', 'include_words', 'value')
    ATTRIBUTES = ('value', 'pos', 'left', 'op', 'right')
    SUPPORTED_OPERATORS = {
        '=': 'eq',
        '!=': 'ne',
        '>': 'gt',
        '>=': 'ge',
        '<': 'lt',
        '<=': 'le',
        'in': 'in'
    }
    count = 0
    successed = 0
    failed = []

    def __init__(self, doc, response, api_name):
        if not isinstance(doc, dict):
            raise RestTestError('FORMAT_ERROR', correct_type='dict')
        if 'type' not in doc.keys():
            raise RestTestError('KEY_NOT_FOUND', key='type', collection=doc)
        if doc['type'] not in self.SUPPORTED_TYPE:
            raise RestTestError('UNSUPPORT_METHOD', method=doc['type'])
        if not response:
            raise RestTestError('NO_RESPONSE')

        self.type = doc['type']
        for attr in self.ATTRIBUTES:
            if attr in doc.keys():
                setattr(self, attr, doc[attr])
            else:
                setattr(self, attr, None)

        self.name = api_name
        self.response = response

    def check_expectation(self):
        method_name = 'check_' + self.type
        mtd = getattr(self, method_name)
        return mtd()

    def check_status_code(self):
        if not self.value:
            raise RestTestError('SOMETHING_MISSING', sth='expect value')

        if str(self.response.status_code) == str(self.value):
            self.print_result('SUCCESS')
        else:
            self.print_result('FAIL')

    def check_include_keys(self):
        if not self.value or not self.pos:
            raise RestTestError('SOMETHING_MISSING',
                                sth='value or pos')

        for key in self.value:
            json_value = utils.get_json_with_path(
                self.response.json(), self.pos)
            if not json_value:
                self.print_result('NOTFOUND', key=key)
            elif isinstance(json_value, dict) and key in json_value.keys():
                self.print_result('SUCCESS', key=key)
            elif isinstance(json_value, list):
                has_key = True
                for item in json_value:
                    if key not in item.keys():
                        has_key = False
                        break
                if has_key:
                    self.print_result('SUCCESS', key=key)
            else:
                self.print_result('FAIL', key=key)

    def check_include_words(self):
        if not self.value or not self.pos:
            raise RestTestError('SOMETHING_MISSING',
                                sth='value or pos')

        for word in self.value:
            json_value = utils.get_json_with_path(
                self.response.json(), self.pos)
            if not json_value:
                self.print_result('NOTFOUND', word=word)
            elif word in json.dumps(json_value, ensure_ascii=False):
                self.print_result('SUCCESS', word=word)
            else:
                self.print_result('FAIL', word=word)

    def check_value(self):
        if self.left is None or self.right is None or not self.op:
            raise RestTestError('SOMETHING_MISSING',
                                sth='left, right or op')
        if self.op not in self.SUPPORTED_OPERATORS.keys():
            raise RestTestError('UNSUPPORT_OPERATOR',
                                operator=self.op)

        oprands = self.deal_operands()
        if not isinstance(oprands, list) or len(oprands) != 2:
            raise RestTestError('OPRANDS_ERROR')

        if oprands[0] is None:
            self.print_result('NOTFOUND', key=self.left)
        elif oprands[1] is None:
            self.print_result('NOTFOUND', key=self.right)
        else:
            if self.campare_operands(oprands):
                self.print_result('SUCCESS')
            else:
                self.print_result('FAIL')

    def print_result(self, result, **params):
        ''' print_result
            this function is to print suitable result for expectation check
            pass 'SUCCESS' OR 'FAIL' as result
            msg only work in 'FAIL' type
            params used to print statement info
        '''
        result_type = ('SUCCESS', 'FAIL', 'NOTFOUND')
        if result not in result_type:
            raise RestTestError('UNSUPPORT_TYPE', type=result,
                                whenclause='print expectation result')

        # print expectation statement
        Expectation.count += 1
        utils.print_log('no. {} expectation being checked'.format(
            ColorText(str(Expectation.count), 'keywords')))
        m_statement = '{} should {}'

        e_type = e_value = None
        if self.type == 'status_code':
            e_type = 'status code'
            e_value = 'be ' + str(self.value)
        if self.type == 'include_keys':
            e_type = 'key ' + params['key']
            e_value = 'in ' + str(self.pos)
        if self.type == 'include_words':
            e_type = 'word ' + params['word']
            e_value = 'in ' + str(self.pos)
        if self.type == 'value':
            e_type = str(self.left)
            e_value = str(self.op) + ' ' + str(self.right)
        m_statement = m_statement.format(
            ColorText(e_type, 'keywords'), ColorText(e_value, 'keywords'))

        # print result
        m_result = m_statement + '   [ {} ]'
        check_result = ''
        if result == 'SUCCESS':
            Expectation.successed += 1
            check_result = ColorText('passed', 'success')
        elif result == 'NOTFOUND':
            error_info = '{} not found in response'.format(str(self.pos))
            if self.type == 'value':
                error_info = '{} not found in response'.format(params['key'])
            fail_info = {
                                        'api': self.name,
                                        'method': self.response.request.method,
                                        'url': self.response.url,
                                        'data': self.response.request.body,
                                        'expectation': error_info,
                                        'code': self.response.status_code,
                                        'response':
                                        json.dumps(self.response.json(),
                                                   ensure_ascii=False,
                                                   sort_keys=True,
                                                   indent=4)
                                 }
            self.failed.append(fail_info)
            check_result = ColorText('failed', 'fail')
        else:
            fail_info = {
                                        'api': self.name,
                                        'method': self.response.request.method,
                                        'url': self.response.url,
                                        'data': self.response.request.body,
                                        'expectation': m_statement,
                                        'code': self.response.status_code,
                                        'response':
                                        json.dumps(self.response.json(),
                                                   ensure_ascii=False,
                                                   sort_keys=True,
                                                   indent=4)
                                 }
            self.failed.append(fail_info)
            check_result = ColorText('failed', 'fail')
        utils.print_log(m_result.format(check_result))

    def deal_operands(self):
        '''get data from response and generate oprands to campare
        '''
        to_deal = (self.left, self.right)
        values = [None, None]
        # deal left and right, result kept in value[0], value[1]
        for i, item in enumerate(to_deal, 0):
            if isinstance(item, str) and str(item).startswith('.'):
                pos = str(item).rfind('.')
                key = str(item)[pos+1:]
                parent = '.'
                if pos > 0:
                    parent = str(item)[:pos]

                # get parent doc
                json_data = utils.get_json_with_path(
                    self.response.json(), parent)
                if not json_data:
                    return None
                # if what we want is a value of key
                if not isinstance(json_data, list):
                    if key in json_data.keys():
                        values[i] = json_data[key]
                    else:
                        values[i] = None
                        # raise RestTestError('KEY_NOT_FOUND',
                        #                     key=key,
                        #                     collection=json_data)
                # if we got a list, get all value in list
                else:
                    v_list = []
                    for data in json_data:
                        if key in data.keys():
                            v_list.append(data[key])
                        else:
                            v_list = None
                            # raise RestTestError('KEY_NOT_FOUND',
                            #                     key=key,
                            #                     collection=data)
                    values[i] = v_list
            # if not a sign to get data from response, just reutrn value
            else:
                values[i] = item

        return values

    def campare_operands(self, oprands):
        if not isinstance(oprands, list) or len(oprands) != 2:
            raise RestTestError('OPRANDS_ERROR')

        # if 'in' comparation
        if self.op == 'in':
            for item in oprands[0]:
                if item not in oprands[1]:
                    return False
            return True

        # if not 'in' comparation
        operator = '__{}__'.format(self.SUPPORTED_OPERATORS[str(self.op)])
        list_ops = []
        sole_ops = []
        for oprand in oprands:
            if isinstance(oprand, list):
                list_ops.append(oprand)
            else:
                sole_ops.append(oprand)

        # if campare in 2 list
        if len(list_ops) == 2 and len(sole_ops) == 0:
            for i, op in enumerate(list_ops[0], 0):
                mtd = getattr(op, operator)
                if not mtd(list_ops[1][i]):
                    return False

        # if campare in 2 operands, no list operand
        if len(sole_ops) == 2 and len(list_ops) == 0:
            mtd = getattr(sole_ops[0], operator)
            return mtd(sole_ops[1])

        # campare with an operand and a list oprand
        if len(sole_ops) == len(list_ops) == 1:
            for list_op in list_ops[0]:
                mtd = getattr(list_op, operator)
                if not mtd(sole_ops[0]):
                    return False

        return True

    @classmethod
    def print_summary(cls, print_response):
        utils.print_separator()
        utils.print_log('[ summary ]')
        utils.print_log('{} expectations checked'.format(
            ColorText(str(cls.count), 'keywords')))
        utils.print_log('{} passed'.format(
            ColorText(str(cls.successed), 'success')))
        utils.print_log('{} failed'.format(
            ColorText(str(len(cls.failed)), 'fail')))

        if cls.failed:
            utils.print_log('')
            utils.print_log('[ fail expectation keywords ]')
            for i, expectation in enumerate(cls.failed, 1):
                if not i == 1:
                    utils.print_log('')
                msg = ColorText(
                    '{}. {}'.format(str(i), expectation['api']), 'keywords')
                utils.print_log(msg)
                utils.print_log('request url: {} {}'.format(
                    expectation['method'], expectation['url']))
                if expectation['data']:
                    expectation['data'] = expectation['data'].split('&')
                    for i, data in enumerate(expectation['data'], 0):
                        if i == 0:
                            utils.print_log('using param: {}'.format(data))
                        else:
                            utils.print_log(' '*6 + '{}'.format(data))
                utils.print_log('status code: {}'.format(expectation['code']))
                utils.print_log('failed on {}'.format(
                   expectation['expectation'], 'fail'))
                if print_response:
                    utils.print_log(
                        'response: {}'.format(expectation['response']))
