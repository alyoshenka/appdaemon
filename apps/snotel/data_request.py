"""Handles requesting data from USDA snotel report generator"""

import requests as req
from bs4 import BeautifulSoup
# pylint: disable=wildcard-import, unused-wildcard-import
from constants import *

def make_station_url(station_id):
    """Generate the correct request url"""
    return PRE_URL + str(station_id) + POST_URL

def get_from_url(url):
    """Get data from the url"""
    return req.get(url)

def make_soup(text):
    """Create bs4 object"""
    return BeautifulSoup(text, 'html.parser')

def get_report_info(soup):
    """Parse info from the soup object"""
    try:
        header = soup.find(id=HEADER_ID)
        if header is None:
            print('No header found!')
        header_list = list(header.stripped_strings)
        site = header_list[0]
        info = header_list[1]
        rept = header_list[2]
        return ({'site': site, 'info': info, 'rept': rept})
    except Exception as err:
        print('Error getting report info: ' + str(err))
        return ({'site': 'Unavailable', 'info': 'Unavailable', 'rept': 'Unavailable'})
    # type^?

def get_report_data(soup):
    """Parse data from the soup object"""
    table = soup.find(id=TABLE_ID)
    try:
        rows = table.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            date    = cols[0].text
            swe     = cols[1].text
            depth   = cols[2].text
            accum   = cols[3].text
            temp    = cols[4].text
            frame = [date, swe, depth, accum, temp]
            data.append(frame)
        return data
    except Exception as err:
        print('Error getting report data: ' + str(err))
        return []
