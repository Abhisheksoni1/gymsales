import json
import logging
import threading

import time

from market_maker.utils import log
import requests


class TradeBlock(object):
    logger = log.setup_custom_logger('root')

    def __init__(self):

        self.logger = logging.getLogger('root')
        self.logger.info("TradeBlock Initalize")
        self.BASE_URL = "https://api.tradeblock.com/"
        self.endpoint = "markets/xbx/"
        self.exited = False
        self.current_xbx_price = None
        self.is_continuous = False

    def __del__(self):
        self.exit()

    def connect(self):
        self.logger.info("Strating Connection...")
        self.get_data()

    def get_data(self):
        self.current_xbx_price = self.__get_data()
        self.logger.info("XBX Price is ${}".format(self.current_xbx_price))

    def start_continuous_prices(self):
        self.is_continuous = True
        threading.Thread(target=self.__continuous_prices).start()

    def stop_continuous_prices(self):
        self.is_continuous = False

    def __continuous_prices(self):
        # self.wst = threading.Thread(target=)
        # self.wst.daemon = True
        # self.wst.start()
        while self.is_continuous:
            self.get_data()
            time.sleep(0.5)

    def _parser(self, data):
        return data['xbx']

    def __get_data(self):
        self.logger.info("Getting XBX Prices...")
        url = self.BASE_URL + self.endpoint
        data = requests.get(url).text
        return self._parser(json.loads(data))

    def exit(self):
        if not self.exited:
            self.exited = True

if __name__=="__main__":
    tradeblock_ws = TradeBlock()
    tradeblock_ws.start_continuous_prices()
    time.sleep(100)
    tradeblock_ws.stop_continuous_prices()