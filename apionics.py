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
    fg = FlightGear('localhost', 5401)
    # fg = FlightGear('192.168.42.9', 5401)
except ConnectionRefusedError:
    sg.popup_error('Opps', 'Looks like you started PiStack before FlightGear'
    ' or did not configure FlightGear - PiStack will exit.', font=(any, 14))
    sys.exit()


# Value, (double)
ver_sp = fg['/instrumentation/vertical-speed-indicator/indicated-speed-fpm']
roll_deg = fg['/instrumentation/attitude-indicator/indicated-roll-deg']





reply = sg.popup_ok_cancel('Do you wish to continue?', font=(any, 14))
print(reply)

if reply == 'Cancel':
    sys.exit()


TINK.setMODE(0,8,'servo')   #Set channel 8 to servo control
time.sleep(1.0)             #Give servo time to settle
TINK.setSERVO(0,8,45.0)      #Move servo to 0 degrees
time.sleep(1.0)             #Give servo time to move


#loop forever
while(True):
    roll_deg = fg['/instrumentation/attitude-indicator/indicated-roll-deg']
    print(roll_deg)
    
    # Reverse and calibrate, FG is 45 0 -45, PiPlate is 0 180deg
    if roll_deg >= 0.0:
        roll_deg_cal = 90.0 - roll_deg
    if roll_deg < 0.0:
        roll_deg_cal = abs(roll_deg + -90.0)
    
#    roll_deg_cal = roll_deg + 45.0
    
    # Travel snubber
    if roll_deg_cal > 180:
        roll_deg_cal = 180
    if roll_deg_cal < 0:
        roll_deg = 0

    TINK.setSERVO(0,8,roll_deg_cal)
    time.sleep(0.2)
