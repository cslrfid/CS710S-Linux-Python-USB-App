import time
from datetime import datetime
import HID
import BTCommands
import Constants

def TransmitData(handle, buffer):
    success = False
    
    if (HID.GetNumHidDevices() > 0):
        try:
            success = HID.TransmitData(handle, buffer)
            
        except Exception as err:
            print(f"USBSocket: Transmission error {err=}, {type(err)=}")
            success = False
    
    return success

    
def ReceiveData(handle, bufferSize, timeout):
    success = False

    try:
        bytesRead = 0
        timer = time.monotonic()
        while bytesRead == 0:
            success, result = HID.ReceiveData(handle, bufferSize, timeout)
            bytesRead = len(result)
            timeElapsed = (time.monotonic() - timer) * 1000 
            if (not success) or (timeElapsed > timeout):
                # print("USBSocket: recive timeout")
                success = False
                break
            time.sleep(Constants.TIMER_READ * 0.001)
    except Exception as err:
        print(f"USBSocket: unexpected {err=}, {type(err)=}")
    
    return success, result

