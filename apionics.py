from telnet import FlightGear
import sys
import piplates.TINKERplate as TINK
import time


# aPionics, a remote mechanical avionics package for FlightGear
# Copyright (C) 2020 Jeffrey Davis <jeff@puffergas.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330,
# Boston, MA 02111-1307 USA


#-------------------
# Variables
#-------------------

active = True


#-------------------
# Functions
#-------------------

def int_apionics():
    """ Initialize the servos and define channels. """
    # Bank (roll_deg), channel 8, servo control, settle time
    TINK.setMODE(0,8,'servo')
    time.sleep(1.0)
    # Variometer, channel 1, servo control, settle time
    TINK.setMODE(0,1,'servo')
    time.sleep(1.0)
    # Fuel gauge, channel 2, servo control, settle time
    TINK.setMODE(0,2,'servo')
    time.sleep(1.0)

def snubber(deg_cal):
    """ Servo travel limit, gear saver. """
    if deg_cal > 180:
        deg_cal = 180
    if deg_cal < 0:
        deg_cal = 0
    return deg_cal


def run_apionics():     
    """ Forever loop that runs aPionics. """
    # 1/2 of an artificial horizon
    # Reverse and calibrate, FG is 45 0 -45, PiPlate is 0 180deg
    roll_deg_cal = 90.0 - roll_deg
    # Travel snubber
    roll_deg_cal = snubber(roll_deg_cal)
    TINK.setSERVO(0,8,roll_deg_cal)


    # Variometer, climb rate
    variometer_deg_cal = 90 + (variometer * 0.045)
    # Travel snubber
    variometer_deg_cal = snubber(variometer_deg_cal)
    TINK.setSERVO(0,1,variometer_deg_cal)

    # Fuel gauge
    fuel_gauge_deg_cal = fuel_gauge * 0.9
    # Travel snubber
    fuel_gauge_deg_cal = snubber(fuel_gauge_deg_cal)
    TINK.setSERVO(0,2,fuel_gauge_deg_cal)


#-------------------
# Core
#-------------------

print("\nWelcome to aPionics")
time.sleep(3.0)

print("Tring to connect to FlightGear")
time.sleep(2.0)

try:
    # fg = FlightGear('localhost', 5401)
    fg = FlightGear('192.168.42.7', 5401)
except ConnectionRefusedError:
    print("Telnet Error; aPionics could not connect to FlightGear.")
    time.sleep(4.0)
    sys.exit()

print("aPionics has connected to FlightGear")
time.sleep(2.0)

print("Initializing avionic istrumentation")
int_apionics()
print("Initialized")
time.sleep(1.0)

print("Linking your instrumentation")

while active:
    # Read Variables
    roll_deg = fg['/instrumentation/attitude-indicator/indicated-roll-deg']
    variometer = fg['/instrumentation/vertical-speed-indicator/indicated-speed-fpm']
    fuel_gauge = fg['/consumables/fuel/tank/level-gal_us']
    
    run_apionics()
