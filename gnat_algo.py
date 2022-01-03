# Builtin imports
import datetime as dt
import threading

# Harvest imports
from harvest.algo import BaseAlgo

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import dash
from dash import dcc
from dash import html


class GNAT_Algo(BaseAlgo):
    def __init__(self):
        self.tickers = {}
        self.dash_thread = threading.Thread(target=self.dash, daemon=True).start()
        self.user_cmds = []
        self.user_cmds_lock = threading.Lock()


    def setup(self):
        def init_ticker(ticker):
            candles_data = go.Candlestick(x=[],
                        open=[],
                        high=[],
                        low=[],
                        close=[])

            candles_figure = go.Figure(data=candles_data)
            candles_figure.update_layout(title=ticker + "OHLC", xaxis_title="Timestamp", yaxis_title="Price (USD)")

            price_figure = go.Figure(go.Scatter(x=[], y=[]))
            candles_figure.update_layout(title=ticker + "Price", xaxis_title="Timestamp", yaxis_title="Price (USD)")

            price_delta_figure = go.Figure(go.Scatter(x=[], y=[]))
            candles_figure.update_layout(title=ticker + "Price Delta", xaxis_title="Timestamp", yaxis_title="Price (USD)")

            return {ticker: {
                "initial_price": None,
                "ohlc": pd.DataFrame(),
                "candles_figure": candles_figure,
                "price_figure": price_figure,
                "price_delta_figure": price_delta_figure
                }
            }

        for symbol in self.trader.watchlist:
            self.tickers.update(init_ticker(symbol))


    def dash(self):
        app = dash.Dash()
        app.layout = self.dash_layout
        app.run_server(debug=True, use_reloader=False)


    def dash_layout(self):
        graphs = []
        for symbol in self.tickers.keys():
            graph = dcc.Graph(id=f"{symbol}_candles_figure", figure=self.tickers[symbol]["candles_figure"])
            graphs.append(graph)
            graph = dcc.Graph(id=f"{symbol}_price_figure", figure=self.tickers[symbol]["price_figure"])
            graphs.append(graph)
            graph = dcc.Graph(id=f"{symbol}_price_delta_figure", figure=self.tickers[symbol]["price_delta_figure"])
            graphs.append(graph)

        return html.Div(graphs)


    def main(self):

        if now - now.replace(hour=0, minute=0, second=0, microsecond=0) <= dt.timedelta(
            seconds=60
        ):
            for ticker_value in self.tickers.values():
                ticker_value["ohlc"] = pd.DataFrame()

        for ticker, ticker_value in self.tickers.items():
            current_price = self.get_asset_current_price(ticker)
            current_ohlc = self.get_asset_current_candle(ticker)

            if current_ohlc is None:
                return
            ticker_value["ohlc"] = ticker_value["ohlc"].append(current_ohlc)
            ticker_value["ohlc"] = ticker_value["ohlc"][
                ~ticker_value["ohlc"].index.duplicated(keep="first")
            ]

            if ticker_value["initial_price"] is None:
                ticker_value["initial_price"] = current_price

            self.process_ticker(ticker, ticker_value, current_price)

        self.user_cmds_lock.aquire()
        for cmd in self.user_cmds:
            print("Processing command:", cmd)
        self.user_cmds.clear()
        self.user_cmds_lock.release()


    def process_ticker(self, ticker, ticker_data, current_price):
        initial_price = ticker_data["initial_price"]
        ohlc = ticker_data["ohlc"]
        candles_figure = ticker_data["candles_figure"]
        price_figure = ticker_data["price_figure"]
        price_delta_figure = ticker_data["price_delta_figure"]

        # Calculate the price change
        delta_price = current_price - initial_price

        # Update candles figure
        candles_figure.update_traces(x=ohlc.index,
                            open=ohlc["open"],
                            high=ohlc["high"],
                            low=ohlc["low"],
                            close=ohlc["close"])

        # Update price figure
        price_figure.update_traces(x=ohlc.index, y=np.append(price_figure.data[0].y, [current_price]))

        # Update price delta figure
        price_delta_figure.update_traces(x=ohlc.index, y=np.append(price_delta_figure.data[0].y, [delta_price]))

