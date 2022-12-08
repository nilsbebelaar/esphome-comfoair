import serial
COM_PORT = 'COM3'

startBytes = bytearray([0x07, 0xF0])
stopBytes = bytearray([0x07, 0x0F])
AckBytes = bytearray([0x07, 0xF3])

level = 0
comfort_temp = 12
level_preset_0_in = 0
level_preset_0_out = 0
level_preset_1_in = 40
level_preset_1_out = 40
level_preset_2_in = 80
level_preset_2_out = 80
level_preset_3_in = 100
level_preset_3_out = 100


def main():
    ser = serial.Serial(COM_PORT, timeout=1)
    while True:
        while not ser.inWaiting():
            continue
        buffer = ser.read_until(expected=stopBytes)
        if buffer[0:2] == startBytes:
            command = buffer[2:4]
            n_bytes = int(buffer[4])
            data = buffer[5:5+n_bytes]
            checksum = buffer[5+n_bytes]
            valid = calcChecksum(buffer[2:-3]) == checksum
            # print(f"\ncommand: {command} | data: {data} | checksum: {checksum} | valid: {valid}")

            if valid:
                ser.write(AckBytes)
                responseCommand, responseData, sendResponse = genResponse(command, data)
                if sendResponse:
                    response = bytearray([*responseCommand, len(responseData), *responseData])
                    checksum = calcChecksum(response)
                    response = bytearray([*startBytes, *response, checksum, *stopBytes])
                    # print(response)
                    ser.write(response)
            else:
                print('Invalid data checksum')

    ser.close()


def genResponse(command, data):
    global level
    global comfort_temp
    global level_preset_0_in
    global level_preset_0_out
    global level_preset_1_in
    global level_preset_1_out
    global level_preset_2_in
    global level_preset_2_out
    global level_preset_3_in
    global level_preset_3_out
    command = command[0]*256+command[1]
    resCommand = bytearray(2)
    resData = bytearray(0)
    sendResponse = True
    match command:
        case 0x0067:  # Bootloader Version Read
            resCommand = bytearray([0x00, 0x68])
            resData = bytearray([0x05, 0x10, 0x50, 0x43, 0x41, 0x33, 0x35, 0x30, 0x20, 0x6C, 0x75, 0x78, 0x65])
        case 0x0069:  # Firmware Version Read
            resCommand = bytearray([0x00, 0x6A])
            resData = bytearray([0x03, 0x14, 0x20, 0x43, 0x41, 0x33, 0x35, 0x30, 0x20, 0x6C, 0x75, 0x78, 0x65])
        case 0x00A1:  # Connector Board Version Read
            resCommand = bytearray([0x00, 0xA2])
            resData = bytearray([0x03, 0x14, 0x20, 0x43, 0x41, 0x33, 0x35, 0x30, 0x20, 0x6C, 0x75, 0b01101001, 0x00])
        case 0x0003:  # Input Read
            resCommand = bytearray([0x00, 0x04])
            resData = bytearray([0x02, 0x10])
        case 0x000B:  # Ventilator Status Read
            resCommand = bytearray([0x00, 0x0C])
            resData = bytearray([55, 78, *int(1875000/1650).to_bytes(2), *int(1875000/1320).to_bytes(2)])
        case 0x000D:  # Valve Status Read
            resCommand = bytearray([0x00, 0x0E])
            resData = bytearray([10, 0, 30, 40])
        case 0x000F:  # Temperature Status Read
            resCommand = bytearray([0x00, 0x10])
            resData = bytearray([int((11+20)*2), int((18+20)*2), int((15+20)*2), int((13+20)*2)])
        case 0x0011:  # Button Status Read
            resCommand = bytearray([0x00, 0x12])
            resData = bytearray([0x00])
        case 0x00CD:  # Ventilation Levels Read
            resCommand = bytearray([0x00, 0xCE])
            resData = bytearray([level_preset_0_out,
                                 level_preset_1_out,
                                 level_preset_2_out,
                                 level_preset_0_in,
                                 level_preset_1_in,
                                 level_preset_2_in,
                                 80,
                                 80,
                                 level,
                                 1,
                                 level_preset_3_out,
                                 level_preset_3_in,
                                 0,
                                 0])
        case 0x00D1:  # Temperatures Read
            resCommand = bytearray([0x00, 0xD2])
            resData = bytearray([int((comfort_temp+20)*2), int((11+20)*2), int((18+20)*2), int((15+20)*2), int((13+20)*2), 0b00001111, 0, 0, 0])
        case 0x00D5:  # Status Read
            resCommand = bytearray([0x00, 0xD6])
            resData = bytearray([0, 1, 1, 2, 0b00000000, 0x00, 0x00, 0x00, 0x00, 0, 0])
        case 0x00D9:  # Malfunctions Read
            resCommand = bytearray([0x00, 0xDA])
            resData = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])
        case 0x00DD:  # Operating Hours Read
            resCommand = bytearray([0x00, 0xDE])
            resData = bytearray([*int(20).to_bytes(3), *int(1000).to_bytes(3), *int(3000).to_bytes(3), *int(10).to_bytes(3),
                                *int(0).to_bytes(3), *int(50).to_bytes(3), *int(4000).to_bytes(3), *int(2000).to_bytes(3)])
        case 0x00DF:  # Bypass Status Read
            resCommand = bytearray([0x00, 0xE0])
            resData = bytearray([0x00, 0x00, 1, 3, 5, 0x00, 1])
        case 0x00E1:  # Preheat Status Read
            resCommand = bytearray([0x00, 0xE2])
            resData = bytearray([2, 0, 0, *int(60).to_bytes(2), 1])
        case 0x0099:  # Ventilation Level Set
            level = int(data[0])
            print(f'Setting Ventilation Level to {hex(level)}')
            sendResponse = False
        case 0x00CF:  # Ventilation Presets Set
            level_preset_0_out = data[0]
            level_preset_0_in = data[3]
            level_preset_1_out = data[1]
            level_preset_1_in = data[4]
            level_preset_2_out = data[2]
            level_preset_2_in = data[5]
            level_preset_3_out = data[6]
            level_preset_3_in = data[7]
            print(f'Setting Level 0 exhaust %: {data[0]}')
            print(f'Setting Level 0 intake %:  {data[3]}')
            print(f'Setting Level 1 exhaust %: {data[1]}')
            print(f'Setting Level 1 intake %:  {data[4]}')
            print(f'Setting Level 2 exhaust %: {data[2]}')
            print(f'Setting Level 2 intake %:  {data[5]}')
            print(f'Setting Level 3 exhaust %: {data[6]}')
            print(f'Setting Level 3 intake %:  {data[7]}')
            sendResponse = False
        case 0x00D3:  # Temperature Set
            comfort_temp = int(data[0])/2-20
            print(f'Setting Comfort Temperature to {comfort_temp}')
            sendResponse = False

    return resCommand, resData, sendResponse


def calcChecksum(dataBuffer):
    checksum = 173
    skipByte = False

    for byte in dataBuffer:
        if byte == 0x07:
            if skipByte:
                continue
            else:
                skipByte = True
        checksum += byte
    return checksum % 256


if __name__ == '__main__':
    main()
