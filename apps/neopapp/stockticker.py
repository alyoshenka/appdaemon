"""
Sets up display for a simple stock ticker

Note that this file is for demo purposes only,
    and will eventually be abstracted into its own repository
"""

# pylint: disable=broad-except
# pylint: disable=import-error
from threading import Thread
from random import shuffle
import requests
import yfinance as yf
import pandas as pd
from neopolitan.board_functions.colors import GREEN, RED
from neopolitan.board_functions.board_data import default_board_data
from neopolitan.naples import Neopolitan
from neopolitan.const import HEIGHT, WIDTH
from neopolitan.writing.data_transformation import dispatch_str_or_lst
from log import get_logger

TICKERS = ['DIS', 'AAL', 'BA', 'META', 'GOOG']
UP = '↑'
DOWN = '↓'
MIN_LEN = WIDTH * HEIGHT * 5 # todo: make sure works when scroll fast
TICKER_IDX = 4
PATH = '/conf/apps/neopapp/'
# PATH = './'

def valid_ticker(sym):
    """Tests whether the ticker is valid"""
    return True

def add_ticker(sym):
    """Add a ticker symbol to the default list"""
    if not valid_ticker(sym):
        return
    df = default_ticker_dataframe()
    df = pd.concat([df, pd.DataFrame([[sym]], columns=['Symbol'])], ignore_index=True)
    write_default_ticker_to_file(df)

def remove_ticker(sym):
    """Remove a ticker symbol from the default list"""
    df = default_ticker_dataframe()
    df = df[df['Symbol'] != sym]
    write_default_ticker_to_file(df)

def write_default_ticker_to_file(df):
    """Update the default tickers file"""
    df['Symbol'].to_csv(PATH + 'default_tickers.csv', index=False)

def default_ticker_dataframe():
    """Generate the pandas dataframe"""
    try:
        return pd.read_csv(PATH + 'default_tickers.csv')
    except Exception as err:
        print(err)
        return None

def get_default_tickers():
    """Load default ticker symbols"""
    try:
        tick = default_ticker_dataframe()
        return tick['Symbol'].to_list()
        # return TICKERS # todo
    # pylint: disable=bare-except
    except:
        get_logger().warning('Unable to load default tickers')
        return TICKERS

def get_snp_tickers():
    """Load S&P 500 ticker symbols"""
    try:
        snp = pd.read_csv(PATH + '/s_and_p.csv')
        thing = snp['Symbol'].to_list()
        shuffle(thing)
        return thing
    # pylint: disable=bare-except
    except:
        get_logger().warning('Unable to load S&P500 tickers')
        return TICKERS

def get_nasdaq_tickers():
    """Load NASDAQ 100 ticker symbols"""
    try:
        snp = pd.read_csv(PATH + 'nasdaq_100.csv')
        thing = snp['Symbol'].to_list()
        thing = [s.strip() for s in thing]
        shuffle(thing)
        return thing
    # pylint: disable=bare-except
    except:
        get_logger().warning('Unable to load NASDAQ100 tickers')
        return TICKERS

def monitor_message_length(neop, tickers):
    """Monitors how much of a message is left, and fetches the next ticker if it is time"""
    # pylint: disable=global-statement
    global TICKER_IDX # bad? yeah probably
    while not neop.display.should_exit:
        if len(neop.board.data) < MIN_LEN:
            if is_connected_to_internet():
                next_sym = tickers[TICKER_IDX]
                TICKER_IDX += 1
                if TICKER_IDX >= len(tickers):
                    TICKER_IDX = 0
                try:
                    next_ticker = get_ticker_data(next_sym)
                    next_msg = \
                        ('  ' + ticker_obj_to_string(next_ticker), \
                        GREEN if next_ticker['up?'] else RED)
                    new_data = dispatch_str_or_lst([next_msg])
                    neop.board.set_data(neop.board.data + new_data)
                    get_logger().info('Got new ticker data for: %s', next_sym)
                except Exception as err:
                    get_logger().warning('Error getting ticker data for %s: %s', next_sym, str(err))
                    new_data = dispatch_str_or_lst('Unable to get data for: ' + next_sym + '  ')
                    neop.board.set_data(neop.board.data + new_data)
            else:
                # ToDo: this is kinda bad code
                new_data = dispatch_str_or_lst([(' - No internet connection -', RED)])
                neop.board.set_data(neop.board.data + new_data)

def default_tickers(events, should_shuffle=False):
    """Run with the default tickers"""
    tickers = get_default_tickers()
    if should_shuffle:
        shuffle(tickers)
    run(events, tickers)

def snp_500(events, should_shuffle=False):
    """Run with S&P 500 tickers"""
    tickers = get_snp_tickers()
    if should_shuffle:
        shuffle(tickers)
    run(events, tickers)

def nasdaq_100(events, should_shuffle=False):
    """Run with NASDAQ100 tickers"""
    tickers = get_nasdaq_tickers()
    if should_shuffle:
        shuffle(tickers)
    run(events, tickers)

# pylint: disable=dangerous-default-value
def run(events, tickers):
    """Run the stock ticker"""
    get_logger().info('Running stock ticker')
    if not tickers:
        get_logger().warning('Ticker data not initialized')

    board_data = default_board_data.copy()
    board_data.message = construct_message(tickers)
    board_data.should_wrap = False
    board_data.scroll_fast()

    try:
        neop = Neopolitan(board_data=board_data, events=events)
        # thread that checks board data length
        #   query new data when it gets too low
        thrd = Thread(target=monitor_message_length, args=(neop, tickers))
        thrd.start()

        neop.loop()
    finally:
        thrd.join()
        del neop

def construct_message(tickers):
    """Constructs the data to send to neopolitan to display stocks"""
    try:
        all_ticker_data = [get_ticker_data(sym) for sym in tickers[0:TICKER_IDX]]
        msg = []
        for tick in all_ticker_data:
            if tick is not None:
                msg.append(('  ' + ticker_obj_to_string(tick), GREEN if tick['up?'] else RED))
            else:
                msg.append(('   Error', RED))
                print('Error:', tick)
        return msg
    except Exception as err:
        get_logger().warning('Error initializing ticker data for %s', str(err))
        return 'Error getting tickers  '

def get_ticker_data(sym):
    """"Query and return formatted data from a ticker symbol"""
    try:
        data = yf.Ticker(str(sym))
    # pylint: disable=broad-except
    except Exception as err:
        print("ERROR", err)
        return None
    info = data.info
    close = info['previousClose']
    cur = info['currentPrice']
    name = info['shortName']
    symbol = info['symbol']
    delta = cur - close
    obj = {
        "symbol": symbol,
        "name": name,
        "dollarDelta": round(delta, 2),
        "percentDelta": round(delta/close*100, 2),
        "up?": delta > 0
    }
    return obj

def ticker_obj_to_string(obj):
    """Converts a ticker object into a nice display string"""
    arrow = UP if obj["up?"] else DOWN
    # pylint: disable=consider-using-f-string
    dollar = '{0:.2f}'.format(obj["dollarDelta"])
    percent = '{0:.2f}'.format(obj["percentDelta"])
    return f'{obj["symbol"]} {arrow} ${dollar} {percent}%'

# ToDo: this should go somewhere else
def is_connected_to_internet():
    """Check whether there is an internet connection"""
    timeout = 1
    try:
        requests.head('http://google.com/', timeout=timeout)
        return True
    except requests.ConnectionError:
        get_logger().warning('No internet connection')
        return False
    except Exception as err:
        get_logger().warning('Error: %s', str(err))
    return False

"""
print(get_default_tickers())
remove_ticker('GOOG')
print(get_default_tickers())
add_ticker('GOOG')
print(get_default_tickers())
"""