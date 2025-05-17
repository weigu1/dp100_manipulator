import hid

def list_hid_devices():
    """
    Lists all HID devices connected to the system.
    Prints the vendor ID, product ID, serial number, and manufacturer string of each device.
    """
    print("Listing all HID devices:")
    print("===============================================================")
    print("Vendor ID : Product ID : Serial Number : Manufacturer")
    print("===============================================================")
    for device_dict in hid.enumerate():
        vendor_id = device_dict.get("vendor_id", 0)
        product_id = device_dict.get("product_id", 0)
        serial_number = device_dict.get("serial_number", "N/A")
        manufacturer = device_dict.get("manufacturer_string", "N/A")
        path = device_dict.get("path", "N/A")
        print(f"{hex(vendor_id)} : {hex(product_id)} : {serial_number} : {manufacturer} : {path}")
    print()

def get_device_info():
    """ Sends a 64-byte field to a USB HID device and receives a 64-byte
        response with device infos. """
    vendor_id = 0x2e3c
    product_id = 0xaf01
    data_get_device_info = bytearray(64)
    data_get_device_info[0:6] = 0xfb, 0x10, 0x00, 0x00, 0x30, 0xc5
    device_info = {"name": None, "h_version": None, "s_version": None,
                   "boot_ver": None, "run area": None, "serial_number": None,
                   "year": None, "month": None, "day": None}
    try:
        device = hid.device()                       # Open the device
        device.open(vendor_id, product_id)
        device.write(data_get_device_info)          # Send the data
        response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
        if len(response) == 64 and response[0] == 0xFA and response[1] == 0x10 \
            and response[2] == 0x00 and response[3] == 0x28:
            print("Valid response received.")
            print(f"Response: {response}")
            name=""
            for i in range(4,20):
                if response[i] == 0x00:
                    break
                else:
                    name += chr(response[i])
            device_info["name"] = name
            device_info["s_version"] = (response[21]*255+response[20])/10
            device_info["h_version"] = (response[23]*255+response[22])/10
            device_info["boot_ver"] = (response[25]*255+response[24])/10
            device_info["run area"] = (response[27]*255+response[26])/10
            serial_number=""
            for i in range(36, 40):
                if response[i] < 16:
                    serial_number+="0"
                serial_number+=str(hex(response[i]))[2:]
            device_info["serial_number"] = serial_number
            device_info["year"] = response[41]*255+response[40]
            device_info["month"] = response[42]
            device_info["day"] = response[43]
            return device_info
        else:
            print("Invalid response received")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close the device
        device.close()
        print("Device closed.")

def get_basic_info():
    """ Sends a 64-byte field to a USB HID device and receives a 64-byte
        response with basic infos. """
    vendor_id = 0x2e3c
    product_id = 0xaf01
    data_get_basic_info = bytearray(64)
    data_get_basic_info[0:6] = 0xfb, 0x30, 0x00, 0x00, 0x31, 0x0f
    basic_info = {"vin": None, "vout": None, "iout": None,
                  "vo_max": None, "temp1": None, "temp2": None,
                  "dc_5v": None, "mode_out": None, "work_st": None}
    try:
        device = hid.device()                       # Open the device
        device.open(vendor_id, product_id)
        device.write(data_get_basic_info)          # Send the data
        response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
        if len(response) == 64 and response[0] == 0xFA and response[1] == 0x30 \
            and response[2] == 0x00 and response[3] == 0x10:
            print("Valid response received.")
            print(f"Response: {response}")
            basic_info["vin"] = (response[5]*255+response[4])/1000
            basic_info["vout"] = (response[7]*255+response[6])/1000
            basic_info["iout"] = (response[9]*255+response[8])/1000
            basic_info["vo_max"] = (response[11]*255+response[10])/1000
            basic_info["temp1"] = (response[13]*255+response[12])/10
            basic_info["temp2"] = (response[15]*255+response[14])/10
            basic_info["dc_5v"] = (response[17]*255+response[16])/1000
            basic_info["mode_out"] = response[18]
            basic_info["work_st"] = response[19]
            return basic_info
        else:
            print("Invalid response received")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close the device
        device.close()
        print("Device closed.")

def get_active_profile_info():
    """ Sends a 64-byte field to a USB HID device and receives a 64-byte
        response with parameter infos. """
    vendor_id = 0x2e3c
    product_id = 0xaf01
    data_get_parameter_info = bytearray(64)
    data_get_parameter_info[0:7] = 0xfb, 0x35, 0x00, 0x01, 0x80, 0xce, 0x28
    parameter_info = {"index": None, "state": None, "vo_set": None,
                      "io_set": None, "ovp_set": None, "ocp_set": None}
    try:
        device = hid.device()                       # Open the device
        device.open(vendor_id, product_id)
        device.write(data_get_parameter_info)          # Send the data
        response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
        if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35: \
            #and response[2] == 0x00 and response[3] == 0x0a:
            print("Valid response received.")
            print(f"Response: {response}")
            parameter_info["index"] = response[4] # actual profile
            parameter_info["state"] = response[5] # on/off
            parameter_info["vo_set"] = (response[7]*255+response[6])/1000
            parameter_info["io_set"] = (response[9]*255+response[8])/1000
            parameter_info["ovp_set"] = (response[11]*255+response[10])/1000 # vmax
            parameter_info["ocp_set"] = (response[13]*255+response[12])/1000 # imax
            return parameter_info
        else:
            print("Invalid response received")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close the device
        device.close()
        print("Device closed.")

def get_profiles():
    """ Get info about the 10 profiles. """
    vendor_id = 0x2e3c
    product_id = 0xaf01
    data_get_profile = bytearray(64)
    data_get_profile[0:7] = 0xfb, 0x35, 0x00, 0x01, 0x02, 0x4e, 0x49
    print(data_get_profile)
    profile_crc = []
    profile_crc.append((0xcf, 0x88))
    profile_crc.append((0x0e, 0x48))
    profile_crc.append((0x4e, 0x49))
    profile_crc.append((0x8f, 0x89))
    profile_crc.append((0xce, 0x4b))
    profile_crc.append((0x0f, 0x8b))
    profile_crc.append((0x4f, 0x8a))
    profile_crc.append((0x8e, 0x4a))
    profile_crc.append((0xce, 0x4e))
    profile_crc.append((0x0f, 0x8e))
    profiles = {}
    try:
        device = hid.device()                       # Open the device
        device.open(vendor_id, product_id)
        for i in range(10):
            data_get_profile[4] = i
            data_get_profile[5] = profile_crc[i][0]
            data_get_profile[6] = profile_crc[i][1]
            print(' '.join(format(x, '02x') for x in data_get_profile))
            device.write(data_get_profile)          # Send the data
            response = device.read(64, timeout_ms=5000) # Read the resp. 5s timeout
            if len(response) == 64 and response[0] == 0xFA and response[1] == 0x35 \
                and response[2] == 0x00 and response[3] == 0x0a:
                print("Valid response received.")
                print(f"Response: {response}")
                list = [(response[7]*255+response[6])/1000, (response[9]*255+response[8])/1000]
                #list = [response[4], response[5], (response[7]*255+response[6])/1000,
                #        (response[9]*255+response[8])/1000, (response[11]*255+response[10])/1000,
                #        (response[13]*255+response[12])/1000]
                profiles[i] = list
            else:
                print("Invalid response received")
                return None
        return profiles
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        # Close the device
        device.close()
        print("Device closed.")

# Example usage
#list_hid_devices()
#answer = get_device_info()
#print(answer)
#answer = get_basic_info()
#print(answer)
answer = get_active_profile_info()
print(answer)
answer = get_profiles()
print(answer)