# -*- encoding:utf-8 -*-

import hmac
import hashlib
import requests
import sys
import time
import base64
import json
from collections import OrderedDict
import websocket

import logging
logging.basicConfig()

class FcoinHttpApi():
    def __init__(self, key, secret, url='https://api.fcoin.com/v2/'):
        self._base_url = url
        self._key = key
        self._secret = secret

    # 公开口请求
    def _public_request(self, method, uri, **payload):
        try:
            r = requests.request(method, self._base_url + uri, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)

        if r.status_code == 200:
            return r.json()

    # 签名
    def _signature(self, sign_str):
        sign_str = base64.b64encode(sign_str)
        return base64.b64encode(hmac.new(self._secret, sign_str, digestmod=hashlib.sha1).digest())
        
    # 认证借口请求
    def _auth_request(self, method, uri, **payload):
        """request a signed url"""

        param=''
        if payload:
            for key in sorted(payload.items()):
                param += '&' + str(k[0]) + '=' + str(k[1])

            param = param.lstrip('&')
        
        timestamp = str(int(time.time() * 1000))
        
        url = self._base_url + uri
        if method == 'GET':
            if param:
                url = url + '?' + param
            sig_str = method + url + timestamp
        elif method == 'POST':
            sig_str = method + url + timestamp + param

        signature = self._signature(sig_str)

        headers = {
            'FC-ACCESS-KEY':       self._key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }

        try:
            r = requests.request(method, url, headers = headers, json=payload)

            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()

    # 获取服务器时间
    def get_server_time(self):
        return self._public_request('GET','/public/server-time')['data']

    # 查询可用币种
    def get_currencies(self):
        """get all currencies"""
        return self._public_request('GET', '/public/currencies')['data']

    # 查询交易对    
    def get_symbols(self):
        """get all symbols"""
        return self._public_request('GET', '/public/symbols')['data']

    # 查询交易tick行情数据
    def get_market_ticker(self, symbol):
        """get market ticker"""
        return self._public_request('GET', 'market/ticker/{symbol}'.format(symbol=symbol))

    # 查询买卖档口数据
    def get_market_depth(self, level, symbol):
        """get market depth"""
        return self._public_request('GET', 'market/depth/{level}/{symbol}'.format(level=level, symbol=symbol))

    '''
    '''
    def get_trades(self, symbol, limit=10):
        """get detail trade"""
        return self._public_request('GET', 'market/trades/{symbol}?limit={limit}'.format(symbol=symbol, limit=limit))

    # 查账户里金额
    def get_balance(self):
        """get user balance"""
        return self._auth_request('GET', 'accounts/balance')

    def list_orders(self, **payload):
        """get orders"""
        return self._auth_request('GET','orders', **payload)

    # 下单    
    def create_order(self, **payload):
        """create order"""
        return self._auth_request('POST','orders', **payload)
    
    # 成交明细
    def get_order(self, order_id):
        """get specfic order"""
        return self._auth_request('GET', 'orders/{order_id}'.format(order_id=order_id))

    def cancel_order(self,order_id):
        """cancel specfic order"""
        return self._auth_request('POST', 'orders/{order_id}/submit-cancel'.format(order_id=order_id))

    def order_result(self, order_id):
        """check order result"""
        return self._auth_request('GET', 'orders/{order_id}/match-results'.format(order_id=order_id))

    # 获取蜡烛图数据
    def get_candle(self, resolution, symbol, **payload):
        """get candle data"""
        return self._public_request('GET', 'market/candles/{resolution}/{symbol}'.format(resolution=resolution, symbol=symbol), **payload)    
