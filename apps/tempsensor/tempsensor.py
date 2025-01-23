import hassapi as hass
import datetime
from time import strftime, localtime

"""
Every x timeframe:
    query temperature 
    if temperature outside of bounds:
        alert
"""

TEMP_SENSOR = 'sensor.medusa_temperature'
HUMD_SENSOR = 'sensor.medusa_humidity'
TIME_SENSOR = 'sensor.last_update'

MIN_TEMP = 30
MAX_TEMP = 80

CHECK_EVERY = 60*5 # 5 minutes
UPDATE_EVERY = 60*5 # 5 minutes

DHT_UPDATE_INTERVAL = 60*5 # 5 minutes

NO_VALUE = -1

NOTIFY_ME = 'notify/mobile_app_pixel_3a'

class TempSensor(hass.Hass):
    def initialize(self):
        self.log('hello from the Temperature Monitor')
        self.run_every(self.check_for_ok_temp, 'now', CHECK_EVERY)
        self.run_every(self.check_for_still_updating, 'now', UPDATE_EVERY)

    def check_for_ok_temp(self, cb_args):
        self.log('Checking for ok temp')
        temp = self.get_temp()
        def notifiy_of_bad_temp():
            def construct_bad_temp_message():
                msg = 'DHT temperature: ' + str(temp) + '°F'
                if temp < MIN_TEMP:
                    data = 'Temperature below ' + str(MIN_TEMP) + '°F!'
                else:
                    data = 'Temperature exceeds ' + str(MAX_TEMP) + '°F!'
                return msg, data
            
            self.log('Bad temperature recorded: ' + str(temp) + ' deg F')
            title, message = construct_bad_temp_message()
            self.call_service(NOTIFY_ME, title=title, message=message)

        if temp <= MIN_TEMP or temp >= MAX_TEMP:
            notifiy_of_bad_temp()

    def check_for_still_updating(self, cb_args):
        self.log('Checking that still updating')
        def has_update_time():
            return self.get_last_update_time() is not NO_VALUE
        def has_updated_within_interval():
            last_update = self.get_last_update_time()
            current_time = (int)(datetime.datetime.now().timestamp())
            # Give it two cycles + offset
            return current_time - last_update < DHT_UPDATE_INTERVAL + 10
        def notify_of_lost_update():
            self.log('Lost update')
            last_update = self.get_last_update_time()
            if last_update is NO_VALUE:
                message = 'Last Update: unavailable'
            else: 
                message = 'Last Update: ' + strftime('%m/%-d/%Y %I:%M:%S %p', localtime(last_update))
            self.call_service(NOTIFY_ME, title='Lost DHT Update!', message=message)

        if not has_update_time() or not has_updated_within_interval():
            notify_of_lost_update()

    def get_temp(self):
        try:
            return (int)(self.get_state(TEMP_SENSOR))
        except:
            return NO_VALUE
    def get_humd(self):
        try:
            return (int)(self.get_state(HUMD_SENSOR))
        except:
            return NO_VALUE
    def get_last_update_time(self):
        try:
            return (int)(self.get_state(TIME_SENSOR))
        except:
            return NO_VALUE


