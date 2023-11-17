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
import datetime
import pytz
from neopolitan.board_functions.colors import GREEN, RED, WHITE
from neopolitan.board_functions.board_data import default_board_data
from neopolitan.naples import Neopolitan
from neopolitan.const import HEIGHT, WIDTH
from neopolitan.writing.data_transformation import dispatch_str_or_lst
from log import get_logger

TICKERS = ['DIS', 'AAL', 'BA', 'META', 'GOOG']
UP = '↑'
DOWN = '↓'
MIN_LEN = WIDTH * HEIGHT * 5 # todo: make sure works when scroll fast
TICKER_IDX = 0
PATH = '/conf/apps/neopapp/'
# PATH = './'

def get_three_day_history(ticker):
    return ticker.history(period='3d')

def get_last_close(ticker):
    history = get_three_day_history(ticker)
    get_logger().info('Ticker: ' + str(ticker.ticker))
    get_logger().info('Trading: ' + str(currently_trading(to_NY_time(datetime.datetime.now()))))
    # outside of hours on a weekday:
    lastDay = history.iloc[1]
    """
    lastDay = history.iloc[1] \
        if currently_trading(to_NY_time(datetime.datetime.now())) \
        else history.iloc[0]
    """
    return round(lastDay['Close'], 2)

def currently_trading(nyc_time):
    if nyc_time.weekday() > 4: # Not on weekends
        return False
    if nyc_time.hour >= 12+4: # Not after 4pm
        return False
    if nyc_time.hour < 9: # Not before 9am
        return False
    if nyc_time.hour == 9 and nyc_time.minute < 30: # Not before 9:30am
        return False
    return True

def to_NY_time(local_time):
    return local_time.astimezone(pytz.timezone('America/New_York'))

def get_current_price(ticker):
    return round(ticker.fast_info['lastPrice'], 2)

def get_price_delta(close_price, current_price):
    return round(current_price - close_price, 2)

def get_percent_delta(close_price, current_price):
    return round(\
    get_price_delta(close_price=close_price, current_price=current_price) \
    / close_price * 100, 2)

def valid_ticker(sym):
    """Tests whether the ticker is valid"""
    return len(sym) > 0 # todo

def add_ticker(sym):
    """Add a ticker symbol to the default list"""
    if not valid_ticker(sym):
        get_logger.warning('Invalid ticker: ' + sym)
        return
    sym = str(sym).strip()
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
        thing = [s.strip() for s in thing]
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
                    get_logger().warning('Error getting ticker data for %s', next_sym) # error msg too long
                    new_data = dispatch_str_or_lst('  Unable to get data for: ' + next_sym)
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
    msg = [('           Currently trading: ' \
    + ('Yes' if currently_trading(to_NY_time(datetime.datetime.now())) else 'No'), \
    WHITE)]
    # could just take this all out now with initial message
    try:
        all_ticker_data = [get_ticker_data(sym) for sym in tickers[0:TICKER_IDX]]
        for tick in all_ticker_data:
            if tick is not None:
                msg.append(('  ' + ticker_obj_to_string(tick), GREEN if tick['up?'] else RED))
    except Exception as err:
        get_logger().warning('Error initializing ticker data for %s', str(err))
        msg.append(('Error getting tickers  ', RED)) 
    return msg

def get_ticker_data(sym):
    """"Query and return formatted data from a ticker symbol"""
    try:
        ticker = yf.Ticker(str(sym))           
        if ticker.history().size == 0: # check for delisted
            return None
    # pylint: disable=broad-except
    except Exception as err:
        get_logger().error("ERROR: " + str(err))
        return None
    close = get_last_close(ticker)
    cur = get_current_price(ticker)
    name = None
    symbol = (str)(sym).upper()
    delta = get_price_delta(close_price=close, current_price=cur)
    pct = get_percent_delta(close_price=close, current_price=cur)
    obj = {
        "symbol": symbol,
        "name": name,
        "currentPrice": cur,
        "dollarDelta": delta,
        "percentDelta": pct,
        "up?": delta > 0
    }
    return obj

def ticker_obj_to_string(obj):
    """Converts a ticker object into a nice display string"""
    arrow = UP if obj["up?"] else DOWN
    # pylint: disable=consider-using-f-string
    dollar = '{0:.2f}'.format(obj["dollarDelta"])
    percent = '{0:.2f}'.format(obj["percentDelta"])
    price = '{0:.2f}'.format(obj["currentPrice"])
    return f'{obj["symbol"]}: ${price} {arrow} ${dollar} {percent}%'

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
ticker = yf.Ticker('tsla')
print(get_current_price(ticker), get_last_close(ticker))
print(get_three_day_history(ticker))
print(get_three_day_history(ticker).iloc[0].name)
print(get_three_day_history(ticker).iloc[1].name)
print(get_three_day_history(ticker).iloc[2].name)
"""
