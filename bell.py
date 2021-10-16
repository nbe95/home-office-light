#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep

BUZZER = 24
BUTTON = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

def ring_bell(channel):
    for i in range(5):
        GPIO.output(BUZZER, 1)
        sleep(0.05)
        GPIO.output(BUZZER, 0)
        sleep(0.05)

GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=ring_bell, bouncetime=1000)

try:
    while (True):
        pass

except KeyboardInterrupt:
    GPIO.cleanup()
