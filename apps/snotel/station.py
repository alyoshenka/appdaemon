import hassapi as hass

import datetime

from data_request import *
from data_manipulation import *


class SnotelStation(hass.Hass):

    def default_data(self): 
        return {
            'station_id': self.args['station_id'],
            'station_link': make_station_url(self.args['station_id']),
            'station_name': '#' + str(self.args['station_id']),  
            'station_info': 'SNOTEL site',
            'last_updated': 'Never',
            'temperature': '-',
            'snow_depth': '-',
            '24_hour': {
                'max_temp': '-',
                'min_temp': '-',
                'delta_swe': '-',
                'delta_depth': '-',
            },
            '72_hour': {
                'max_temp': '-',
                'min_temp': '-',
                'delta_swe': '-',
                'delta_depth': '-',
            },
            '168_hour': {
                'max_temp': '-',
                'min_temp': '-',
                'delta_swe': '-',
                'delta_depth': '-',
            }
        }

    def initialize(self):
        self.log('Snotel Station initialized')
        station_id = str(self.args['station_id'])
        self.log('Station id: ' + station_id)
        self.set_state(entity_id='sensor.snotel_station_' + station_id, state=station_id, attributes=self.default_data())
        self.update()

    def terminate(self):
        station_id = str(self.args['station_id'])
        self.set_state(entity_id='sensor.snotel_station_' + station_id, state=station_id, attributes=self.default_data())
        self.log('Snotel Station ' + station_id + ' terminated')

    def update(self):
        self.log('Updating data: ' + str(self.args['station_id']))
        try:
            url = make_station_url(self.args['station_id'])
            res = get_from_url(url)
            soup = make_soup(res.text)
            self.log('Updating data for ' + get_report_info(soup)['site'])

            info = get_report_info(soup)
            data = get_report_data(soup)
            df = arr_to_df(data)

            new_data = self.default_data()

            new_data['station_name'] = info['site']
            new_data['station_info'] = info['info']

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

            self.set_state(entity_id='sensor.snotel_station_' + str(self.args['station_id']), attributes=new_data)

            self.log('Done updating Station ' + str(self.args['station_id']))


        except Exception as err:
            self.log('Error updating ' + str(self.args['station_id']) + ': ' + str(err))