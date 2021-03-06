#!/usr/bin/env python3
#Sunseeker follows the sun and using pysolar and rpi2
#Author: Lars Fendell
import logging
import time
from motor import Motor
import datetime
from pysolar import solar
import RPi.GPIO as GPIO

class App(object):
    date = datetime.datetime.now()
    def __init__(self):
        self.longitude = 13.01053
        self.latitude =  56.69815
        # Pins and settings for altitude motor
        self.altitudeMotorStepPin = 21
        self.altitudeMotorDirPin = 20
        self.altitudeMotorEnablePin = 16
        self.altitudeMotorPosAdress = 0 # Adress of i2c AD converter
        self.altitudeMotorSPR = 400 # Steps per revolution
        self.altitudeMotorMinPos = 2
        self.altitudeMotorMaxPos = 70 
        # create motor object
        self.altitudeMotor = Motor(self.altitudeMotorStepPin,
                                   self.altitudeMotorDirPin,
                                   self.altitudeMotorEnablePin,
                                   self.altitudeMotorPosAdress,
                                   self.altitudeMotorSPR,
                                   self.altitudeMotorMinPos,
                                   self.altitudeMotorMaxPos)

        # Pins and settings for azimuth motor
        self.azimuthMotorStepPin = 26
        self.azimuthMotorDirPin = 19
        self.azimuthMotorEnablePin = 13
        self.azimuthMotorPosAdress = 1 # Adress of i2c AD converter
        self.azimuthMotorSPR = 400 # Steps per revolution
        self.azimuthMotorMinPos = 20
        self.azimuthMotorMaxPos = 280
        # create motor object
        self.azimuthMotor = Motor(self.azimuthMotorStepPin,
                                   self.azimuthMotorDirPin,
                                   self.azimuthMotorEnablePin,
                                   self.azimuthMotorPosAdress,
                                   self.azimuthMotorSPR,
                                   self.azimuthMotorMinPos,
                                   self.azimuthMotorMaxPos)
        # settings
        self.updateTime = 10.0
        self.sunAltitude = 0.0
        self.sunAzimuth = 0.0
        self.jogCCW = 23
        self.jogCW = 24
        self.jogMode = 25
        self.jogAltMotor = 18
        self.wentToSunrise = False
        self.running = False
        self.isRunning = 6
        self.setup_pins()
        print('Init done')
        


    def check_altitude(self):
        print("Altitude motor pos:{} Sun altitude:{}".format(self.altitudeMotor.get_pos(), self.sunAltitude))
        if(self.sunAltitude > self.altitudeMotor.get_pos() and (self.sun_going_up(self.sunAltitude)) or self.sunAltitude - self.altitudeMotor.get_pos() > 2.0):
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
        GPIO.setup(self.altitudeMotorStepPin, GPIO.OUT)
        GPIO.setup(self.altitudeMotorDirPin, GPIO.OUT)
        GPIO.setup(self.altitudeMotorEnablePin, GPIO.OUT)
        GPIO.setup(self.azimuthMotorStepPin, GPIO.OUT)
        GPIO.setup(self.azimuthMotorDirPin, GPIO.OUT)
        GPIO.setup(self.azimuthMotorEnablePin, GPIO.OUT)
        GPIO.setup(self.isRunning, GPIO.OUT)
        GPIO.setup(self.jogCCW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.jogCW, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.jogMode, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.jogAltMotor, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
          
    def get_sun_pos(self):
        """Get sun altitude and azimuth using pysolar"""
        self.date = datetime.datetime.now()
        self.sunAltitude = solar.get_altitude(self.latitude, self.longitude, self.date)
        self.sunAzimuth = self.offset(solar.get_azimuth(self.latitude, self.longitude, self.date))

    def offset(self, sun_value):
        """offset between pot and pysolar"""
        offset = 180.0
        if abs(sun_value) >= 0 and abs(sun_value) < 180:
            return abs(sun_value) + offset
        else:
            return abs(sun_value + offset)


    def run(self):
        """Start app and main loop"""
        startTime = time.time()
        self.running = True
        while self.running:
            GPIO.output(self.isRunning, GPIO.HIGH)
            if(time.time() > (startTime + self.updateTime) and not self.jog_mode()):
                self.update()
                startTime = time.time()
            elif self.jog_mode():
                self.jog()
        

    def jog(self):
        if GPIO.input(self.jogCW) and not GPIO.input(self.jogCCW):
            if not GPIO.input(self.jogAltMotor):
                self.azimuthMotor.jog(self.jogCW, False)
            else:
                self.altitudeMotor.jog(self.jogCW, False)
        elif GPIO.input(self.jogCCW) and not GPIO.input(self.jogCW):
            if not GPIO.input(self.jogAltMotor):
                self.azimuthMotor.jog(self.jogCCW, True)
            else:
                self.altitudeMotor.jog(self.jogCCW, True)
                        
    def update(self):
        """Update App ,general things to do every cycle"""
        self.get_sun_pos()
        if(self.sunAltitude > 15.0):
            self.check_altitude()
            self.check_azimuth()
            self.wentToSunrise = False
        elif(self.sunAltitude < 15.0 and not self.wentToSunrise):
            print('Sun to low\n')
            next_pos = self.check_next_sunrise()
            print('Going to {} pos.\n'.format(next_pos))
            self.azimuthMotor.move(next_pos, True)
            self.wentToSunrise = True
        else:
            pass

    def check_next_sunrise(self):
        """Check azimuth of next sunrise"""
        new_date = self.date
        while(solar.get_altitude(self.latitude, self.longitude, new_date) < 15.0):
            print(new_date)
            new_date += datetime.timedelta(minutes=10)
        return self.offset(solar.get_azimuth(self.latitude, self.longitude, new_date))
    
    def jog_mode(self):
       return GPIO.input(self.jogMode)
        
    def on_exit(self):
        """cleanup when app closes"""
        self.altitudeMotor.disable()
        self.azimuthMotor.disable()
        GPIO.output(self.isRunning, GPIO.LOW)
        
        
def main():
    app = App()
    try:
        app.run()
    finally:
        app.on_exit()


if __name__ == '__main__':
    main()

