import can

if __name__ == "__main__":
    # declare interface
    can.rc['interface'] = 'InnoMaker'
    can.rc['channel'] = 0
    can.rc['bitrate'] = 500000
    bus = can.ThreadSafeBus()

    # create a message
    daten = 100
    message = can.Message(arbitration_id=1, dlc=1, is_fd=False, is_extended_id=False, data=daten.to_bytes(1, 'big'))
    # send the message
    bus.send(message)

    # listen on the bus for a message
    while 1:
        recv = bus.recv(0.001)  # get received msg
        if recv is not None:
            print('[INFO -> Input] {}'.format(recv))



