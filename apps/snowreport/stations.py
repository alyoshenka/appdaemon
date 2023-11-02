import pandas as pd
import os

CONTAINER_PATH = '/conf/apps/snowreport/'
SYSTEM_PATH =  './'
SNOTEL_STATIONS = 'snotel_stations.csv' 

def use_container():
    """Returns whether to use container path or system path"""
    if os.path.isfile(CONTAINER_PATH + SNOTEL_STATIONS):
        return True
    assert os.path.isfile(SYSTEM_PATH + SNOTEL_STATIONS)
    return False

def get_path():
    """Returns the snotel file path, depending on container or not"""
    return (CONTAINER_PATH if use_container() else SYSTEM_PATH) + SNOTEL_STATIONS

def load_stations():
    """Load SNOTEL stations and return dataframe"""
    try:
        df = pd.read_csv(CONTAINER_PATH + SNOTEL_STATIONS)
        df = df.set_index('Station')
        return df
    except FileNotFoundError as err:
        try:
            df = pd.read_csv(SYSTEM_PATH + SNOTEL_STATIONS)
            df = df.set_index('Station')
            return df
        except Exception as err:
            print('Error loading from system:', err)
            return None
    except Exception as err:
        print('Error loading snotel stations:', err)
        return None

def get_station_ids(station_df=load_stations()):
    """Get station id's from dataframe"""
    if station_df is None:
        print('No station dataframe')
        return None
    return station_df.index.to_list()

def add_station(station_id, station_area=None, station_name=None):
    """Add a snotel station"""
    df = load_stations()
    df.loc[station_id] = [station_area, station_name]
    df.to_csv(get_path())

def remove_station(station_id):
    """Remove a snotel station"""
    df = load_stations()
    df = df.drop(station_id)
    df.to_csv(get_path())

def update_station(station_id, station_area=None, station_name=None):
    if station_area is None and station_name is None:
        return
    df = load_stations()
    if station_area is not None:
        df.loc[station_id, ['Area']] = [station_area]
    if station_name is not None:
        df.loc[station_id, ['Name']] = [station_name]
    df.to_csv(get_path())

def run_tests(): 
    print(load_stations())
    print('Use container:', str(use_container()))
    print('Path:', get_path())
    print(get_station_ids(load_stations()))
    add_station(1000)
    update_station(1000, station_area="test area")
    update_station(1000, station_name="test name")
    print(load_stations())
    print(get_station_ids(load_stations()))
    remove_station(1000)
    print(get_station_ids(load_stations()))

# run_tests()