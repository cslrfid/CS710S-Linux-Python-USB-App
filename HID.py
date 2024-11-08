import ctypes
import hid
import BTCommands

# USB Parameters
# VID = 0x10C4
# PID = 0x8468
VID = 0x03EB
PID = 0x2678
HID_READ_TIMEOUT = 0
HID_WRITE_TIMEOUT = 1000

# HID Report IDs
ID_IN_CONTROL = 0xFE
ID_OUT_CONTROL = 0xFD
ID_IN_DATA = 0x01
ID_OUT_DATA = 0x02

# HID Report Sizes
SIZE_IN_CONTROL = 5
SIZE_OUT_CONTROL = 5
SIZE_IN_DATA = 64
SIZE_OUT_DATA = 64
SIZE_MAX_WRITE = 62
SIZE_MAX_READ = 62

# Return Codes
HID_DEVICE_SUCCESS = 0x00
HID_DEVICE_NOT_FOUND = 0x01
HID_DEVICE_NOT_OPENED = 0x02
HID_DEVICE_ALREADY_OPENED = 0x03
HID_DEVICE_TRANSFER_TIMEOUT = 0x04
HID_DEVICE_TRANSFER_FAILED = 0x05
HID_DEVICE_CANNOT_GET_HID_INFO = 0x06
HID_DEVICE_HANDLE_ERROR = 0x07
HID_DEVICE_INVALID_BUFFER_SIZE = 0x08
HID_DEVICE_SYSTEM_CODE = 0x09
HID_DEVICE_UNSUPPORTED_FUNCTION = 0x0A
HID_DEVICE_UNKNOWN_ERROR = 0xFF

# String Types
HID_VID_STRING = 0x01
HID_PID_STRING = 0x02
HID_PATH_STRING = 0x03
HID_SERIAL_STRING = 0x04
HID_MANUFACTURER_STRING = 0x05
HID_PRODUCT_STRING = 0x06
MAX_PATH_LENGTH = 260

MAX_REPORT_REQUEST_XP = 512

_mod = ctypes.cdll.LoadLibrary('libslabhiddevice.so')

HidDevice_GetNumHidDevices = _mod.HidDevice_GetNumHidDevices
HidDevice_GetNumHidDevices.argtypes = (ctypes.c_int, ctypes.c_int)
HidDevice_GetNumHidDevices.restype = ctypes.c_int

HidDevice_GetMaxReportRequest = _mod.HidDevice_GetMaxReportRequest
HidDevice_GetMaxReportRequest.argtypes = (ctypes.c_void_p,)
HidDevice_GetMaxReportRequest.restype = ctypes.c_int

HidDevice_GetHidString = _mod.HidDevice_GetHidString
HidDevice_GetHidString.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_byte, ctypes.c_char_p, ctypes.c_int)
HidDevice_GetHidString.restype = ctypes.c_byte

HidDevice_GetString = _mod.HidDevice_GetString
HidDevice_GetString.argtypes = (ctypes.c_void_p, ctypes.c_byte, ctypes.c_int)
HidDevice_GetString.restype = ctypes.c_byte

HidDevice_Open = _mod.HidDevice_Open
HidDevice_Open.argtypes = (ctypes.POINTER(ctypes.c_void_p), ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int)
HidDevice_Open.restype = ctypes.c_byte

HidDevice_SetTimeouts = _mod.HidDevice_SetTimeouts
HidDevice_SetTimeouts.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_int)
HidDevice_SetTimeouts.restype = None

HidDevice_Close = _mod.HidDevice_Close
HidDevice_Close.argtypes = (ctypes.c_void_p,)
HidDevice_Close.restype = ctypes.c_int

HidDevice_IsOpened = _mod.HidDevice_IsOpened
HidDevice_IsOpened.argtypes = (ctypes.c_void_p,)
HidDevice_IsOpened.restype = ctypes.c_bool

HidDevice_SetOutputReport_Interrupt = _mod.HidDevice_SetOutputReport_Interrupt
HidDevice_SetOutputReport_Interrupt.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int)
HidDevice_SetOutputReport_Interrupt.restype = ctypes.c_byte 

HidDevice_GetInputReport_Interrupt = _mod.HidDevice_GetInputReport_Interrupt
HidDevice_GetInputReport_Interrupt.argtypes = (ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
HidDevice_GetInputReport_Interrupt.restype = ctypes.c_byte 

HidDevice_GetOutputReportBufferLength = _mod.HidDevice_GetOutputReportBufferLength
HidDevice_GetOutputReportBufferLength.argtypes = (ctypes.c_void_p,)
HidDevice_GetOutputReportBufferLength.restype = ctypes.c_int16


def GetNumHidDevices():
    return len(hid.enumerate(VID, PID))

def GetMaxReportRequest(device):
    return HidDevice_GetMaxReportRequest(device)

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
    return handle

def Close(handle):
    handle.close()
    return True

def IsOpen(handle):
    hdl = ctypes.c_void_p(handle)
    return HidDevice_IsOpened(hdl)

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

def ReceiveData(handle, bufferSize):
    try:
        success = False
        buffer = bytearray(bufferSize)
        buffer = handle.read(bufferSize)
        success = True
    except Exception as err:
        success = False
    
    return success, bytes(buffer)




def main():
    # Module unit testing
    handle = 0

    NumOfConnectedDevices = GetNumHidDevices()
    print("CS710S USB library loaded: ", _mod)
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