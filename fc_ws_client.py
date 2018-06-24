# -*- encoding:utf-8 -*-

import time
import websocket
import json

_CONNECT_TIMEOUT_INTERVAL_SEC = 10

CONN_STATUS_DISCONNECT   = 1
CONN_STATUS_CONNECTING  = 2
CONN_STATUS_CONNECT      = 3
CONN_STATUS_CLOSE        = 4

class CallbackFnc(object):
    def __init__(self, cb=None):
        self._cb = cb

    def call(self, param):
        if self._cb:
            self._cb(param)


class FCoinWebSocketClient():
    def __init__(self, key, secret, host='wss://api.fcoin.com/v2/ws', need_reconn = True, max_reconn_time = 10):
        self._host = host
        self._key = key
        self._secret = secret
        self._ws = None
        self._disconnect = True
        self._need_reconnect = need_reconn
        self._conn_status = CONN_STATUS_DISCONNECT
        self._max_reconnect_times =  max_reconn_time
        self._reconnect_retry_times = 0
        self._topic_cb_map = {}

    def start(self):
        try:   
            self._ws = websocket.WebSocketApp(self._host, 
                                          on_message = self._on_message,
                                          on_error = self._on_error,
                                          on_close = self._on_close,
                                          on_open = self._on_open)

            
        except Exception, e:
            rospy.logerr('FCWebSocket %s init falied. Reason: %s', self._host, str(e)) 
        

        self._set_conn_status(CONN_STATUS_DISCONNECT)

        while CONN_STATUS_CLOSE != self.get_conn_status():
			s = self.get_conn_status()
			if CONN_STATUS_DISCONNECT == s:
				self._connect()
			elif CONN_STATUS_CONNECTING == s:
				# 检查超时
				now = int(time.time())
				if now >= self._connection_timeout_sec:
					if False == self._need_reconnect or self._reconnect_retry_times >= self._max_reconnect_times:
						self._set_conn_status(CONN_STATUS_CLOSE)
					else :
						self._reconnect()

    def _connect(self):
    	self._set_conn_status(CONN_STATUS_CONNECTING)
    	self._ws.run_forever()
    	

    def _reconnect(self):
    	self._ws.sock = None
    	self._set_conn_status(CONN_STATUS_DISCONNECT)
    	
    
    def regist_topic_callback(self, topic, cb):
        obj = CallbackFnc(cb)
        self._topic_cb_map[str(topic)] = obj

    def regist_


    def get_conn_status(self):
    	return self._conn_status;


    def _set_conn_status(self, status):
    	self._conn_status = status

        if CONN_STATUS_DISCONNECT == status:
            self._connection_timeout_sec = 0
            self._reconnect_retry_times += 1
        elif CONN_STATUS_CONNECTING == status:
            self._connection_timeout_sec = int(time.time()) + _CONNECT_TIMEOUT_INTERVAL_SEC
    	elif CONN_STATUS_CONNECT == status:
            self._connection_timeout_sec = 0
            self._reconnect_retry_times  = 0


    def _on_message(self, ws, message):
        try:
            jsonObj = json.loads(str(message))
        except json.JSONDecodeError as e:
            print("json decode failed!")
            return

        if False == isinstance(jsonObj, dict):
            print("jsonObj Invalid")
            return
        elif False == jsonObj.has_key("type"):
            print jsonObj
            print("jsonObj type key is nil")
            return

        t = jsonObj["type"]
        if t == "hello":
            print 'connect server success!'
        elif t == "topics":
            print 'regist {topic} success!'.format(topic=jsonObj["topics"])
        else:
            # 找topic注册的处理函数
            if self._topic_cb_map.has_key(t):
                cb = self._topic_cb_map[t]
                cb.call(jsonObj)


            #print (t)
            return

    def _on_open(self, ws):
        self._set_conn_status(CONN_STATUS_CONNECT)

        for topic in self._topic_cb_map.keys():
            self._subcribe(topic)
            print('regist topic {t}'.format(t=str(topic)))


    def _on_close(self, ws):
        print("web socket close")
        if CONN_STATUS_CLOSE == self.get_conn_status() or False == self._need_reconnect:
        	return
        else :
        	self._reconnect()


    def _on_error(self, ws, error):
        print(error)
        self._set_conn_status(CONN_STATUS_CLOSE)


    def _subcribe(self, topic):
        arg = topic
        if not isinstance(topic, list):
            arg = [topic]
        
        q = {'cmd': 'sub', 'args': arg, 'id': '1'}
        payload = json.dumps(q)
        self._ws.send(payload)

    # def subcrib_ticker_info(self, )

