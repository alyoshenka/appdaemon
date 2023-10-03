"""See ReadMe for details"""

# pylint: disable=import-error
import hassapi as hass

from snowdata import aggregate_station_data, passes_snow_threshold, get_snowfall_24, get_swe_24, STATIONS

NOTIFY_ME = 'notify/mobile_app_pixel_3a'
SNOTEL1 = 'https://wcc.sc.egov.usda.gov/reportGenerator/view/customSingleStationReport/hourly/start_of_period/'
SNOTEL2 = '%7Cid=%22%22%7Cname/-167,0/WTEQ::value,SNWD::value,PREC::value,TOBS::value?fitToScreen=false'

class SnowReporter(hass.Hass):
    def initialize(self):
        self.log('Hello from the SnowReporter')
    
        self.listen_event(self.send_phone_notification, event='state_changed', entity_id='input_button.ping')

        self.listen_event(self.phone_action, event="mobile_app_notification_action", action="do_a_thing")

        self.listen_event(self.generate_snow_report, event='state_changed', entity_id='input_button.generate_snow_report')

        self.set_state(entity_id="sensor.station_000", state="polling", attributes={"delta snow": 5, "delta swe": 0.1})
        for station in STATIONS:
            self.set_state(entity_id='sensor.station_'+str(station), state='Unknown', attributes={"delta snow": -1, "delta swe": -1})


    def terminate(self):
        self.log('Goodbye from the SnowReporter')
        for station in STATIONS:
            self.set_state(entity_id='sensor.station_'+str(station), state='Unknown', attributes={"delta snow": -1, "delta swe": -1})

    def send_phone_notification(self, event_name, data, kwargs):
        self.log('Button pressed, sending phone notification')
        self.call_service(NOTIFY_ME, message='this is a message', data={"actions":[{"action":"do_a_thing","title":"Do A Thing"}]})
        
    def notify_phone_of_new_snow_report(self):
        """Notify that new report has been generated, and link to HA dashboard"""
        self.call_service(NOTIFY_ME, message='New Snow Report', data={"clickAction": "/lovelace/snowsports", "notification_icon": "mdi:snowflake"})

    def notify_phone_of_exciting_snow_report(self, report):
        """Notify that snow total has exceeded threshold, and link to snotel site"""
        link = SNOTEL1 + report['station_information']['triplet'] + SNOTEL2
        self.call_service(NOTIFY_ME, message='IT SNOWED', data={"clickAction": link, "notification_icon": "mdi:exit-run"})
    
    def phone_action(self, event_name, data, kwargs):
        self.log('Phone action taken')

    def generate_snow_report(self, event_name, data, kwargs):
        self.log('Snow!!')
        data = aggregate_station_data()
        cool_snow = passes_snow_threshold(data, past_24=0.1, past_72=0.1)
        self.notify_phone_of_new_snow_report()
        for cool in cool_snow:
            self.notify_phone_of_exciting_snow_report(cool)
        for station in data:
            station_name = station['station_information']['name']
            station_id = station['station_information']['triplet'][0:3]
            entity_id = "sensor.station_" + station_id
            self.log('got data for: ' + str(station_id))
            snow = get_snowfall_24(station)
            swe = get_swe_24(station)

            self.set_state(entity_id=entity_id, state=station_name, attributes={"delta snow": snow, "delta swe": swe})
        self.log('Done')
