"""  DP100 functions """

import os
from time import sleep
import hid
import csv
from datetime import datetime
import matplotlib.pyplot as plt
plt.matplotlib.use('agg')

class DP100Functions:
    def __init__(self, queue_2_main, queue_2_gui, queue_2_png):
        """ Initialize the DP100Functions class with queues for communication. """
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
        self.queue_2_png = queue_2_png  # Correctly assign queue_2_png
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.script_dir)  # Set working directory to script's directory
        self.vendor_id = 0x2e3c
        self.product_id = 0xaf01
        self.csv_filename = "dp100_vi_data.csv"
        self.png_filename = "dp100_vi_data.png"
        self.png_width = 15,
        self.png_height = 5,
        self.max_voltage_axis = 10.0
        self.max_current_axis = 1.0
        self.png_thread_exit_flag = False  # Exit flag for the PNG thread

    def get_device_info(self):
        """ Sends a command field (64-byte) to the DP100 HID device
            and receives a 64-byte response with device infos. """
        data_get_device_info = bytearray(64)
        data_get_device_info[0:6] = 0xfb, 0x10, 0x00, 0x00, 0x30, 0xc5
        device_info = {"name": None, "h_version": None, "s_version": None,
                      "boot_ver": None, "run_area": None, "serial_number": None,
                      "year": None, "month": None, "day": None}
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            device.write(data_get_device_info)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x10 \
                and response[2] == 0x00 and response[3] == 0x28:
                name=""
                for i in range(4,20):
                    if response[i] == 0x00:
                        break
                    else:
                        name += chr(response[i])
                device_info["name"] = name
                device_info["h_version"] = (response[21]*255+response[20])/10
                device_info["s_version"] = (response[23]*255+response[22])/10
                device_info["boot_ver"] = (response[25]*255+response[24])/10
                device_info["run_area"] = (response[27]*255+response[26])/10
                serial_number=""
                for i in range(36, 40):
                    if response[i] < 16:
                        serial_number+="0"
                    serial_number+=str(hex(response[i]))[2:]
                device_info["serial_number"] = serial_number
                device_info["year"] = response[41]*255+response[40]
                device_info["month"] = response[42]
                device_info["day"] = response[43]
                #prepare info for GUI
                text = "Device_info:\n"
                text += "Name: " + str(device_info["name"]) + "\n"
                text += "Hardware version: " + str(device_info["h_version"]) + "\n"
                text += "Software version: " + str(device_info["s_version"]) + "\n"
                text += "Boot version: " + str(device_info["boot_ver"]) + "\n"
                text += "Run area: " + str(device_info["run_area"]) + "\n"
                text += "Serial number: " + str(device_info["serial_number"]) + "\n"
                text += "Year: " + str(device_info["year"]) + "\n"
                text += "Month: " + str(device_info["month"]) + "\n"
                text += "Day: " + str(device_info["day"]) + "\n"
                self.queue_2_gui.put(text)
                # create CSV file
                self.create_csv_file()
                return device_info
            else:
                print("Invalid response received")
                return None
        except Exception as e:
            print(f"Error: {e}")
            text = "Error:\n" + str(e) + "\n"
            self.queue_2_gui.put(text)
            return None
        finally:
            device.close()

    def get_basic_info(self):
        """ Sends a command field (64-byte) to the DP100 HID device
            and receives a 64-byte response with basic infos. """
        data_get_basic_info = bytearray(64)
        data_get_basic_info[0:6] = 0xfb, 0x30, 0x00, 0x00, 0x31, 0x0f
        basic_info = {"vin": None, "vout": None, "iout": None,
                      "vo_max": None, "temp1": None, "temp2": None,
                      "dc_5v": None, "mode_out": None, "work_st": None}
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            device.write(data_get_basic_info)           # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x30 \
                and response[2] == 0x00 and response[3] == 0x10:
                basic_info["vin"] = (response[5]*255+response[4])/1000
                basic_info["vout"] = (response[7]*255+response[6])/1000
                basic_info["iout"] = (response[9]*255+response[8])/1000
                basic_info["vo_max"] = (response[11]*255+response[10])/1000
                basic_info["temp1"] = (response[13]*255+response[12])/10
                basic_info["temp2"] = (response[15]*255+response[14])/10
                basic_info["dc_5v"] = (response[17]*255+response[16])/1000
                basic_info["mode_out"] = response[18]
                basic_info["work_st"] = response[19]
                text = "Basic_info:\n"  # Prepare info for GUI
                text += "Vin: " + str(basic_info["vin"]) + " V\n"
                text += "Vout: " + str(basic_info["vout"]) + " V\n"
                text += "Iout: " + str(basic_info["iout"]) + " A\n"
                text += "Vo_max: " + str(basic_info["vo_max"]) + " V\n"
                text += "Temp1: " + str(basic_info["temp1"]) + " °C\n"
                text += "Temp2: " + str(basic_info["temp2"]) + " °C\n"
                text += "DC 5V: " + str(basic_info["dc_5v"]) + " V\n"
                text += "Mode: " + str(basic_info["mode_out"]) + "\n"
                text += "Work state: " + str(basic_info["work_st"]) + "\n"
                self.queue_2_gui.put(text)
                current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                # Save vin, vout, and current time to a CSV file
                with open(self.csv_filename, mode="a") as file:
                    writer = csv.writer(file)
                    writer.writerow([current_time, basic_info["vout"], basic_info["iout"]])
                return basic_info
            else:
                print("Invalid response received")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def get_active_profile_info(self, flag_send_2_gui = False):
        """ Sends a command field (64-byte) to the DP100 HID device
            and receives a 64-byte response with infos about the active profile. """
        data_active_profile_info = bytearray(64)
        data_active_profile_info[0:7] = 0xfb, 0x35, 0x00, 0x01, 0x80, 0xce, 0x28
        parameter_info = {"index": None, "state": None, "vo_set": None,
                          "io_set": None, "ovp_set": None, "ocp_set": None}
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            device.write(data_active_profile_info)      # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                parameter_info["index"] = response[4]   # actual profile
                parameter_info["state"] = response[5]   # on/off
                parameter_info["vo_set"] = (response[7]*255+response[6])/1000
                parameter_info["io_set"] = (response[9]*255+response[8])/1000
                parameter_info["ovp_set"] = (response[11]*255+response[10])/1000 # vmax
                parameter_info["ocp_set"] = (response[13]*255+response[12])/1000 # imax
                self.max_voltage_axis = parameter_info["vo_set"] + parameter_info["vo_set"]/10
                self.max_current_axis = parameter_info["io_set"] + parameter_info["io_set"]/10
                if flag_send_2_gui:                #prepare info for GUI
                    text = "Active_profile:\n"
                    text += "Index: " + str(parameter_info["index"]) + "\n"
                    text += "State: " + str(parameter_info["state"]) + "\n"
                    text += "vo_set: " + str(parameter_info["vo_set"]) + "\n"
                    text += "io_set: " + str(parameter_info["io_set"]) + "\n"
                    self.queue_2_gui.put(text)
                return parameter_info
            else:
                print("Invalid response received")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def get_profiles(self):
        """ Get info about the 10 profiles. """
        data_get_profile = bytearray(64)
        data_get_profile[0:4] = 0xfb, 0x35, 0x00, 0x01
        profiles = {}
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            for i in range(10):
                data_get_profile[4] = i
                crc = self.modbus_crc(data_get_profile[0:5])
                data_get_profile[5] = crc[0]
                data_get_profile[6] = crc[1]
                #print(' '.join(format(x, '02x') for x in data_get_profile[0:10]))
                device.write(data_get_profile)          # Send the data
                response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
                if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                    and response[2] == 0x00 and response[3] == 0x0a:
                    list = [response[4], response[5], (response[7]*255+response[6])/1000,
                            (response[9]*255+response[8])/1000, (response[11]*255+response[10])/1000,
                            (response[13]*255+response[12])/1000]
                    profiles[i] = list
                else:
                    print("Invalid response received")
                    return None
            #prepare info for GUI
            text = "Profiles_info:\n"
            for i in range(10):
                text += "state_" + str(i) + ": " + str(profiles[i][1]) + "\n"
                text += "vo_set_" + str(i) + ": " + str(round(profiles[i][2]+0.05,1)) + " V\n"
                text += "io_set" + str(i) + ": " + str(round(profiles[i][3]+0.05,1)) + " A\n"
            self.queue_2_gui.put(text)
            return profiles
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def change_profile(self, nr, vo_set, io_set):
        """ Change one profile. """
        data_get_profile = bytearray(64)
        data_get_profile[0:4] = 0xfb, 0x35, 0x00, 0x01
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            data_get_profile[4] = nr
            crc = self.modbus_crc(data_get_profile[0:5])
            data_get_profile[5] = crc[0]
            data_get_profile[6] = crc[1]
            device.write(data_get_profile)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            #print(' '.join(format(x, '02x') for x in response[0:17]))
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                data_get_profile[1:15] = response[1:15]
                # changing bytes
                data_get_profile[4] = 0x40 + nr
                vo_set_b = [int(vo_set*1000)%256, int(vo_set*1000)//256]
                io_set_b = [int(io_set*1000)%256, int(io_set*1000)//256]
                data_get_profile[6:8] = vo_set_b
                data_get_profile[8:10] = io_set_b
                crc = self.modbus_crc(data_get_profile[0:14])
                data_get_profile[14] = crc[0]
                data_get_profile[15] = crc[1]
                device.write(data_get_profile)          # Send the data
                response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
                return response[4]
            else:
                print("Invalid response received")
                return None
            return response[4:14]
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def activate_profile(self, nr):
        """ Activate one profile. """
        data_get_profile = bytearray(64)
        data_get_profile[0:4] = 0xfb, 0x35, 0x00, 0x01
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            data_get_profile[4] = nr
            crc = self.modbus_crc(data_get_profile[0:5])
            data_get_profile[5] = crc[0]
            data_get_profile[6] = crc[1]
            device.write(data_get_profile)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            #print(' '.join(format(x, '02x') for x in response[0:17]))
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                data_get_profile[1:15] = response[1:15]
                # changing bytes
                data_get_profile[4] = 0xA0 + nr
                crc = self.modbus_crc(data_get_profile[0:14])
                data_get_profile[14] = crc[0]
                data_get_profile[15] = crc[1]
                device.write(data_get_profile)          # Send the data
                response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
                return response[4]
            else:
                print("Invalid response received")
                return None
            return response[4:14]
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def on_off(self):
        """ Switch on/off current profile"""
        answer = self.get_active_profile_info()
        nr = answer["index"]
        state = answer["state"]
        data_get_profile = bytearray(64)
        data_get_profile[0:4] = 0xfb, 0x35, 0x00, 0x01
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            data_get_profile[4] = nr
            crc = self.modbus_crc(data_get_profile[0:5])
            data_get_profile[5] = crc[0]
            data_get_profile[6] = crc[1]
            device.write(data_get_profile)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            #print(' '.join(format(x, '02x') for x in response[0:17]))
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                data_get_profile[1:15] = response[1:15]
                # changing bytes
                data_get_profile[4] = 0x20 + nr  # 0x20 to switch
                if state: # if on
                    data_get_profile[5] = 0x00 # switch off
                    #print("we switch off")
                else:
                    data_get_profile[5] = 0x01 # switch on
                    #print("switch on")
                crc = self.modbus_crc(data_get_profile[0:14])
                data_get_profile[14] = crc[0]
                data_get_profile[15] = crc[1]
                #print(' '.join(format(x, '02x') for x in data_get_profile[0:17]))
                device.write(data_get_profile)          # Send the data
                response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
                if response[4] == 1:    #prepare info for GUI
                    text = "On_off:\n"
                    text += "State: " + str(not state) + "\n"
                    self.queue_2_gui.put(text)
                return response[4]
            else:
                print("Invalid response received")
                return None
            return response[4:14]
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def off(self):
        """ Switch off current profile"""
        answer = self.get_active_profile_info()
        nr = answer["index"]
        state = answer["state"]
        data_get_profile = bytearray(64)
        data_get_profile[0:4] = 0xfb, 0x35, 0x00, 0x01
        try:
            device = hid.device()                       # Open the device
            device.open(self.vendor_id, self.product_id)
            data_get_profile[4] = nr
            crc = self.modbus_crc(data_get_profile[0:5])
            data_get_profile[5] = crc[0]
            data_get_profile[6] = crc[1]
            device.write(data_get_profile)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            #print(' '.join(format(x, '02x') for x in response[0:17]))
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                data_get_profile[1:15] = response[1:15]
                # changing bytes
                data_get_profile[4] = 0x20 + nr  # 0x20 to switch
                data_get_profile[5] = 0x00 # switch off
                #print("we switch off")
                crc = self.modbus_crc(data_get_profile[0:14])
                data_get_profile[14] = crc[0]
                data_get_profile[15] = crc[1]
                #print(' '.join(format(x, '02x') for x in data_get_profile[0:17]))
                device.write(data_get_profile)          # Send the data
                response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
                if response[4] == 1:    #prepare info for GUI
                    text = "On_off:\n"
                    text += "State: " + str(not state) + "\n"
                    self.queue_2_gui.put(text)
                return response[4]
            else:
                print("Invalid response received")
                return None
            return response[4:14]
        except Exception as e:
            print(f"Error: {e}")
            return None
        finally:
            device.close()

    def modbus_crc(self, buf):
        """ Calculate modbus crc from a list. LB first!
            from here: https://github.com/raphaelnunes67/MODBUS-CRC16 """
        crc = 0xFFFF
        for i in range(len(buf)):
            crc ^= buf[i]
            for bit in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc%256, crc//256

    def create_png_from_csv(self, csv_filename, png_filename):
        """ Reads data from a CSV file and creates a PNG file with a plot of vout and iout over time. """
        png_width = 15,
        png_height = 5,
        timestamps = []
        vout_values = []
        iout_values = []
        try:  # Read data from the CSV file
            with open(csv_filename, mode="r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 3:
                        continue  # Skip rows with insufficient data
                    try:
                        timestamps.append(datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S"))
                        vout_values.append(float(row[1]))
                        iout_values.append(float(row[2]))
                    except ValueError:
                        continue  # Skip rows with invalid data
        except FileNotFoundError:
            print(f"Error: File '{csv_filename}' not found.")
            return

        # Create the plot
        plt.figure(figsize=(15, 5))

        # Plot Vout on the primary y-axis
        ax1 = plt.gca()  # Get the current axes
        ax1.plot(timestamps, vout_values, label="Vout (V)", color="blue", marker="x")
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Voltage (V)", color="blue")
        ax1.tick_params(axis="y", labelcolor="blue")
        ax1.grid(True)
        ax1.set_ylim(0, self.max_voltage_axis)  # Set y-axis limits for voltage

        # Create a secondary y-axis for Iout
        ax2 = ax1.twinx()
        ax2.plot(timestamps, iout_values, label="Iout (A)", color="red", marker="o")
        ax2.set_ylabel("Current (A)", color="red")
        ax2.tick_params(axis="y", labelcolor="red")
        ax2.set_ylim(0, self.max_current_axis)  # Set y-axis limits for current

        # Add a title and legend
        plt.title("Vout and Iout Over Time")
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")

        # Save the plot as a PNG file
        plt.tight_layout()
        plt.savefig(png_filename) # Save the plot as a PNG file
        plt.close()
        #print(f"Plot saved as '{png_filename}'")
        #prepare info for GUI
        text = "PNG:\n"
        text += "plotted\n"
        self.queue_2_gui.put(text)

    def png_creation_thread(self):
        """Thread-safe wrapper for creating PNG files."""
        print("PNG creation thread started.")
        while not self.png_thread_exit_flag:
            try:
                # Check if there is a message in the queue
                if not self.queue_2_png.empty():
                    message = self.queue_2_png.get_nowait()
                    #print(f"PNG thread received message: {message}")
                    if message == "CREATE_PNG":
                        #print("Generating PNG...")
                        self.create_png_from_csv(self.csv_filename, self.png_filename)
                        #print("PNG generated successfully.")
            except Exception as e:
                print(f"Error in PNG creation thread: {e}")
            sleep(1)  # Prevent busy-waiting
        print("PNG creation thread exiting.")

    def create_csv_file(self):
        with open(self.csv_filename, mode="w",newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Vout (V)", "Iout (A)"])



#answer = change_profile(2,4.3,0.5, True)
