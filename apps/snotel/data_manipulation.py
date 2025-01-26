"""Creates datafram and extracts useful information"""

import pandas as pd
import math
# pylint: disable=wildcard-import, unused-wildcard-import
from constants import *

BAD_VAL = 1000

def arr_to_df(arr):
    # todo: array validation (num/type of cols)
    """Generate a dataframe from the array"""
    def fill_from_next_oldest(df):
        """If gap in data, fill from next oldest"""
        df = df.bfill()
        return df
    # DATA VALIDATION!
    df = pd.DataFrame(arr, columns=COLUMNS)
    #df[DATETIME] = pd.to_datetime(df[DATETIME])
    df[SWE] = pd.to_numeric(df[SWE])
    df[DEPTH] = pd.to_numeric(df[DEPTH])
    df[PRECIP] = pd.to_numeric(df[PRECIP])
    df[TEMP] = pd.to_numeric(df[TEMP])
    #df = df.set_index(df.columns[0])
    df = fill_from_next_oldest(df)
    return df

def get_past_x_days(df, x):
    """Get the past x days of data"""
    # todo: ensure table has enough rows 
    #   (that gets rid of below line)
    try:
        end = x * 24
        if num_rows(df) < end:
            # todo: return error
            print('Not enough data!')
            return None
        return df.head(end)
    except:
        return df                 

def get_temp(df):
    """Get most recent temperature"""
    try:
        res = df.iloc[0][TEMP]
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for temp!')
        return BAD_VAL

def get_depth(df):
    """Get most recent snow depth"""
    try:
        res = df.iloc[0][DEPTH]
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for depth!')
        return BAD_VAL

def delta_swe(df):
    """Get the delta SWE from the given dataframe"""
    try:
        res = round(df.iloc[0][SWE] - df.iloc[-1][SWE], 1)
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for delta swe!')
        return BAD_VAL

def delta_depth(df):
    """Get the delta snow depth from the given dataframe"""
    try:
        res = round(df.iloc[0][DEPTH] - df.iloc[-1][DEPTH], 1)
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for delta depth!')
        return BAD_VAL

def max_temp(df):
    """Get the maximum temperature from the given dataframe"""
    try:
        res = df[TEMP].max()
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for max temp!')
        return BAD_VAL

def min_temp(df):
    """Get the minimum temperature from the given dataframe"""
    try:
        res = df[TEMP].min()
        return res if not math.isnan(res) else BAD_VAL
    except:
        print('Bad value for min temp!')
        return BAD_VAL

def check_if_val_is_num():
    """check to ensure queried table value is solid"""
    # how to handle if it's not??
    pass

def num_rows(df):
    """Get the number of rows in the dataframe"""
    return df.shape[0]

