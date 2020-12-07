import PySimpleGUI as sg
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


sg.theme('SystemDefault')


try:
    # fg = FlightGear('localhost', 5401)
    fg = FlightGear('192.168.42.7', 5401)
except ConnectionRefusedError:
    sg.popup_error('Opps', 'Looks like you started PiStack before FlightGear'
    ' or did not configure FlightGear - PiStack will exit.', font=(any, 14))
    sys.exit()


# Value, (double)
# roll_deg = fg['/instrumentation/attitude-indicator/indicated-roll-deg']
# variometer = fg['/instrumentation/vertical-speed-indicator/indicated-speed-fpm']


reply = sg.popup_ok_cancel('Do you wish to continue?', font=(any, 14))
print(reply)

if reply == 'Cancel':
    sys.exit()


# Bank (roll_deg), channel 8, servo control, settle time
TINK.setMODE(0,8,'servo')
time.sleep(1.0)

# Variometer, channel 7, servo control, settle time
TINK.setMODE(0,1,'servo')
time.sleep(1.0)

# Fuel gauge
TINK.setMODE(0,2,'servo')
time.sleep(1.0)


#loop forever
while(True):
    # Horizon, 1/2
    roll_deg = fg['/instrumentation/attitude-indicator/indicated-roll-deg']
    #print(roll_deg)
    
    # Reverse and calibrate, FG is 45 0 -45, PiPlate is 0 180deg
    roll_deg_cal = 90.0 - roll_deg

    # Travel snubber
    if roll_deg_cal > 180:
        roll_deg_cal = 180
    if roll_deg_cal < 0:
        roll_deg_cal = 0

    TINK.setSERVO(0,8,roll_deg_cal)
    time.sleep(0.2)


    # Variometer, climb rate
    variometer = fg['/instrumentation/vertical-speed-indicator/indicated-speed-fpm']
    #print(variometer)
    
    variometer_deg_cal = 90 + (variometer * 0.045)

    # Travel snubber
    if variometer_deg_cal > 180:
        variometer_deg_cal = 180
    if variometer_deg_cal < 0:
        variometer_deg_cal = 0

    TINK.setSERVO(0,1,variometer_deg_cal)
    time.sleep(0.2)

    # Fuel gauge
    fuel_gauge = fg['/consumables/fuel/tank/level-gal_us']
    print(fuel_gauge)
    
    fuel_gauge_deg_cal = fuel_gauge * 0.9

    # Travel snubber
    if fuel_gauge_deg_cal > 180:
        fuel_gauge_deg_cal = 180
    if fuel_gauge_deg_cal < 0:
        fuel_gauge_deg_cal = 0

    TINK.setSERVO(0,2,fuel_gauge_deg_cal)
    time.sleep(0.2)