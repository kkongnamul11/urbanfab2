import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)

print "start led"

gpio.setup(17, gpio.OUT)
gpio.setup(27, gpio.OUT)
gpio.setup(22, gpio.OUT)


try:
    while True:
        gpio.output(17,False)
        gpio.output(27,False)
        gpio.output(22,False)
        time.sleep(1)

        gpio.output(17,True)
        gpio.output(27,True)
        gpio.output(22,True)
        time.sleep(1)

except KeyboardInterrupt:
    gpio.cleanup()

        
