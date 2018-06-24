# -*- encoding:utf-8 -*-

import ws

class WebSock():
	def __init__(self, host='wss://api.fcoin.com/v2/ws'):
        self._host = host
        self._ws = None

    def regist_message_handler(self):
        pass

    def start(self):
        try:   
            self._ws = websocket.WebSocketApp(self._host, 
                                          	  on_message = self._on_message,
                                          	  on_error = self._on_error,
                                          	  on_close = self._on_close,
                                          	  on_open = self._on_open)

            self._ws.run_forever()
        except Exception, e:
            rospy.logerr('FCWebSocket %s init falied. Reason: %s', self._host, str(e)) 
        

        # 1. 创建websocket, 起线程跑
        
        # 2. 需要同时处理重连


    def init_websocket(self):
        pass

    def regist_message_handler(slef, ):
        pass



    def _on_message(self, ws, message):
        print(message)

    def _on_open(self, ws):
        print("web socket connet")

        # topics = ["ticker.ethbtc", "ticker.btcusdt"]
        # fcoin_ws.handle(print)
        # fcoin_ws.sub(topics)
        self._subcribe(["ticker.ftusdt"])


    def _on_close(self, ws):
        print("web socket close")

    def _on_error(self, ws, e):
        print("web socket error %v", str(e))

    def _subcribe(self, channel):
        if not isinstance(channel, list):
            channel = [channel]
        
        q = {'cmd': 'sub', 'args': channel, 'id': '1'}
        payload = json.dumps(q)
        self._ws.send(payload)

