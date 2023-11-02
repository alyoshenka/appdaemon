"""See ReadMe for details"""

# pylint: disable=import-error
import hassapi as hass
import threading
import datetime

from stations import get_station_ids

from snowdata import \
    get_sntl_data, \
    aggregate_station_data, \
    passes_snow_threshold, \
    get_snowfall_24, get_swe_24, get_swe_72, get_snowfall_72, \
    get_name, get_air_temp, get_elevation

from stations import get_station_ids, add_station, remove_station
  

NOTIFY_ME = 'notify/mobile_app_pixel_3a'
SNOTEL1 = 'https://wcc.sc.egov.usda.gov/reportGenerator/view/customSingleStationReport/hourly/start_of_period/'
SNOTEL2 = '|id=%22%22|name/-167,0/WTEQ::value,SNWD::value,PREC::value,TOBS::value?fitToScreen=false&sortBy=0:-1'

NO_DATA = '?'

# --- Attribute Names ---
TEMP = 'air temp'
ELEV = 'elevation'
SNOW_24 = '24 snow'
SWE_24 = '24 swe'
SNOW_72 = '72 snow'
SWE_72 = '72 swe'
LINK = 'link'
# ---
DEFAULT_ATTRIBUTES = { SNOW_24: NO_DATA, SWE_24: NO_DATA, TEMP: NO_DATA, ELEV: NO_DATA, SNOW_72: NO_DATA, SWE_72: NO_DATA, LINK: '' }

class SnowReporter(hass.Hass):
    def initialize(self):
        self.log('Hello from the SnowReporter')
    
        self.listen_event(self.send_phone_notification, event='state_changed', entity_id='input_button.ping')
        self.listen_event(self.phone_action, event="mobile_app_notification_action", action="do_a_thing")
        self.listen_event(self.generate_snow_report, event='state_changed', entity_id='input_button.generate_snow_report')

        for station in get_station_ids():
            self.set_state(entity_id='sensor.station_'+str(station), state='Station #' + str(station), attributes=DEFAULT_ATTRIBUTES)

        self.set_state(entity_id='sensor.snotel_stations', state=get_station_ids())

    def terminate(self):
        self.log('Goodbye from the SnowReporter')
        for station in get_station_ids():
            self.set_state(entity_id='sensor.station_'+str(station), state='Station #' + str(station), attributes=DEFAULT_ATTRIBUTES)

    def send_phone_notification(self, event_name, data, kwargs):
        self.log('Button pressed, sending phone notification')
        self.call_service(NOTIFY_ME, message='this is a message', data={"actions":[{"action":"do_a_thing","title":"Do A Thing"}]})
        
    def notify_phone_of_new_snow_report(self):
        """Notify that new report has been generated, and link to HA dashboard"""
        self.call_service(NOTIFY_ME, message='New Snow Report', data={"clickAction": "/lovelace/snowsports", "notification_icon": "mdi:snowflake"})

    def notify_phone_of_exciting_snow_report(self, report):
        """Notify that snow total has exceeded threshold, and link to snotel site"""
        link = SNOTEL1 + report['station_information']['triplet'] + SNOTEL2
        self.log('Notifying mobile of new snow at ' + get_name(report))
        station = report['station_information']['name']
        self.call_service(NOTIFY_ME, message=station + ' has new snow', data={"clickAction": link, "notification_icon": "mdi:exit-run"})
    
    def phone_action(self, event_name, data, kwargs):
        self.log('Phone action taken')

    def generate_snow_report(self, event_name, data, kwargs):
        self.log('Generating snow report')
        self.log(datetime.datetime.now())
        self.set_state(entity_id='sensor.last_snow_update', state=str(datetime.datetime.now()))

        def generate_station_report(station_id):
            def get_24_threshold():
                try:
                    return float(self.get_state('input_number.24_hour_snow_threshold'))
                except Exception as err:
                    self.log('Error getting 24 hr snow threshold: ' + str(err))
                    return 3
            def get_72_threshold():
                try:
                    return float(self.get_state('input_number.72_hour_snow_threshold'))
                except Exception as err:
                    self.log('Error getting 72 hr snow threshold: ' + str(err))
                    return 5

            self.log('Generating data for: ' + str(station_id))
            data = get_sntl_data(station_id)
            if data is None:
                return
            station_name = data['station_information']['name']
            station_id = data['station_information']['triplet'][0:3]
            entity_id = "sensor.station_" + station_id
            self.log('Got data for: ' + station_name + ' (#' + station_id + ')')
            snow24 = get_snowfall_24(data)
            swe24 = get_swe_24(data)
            snow72 = get_snowfall_72(data)
            swe72 = get_swe_72(data)
            temp = get_air_temp(data)
            elev = get_elevation(data)
            link = SNOTEL1 + data['station_information']['triplet'] + SNOTEL2
            self.set_state(entity_id=entity_id, state=station_name, attributes={SNOW_24: snow24, SWE_24: swe24, TEMP: temp, ELEV: elev, SNOW_72: snow72, SWE_72: swe72, LINK: link})
            try:
                if float(snow24) >= get_24_threshold() or float(snow72) >= get_72_threshold():
                    self.notify_phone_of_exciting_snow_report(data)
            except Exception as err:
                pass
        for station in get_station_ids():
            self.log('Getting data for station #' + str(station))
            t = threading.Thread(target=generate_station_report, args=(station,))
            t.start()
        self.notify_phone_of_new_snow_report()
