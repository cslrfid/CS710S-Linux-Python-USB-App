import HID
import CS108FwUpgrade
import sys
import os
import utils

def main():
    
    handle = None
    print("----------------------------")
    print("CS710S Firmware Upgrade Toool")
    print("----------------------------")

    if (len(sys.argv) < 3) or (sys.argv[1].lower() != "/b" and sys.argv[1].lower() != "/n" and sys.argv[1].lower() != "/r"):
        print("Usage: python main.py [ /B | /N ] file")
        return
    
    if not os.path.exists(sys.argv[2]):
        print("File specificed ({}) not found".format(sys.argv[2]))
        return
    
    NumOfConnectedDevices = HID.GetNumHidDevices()
    print("Number of USB device(s) connected: ", NumOfConnectedDevices)
    for i in range(NumOfConnectedDevices):
        print("Device {}: {}".format(i, str(HID.GetHidString(i))))      
    
    if NumOfConnectedDevices != 0:
        handle = HID.Open()
    else:
        print("No CS710S device connected")
        return

    if sys.argv[1].lower() == "/b":
        isBLMode, atVersion=CS108FwUpgrade.GetAtmelVersion(handle)
        print("Current Atmel processor firmware version: {}".format(atVersion))
        btVersion=CS108FwUpgrade.GetBTVersion(handle)
        print("Current Bluetooth firmware version: {}".format(btVersion))

        if isBLMode:
            print("Reader is in bootloader mode.  Please update Atmel firmware before proceeding with Bluetooth firmware.")
            return

        fileName = sys.argv[2]
        print("\nUpgrade Bluetooth firmware with file:", fileName)
        in_file = open(fileName, "rb") # opening for [r]eading as [b]inary
        stream = in_file.read()
        in_file.close()

        if CS108FwUpgrade.UpdateBTImage(handle, stream):
            print("Bluetooth firmware upgrade successful.  Please reboot the reader.")
        else:
            print("Bluetooth firmware upgrade failed")
        
        HID.Close(handle)
    elif sys.argv[1].lower() == "/n":
        isBLMode, atVersion=CS108FwUpgrade.GetAtmelVersion(handle)
        print("Current Atmel processor firmware version: {}".format(atVersion))
        btVersion=CS108FwUpgrade.GetBTVersion(handle)
        print("Current Bluetooth firmware version: {}".format(btVersion))

        fileName = sys.argv[2]
        print("\nUpgrade Atmel processor firmware with file:", fileName)
        in_file = open(fileName, "rb") # opening for [r]eading as [b]inary
        stream = in_file.read()
        in_file.close()

        if CS108FwUpgrade.UpdateAtmelImage(handle, stream):
            print("Atmel processor firmware upgrade successful.  Please reboot the reader.")
        else:
            print("Atmel processor firmware upgrade failed")
        
        HID.Close(handle)
 
if __name__ == '__main__':
    main()