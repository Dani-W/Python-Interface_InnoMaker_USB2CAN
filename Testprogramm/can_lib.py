import time
import can
from threading import Thread
# import own Libs
import CommunicationList
import converters as conv
from datetime import datetime


class canLib:
    # declare interface
    can.rc['interface'] = 'InnoMaker'
    can.rc['channel'] = 0
    can.rc['bitrate'] = 500000

    canRunning = False
    send_msg = None
    bus = None
    recv_msg = None
    callback = None
    callbackavailable = False
    console = False  # for information output in console

    # CAN Type-ID's length for standard CAN
    CAN_id_length = 11

    def __init__(self, returnObj=None, console=False):
        """
        initializes communication and starts the various processes in threads
        :return: None
        """
        try:
            self.bus = can.ThreadSafeBus()
            self.canRunning = True
        except Exception:
            print('Error initializing CAN-Interface')

        # intitialize send and receive list
        self.send_msg = CommunicationList.CommunicationList()
        self.recv_msg = CommunicationList.CommunicationList()

        # initialize and start Threads
        self.receive = Thread(target=self.receiveCAN, args=())
        self.send = Thread(target=self.sendCAN, args=())
        self.send.start()
        self.receive.start()

        # check for callbackobject with which i can call the callbackfunctions
        if returnObj is None:
            self.callbackavailable = False
        else:
            self.callback = returnObj
            self.callbackavailable = True
        self.console = console

    def receiveCAN(self):  # receive function
        """
        Thread for regular retrieval of receive data from the FIFO of the interface. Data is added to the recv_msg list
        :return: none
        """
        while 1:
            if self.canRunning:
                recv = self.bus.recv(0.001)  # get received msg
                if recv is not None:
                    self.recv_msg.put(recv.arbitration_id, recv.dlc, recv.data, False, datetime.now())
                    print('[INFO -> Input] {}'.format(recv))  # for testing, prints data which are send

    def add_msg(self, type_id, dlc, data):
        self.send_msg.put(type_id, dlc, data, True, True, datetime.now())  # add to send list

    def sendCAN(self):
        """
        Thread takes messages from the message list, converts them and sends them on the bus.
        :return: None
        """
        while True:
            time.sleep(0.001)
            if self.canRunning:
                if not self.send_msg.empty():
                    # Get the Message from the Queue
                    try:
                        id, dlc, mymsg = self.send_msg.get()
                    except:
                        pass
                    finally:
                        # build Message
                        if id is None:  # elements are None if no msg in list or msg is in list but have to wait a
                            pass  # second
                        else:
                            canid = int(conv.conv_bitarr_to_string(id), 2)  # convert ID to right TxID format
                            send = conv.conv_int_to_bytes(mymsg, dlc)  # convert data in Bytes to send
                            # create can message
                            msg = can.Message(arbitration_id=canid, dlc=dlc, is_fd=False, is_extended_id=False, data=send)
                            try:
                                self.bus.send(msg)  # send can message

                                print('[INFO -> Output] {}'.format(msg))

                            except Exception:
                                print('[ERROR] sendCAN Senden fehlgeschlagen')
                                # self.canRunning = False

    def shutdown(self):
        self.bus.shutdown()  # closes the connection with the device
