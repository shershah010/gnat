import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State


# global tickers
global_tickers = None
global_tickers_lock = None

app = dash.Dash("GNAT")


def setup_dash(tickers, tickers_lock):
    # Update global variables
    global global_tickers
    global global_tickers_lock
    global_tickers = tickers
    global_tickers_lock = tickers_lock

    # Create the navigation
    tickers_lock.acquire()

    layout = html.Div(
        [
            html.H1("GNAT"),
            dcc.Tabs(
                id="tabs-graph",
                value=list(tickers.keys())[0],
                children=[
                    dcc.Tab(label=symbol, value=symbol) for symbol in tickers.keys()
                ],
            ),
            html.Div(id="tabs-content-graph"),
        ]
    )

    tickers_lock.release()

    # embedding the navigation bar
    app.layout = layout

    app.run_server(debug=False, use_reloader=False)


def dash_layout(symbol):
    graphs = []

    if global_tickers is None or global_tickers_lock is None:
        return html.H1("GNAT UI is starting up...")

    ticker = global_tickers.get(symbol)
    if ticker is not None:
        global_tickers_lock.acquire()
        graph = dcc.Graph(
            id=f"{symbol}_candles_figure",
            figure=ticker["candles_figure"],
        )
        graphs.append(graph)
        graph = dcc.Graph(id=f"{symbol}_price_figure", figure=ticker["price_figure"])
        graphs.append(graph)
        graph = dcc.Graph(
            id=f"{symbol}_price_delta_figure",
            figure=ticker["price_delta_figure"],
        )
        graphs.append(graph)
        graph = dcc.Graph(
            id=f"{symbol}_sma_figure",
            figure=ticker["sma_figure"],
        )
        graphs.append(graph)
        graph = dcc.Graph(
            id=f"{symbol}_ema_figure",
            figure=ticker["ema_figure"],
        )
        graphs.append(graph)
        graph = dcc.Graph(
            id=f"{symbol}_bbands_figure",
            figure=ticker["bbands_figure"],
        )
        graphs.append(graph)
        graphs.append(generate_table(ticker["ohlc"].iloc[::-1]))
        global_tickers_lock.release()

    return html.Div(graphs)


def generate_table(df, max_rows=10):
    if df.empty:
        return html.Div([html.H3("Waiting for data...")])

    df["timestamp"] = df.index.strftime("%I:%M:%S %p")
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    table = html.Table(
        [
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                    for i in range(min(len(df), max_rows))
                ]
            ),
        ]
    )

    return html.Div([html.H3("OHLC"), table], className="ohlc-table container")


@app.callback(Output("tabs-content-graph", "children"), [Input("tabs-graph", "value")])
def display_page(tab):
    return dash_layout(tab)
