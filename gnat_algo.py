# Builtin imports
import datetime as dt
import threading

# Harvest imports
from harvest.algo import BaseAlgo

import numpy as np
import pandas as pd
import plotly.graph_objects as go


class GNAT_Algo(BaseAlgo):
    def __init__(self):
        self.tickers = {}
        self.tickers_lock = threading.Lock()
        self.user_cmds = []
        self.user_cmds_lock = threading.Lock()

    def setup(self):
        def init_ticker(ticker):
            candles_data = go.Candlestick(x=[], open=[], high=[], low=[], close=[])

            candles_figure = go.Figure(data=candles_data)
            candles_figure.update_layout(
                title=ticker + " OHLC",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            price_figure = go.Figure(go.Scatter(x=[], y=[]))
            price_figure.update_layout(
                title=ticker + " Price",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            price_delta_figure = go.Figure(go.Scatter(x=[], y=[]))
            price_delta_figure.update_layout(
                title=ticker + " Price Delta",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            sma_figure = go.Figure(go.Scatter(x=[], y=[]))
            sma_figure.update_layout(
                title=ticker + " SMA",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            ema_figure = go.Figure(go.Scatter(x=[], y=[]))
            ema_figure.update_layout(
                title=ticker + " EMA",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            bbands_figure = go.Figure(
                [
                    go.Scatter(x=[], y=[], name="top"),
                    go.Scatter(x=[], y=[], name="middle"),
                    go.Scatter(x=[], y=[], name="bottom"),
                ]
            )
            bbands_figure.update_layout(
                title=ticker + " Bollinger Bands",
                xaxis_title="Timestamp",
                yaxis_title="Price (USD)",
            )

            return {
                ticker: {
                    "previous_price": None,
                    "ohlc": pd.DataFrame(),
                    "candles_figure": candles_figure,
                    "price_figure": price_figure,
                    "price_delta_figure": price_delta_figure,
                    "sma_figure": sma_figure,
                    "ema_figure": ema_figure,
                    "bbands_figure": bbands_figure,
                }
            }

        self.tickers_lock.acquire()
        for symbol in self.trader.watchlist:
            self.tickers.update(init_ticker(symbol))
        self.tickers_lock.release()

    def main(self):
        now = dt.datetime.now()
        if now - now.replace(hour=0, minute=0, second=0, microsecond=0) <= dt.timedelta(
            seconds=60
        ):
            self.tickers_lock.acquire()
            for ticker_value in self.tickers.values():
                ticker_value["ohlc"] = pd.DataFrame()
            self.tickers_lock.release()

        self.tickers_lock.acquire()
        for ticker, ticker_value in self.tickers.items():
            current_price = self.get_asset_current_price(ticker)
            current_ohlc = self.get_asset_current_candle(ticker)

            if current_ohlc is None:
                return
            ticker_value["ohlc"] = ticker_value["ohlc"].append(current_ohlc)
            ticker_value["ohlc"] = ticker_value["ohlc"][
                ~ticker_value["ohlc"].index.duplicated(keep="first")
            ]

            if ticker_value["previous_price"] is None:
                ticker_value["previous_price"] = current_price

            self.process_ticker(ticker, ticker_value, current_price)
        self.tickers_lock.release()

        self.user_cmds_lock.acquire()
        for cmd in self.user_cmds:
            action, ticker, amount = cmd.split(" ")
            amount = int(amount)

            if action == "buy":
                self.buy(ticker, amount)
            elif action == "sell":
                self.sell(ticker, amount)

        self.user_cmds.clear()
        self.user_cmds_lock.release()

    def process_ticker(self, ticker, ticker_data, current_price):
        previous_price = ticker_data["previous_price"]
        ohlc = ticker_data["ohlc"]
        candles_figure = ticker_data["candles_figure"]
        price_figure = ticker_data["price_figure"]
        price_delta_figure = ticker_data["price_delta_figure"]
        sma_figure = ticker_data["sma_figure"]
        ema_figure = ticker_data["ema_figure"]
        bbands_figure = ticker_data["bbands_figure"]

        # Calculate the price change
        delta_price = current_price - previous_price
        ticker_data["previous_price"] = current_price

        # Update candles figure
        candles_figure.update_traces(
            x=ohlc.index,
            open=ohlc["open"],
            high=ohlc["high"],
            low=ohlc["low"],
            close=ohlc["close"],
        )

        # Update price figure
        price_figure.update_traces(
            x=ohlc.index, y=np.append(price_figure.data[0].y, [current_price])
        )

        # Update price delta figure
        price_delta_figure.update_traces(
            x=ohlc.index, y=np.append(price_delta_figure.data[0].y, [delta_price])
        )

        # Peroid for calculating below stats is 14 minutes.
        if len(ohlc) > 13:
            sma = self.sma(ticker)
            ema = self.ema(ticker)
            t, m, b = self.bbands(ticker)
            # Update SMA figure
            sma_figure.update_traces(x=list(range(len(sma))), y=sma)

            # Update EMA figure
            ema_figure.update_traces(x=list(range(len(ema))), y=ema)

            # Update BBANDS figure

            bbands_figure.update_traces(
                x=list(range(len(t))), y=t, selector=dict(name="top")
            )

            bbands_figure.update_traces(
                x=list(range(len(m))), y=m, selector=dict(name="middle")
            )

            bbands_figure.update_traces(
                x=list(range(len(b))), y=b, selector=dict(name="bottom")
            )
