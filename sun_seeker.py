#!/usr/bin/env python3
#Sunseeker follows the sun and using pysolar and rpi2
#Author: Lars Fendell
import logging
import time
from motor import Motor
import configparser
import datetime
from pysolar import solar
import RPi.GPIO as GPIO

class App(object):
    date = datetime.datetime.now()
    config = configparser.ConfigParser()
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
        logging.info('Sun altitude: {0:1f}\n Sun azimuth: {1:1f}\n'.format(self.sunAltitude, self.sunAzimuth))
        self.check_altitude()
        self.check_azimuth()
        self.altitudeMotor.move(10, True)


    def check_altitude(self):
        print("Altitude motor pos:{} Sun altitude:{}".format(self.altitudeMotor.get_pos(), self.sunAltitude))
        if(self.sunAltitude > self.altitudeMotor.get_pos()):
            self.altitudeMotor.move(self.sunAltitude, False)

    def check_azimuth(self):
        print("Azimuth motor pos:{} Sun azimuth:{}".format(self.azimuthMotor.get_pos(), self.sunAzimuth))
        if(self.sunAzimuth > self.azimuthMotor.get_pos()):
            self.azimuthMotor.move(self.sunAzimuth, False)
 
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
        self.date = datetime.datetime.now()
        self.sunAltitude = solar.get_altitude(self.latitude, self.longitude, self.date)
        self.sunAzimuth = solar.get_azimuth(self.latitude, self.longitude, self.date)

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
