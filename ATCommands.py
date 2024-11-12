import Constants

def GetVersion():

    buffer = bytearray(10)

    # header
    buffer[0] = Constants.PREFIX
    buffer[1] = Constants.CONNECTION_USB
    buffer[2] = 2 # payload length
    buffer[3] = Constants.TYPE_SILAB
    buffer[4] = Constants.RESERVE
    buffer[5] = Constants.LINK_DOWN
    buffer[6] = 0
    buffer[7] = 0

    # payload
    buffer[8] = 0xB0
    buffer[9] = 0x00

    return bytes(buffer)


def ResetAtmel():

    buffer = bytearray(10)

    # header
    buffer[0] = Constants.PREFIX
    buffer[1] = Constants.CONNECTION_USB
    buffer[2] = 2 # payload length
    buffer[3] = Constants.TYPE_SILAB
    buffer[4] = Constants.RESERVE
    buffer[5] = Constants.LINK_DOWN
    buffer[6] = 0
    buffer[7] = 0

    # payload
    buffer[8] = 0xB0
    buffer[9] = 0x0C

    return bytes(buffer)

def SendImageData(subpart_data, total_subpart, subpart, length):
    
    buffer = bytearray(248)

    # header
    buffer[0] = Constants.PREFIX
    buffer[1] = Constants.CONNECTION_USB
    buffer[2] = 240 #payload length
    buffer[3] = Constants.TYPE_SILAB
    buffer[4] = Constants.RESERVE
    buffer[5] = Constants.LINK_DOWN
    buffer[6] = 0
    buffer[7] = 0
    # payload
    buffer[8] = 0xB0
    buffer[9] = 0x01
    buffer[10] = (total_subpart >> 8) & 0xFF
    buffer[11] = total_subpart & 0xFF
    buffer[12] = (subpart >> 8) & 0xFF
    buffer[13] = subpart & 0xFF

    for i in range(0, length):
        buffer[i + 14] = subpart_data[i]

    for i in range(length, 234):
        buffer[i + 14] = 0xFF

    return bytes(buffer)