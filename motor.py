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


    def get_pos(self):
        self.pos = self.adc.read_adc(self.posAdress, self.GAIN)
        self.pos = int(self.map(self.pos, 0, 26140, 0, 360))
        return self.pos

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def move(self, dir, sunPos):
        """Run motor, takes in direction and suns position"""
        GPIO.output(self.enablePin, GPIO.HIGH)
        print(self.enablePin)
        delay = 0.02
        while(sunPos > self.get_pos()):
                GPIO.output(self.stepPin, GPIO.HIGH)
                time.sleep(delay)
                GPIO.output(self.stepPin, GPIO.LOW)
                time.sleep(delay)
        GPIO.output(self.enablePin, GPIO.LOW)
