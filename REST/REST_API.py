
#!-*-coding:utf-8 -*-
#@TIME    : 2018/6/25/0025 12:33
#@Author  : Nogo

import requests
import hmac
import hashlib
import json

class REST_API(object):

    def __init__(self, base_url='https://api.coinpark.cc/v1/'):
        self.base_url = base_url
        self.key = ''
        self.secret = ''
        pass

    def auth(self, key, secret):
        self.key = key
        self.secret = secret

    def get_sign(self, data, secret):
        result = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.md5).hexdigest()
        return result

    def public_request(self, method, api_url, **payload):
        try:
            r_url = self.base_url + api_url
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def signed_request(self, method, api_url, cmds):
        try:
            r_url = self.base_url + api_url
            s_cmds = json.dumps(cmds)
            sign = self.get_sign(s_cmds, self.secret)
            data = {'cmds': s_cmds, 'apikey': self.key, 'sign': sign}
            r = requests.request(method, r_url, json=data)
            r.raise_for_status()
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, {'error': 'E10000', 'data': r.status_code}
        except Exception as err:
            return False, {'error': 'E10002', 'data': err}

    def get_symbols(self):
        """获取交易对"""
        return self.public_request('GET', 'mdata', cmd='pairList')

    def get_kline(self, symbol, period, size=1000):
        """
        获取K线
        :param symbol:交易对 如BIX_BTC
        :param period:['1min', '3min', '5min', '15min', '30min', '1hour', '2hour', '4hour', '6hour', '12hour', 'day', 'week']
        :param size: 要几条，1-1000，不传返回1000
        交易对 如BIX_BTC
        """
        return self.public_request('GET', 'mdata', cmd='kline', pair=symbol, period=period, size=size)

    def get_allmakret(self):
        """获取全币种行情"""
        return self.public_request('GET', 'mdata', cmd='marketAll')

    def get_market(self, symbol):
        """
        获取指定交易对行情
        :param symbol: 交易对 如BIX_BTC
        :return:
        """
        return self.public_request('GET', 'mdata', cmd='market', pair=symbol)

    def get_depth(self, symbol, size=200):
        """
        获取指定交易对深度
        :param symbol: 交易对 如BIX_BTC
        :param size: //要几条，1-200，不传返回200
        :return:
        """
        return self.public_request('GET', 'mdata', cmd='depth', pair=symbol, size=size)

    def get_deals(self, symbol, size=200):
        """
        获取指定交易对成交记录
        :param symbol:交易对 如BIX_BTC
        :param size: //要几条，1-200，不传返回200
        :return:
        """
        return self.public_request('GET', 'mdata', cmd='deals', pair=symbol, size=size)

    def get_ticker(self, symbol):
        """
        查询市场ticker
        :param symbol: 交易对 如BIX_BTC
        :return:
        """
        return self.public_request('GET', 'mdata', cmd='ticker', pair=symbol)

    def get_balance(self, select):
        cmds = [
            {
                'cmd': 'transfer/assets',
                'body': {'select': select}
             }
        ]
        return self.signed_request('POST', 'transfer', cmds)

    def get_withdrawInfo(self, withdraw_id):
        cmds = [
            {
                'cmd': 'transfer/withdrawInfo',
                'body': {'id': withdraw_id}
             }
        ]
        return self.signed_request('POST', 'transfer', cmds)

    def create_order_cmd(self, index, symbol, order_side, order_type, price, amount, money, pay_bix=0, account_type=0):
        """
        下单命令
        :param index:随机数，int类型，批量时唯一标识某个cmd
        :param symbol:交易对, BIX_BTC, BIX_ETH, ...
        :param order_side:交易方向，1-买，2-卖
        :param order_type:交易类型，1-市价单，2-限价单
        :param price:委托价格
        :param amount:委托数量
        :param money:委托金额(order_type=1时需要)
        :param pay_bix:是否bix抵扣手续费，0-不抵扣，1-抵扣
        :param account_type:账户类型，0-普通账户，1-信用账户
        :return:
        """
        cmd = {
            'cmd': "orderpending/trade",
            'index': index,
            'body': {
                'pair': symbol,                  #交易对, BIX_BTC, BIX_ETH, ...
                'account_type': account_type,    #账户类型，0-普通账户，1-信用账户
                'order_type': order_type,        #交易类型，1-市价单，2-限价单
                'order_side': order_side,        #交易方向，1-买，2-卖
                'pay_bix': pay_bix,              #是否bix抵扣手续费，0-不抵扣，1-抵扣
                'price': price,                  #委托价格
                'amount': amount,                #委托数量
                'money': money                   #委托金额(order_type=1时需要)
            }
        }
        '''
        source = json.dumps(cmd) + str(random.randint(0,999999))
        md5 = hashlib.md5()
        md5.update(source.encode(encoding='utf-8'))
        index = md5.hexdigest()
        cmd['index'] = index
        return index, cmd
        '''
        return cmd

    def cancel_order_cmd(self, index, order_id):
        """
        撤单命令
        :param index: 随机数，int类型，批量时唯一标识某个cmd
        :param id: 委托单id
        :return:
        """
        cmd = {
            'cmd': "orderpending/cancelTrade",
            'index': index,
            'body': {
                'orders_id': order_id
            }
        }
        return cmd

    def get_order_pending_list_cmd(self, page, size, pair=None, account_type=None, coin_symbol=None,
                                   currency_symbol=None, order_side=None):
        """
        获取当前订单
        :param page: 第几页，从1开始
        :param size: 要几条
        :param pair:  交易对, 兼容参数
        :param account_type: 账户类型，0 - 普通账户，1 - 信用账户
        :param coin_symbol: 交易币种
        :param currency_symbol: 定价币种
        :param order_side: 交易方向，1 - 买，2 - 卖
        :return:
        """
        cmd = {
            'cmd': 'orderpending/orderPendingList',
        }
        body = {'page': page, 'size': size}
        if pair:
            body['pair'] = pair
        if account_type:
            body['account_type'] = account_type
        if coin_symbol:
            body['coin_symbol'] = coin_symbol
        if currency_symbol:
            body['currency_symbol'] = currency_symbol
        if order_side:
            body['order_side'] = order_side
        cmd['body'] = body
        return cmd
    def get_pending_history_list_cmd(self, page, size, pair=None, account_type=None, coin_symbol=None,
                                   currency_symbol=None, order_side=None, hide_cancel=None):
        """
        获取历史订单
        :param page: 第几页，从1开始
        :param size: 要几条
        :param pair:  交易对, 兼容参数
        :param account_type: 账户类型，0 - 普通账户，1 - 信用账户
        :param coin_symbol: 交易币种
        :param currency_symbol: 定价币种
        :param order_side: 交易方向，1 - 买，2 - 卖
        :param hide_cancel: 隐藏已撤销订单，0-不隐藏，1-隐藏
        :return:
        """
        cmd = {
            'cmd': 'orderpending/pendingHistoryList',
        }
        body = {'page': page, 'size': size}
        if pair:
            body['pair'] = pair
        if account_type:
            body['account_type'] = account_type
        if coin_symbol:
            body['coin_symbol'] = coin_symbol
        if currency_symbol:
            body['currency_symbol'] = currency_symbol
        if order_side:
            body['order_side'] = order_side
        if hide_cancel:
            body['hide_cancel'] = hide_cancel
        cmd['body'] = body
        return cmd

    def get_order_cmd(self, order_id):
        """
        获取订单详情
        :param order_id: 订单ID
        :return:
        """
        cmd = {
            'cmd': 'orderpending/order',
            'body': {
                'id': order_id
            }
        }
        return cmd

    def get_order_history_list_cmd(self, page, size, pair=None, account_type=None, coin_symbol=None,
                                   currency_symbol=None, order_side=None):
        """
        获取成交明细
        :param page: 第几页，从1开始
        :param size: 要几条
        :param pair:  交易对, 兼容参数
        :param account_type: 账户类型，0 - 普通账户，1 - 信用账户
        :param coin_symbol: 交易币种
        :param currency_symbol: 定价币种
        :param order_side: 交易方向，1 - 买，2 - 卖
        :return:
        """
        cmd = {
            'cmd': 'orderpending/orderHistoryList',
        }
        body = {'page': page, 'size': size}
        if pair:
            body['pair'] = pair
        if account_type:
            body['account_type'] = account_type
        if coin_symbol:
            body['coin_symbol'] = coin_symbol
        if currency_symbol:
            body['currency_symbol'] = currency_symbol
        if order_side:
            body['order_side'] = order_side
        cmd['body'] = body
        return cmd

    def multi_sign_cmd(self, cmds ,api_url ='orderpending'):
        """
        批量请求
        :param cmds:命令参数列表
        :return:
        """
        if isinstance(cmds, list):
            s_cmds = cmds
        else:
            s_cmds =[cmds]
        return self.signed_request('POST', api_url, s_cmds)

