

from machine import Pin

#configure pin numbers here
drain = 25
button = 26

#connect to Wifi and fetch the time from NTP, unless the button is pressed down
#Press down the button while connecting to uPyCraft V1.0 IDE to avoid a timeout 
Pin(drain, Pin.OUT, value=0) #drain
button_pin = Pin(button, Pin.IN, Pin.PULL_UP) #read button state
if button_pin.value():
  import do_connect
  do_connect.disconnect()
  import handheld_night_light
  





