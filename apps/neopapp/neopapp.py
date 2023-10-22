# pylint: disable=import-error
import hassapi as hass
import neopolitan.nonblocking as nb
from stockticker import \
  default_tickers, snp_500, nasdaq_100, \
  get_default_tickers, \
  add_ticker, remove_ticker

class Neopolitan(hass.Hass):
  
  def initialize(self):

    self.log('Hello from Neopolitan App') 

    no_args_funcs = [
      (nb.open_display,  'input_button.open_neopolitan'),
      (nb.close_display, 'input_button.close_neopolitan'),
      (lambda : nb.open_display(default_tickers), 'input_button.neopstocks_default'),
      (lambda : nb.open_display(nasdaq_100), 'input_button.neopstocks_nasdaq'),
      (lambda : nb.open_display(snp_500), 'input_button.neopstocks_snp')
    ]
    for listener in no_args_funcs:
      self.listen_event(self.cb(func=listener[0]), event='state_changed', entity_id=listener[1])

    self.listen_event(self.update_text, event='state_changed', entity_id='input_text.update_neopolitan_text')
    self.listen_event(self.update_scroll_speed, event='state_changed', entity_id='input_number.neopolitan_scroll_speed')
    # listen for ticker +/-
    self.set_state(entity_id='input_text.add_ticker', state='')
    self.set_state(entity_id='input_text.remove_ticker', state='')
    self.listen_event(self.add_ticker_event, event='state_changed', entity_id='input_text.add_ticker')
    self.listen_event(self.remove_ticker_event, event='state_changed', entity_id='input_text.remove_ticker')
    self.listen_event(self.update_ticker_event, event='state_changed', entity_id='input_text.add_ticker')
    self.listen_event(self.update_ticker_event, event='state_changed', entity_id='input_text.remove_ticker')
    # publish default tickers as state
    self.set_state(entity_id='sensor.default_tickers', state='Default Tickers Loaded', attributes={'tickers': get_default_tickers()})

  def terminate(self):
    self.log('Goodbye from Neopolitan App')
    nb.close_display()
    self.set_state(entity_id='sensor.default_tickers', state='No Default Tickers', attributes={'tickers': []})

  def cb(self, func):
    return lambda event_name, data, kwargs: func()
  
  def update_text(self, event_name, data, kwargs):
    try:
      msg = data['new_state']['state']
      nb.open_display()
      nb.update_display({'say': msg})
    except Exception as err:
      self.log(err)

  def update_scroll_speed(self, event_name, data, kwargs):
    try:
      spd = data['new_state']['state']
      spd = 1 - float(spd)
      if spd < 0:
        spd = 0
      nb.update_display({'speed': spd})
    except Exception as err:
      self.log(err)

  def stocks_default(self, event_name, data, kwargs):
    nb.open_display(default_tickers)

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
    self.set_state(entity_id='sensor.default_tickers', state='Default Tickers Loaded', attributes={'tickers': get_default_tickers()})
  