import hid
import BTCommands

# USB Parameters
VID = 0x03EB
PID = 0x2678

# HID Report IDs
ID_IN_DATA = 0x01
ID_OUT_DATA = 0x02

# HID Report Sizes
SIZE_IN_DATA = 64
SIZE_OUT_DATA = 64
SIZE_MAX_WRITE = 62
SIZE_MAX_READ = 62

def GetNumHidDevices():
    return len(hid.enumerate(VID, PID))

def GetMaxReportRequest(device):
    return SIZE_OUT_DATA

def GetHidString(deviceIndex):
    count = 0
    for device in hid.enumerate(VID, PID):
        if count == deviceIndex:
            return device["path"]
        else:
            count += 1
    return ""

def Open():
    handle = hid.Device(VID, PID)
    handle.read(64, 500)
    return handle

def Close(handle):
    handle.close()
    return True

def IsOpen(handle):
    return True

def TransmitData(handle, buffer):
    
    success = False
    reportSize = SIZE_OUT_DATA
    report = bytes(reportSize)
    
    bytesWritten = 0
    bytesToWrite = len(buffer)


    while bytesWritten < bytesToWrite:
        transferSize = min(bytesToWrite - bytesWritten, SIZE_MAX_WRITE)
        report = bytearray(reportSize)
        report[0] = ID_OUT_DATA
        report[1] = transferSize
        report[2:2+transferSize] = buffer[bytesWritten:bytesWritten+transferSize]
        sent = handle.write(bytes(report))
        
        if sent != len(report):
            success = False
            break

        bytesWritten += transferSize

    # Write completed successfully
    if bytesWritten == bytesToWrite:    
        success = True
		        
    return success

def ReceiveData(handle, bufferSize, timeout):
    try:
        success = False
        buffer = bytearray(bufferSize)
        buffer = handle.read(bufferSize, timeout)
        success = True
    except Exception as err:
        success = False
    
    return success, bytes(buffer)




def main():
    # Module unit testing
    handle = 0

    NumOfConnectedDevices = GetNumHidDevices()
    print("CS710S USB library loaded")
    print("Number of USB device(s) connected: ", NumOfConnectedDevices)
    for i in range(NumOfConnectedDevices):
        print("Device {}: HIDString={}".format(i, GetHidString(i)))      
    
    if NumOfConnectedDevices > 0:
        handle = Open(0)
        if handle != None:
            print("Device 0 opened: {}".format(handle))
        else:
            print("Unable to open device 0")
            return
    
        print("Get BT firmware version")
        command = BTCommands.GetVersion()

        if not TransmitData(handle, command):
            print("Device failed to transmit data.")
        else:
            bufferSize = GetMaxReportRequest(handle) * SIZE_MAX_READ
            status, result = ReceiveData(handle, bufferSize)
            if not status:
                print("Device failed to receive data.")
                return
            else:
                print("Received Data: {}".format(result.hex().upper()))

        if Close(handle):
            print("Device 0 closed")
        else:
            print("Unable to close device 0")

if __name__ == '__main__':
        main()