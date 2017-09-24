import json
import logging
import ssl
import threading
from time import sleep
import websocket
from market_maker.utils import log
import sys


class TradeBlockWebsocket(object):
    logger = log.setup_custom_logger('root')

    def __init__(self, key=None):

        self.logger = logging.getLogger('root')
        self.logger.info("TradeBlock Websock Initalize")
        self.BASE_URL = "wss://clientapi.tradeblock.com/json/"
        self.CLIENT_KEY = key
        self.exited = False
        self.ws_client = websocket.WebSocketApp(self.BASE_URL,
                                                on_message=self._on_message,
                                                on_error=self._on_error,
                                                on_open=self._on_open,
                                                on_close=self._on_close)

    def __del__(self):
        self.exit()

    def connect(self):
        self.logger.info("Strating Connection...")
        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.wst = threading.Thread(target=lambda: self.ws_client.run_forever(sslopt=sslopt_ca_certs))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        while (not self.ws_client.sock or not self.ws_client.sock.connected) and conn_timeout:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            sys.exit(1)

    def _on_open(self, ws):
        self.logger.debug("Going to send First Message")
        self.ws_client.send(json.dumps({'action': 'subscribe', 'channel': 'indices'}))
        self.logger.info("Subscribe Message Send.")

    def _on_message(self, ws, message):
        message = json.loads(message)
        self.logger.info(json.dumps(message))

    def _on_error(self, ws, error):
        if not self.exited:
            self.logger.error(error)
            self.exit()

    def _on_close(self, ws):
        self.logger.info('Websocket Closed')
        self.exit()

    def exit(self):
        if not self.exited:
            self.exited = True
            self.ws_client.close()


if __name__=="__main__":
    tradeblock_ws = TradeBlockWebsocket()
    tradeblock_ws.connect()