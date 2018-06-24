import logging
import Adafruit_ADS1x15
import pysolar
import datetime
import time
import RPi.GPIO as GPIO

class Motor(object):
    GAIN = 1
    adc = Adafruit_ADS1x15.ADS1115()

    
    def __init__(self, StepPin, DirPin, EnablePin, PosAdress, spr):
        self.stepPin = StepPin
        self.dirPin = DirPin
        self.enablePin = EnablePin
        self.posAdress = PosAdress
        self.pos = 0
        self.SPR = spr
        self.pulse_delay = 0.0005


    def get_pos(self):
        """Returns pos of motor read from pot adc"""
        self.pos = self.adc.read_adc(self.posAdress, self.GAIN)
        self.pos = int(self.map(self.pos, 0, 26140, 0, 360))
        return self.pos

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def move(self, set_pos, CCW=False):
        """Run motor, takes in direction and suns position"""
        GPIO.output(self.enablePin, GPIO.LOW)
        if not CCW:
            GPIO.output(self.dirPin, GPIO.HIGH)
            while(set_pos > self.get_pos()):
                self.pulse()
        else:
            GPIO.output(self.dirPin, GPIO.LOW)
            while(set_pos < self.get_pos()):
                self.pulse()
        self.disable()

    def jog(self, buttonPressed, CCW=False):
        """Run motor, takes in direction and suns position"""
        GPIO.output(self.enablePin, GPIO.LOW)
        if not CCW:
            GPIO.output(self.dirPin, GPIO.HIGH)
            while GPIO.input(buttonPressed):
                self.pulse()
        else:
            GPIO.output(self.dirPin, GPIO.LOW)
            while GPIO.input(buttonPressed):
                self.pulse()
        self.disable()

    def pulse(self):
        """pulse for stepper"""
        GPIO.output(self.stepPin, GPIO.HIGH)
        time.sleep(self.pulse_delay)
        GPIO.output(self.stepPin, GPIO.LOW)
        time.sleep(self.pulse_delay)
    def disable(self):
        GPIO.output(self.enablePin, GPIO.HIGH)
