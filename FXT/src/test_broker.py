#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from src.local_data import LocalData
from src.stat import Stat
from src.trade import Trade


class TestBrokerLocal():
    def __init__(self, account_balance, margin_rate, start_date, end_date):
        self.wallet = account_balance
        self.test_data = {'start_date':start_date, 'end_date':end_date}

        self.stat = Stat()
        self.local_data = LocalData()

        self.last_tick = {}

    def get_tick_data(self, instrument):
        for tick in self.local_data.read_tfx_files(instrument, self.test_data['start_date'], self.test_data['end_date']):
            self.stat.add_tick(tick)
            self.last_tick[instrument] = tick
            yield tick

    def open(self, instrument, volume):
        if volume > 0:
            price = self.last_tick[instrument][1]
        elif volume < 0:
            price = self.last_tick[instrument][2]

        trade = Trade(instrument, volume, price, self.margin_rate)
        self.wallet -= trade.margin

        return trade

    def close(self, trade):
        if trade.volume > 0:
            price = self.last_tick[trade.instrument][2]
        elif trade.volume < 0:
            price = self.last_tick[trade.instrument][1]

        self.wallet += trade.margin
        self.wallet += trade.get_profit(price)

    def convert_currency(self, instrument, base_volume, rate=None):
        if rate:
            return base_volume * rate
        else:
            tick = self.get_tick_data(instrument)

            if base_volume > 0: # buy
                return tick[1] * abs(base_volume)
            else: # sell
                return tick[2] * base_volume

    def get_account_info(self):
        self.margin_rate = 0.05
        self.account_currency = 'EUR'

    def get_account_state(self):
        self.wallet = 1000

    def get_active_trades(self):
        return []

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
