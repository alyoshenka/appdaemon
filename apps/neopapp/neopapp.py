# pylint: disable=import-error
import hassapi as hass
import neopolitan.nonblocking as nb
from stockticker import default_tickers, snp_500, nasdaq_100

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

  def terminate(self):
    self.log('Goodbye from Neopolitan App')
    nb.close_display()

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
  