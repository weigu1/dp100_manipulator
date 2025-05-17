#!/usr/bin/env python
#
# -*- coding: utf-8 -*-

""" Simple html/css homepage creator using markdown """
###############################################################################
#
#  dp100.py
#
#  Version 1.0 2025-05
#
#  Copyright 2025 weigu <weigu@weigu.lu>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
###############################################################################

import threading
import os

from time import gmtime, strftime, localtime, sleep
import queue
from dp100_gui import start_gui, GUI
from dp100_functions import DP100Functions

def main_loop(dp, flags_2_main, queue_2_main, queue_2_gui, queue_2_png):
    """Main loop for handling device communication and GUI updates"""
    try:
        dp.create_csv_file()
        while not flags_2_main["flag_exit"].is_set():  # Check the exit flag
            if flags_2_main["flag_connect"].is_set():
                dev = dp.get_device_info()
                print(f"device_info: {dev}")
                basic = dp.get_basic_info()
                print(f"basic_info: {basic}")
                profiles = dp.get_profiles()
                print(f"profiles: {profiles}")
                active_profile = dp.get_active_profile_info(True)
                print(f"get_active_profile_info: {active_profile}")
                flags_2_main["flag_connect"].clear()
            if flags_2_main["flag_get_basic_info"].is_set():
                basic = dp.get_basic_info()
                queue_2_png.put("CREATE_PNG") # Signal the PNG creation thread to generate a PNG
                queue_2_gui.put("PNG:\nplotted\n")
                # do not stop this by clearing the flag!
            if flags_2_main["flag_on_off"].is_set():
                dp.on_off()
                flags_2_main["flag_on_off"].clear()
            if flags_2_main["flag_change_profile"].is_set():
                dp.change_profile(int(change_profile[0]),
                                  float(change_profile[1]),
                                  float(change_profile[2]))
                profiles = dp.get_profiles()
                flags_2_main["flag_change_profile"].clear()
            if flags_2_main["flag_activate_profile"].is_set():
                dp.off()
                dp.activate_profile(int(activate_profile))
                active_profile = dp.get_active_profile_info(True)
                flags_2_main["flag_activate_profile"].clear()
            if flags_2_main["flag_reset_png"].is_set():
                dp.create_csv_file()
                flags_2_main["flag_reset_png"].clear()
            try:
                change_profile = ""
                activate_profile = ""
                message = queue_2_main.get_nowait()
                message = message.split('\n')
                print(f"Message from GUI: {message}")
                if message[0] == "change_profile:":
                    change_profile = message[1:4]
                    flags_2_main["flag_change_profile"].set()
                if message[0] == "activate_profile:":
                    activate_profile = message[1]
                    flags_2_main["flag_activate_profile"].set()
            except queue.Empty:
                pass
            sleep(1)  # Prevent busy-waiting
    except KeyboardInterrupt:
        print("Keyboard interrupt by user")
    print("Main loop terminated.")

def main():
    """Setup and start main loop"""
    print("Program started! Version 3.0 (2025)")
    flags_2_main = {"flag_connect": 0,
                    "flag_get_basic_info" : 1,
                    "flag_on_off" : 2,
                    "flag_change_profile" : 3,
                    "flag_activate_profile" : 4,
                    "flag_reset_png" : 5,
                    "flag_exit" : 6}
    for f in flags_2_main:
        flags_2_main[f] = threading.Event()

    queue_2_main = queue.Queue()  # Queue for communication from GUI to main_loop
    queue_2_gui = queue.Queue()   # Queue for communication from main_loop to GUI
    queue_2_png = queue.Queue()   # Queue for communication from main_loop to PNG creation thread

    dp = DP100Functions(queue_2_main, queue_2_gui, queue_2_png)

    # Create GUI, main loop, and PNG creation threads
    gui_thread = threading.Thread(target=start_gui, args=(flags_2_main, queue_2_main, queue_2_gui, dp.png_filename))
    main_thread = threading.Thread(target=main_loop, args=(dp, flags_2_main, queue_2_main, queue_2_gui, queue_2_png))
    png_thread = threading.Thread(target=dp.png_creation_thread)

    gui_thread.start()
    main_thread.start()
    png_thread.start()

    try:
        gui_thread.join()  # Wait for GUI thread to finish
    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")

    # Set the exit flag to stop the main loop and PNG thread
    flags_2_main["flag_exit"].set()
    dp.png_thread_exit_flag = True

    # Wait for the main loop and PNG threads to finish
    main_thread.join()
    png_thread.join()

    print("All threads terminated. Program exiting.")

if __name__ == '__main__':
    main()