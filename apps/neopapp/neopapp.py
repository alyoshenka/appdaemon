# pylint: disable=import-error
# pylint: disable=broad-exception-caught
# pylint: disable=unused-argument

# these should be dealt with
# pylint: disable=missing-method-docstring
# pylint: disable=bad-indentation
# pylint: disable=missing-function-docstring

# todo: look into dependencies for stockticker.py so it will reload on save??

import hassapi as hass
import neopolitan.nonblocking as nb
from stockticker import \
  default_tickers, snp_500, nasdaq_100, \
  get_default_tickers, \
  add_ticker, remove_ticker

class Neopolitan(hass.Hass):

  # --- AppDaemon Setup ---
  def initialize(self):
    self.log('Hello from Neopolitan App') 

    # --- Initialize State ---
    self.reset_scroll_speed()
    # ---
    # --- Display Functions ---
    self.listen_event(self.open_display, \
      event='state_changed', entity_id='input_button.open_neopolitan')
    self.listen_event(self.close_display, \
      event='state_changed', entity_id='input_button.close_neopolitan')
    # ---
    # --- Ticker Display Functions ---
    self.listen_event(self.display_stocks_default, \
      event='state_changed', entity_id='input_button.neopstocks_default')
    self.listen_event(self.display_stocks_snp, \
      event='state_changed', entity_id='input_button.neopstocks_snp')
    self.listen_event(self.display_stocks_nasdaq, \
      event='state_changed', entity_id='input_button.neopstocks_nasdaq')
    # ---
    # --- Text Updates ---
    self.listen_event(self.update_text, event='state_changed', \
                      entity_id='input_text.update_neopolitan_text')
    self.listen_event(self.update_scroll_speed, event='state_changed', \
                      entity_id='input_number.neopolitan_scroll_speed')
    # ---
    # --- Listen For Ticker +/- ---
    self.set_state(entity_id='input_text.add_ticker', state='')
    self.set_state(entity_id='input_text.remove_ticker', state='')
    self.listen_event(self.add_ticker_event, \
      event='state_changed', entity_id='input_text.add_ticker')
    self.listen_event(self.remove_ticker_event, \
      event='state_changed', entity_id='input_text.remove_ticker')
    self.listen_event(self.update_ticker_event, \
      event='state_changed', entity_id='input_text.add_ticker')
    self.listen_event(self.update_ticker_event, \
      event='state_changed', entity_id='input_text.remove_ticker')
    # ---
    # publish default tickers as state
    self.set_state(entity_id='sensor.default_tickers', \
      state='Default Tickers Loaded', attributes={'tickers': get_default_tickers()})

  def terminate(self):
    self.log('Goodbye from Neopolitan App')
    nb.close_display()
    self.set_state(entity_id='sensor.default_tickers', \
      state='No Default Tickers', attributes={'tickers': []}) 
  # ---  
  # --- Text Updates ---
  def update_text(self, event_name, data, kwargs):
    self.log('Updating Text')
    try:
      msg = data['new_state']['state']
      nb.open_display()
      self.log('Text: ' + msg)
      nb.update_display({'say': msg})
    except Exception as err:
      self.log(err)

  def update_scroll_speed(self, event_name, data, kwargs):
    self.log('Updating Scroll Speed')
    try:
      spd = data['new_state']['state']
      spd = 1 - float(spd)
      if spd <= 0:
        spd = 0.01
      self.log('Scroll Speed: ' + str(spd))
      nb.update_display({'speed': spd})
    except Exception as err:
      self.log(err)

  def reset_scroll_speed(self):
    """Reset the scroll speed in the UI when a new display opens"""
    DEFAULT_SCROLL_SPEED = 0.8
    self.set_state(entity_id='input_number.neopolitan_scroll_speed', state=DEFAULT_SCROLL_SPEED)
  # ---
  # --- Update Custom Tickers ---
  def add_ticker_event(self, event_name, data, kwargs):
    ticker = data['new_state']['state']
    self.log('Adding ticker: ' + ticker)
    add_ticker(ticker)
  
  def remove_ticker_event(self, event_name, data, kwargs):
    ticker = data['new_state']['state']
    self.log('Removing ticker: ' + ticker)
    remove_ticker(ticker)

  def update_ticker_event(self, event_name, data, kwargs):
    self.log('Updating tickers')
    self.set_state(entity_id='sensor.default_tickers', state='Default Tickers Loaded', \
                   attributes={'tickers': get_default_tickers()}) 
  # ---
  # --- General Display Functions
  def open_display(self, event_name, data, kwargs):
    self.log('Opening Neopolitan Display')
    self.reset_scroll_speed()
    nb.open_display()

  def close_display(self, event_name, data, kwargs):
    self.log('Closing Neopolitan Display')
    self.reset_scroll_speed()
    nb.close_display()

  # ---
  
  def shuffle_tickers(self): 
    return self.get_state('input_boolean.shuffle_tickers') == 'on'

  # --- Display Stocks ---
  def display_stocks_default(self, event_name, data, kwargs):
    self.log('Displaying Default Tickers')
    self.reset_scroll_speed()
    # This is so disgusting
    nb.open_display(lambda events: default_tickers(events, should_shuffle=self.shuffle_tickers())) 

  def display_stocks_snp(self, event_name, data, kwargs):
    self.log('Displaying SNP Tickers')
    self.reset_scroll_speed()
    # This is so disgusting
    nb.open_display(lambda events: snp_500(events, should_shuffle=self.shuffle_tickers())) 

  def display_stocks_nasdaq(self, event_name, data, kwargs):
    self.log('Displaying NASDAQ Tickers')
    self.reset_scroll_speed()
    # This is so disgusting
    nb.open_display(lambda events: nasdaq_100(events, should_shuffle=self.shuffle_tickers())) 
  # ---