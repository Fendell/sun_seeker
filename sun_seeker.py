#!/usr/bin/env python3
#Sunseeker follows the sun and using pysolar and rpi2
#Author: Lars Fendell
import time
from motor import Motor
import configparser
import datetime
from pysolar import solar
import RPi.GPIO as GPIO

class App(object):
    date = datetime.datetime.now()
    config = configparser.ConfigParser()
    CW = 0
    CCW = 1
    def __init__(self):
        self.config.read('config.ini')
        self.longitude = float(self.config['SETTINGS']['longitude'])
        self.latitude =  float(self.config['SETTINGS']['latitude'])
        self.altitudeMotor = Motor(int(self.config['GPIO']['altitudemotorstep']),
                                   int(self.config['GPIO']['altitudemotordir']),
                                   int(self.config['GPIO']['altitudemotorenable']),
                                   int(self.config['SETTINGS']['altitudemotorPosAdress']),
                                   int(self.config['SETTINGS']['altitudeMotorSPR']))

        self.azimuthMotor = Motor(int(self.config['GPIO']['azimuthmotorstep']),
                                  int(self.config['GPIO']['azimuthmotordir']),
                                  int(self.config['GPIO']['azimuthmotorenable']),
                                  int(self.config['SETTINGS']['azimuthmotorPosAdress']),
                                  int(self.config['SETTINGS']['azimuthMotorSPR']))
        self.updateTime = 2.0
        self.sunAltitude = 0.0
        self.sunAzimuth = 0.0
        self.setup_pins()
        print('Init done')
        
    def update(self):
        """Update App ,general things to do every cycle"""
        self.get_sun_pos()
        if(self.sunAltitude > self.altitudeMotor.get_pos()):
            self.altitudeMotor.move(self.CW, self.sunAltitude)
        self.azimuthMotor.get_pos()
        print(self.date, 'Altitude: ', self.sunAltitude)

    def setup_pins(self):
        #Ställ in GPIO utgångar
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorStep']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorDir']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorEnable']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorStep']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorDir']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorEnable']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['isRunning']), GPIO.OUT)
          
    def get_sun_pos(self):
        """Get sun altitude and azimuth using pysolar"""
        self.sunAltitude = 30.0
        self.sunAzimuth = 170.0

    def run(self):
        startTime = time.time()
        while True:
            if(time.time() > startTime + self.updateTime):
                self.update()
                startTime = time.time()

    def cleanup(self):
        """cleanup when app closes"""
        GPIO.cleanup()
        
        
def main():
    app = App()
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == '__main__':
    main()
