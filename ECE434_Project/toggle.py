#!/usr/bin/env python3
# This function was written by James Werne. Run ./togglegpio.py at the command line,
#   then follow the instructions to toggle a pin at a specified frequency

import Adafruit_BBIO.GPIO as GPIO
import time


print("Enter the pin you wish to toggle (ex: P9_42): ")     # enter gpio pin
LED = input()                                               # pin gets set as an output
GPIO.setup(LED, GPIO.OUT)

print("Enter a sleep value below (in sec):")                # enter sleep time
sleep = float(input())                                      # period = 2*sleep, since it's high for (sleep) seconds, then low for (sleep) seconds

while True:
    GPIO.output(LED, 1)
    time.sleep(sleep)
    GPIO.output(LED, 0)
    time.sleep(sleep)