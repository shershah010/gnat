import threading
from typing import List

from gnat_algo import GNAT_Algo

from harvest.trader import LiveTrader
from harvest.api.dummy import DummyStreamer
from harvest.storage.csv_storage import CSVStorage

def validate_assets(assets: List[str]):
    pass


def start_harvest(assets, algo, storage, streamer, broker):
    trader = LiveTrader(streamer=streamer, storage=storage, broker=broker debug=True)
    trader.set_symbol(assets)
    trader.set_algo(gnat_algo)
    # Update every minute
    trader.start("1MIN", all_history=False)


def get_input()
    cmd = ""
    print("Type 'q' or 'quit' to exit.")
    while cmd != "q" or cmd != "quit":
        print("Enter a command:")
        cmd = input().lower()
        print("You typed:", cmd)
        print("User input handling still in progress.")

    print("Goodbye!")


if __name__ == "__main__":
    # Get assets
    print("List your assets' ticker with comma seperation. For cryptos, prefex the ticker with an '@' (e.g @DOGE).")
    assets = input()
    validate_assets(assets)

    # Get Harvest configuration
    # Store the OHLC data in a folder called `gnat_storage` with each file stored as a csv document
    csv_storage = CSVStorage(save_dir="gnat_storage")
    dummy = DummyStreamer(dt.datetime.now())

    # Init the GNAT algo and get the dash thread
    gnat_algo = GNAT_Algo()
    dash_thread = gnat_algo.dash_thread
    # Start Harvest
    harvest_thread = threading.Thread(target=start_harvest, args=(assets, gnat_algo, csv_storage, dummy, None) daemon=True).start()

    # Listen for user input
    get_input()
    