import hassapi as hass

import datetime

from data_request import *
from data_manipulation import *

DEFAULT_DATA = {
    'station_id': 0,
    'station_name': 'Bozeman',  
    'last_updated': 'Never',
    'temperature': 100,
    'snow_depth': 100,
    '24_hour': {
        'max_temp': 100,
        'min_temp': 100,
        'delta_swe': 100,
        'delta_depth': 100,
    },
    '72_hour': {
        'max_temp': 100,
        'min_temp': 100,
        'delta_swe': 100,
        'delta_depth': 100,
    },
    '168_hour': {
        'max_temp': 100,
        'min_temp': 100,
        'delta_swe': 100,
        'delta_depth': 100,
    }
}


class SnotelStation(hass.Hass):

    def initialize(self):
        self.log('Snotel Station initialized')
        self.log('Station id: ' + str(self.args['station_id']))
        self.set_state(entity_id='sensor.test_snotel_data', state=self.args['station_id'], attributes=DEFAULT_DATA)

        self.update()

    def terminate(self):
        self.log('Snotel Station terminated')

    def update(self):
        self.log('Updating data: ' + str(self.args['station_id']))
        try:
            url = make_station_url(self.args['station_id'])
            res = get_from_url(url)
            soup = make_soup(res.text)
            self.log('Updating data for ' + get_report_info(soup)['site'])

            data = get_report_data(soup)
            df = arr_to_df(data)

            new_data = DEFAULT_DATA

            new_data['last_updated'] = datetime.datetime.now()
            new_data['temperature'] = get_temp(df)
            new_data['snow_depth'] = get_depth(df)

            one_day = get_past_x_days(df, 1)
            three_day = get_past_x_days(df, 3)

            new_data['24_hour']['max_temp'] = max_temp(one_day)
            new_data['24_hour']['min_temp'] = min_temp(one_day)
            new_data['24_hour']['delta_swe'] = delta_swe(one_day)
            new_data['24_hour']['delta_depth'] = delta_depth(one_day)

            new_data['72_hour']['max_temp'] = max_temp(three_day)
            new_data['72_hour']['min_temp'] = min_temp(three_day)
            new_data['72_hour']['delta_swe'] = delta_swe(three_day)
            new_data['72_hour']['delta_depth'] = delta_depth(three_day)

            new_data['168_hour']['max_temp'] = max_temp(df)
            new_data['168_hour']['min_temp'] = min_temp(df)
            new_data['168_hour']['delta_swe'] = delta_swe(df)
            new_data['168_hour']['delta_depth'] = delta_depth(df)

            self.set_state(entity_id='sensor.test_snotel_data', state='ON', attributes=new_data)

            self.log('Done updating Station ' + str(self.args['station_id']))


        except Exception as err:
            self.log('Error updating ' + str(self.args['station_id']) + ': ' + str(err))