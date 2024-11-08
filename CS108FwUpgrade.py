import BTCommands
import SLCommands
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

def GetSLVersion(handle):

    command = RFIDCommands.PowerOn(True)

    if not USBSocket.TransmitData(handle, command):
        print("Device failed to transmit data.")
        return ""

    if HID.IsOpen(handle):
        USBSocket.ReceiveData(handle, 128, 2000)
    else:
        print("Device is not connected.")
        return ""

    command = SLCommands.GetVersion()

    if not USBSocket.TransmitData(handle, command):
        print("Device failed to transmit data.")
        return ""
    
    if HID.IsOpen(handle):
        status, buffer = USBSocket.ReceiveData(handle, 128, 1000)
        if status:
            if (buffer[0] == Constants.PREFIX) and (len(buffer) >= 13) and (buffer[8] == 0xB0) and (buffer[9] == 0x00):
                crc = (buffer[6] << 8) | buffer[7]

                slVersion = "{}.{}.{}".format(buffer[10],buffer[11],buffer[12])
                return slVersion
        else:
            print("Cannot get Silicon Labs (network processor) firmware version")
            return ""
    else:
        print("Device is not connected.")
        return ""

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
                        utils.WaitForSeconds(15)
                        print("")
                        return True
                    else:
                        print("\rCompleted: {0:3.1f}%".format((subpart * 100) / total_subpart), end="")
                        subpart+=1
        else:
            print("Device is not connected.")
            return False 



    """ while True:
        if retry == 0:
            if len(stream) >=64:
                subpartBuffer = stream[0:64]
                stream = stream[64:]
            else:
                subpartBuffer = stream[0:]
                stream = stream[0:]

        if len(subpartBuffer) > 0:
            command = BTCommands.SendImageData(subpartBuffer, subpart)
        else:
            print("Not enough image data.")
            return False

        if not USBSocket.TransmitData(command):
            print("Device failed to transmit data.")
            return False

        if HID.IsOpen(handle):
            readBuffer = bytes(128)
            status, readBuffer = USBSocket.ReceiveData(handle, len(readBuffer), 5000)
            if status:
                if (readBuffer[0] == Constants.PREFIX) and (len(readBuffer) >= 11) and (readBuffer[8] == 0xC0) and (readBuffer[9] == 0x01):
                    if readBuffer[10] == 1:
                        print("")
                        return False
                    elif readBuffer[10] == 2:
                        print("\rCompleted:100.0%")
                        utils.WaitForSeconds(15)
                        print("")
                        return True
                    else:
                        print("\rCompleted: {0:3.1f}%".format((subpart * 100) / Constants.BT_IMAGE_TOTAL_SUBPART), end="")
                        subpart+=1
                        retry = 0
                else:
                    retry+=1
            else:
                retry+=1
        else:
            print("Device is not connected.")
            return False """


def UpdateSilabImage(handle, stream):
    if len(stream) != Constants.SILAB_IMAGE_SIZE:
        print("Incorrect image file size.")
        return False

    subpart = 1
    subpartBuffer = bytes(114)
    command = bytes()
    retry = 0

    while True:
        if retry == 0:
            if len(stream) >= 114:
                subpartBuffer = stream[0:114]
                stream = stream[114:]
            else:
                subpartBuffer = stream[0:]
                stream = stream[0:]
        if len(subpartBuffer) > 0:
            command = SLCommands.SendImageData(subpartBuffer, subpart)
        else:
            print("Not enough image data.")
            return False

        if not USBSocket.TransmitData(handle, command):
            print("Device failed to transmit data.")
            return False

        if HID.IsOpen(handle):
            readBuffer = bytes(128)
            status, readBuffer = USBSocket.ReceiveData(handle, len(readBuffer), 1000)
            if status:
                if (readBuffer[0] == Constants.PREFIX) and (len(readBuffer) >= 11) and (readBuffer[8] == 0xB0) and (readBuffer[9] == 0x01):
                    if readBuffer[10] == 1:
                        print("")
                        return False
                    elif readBuffer[10] == 2:
                        print("\rCompleted:100.0%")
                        utils.WaitForSeconds(15)
                        print("")
                        return True
                    else:
                        print("\rCompleted: {0:3.1f}%".format((subpart * 100) / Constants.SILAB_IMAGE_TOTAL_SUBPART), end="")
                        subpart+=1
                        retry = 0
                else:
                    retry+=1
            else:
                retry+=1
        else:
            print("Device is not connected.")
            return False        