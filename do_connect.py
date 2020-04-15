import network
import ntptime
import time
from machine import Pin

#Set this value to your LED pin:
LED_pin = 2
WIFI_SSID = "XXXXX"
WIFI_PW = "YYYYY"

wlan = network.WLAN(network.STA_IF)
LED = Pin(LED_pin, Pin.OUT)    
    
def do_connect():
    LED.value(1)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(WIFI_SSID, WIFI_PW)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    print('network config:', wlan.ifconfig())
    LED.value(0)
    time.sleep(1)
    LED.value(1)
    while 2000 == time.localtime()[0]:
      try:
        ntptime.settime()
      except:
        time.sleep(1)
    LED.value(0)
    
    
def disconnect():
    wlan.active(False)
    
do_connect()



