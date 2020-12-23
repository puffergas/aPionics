from telnet import FlightGear
import sys
import piplates.TINKERplate as TINK
import time
import threading


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
# Functions
#-------------------

def int_apionics():
    """ Initialize the servos and define channels. """
    # Bank (roll_deg), channel 8, servo control, settle time
    TINK.setMODE(0,8,'servo')
    time.sleep(0.5)
    # Variometer, channel 1, servo control, settle time
    TINK.setMODE(0,1,'servo')
    time.sleep(0.5)
    # Fuel gauge, channel 2, servo control, settle time
    TINK.setMODE(0,2,'servo')
    time.sleep(0.5)

def snubber(deg_cal):
    """ Servo travel limit, gear saver. """
    if deg_cal > 180:
        deg_cal = 180
    if deg_cal < 0:
        deg_cal = 0
    return deg_cal


#-------------------
# Thread Functions
#-------------------

def art_hor_thread(fg_art_hor):     
    """ Artificial Horizon loop thread. """
    # 1/2 of an artificial horizon
    while True:
        # Read Variable
        roll_deg = fg_art_hor['/instrumentation/attitude-indicator/indicated-roll-deg']
        # Reverse and calibrate, FG is 45 0 -45, PiPlate is 0 180deg
        roll_deg_cal = 90.0 - roll_deg
        # Travel snubber
        roll_deg_cal = snubber(roll_deg_cal)
        TINK.setSERVO(0,8,roll_deg_cal)

def climb_thread(fg_climb):
    """ Climb Rate loop thread. """
    while True:
        # Read variable
        variometer = fg_climb['/instrumentation/vertical-speed-indicator/indicated-speed-fpm']
         # Variometer, climb rate
        variometer_deg_cal = 90.0 + (variometer * 0.0225)
        # Travel snubber
        variometer_deg_cal = snubber(variometer_deg_cal)
        TINK.setSERVO(0,1,variometer_deg_cal)

def slow_gauge(fg_slow):
    """ A place for slow changing instruments. """
    while True:
        # Fuel gauge
        fuel_gauge = fg_slow['/consumables/fuel/tank/level-gal_us']
        fuel_gauge_deg_cal = fuel_gauge * 0.9
        # Travel snubber
        fuel_gauge_deg_cal = snubber(fuel_gauge_deg_cal)
        TINK.setSERVO(0,2,fuel_gauge_deg_cal)


#-------------------
# Main function
#-------------------

def main():
    """ This is the core of aPionics. """
    print("\nWelcome to aPionics")
    time.sleep(3.0)

    print("Tring to connect to FlightGear")
    time.sleep(2.0)

    try:
        # fg_slow = FlightGear('localhost', 5401)
        fg_slow = FlightGear('192.168.42.7', 5401)
    except ConnectionRefusedError:
        print("Telnet Error; aPionics could not connect to FlightGear.")
        time.sleep(4.0)
        sys.exit()

    try:
        # fg_art_hor = FlightGear('localhost', 5401)
        fg_art_hor = FlightGear('192.168.42.7', 5402)
    except ConnectionRefusedError:
        print("Telnet Error; aPionics Artificial Horizon could not connect to FlightGear.")
        time.sleep(4.0)
        sys.exit()

    try:
        # fg_climb = FlightGear('localhost', 5401)
        fg_climb = FlightGear('192.168.42.7', 5403)
    except ConnectionRefusedError:
        print("Telnet Error; aPionics Climb Rate could not connect to FlightGear.")
        time.sleep(4.0)
        sys.exit()

    print("aPionics has connected to FlightGear")
    time.sleep(2.0)

    print("Initializing avionic instrumentation")
    int_apionics()
    print("Initialized")
    time.sleep(1.0)

    print("Linking your instrumentation")

    # Create treads
    ignition_art_hor_thread = threading.Thread(target=art_hor_thread, args=(fg_art_hor,), daemon=True)
    ignition_climb_thread = threading.Thread(target=climb_thread, args=(fg_climb,), daemon=True)
    ignition_slow_gauge = threading.Thread(target=slow_gauge, args=(fg_slow,), daemon=True)

    # Start treads
    ignition_art_hor_thread.start()
    ignition_climb_thread.start()
    ignition_slow_gauge.start()
    
    quit_apionics = input("Type e to exit this program: ")
    if quit_apionics == "e":
        print("Exiting")
        sys.exit()    


if __name__=="__main__":
    main()