"""Generatese data about recent snowfall using SNOTEL data"""

import requests
import json

API = 'https://powderlines.kellysoftware.org/api/station/'
DAYS = 2
STATIONS = [
    # Bridgers
    929, # Sac
    365, # Brackett Creek
    # Crazies
    725, # S Fork Shields
    700, # Porcupine
    # Northern Gallatins
    578, # Lick Creek
    754, # Shower Falls
    # Northern Madisons
    590, # Lone Mountain
    # Middle Madisons
    385, # Carrot Basin
    328, # Beaver Creek
    # Cooke City
    670, # Northeast Entrance
    862, # White Mill
    480, # Fisher Creek
]
DELTA_SWE = 'Change In Snow Water Equivalent (in)'
DELTA_SNOW = 'Change In Snow Depth (in)'
TEMPERATURE = 'Observed Air Temperature (degrees farenheit)'

TIMEOUT = 2

NO_VALUE = '*'

# --- Useful Functions ---

def round_one_decimal(number):
    return round(number,1)

def get_sntl_data(station_id):
    """Get past DAYS+1 weather data from station station_id"""
    try:
        url = API + str(station_id) + ':MT:SNTL?days=' + str(DAYS)
        res = requests.get(url, timeout=TIMEOUT).content
        dat = res.decode('utf-8')
        obj = json.loads(dat)
        return obj
    except Exception as err:
        print(err, ':', url)
        return None
    
def aggregate_station_data():
    """Get data from all stations"""
    data = []
    for station in STATIONS:
        add = get_sntl_data(station)
        if add is not None:
            data.append(add)
    return data

def passes_snow_threshold(data, past_24=5, past_72=10):
    """Return all stations with 
        >= past_24 in snowfall in the past day or 
        >= past_72 in snowfall in the past 3 days"""
    def func(station):
        if len(station['data']) != 3:
            return False
        if station['data'][2][DELTA_SNOW] == '':
            return False
        if float(station['data'][2][DELTA_SNOW]) >= past_24:
            return True
        if station['data'][1][DELTA_SNOW] == '' or station['data'][0][DELTA_SNOW] == '':
            return False
        return float(station['data'][2][DELTA_SNOW]) \
             + float(station['data'][1][DELTA_SNOW]) \
             + float(station['data'][0][DELTA_SNOW]) >= past_72
    
    return list(filter(func, data))

# ---

# --- "Fun" Functions ---

def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=2))
    
def parse_day_data(day_obj):
    delta_swe = day_obj[DELTA_SWE]
    delta_snow = day_obj[DELTA_SNOW]
    temperature = day_obj[TEMPERATURE]
    # print('     Delta SWE:', delta_swe, 'New Snow:', delta_snow, 'Temp:', temperature)

def parse_sntl_data(obj):
    station_name = obj['station_information']['name']
    elevation = obj['station_information']['elevation']
    print('-', station_name)
    print(' ', elevation, 'ft')
    print(' Today:')
    parse_day_data(obj['data'][2])
    print(' Yesterday:')
    parse_day_data(obj['data'][1])
    print(' Two Days Ago:')
    parse_day_data(obj['data'][0])

def get_day(data, idx):
    """Return specified day, or None"""
    try:
        assert len(data['data']) == DAYS+1
        return data['data'][idx]
    except Exception as err:
        print('unable to get data from day:', err)
        return None
    
def get_snowfall_24(station):
    """Get 24 hr snowfall from day"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][DELTA_SNOW])
        return round_one_decimal(num)
    except Exception as err:
        print('No 24hr snowfall for', get_id(station), '-', err)
        return NO_VALUE
    
def get_snowfall_48(station):
    """Get 48 hr snowfall from data"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][DELTA_SNOW]) + float(station['data'][1][DELTA_SNOW])
        return round_one_decimal(num)
    except Exception as err:
        print('No 48hr snowfall for', get_id(station), '-', err)
        return NO_VALUE
    
def get_snowfall_72(station):
    """Get 72 hr snowfall from data"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][DELTA_SNOW]) + float(station['data'][1][DELTA_SNOW]) + float(station['data'][0][DELTA_SNOW])
        return round_one_decimal(num)
    except Exception as err:
        print('No 72hr snowfall for', get_id(station), '-', err)
        return NO_VALUE

def get_swe_24(station):
    """Get 24 hr snowfall from day"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][DELTA_SWE])
        return round_one_decimal(num)
    except Exception as err:
        print('No 24hr swe for', get_id(station), '-', err)
        return NO_VALUE

def get_swe_72(station):
    """Get 72 hr swe from data"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][DELTA_SWE]) + \
                float(station['data'][1][DELTA_SWE]) + \
                float(station['data'][0][DELTA_SWE])
        return round_one_decimal(num)
    except Exception as err:
        print('No 72hr swe for', get_id(station), '-', err)
        return NO_VALUE

def get_air_temp(station):
    """Get the observed air temperature"""
    try:
        assert len(station['data']) == DAYS+1
        num = float(station['data'][2][TEMPERATURE])
        return round_one_decimal(num)
    except Exception as err:
        print('unable to get air temperature:', err)
        return NO_VALUE
    
def get_elevation(station):
    """Get the elevation"""
    try:
        return station['station_information']['elevation']
    except Exception as err:
        print('unable to get air temperature:', err)
        return NO_VALUE

def get_name(station):
    """Get the name"""
    try:
        return station['station_information']['name']
    except Exception as err:
        print('unable to get station name:', err)
        return NO_VALUE

def get_id(station):
    """Get the id number"""
    try:
        return station['station_information']['triplet'].split(':',1)[0]
    except Exception as err:
        print('unable to get station id:', err)
        return NO_VALUE

def top_x_snowfall(data, x, days=0):
    amount = 0
    station = None
    for s in data:
        #print(station['station_information']['name'], station['data'][2][DELTA_SNOW])
        try:
            check = float(s['data'][DAYS][DELTA_SNOW])
        except Exception as err:
            # print(err)
            check = 0
        if check > amount:
            amount = check
            station = s
    print('Max Snow:')
    parse_sntl_data(station)

# ---

# --- Tests

print('Running Tests')

data = aggregate_station_data()
print('Station[0]:')
pretty_print(data[0])
print('---')
print(get_snowfall_24(data[0]))
print(get_air_temp(data[0]))


# top_x_snowfall(data, 3)
print(len(passes_snow_threshold(data, past_24=0.1, past_72=0.1)))
for station in passes_snow_threshold(data, past_24=0.1, past_72=0.1):
    parse_sntl_data(station)
print(round(1.25, 1))

# ---