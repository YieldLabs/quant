import ccxt
import math

from core.position import PositionSide
from datasource.retry import retry
from ccxt.base.errors import RequestTimeout, NetworkError

from .abstract_broker import AbstractBroker
from .margin_mode import MarginMode
from .position_mode import PositionMode


class FuturesBybitBroker(AbstractBroker):
    def __init__(self, api_key, secret):
        super().__init__()
        self.exchange = ccxt.bybit({'apiKey': api_key, 'secret': secret})

    def set_settings(self, symbol, leverage=1, position_mode=PositionMode.ONE_WAY, margin_mode=MarginMode.ISOLATED):
        is_hedged = position_mode != PositionMode.ONE_WAY
        try:
            self.exchange.set_leverage(leverage, symbol)
            self.exchange.set_position_mode(is_hedged, symbol)
            self.exchange.set_margin_mode(margin_mode.value, symbol, {'leverage': leverage})
        except Exception as e:
            print(e)

    def _create_order(self, order_type, side, symbol, position_size, price=None, extra_params=None):
        order_params = {
            'symbol': symbol,
            'type': order_type,
            'side': side,
            'amount': position_size,
        }

        if price is not None:
            order_params['price'] = price

        if extra_params is not None:
            order_params['params'] = extra_params

        return self.exchange.create_order(**order_params)

    def _create_order_params(self, order_type, side, symbol, position_size):
        return {
            'order_type': order_type,
            'side': side.value,
            'symbol': symbol,
            'position_size': position_size,
            'extra_params': None,
        }

    def _create_extra_params(self, stop_loss_price, take_profit_price):
        extra_params = {}

        if stop_loss_price:
            extra_params['stopLoss'] = str(stop_loss_price)

        if take_profit_price:
            extra_params['takeProfit'] = str(take_profit_price)

        if extra_params:
            extra_params['timeInForce'] = 'PostOnly'

        return extra_params if extra_params else None

    def place_market_order(self, side, symbol, position_size, stop_loss_price=None, take_profit_price=None):
        order_params = self._create_order_params('market', side, symbol, position_size)
        order_params['extra_params'] = self._create_extra_params(stop_loss_price, take_profit_price)

        res = self._create_order(**order_params)

        return res['info']['orderId']

    def place_limit_order(self, order_side, symbol, entry_price, position_size, stop_loss_price=None, take_profit_price=None):
        order_params = self._create_order_params('limit', order_side.value, symbol, position_size)
        order_params.update({
            'price': entry_price,
            'extra_params': self._create_extra_params(stop_loss_price, take_profit_price)
        })

        res = self._create_order(**order_params)

        return res['info']['orderId']

    def update_stop_loss(self, order_id, symbol, side, stop_loss_price):
        order_params = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'params': self._create_extra_params(stop_loss_price)
        }

        self.exchange.edit_limit_order(**order_params)

    def has_open_position(self, symbol):
        return self.get_open_position(symbol) is not None

    def close_position(self, symbol):
        if not self.has_open_position(symbol):
            return

        open_position = self.get_open_position(symbol)

        self._create_order('market', 'sell' if open_position['position_side'] == PositionSide.LONG else 'buy', symbol, open_position['position_size'])

    def close_order(self, order_id, symbol):
        self.exchange.cancel_order(order_id, symbol)

    def get_account_balance(self, currency='USDT'):
        balance = self.exchange.fetch_balance()
        return float(balance['total'][currency])

    def get_symbol_info(self, symbol):
        market_info = self.exchange.fetch_markets()
        symbol_info = [market for market in market_info if market['id'] == symbol and market['linear']][0]

        trading_fee = symbol_info.get('taker', 0) + symbol_info.get('maker', 0)
        min_position_size = symbol_info.get('amount', {}).get('min', 1.0)

        position_precision = symbol_info.get('precision', {}).get('amount', 0)
        price_precision = symbol_info.get('precision', {}).get('price', 0)

        return trading_fee, min_position_size, int(abs(math.log10(position_precision))), int(abs(math.log10(price_precision)))

    def get_open_position(self, symbol):
        positions = self.exchange.fetch_positions(symbol)

        open_positions = [position for position in positions if float(position['info']['size']) != 0.0]

        if len(open_positions) > 0:
            current_position = open_positions[0]

            return {
                'position_side': PositionSide.LONG if current_position['side'] == 'long' else PositionSide.SHORT,
                'entry_price': float(current_position['entryPrice']),
                'position_size': float(current_position['info']['size']),
                'stop_loss_price': float(current_position['info']['stopLoss']),
                'take_profit_price': float(current_position['info']['takeProfit']),
            }

        return None

    def get_symbols(self):
        markets = self.exchange.fetch_markets()
        return [market_info['id'] for market_info in markets if market_info['linear'] and not market_info['type'] == 'future' and market_info['settle'] == 'USDT']

    @retry(max_retries=7, handled_exceptions=(RequestTimeout, NetworkError))
    def _fetch(self, symbol, timeframe, start_time, current_limit):
        return self.exchange.fetch_ohlcv(
            symbol, timeframe, since=start_time, limit=current_limit)

    def get_historical_data(self, symbol, timeframe, lookback=1000):
        start_time = self.exchange.milliseconds() - lookback * \
            self.exchange.parse_timeframe(timeframe) * 1000

        fetched_ohlcv = 0

        while fetched_ohlcv < lookback:
            current_limit = min(lookback - fetched_ohlcv, 1000)

            current_ohlcv = self._fetch(symbol, timeframe, start_time, current_limit)

            if not current_ohlcv:
                break

            for data in current_ohlcv:
                yield data

                fetched_ohlcv += 1

            start_time = current_ohlcv[-1][0] + \
                self.exchange.parse_timeframe(timeframe) * 1000
