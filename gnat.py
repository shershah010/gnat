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


def valid_cmd(cmd: str):
    """
    Returns true if the given command is valid.
    Valid commads are of the form: 
        ACTION TICKER AMOUNT
    """

    tokens = cmd.split(' ')

    if len(tokens) != 3
        print("Incorrect format: require ACTION TICKER AMOUNT")
        return False

    if tokens[0] not in ('buy', 'sell')
        print("ACTION is not either 'buy' or 'sell'")
        return False

    try:
        int(tokens[2])
    except:
        print("AMOUNT not an integer")
        return False

    if int(tokens[2]) <= 0:
        print("AMOUNT is not positive")
        return False

    return True


def get_input(user_cmds, lock)
    cmd = ""
    print("Type 'q' or 'quit' to exit.")
    while cmd != "q" or cmd != "quit":
        print("Enter a command:")
        cmd = input()
        if valid_cmd(cmd):
            self.lock.aquire()
            user_cmds.append(cmd)
            self.lock.release()

    print("Goodbye!")


if __name__ == "__main__":
    # Get assets
    print("List your assets' ticker with comma seperation. For cryptos, prefex the ticker with an '@' (e.g @DOGE).")
    assets = input()
    validate_assets(assets)

    # Store the OHLC data in a folder called `gnat_storage` with each file stored as a csv document
    csv_storage = CSVStorage(save_dir="gnat_storage")

    # Get Harvest configuration
    print("Pick a streamer: dummy, yahoo, polygon, alpaca.")
    streamer = input()
    print("Pick a broker: paper, alpaca.")
    broker = input()
    print("Path to secret.yaml if needed.")
    secret_path = input()

    # Init the GNAT algo and get the dash thread
    gnat_algo = GNAT_Algo()
    dash_thread = gnat_algo.dash_thread
    # Start Harvest
    harvest_thread = threading.Thread(target=start_harvest, args=(assets, gnat_algo, csv_storage, streamer, broker) daemon=True).start()

    # Listen for user input
    get_input(gnat_algo.user_cmds, gnat_algo.user_cmds_lock)
    