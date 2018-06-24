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
        self.updateTime = 10.0
        self.sunAltitude = 0.0
        self.sunAzimuth = 0.0
        self.setup_pins()
        self.jogCCW = int(self.config['GPIO']['jogCCW'])
        self.jogCW = int(self.config['GPIO']['jogCW'])
        self.jogMode = int(self.config['GPIO']['jogMode'])
        print('Init done')
        


    def check_altitude(self):
        print("Altitude motor pos:{} Sun altitude:{}".format(self.altitudeMotor.get_pos(), self.sunAltitude))
        if(self.sunAltitude > self.altitudeMotor.get_pos() and self.sun_going_up(self.sunAltitude)):
            self.altitudeMotor.move(self.sunAltitude, False)
        elif(self.sunAltitude < self.altitudeMotor.get_pos() and not self.sun_going_up(self.sunAltitude)):
            self.altitudeMotor.move(self.sunAltitude, True)
        else:
             pass
            
    def sun_going_up(self, current_alt):
        """Check if sun is still rising"""
        new_time = self.date + datetime.timedelta(minutes=1)
        future_alt = solar.get_altitude(self.latitude, self.longitude, new_time)
        return current_alt < future_alt

    def check_azimuth(self):
        print("Azimuth motor pos:{} Sun azimuth:{}".format(self.azimuthMotor.get_pos(), self.sunAzimuth))
        if(self.sunAzimuth > self.azimuthMotor.get_pos()):
            self.azimuthMotor.move(self.sunAzimuth, False)
 
    def setup_pins(self):
        """Ställ in GPIO utgångar"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorStep']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorDir']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['altitudeMotorEnable']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorStep']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorDir']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['azimuthMotorEnable']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['isRunning']), GPIO.OUT)
        GPIO.setup(int(self.config['GPIO']['jogCCW']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(int(self.config['GPIO']['jogCW']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(int(self.config['GPIO']['jogMode']), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
          
    def get_sun_pos(self):
        """Get sun altitude and azimuth using pysolar"""
        self.date = datetime.datetime.now()
        self.sunAltitude = solar.get_altitude(self.latitude, self.longitude, self.date)
        self.sunAzimuth = self.offset(solar.get_azimuth(self.latitude, self.longitude, self.date))

    def offset(self, sun_value):
        offset = 180.0
        if abs(sun_value) >= 0 and abs(sun_value) < 180:
            return abs(sun_value) + offset
        else:
            return abs(sun_value + offset)


    def run(self):
        """Start app"""
        startTime = time.time()
        while True:
            if(time.time() > startTime + self.updateTime):
                self.update()
                startTime = time.time()

    def update(self):
        """Update App ,general things to do every cycle"""
        if self.jog_mode():
            if GPIO.input(self.jogCW) and not GPIO.input(self.jogCCW):
                self.azimuthMotor.jog(self.jogCW, False)
            elif GPIO.input(self.jogCCW) and not GPIO.input(self.jogCW):
                self.azimuthMotor.jog(self.jogCCW, True)
            else:
                pass
        else:
            self.get_sun_pos()
            self.check_altitude()
            self.check_azimuth()



    def jog_mode(self):
       return GPIO.input(self.jogMode)


        
    def on_exit(self):
        """cleanup when app closes"""
        self.altitudeMotor.disable()
        self.azimuthMotor.disable()
        
        
def main():
    app = App()
    try:
        app.run()
    finally:
        app.on_exit()


if __name__ == '__main__':
    main()

