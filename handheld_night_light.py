
#Copyright Thomas TEMPE 2020
#DWTFYL License

#INSTRUCTIONS:
#set the desired on/off hours in self.times
#set your WIFI password in do_connect_tt.py
#set the pins here, as well as in main.py
neopixel_data_pin = 12
button_pin_1 = 25
button_pin_2 = 26
#set your timezone here:
GMT=0
timezone = GMT+8 
#see my instructions for building the whole device on Instructables.com

import time
import machine
import network
from machine import Pin
from neopixel import NeoPixel
import math
import micropython



micropython.alloc_emergency_exception_buf(100) #for catching exceptions in the interrupt callback


red = (25, 0, 0)
yellow = (50, 50, 0)
night_light = (200,100,0)
white = (150, 200, 255)

green = (0,255,0)
blue = (0,0,255)
off = (0,0,0)
rtc = machine.RTC()

def localtime():
    'Returns the time of day, as a float representing the number of hours'
    return (rtc.datetime()[4]+timezone)%24+rtc.datetime()[5]/60

    
def dim(color, k):
    "apply a coefficient to a light triplet"
    a, b, c = color
    return ( round(a*k), round(b*k), round(c*k))



class Flashing_lights:
    'Controls two neopixels that flash continuously'
    def __init__(self, neopixel_pin):
        self.n = NeoPixel(Pin(neopixel_pin, Pin.OUT),2)
        self.n[0]=(0,0,0)
        self.n[1]=(0,0,0)
        self.n.write()
        self.brightness_max = 1
        self.brightness_min = .03
        self.color = (100,0,0)
        self.progress=0
        self.epoch = time.ticks_ms()

        self.breath = 27

    def set_color(self, color, brightness_min=0.03):
        self.color = color
        self.epoch = localtime()
        self.brightness_min=brightness_min

    def loop(self):
        k = ((math.cos((time.ticks_ms()-self.epoch)/450)+1)/2.8)*(self.brightness_max-self.brightness_min)+self.brightness_min
        
        self.n[1]=self.n[0]=dim(self.color, k)
        self.n.write()

class Handheld_night_light:
    def __init__(self, button_in_pin, button_pw_pin, fl):
        self.interrupted=0
        self.fl = fl
        self.light_sustain_duration = 10*60*1000 #milliseconds
        self.light_fade_duration = 15*60*1000
        self.light_fade_coeff = float(red[0])/night_light[0]
        self.LED = Pin(2, Pin.OUT)

        #until 7AM, flash red, with minimum coef of 0.03; when presses, turn to night_light for 25 minutes
        self.times = [(7, red, 0.03, night_light, 25), 
                      (8, yellow, 0.2, off, 120), 
                      (9, white, 0.4, off, 60), 
                      (20, off, 0, red, 1), 
                      (20+55/60, yellow, 0.2, red, 60), 
                      (25,red, 0.03, night_light, 25)]


        #Push button setup
        self.pw_pin=Pin(button_pw_pin, Pin.OUT) #drain
        self.pw_pin.value(0)
        self.button_pin = Pin(button_in_pin, Pin.IN, Pin.PULL_UP) #read button state
        self.button_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.button_callback)

    
    def button_callback(self, p):
        self.interrupted = 1
        #self.LED.value(not self.LED.value())

        
        
    def light(self, color, how_long):
        "turn on the light mode. Returns when the light is turned off"
        self.fl.set_color(color, .4)
        self.light_sustain_duration=how_long*.4*60*1000
        self.light_fade_duration=how_long*.6*60*1000
        start = time.ticks_ms()
        time.sleep_ms(200)#debounce
        duration = 0
        while((not self.interrupted) and (duration < self.light_sustain_duration+self.light_fade_duration)):
          duration = time.ticks_ms()-start
          if duration > self.light_sustain_duration: #fade-out

            k = (self.light_fade_duration-(duration-self.light_sustain_duration))/(self.light_fade_duration)*(1-self.light_fade_coeff)+self.light_fade_coeff
            self.fl.set_color(dim(color, k))
          self.fl.loop()
        print("light off")
        self.interrupted=0
        time.sleep_ms(200)#debounce
        return
        
    def loop(self):
        for t, c, k, cc, hl in self.times:
            if t>localtime():
#                print(t, ">", localtime(), "=> ", c, cc)
                if self.interrupted:
                    print("light on")
                    self.interrupted=0
                    self.light(cc, hl)
                else:
                    self.fl.set_color(c, k)
                break
        self.fl.loop()



fl = Flashing_lights(neopixel_data_pin)
hnl = Handheld_night_light(button_pin_1, button_pin_2,fl)


while(1):
    hnl.loop()
    time.sleep_ms(50)







