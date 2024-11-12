import BTCommands
import ATCommands
import RFIDCommands
import USBSocket
import CRC
import HID
import utils
import Constants
import math

def GetBTVersion(handle):

    command = BTCommands.GetVersion()

    if not USBSocket.TransmitData(handle, command):
        print("Device failed to transmit data.")
        return ""

    if HID.GetNumHidDevices() > 0:
        status, buffer = USBSocket.ReceiveData(handle, 64, 2000)
        result = list(buffer)
        if status:
            if (result[2] == Constants.PREFIX) and (len(result) >= 15) and (result[10] == 0xC0) and (result[11] == 0x00):
                crc = (result[8] << 8) | result[9]

                if (crc != 0) and (not CRC.CheckCRC(result, 2, 13, crc)):  
                    print("Wrong CRC received")
                    return ""

                btVersion = "{}.{}.{}".format(result[12],result[13],result[14])
                return btVersion
        else:
            print("Cannot get bluetooth firmware version")
            return ""
    else:
        print("Device is not connected.")
        return ""

def GetAtmelVersion(handle):
    command = ATCommands.GetVersion()

    if not USBSocket.TransmitData(handle, command):
        print("Device failed to transmit data.")
        return False, ""
    
    if HID.GetNumHidDevices() > 0:
        status, buffer = USBSocket.ReceiveData(handle, 64, 1000)
        if status:
            if (buffer[2] == Constants.PREFIX) and (len(buffer) >= 15) and (buffer[10] == 0xB0) and (buffer[11] == 0x00):
                crc = (buffer[8] << 8) | buffer[9]

                atVersion = "{}.{}.{}".format(buffer[12],buffer[13],buffer[14])

                if buffer[12] == 0x00 and buffer[13] == 0x01:
                    return True, atVersion
                else: 
                    return False, atVersion
        else:
            print("Cannot get Atmel processor firmware version")
            return False, ""
    else:
        print("Device is not connected.")
        return False, ""

def UpdateBTImage(handle, stream):
    if len(stream) < 100000 or len(stream) > 150000:
        print("Incorrect image file size.")
        return False

    lengh = 0
    total_subpart = math.ceil(float(len(stream)) / 234)
    subpart = 0
    size = len(stream) - 2
    timeout = 1000
    subpartBuffer = bytearray(240)
    readBuffer = bytes(256)
    crc = bytes(2)
    bytesRead = 0
    command = bytes()
    prt = 0

    USBSocket.ReceiveData(readBuffer, len(readBuffer), 1000)

    while True:
        if subpart == 0:
            crc = stream[size:]
            subpartBuffer[0] = (size >> 24) & 0xFF
            subpartBuffer[1] = (size >> 16) & 0xFF
            subpartBuffer[2] = (size >> 8) & 0xFF
            subpartBuffer[3] = size & 0xFF
            subpartBuffer[4] = crc[0]
            subpartBuffer[5] = crc[1]

            command = BTCommands.SendImageData(subpartBuffer, total_subpart, 0, 6)
            prt = 0
        else:
            length = 234 if len(stream) - prt >= 234 else len(stream) - prt
            
            subpartBuffer = stream[prt:prt+length]
            prt += length
            command = BTCommands.SendImageData(subpartBuffer, total_subpart, subpart, length)

        if not USBSocket.TransmitData(handle, command):
            print("Device failed to transmit data.")
            return False

        if subpart == total_subpart:
            timeout = 5000
        else:
            timeout = 1000
        
        if HID.GetNumHidDevices() > 0:
            status, readBuffer = USBSocket.ReceiveData(handle, len(readBuffer), timeout)
            if status:
                if (readBuffer[2] == Constants.PREFIX) and (len(readBuffer) >= 13) and (readBuffer[10] == 0xC0) and (readBuffer[11] == 0x01):
                    if readBuffer[12] == 1:
                        print("")
                        return False
                    elif readBuffer[12] == 2:
                        print("\rCompleted:100.0%")
                        utils.WaitForSeconds(5)
                        print("")
                        return True
                    else:
                        print("\rCompleted: {0:3.1f}%".format((subpart * 100) / total_subpart), end="")
                        subpart+=1
                else:
                    continue
        else:
            print("Device is not connected.")
            return False 


def UpdateAtmelImage(handle, stream):
    if len(stream) < 350000 or len(stream) > 450000:
        print("Incorrect image file size.")
        return False

    lengh = 0
    total_subpart = math.ceil(float(len(stream)) / 234)
    subpart = 0
    size = len(stream) - 2
    timeout = 1000
    subpartBuffer = bytearray(240)
    readBuffer = bytes(256)
    crc = bytes(2)
    bytesRead = 0
    command = bytes()
    prt = 0

    USBSocket.ReceiveData(readBuffer, len(readBuffer), 1000)

    while True:
        if subpart == 0:
            crc = stream[size:]
            subpartBuffer[0] = (size >> 24) & 0xFF
            subpartBuffer[1] = (size >> 16) & 0xFF
            subpartBuffer[2] = (size >> 8) & 0xFF
            subpartBuffer[3] = size & 0xFF
            subpartBuffer[4] = crc[0]
            subpartBuffer[5] = crc[1]

            command = ATCommands.SendImageData(subpartBuffer, total_subpart, 0, 6)
            prt = 0
        else:
            length = 234 if len(stream) - prt >= 234 else len(stream) - prt
            
            subpartBuffer = stream[prt:prt+length]
            prt += length
            command = ATCommands.SendImageData(subpartBuffer, total_subpart, subpart, length)

        if not USBSocket.TransmitData(handle, command):
            print("Device failed to transmit data.")
            return False
        
        if HID.GetNumHidDevices() > 0:
            status, readBuffer = USBSocket.ReceiveData(handle, len(readBuffer), timeout)
            if status:
                if (readBuffer[2] == Constants.PREFIX) and (len(readBuffer) >= 13) and (readBuffer[10] == 0xB0) and (readBuffer[11] == 0x01):
                    if readBuffer[12] == 1:
                        print("")
                        return False
                    elif readBuffer[12] == 2:
                        print("\rCompleted:100.0%")
                        utils.WaitForSeconds(5)
                        print("")
                        return True
                    else:
                        print("\rCompleted: {0:3.1f}%".format((subpart * 100) / total_subpart), end="")
                        subpart+=1
                else:
                    continue
        else:
            print("Device is not connected.")
            return False 