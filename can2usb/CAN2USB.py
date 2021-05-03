from ctypes import *
import sys
import os
import time
import struct
import clr
from can import BusABC, Message, CanError




#Finding the Path of the DLL
str1=os.path.realpath(__file__)
str1=str1.replace("CAN2USB.py","InnoMakerUsb2CanLib.dll")
#print(os.path.realpath(__file__))                  # For Debug Purposes. Should print out the correct path
#print(str1)
clr.AddReference(str1)
from InnoMakerUsb2CanLib import *


class CAN2BUS(BusABC):
    Device = InnoMakerDevice()
    bus = UsbCan()

    # bus.removeDeviceDelegate = bus.RemoveDeviceNotifyDelegate()
    # bus.addDeviceDelegate = bus.AddDeviceNotifyDelegate()

    #initiates the CAN2BUS module and starts searching for a hardware module to connect to
    def __init__(self, channel, can_filters=None, poll_interval=0.01,
                 receive_own_messages=False,
                 bitrate=None, rx_queue_size=1, app_name="CAN2USB",
                 serial=None, fd=False, data_bitrate=None, sjwAbr=0, tseg1Abr=0,
                 tseg2Abr=0, sjwDbr=0, tseg1Dbr=0, tseg2Dbr=0, **kwargs):
        canmode = "normal"
        self.bus.scanInnoMakerDevices() #search for devices connected to USB
        self.buffer = bytearray(20)
        if self.bus.getInnoMakerDeviceCount() > 0:
            self.channel_info = 'CAN2USB'
            for i in range(0, self.bus.getInnoMakerDeviceCount()): #todo: should work for more than one CAN2USB but not tested yet
                self.Device.deviceId = self.bus.getInnoMakerDevice(i).deviceId
                self.Device.InnoMakerDev = self.bus.getInnoMakerDevice(i).InnoMakerDev
                self.Device.usbReg = self.bus.getInnoMakerDevice(i).usbReg
                print("Device Number " + str(i) + " has the deviceID " + self.bus.getInnoMakerDevice(i).deviceId)
                self.connect(bitrate, canmode)
            super(CAN2BUS, self).__init__(channel=channel, **kwargs)
        else:
            #if no hardware CAN2USB was found
            print('No Device found')

    #The update-function can be used to start a new search for hardware modules
    def update(self):
        self.bus.scanInnoMakerDevices()
        if self.bus.getInnoMakerDeviceCount() > 0:
            for i in range(0, self.bus.getInnoMakerDeviceCount()):
                self.Device.deviceId = self.bus.getInnoMakerDevice(i).deviceId
                self.Device.InnoMakerDev = self.bus.getInnoMakerDevice(i).InnoMakerDev
                self.Device.usbReg = self.bus.getInnoMakerDevice(i).usbReg
                # print("Device Number " + str(i) + " has the deviceID " + self.bus.getInnoMakerDevice(i).deviceId)
        else:
            print('No Device connected')

    # The connect-function enables the connection between the CAN2USB device and the software
    # It also sends the predefined configurations to the CAN2USB device
    def connect(self, bitrate, canmode):
        switchbus = {
            "normal": CAN2BUS.bus.UsbCanMode.UsbCanModeNormal,
            "loopback": CAN2BUS.bus.UsbCanMode.UsbCanModeLoopback,
            "ListenOnly": CAN2BUS.bus.UsbCanMode.UsbCanModeListenOnly
        }
        usbCanMode = switchbus.get(canmode, 4)
        if usbCanMode == 4:
            print("usbCanMode invalid")
        else:

            switchrate = {
                20000: Baud20K,
                33330: Baud33K,
                40000: Baud40K,
                50000: Baud50K,
                66660: Baud66K,
                80000: Baud80K,
                83330: Baud83K,
                100000: Baud100K,
                125000: Baud125K,
                200000: Baud200K,
                250000: Baud250K,
                400000: Baud400K,
                500000: Baud500K,
                666000: Baud666K,
                800000: Baud800K,
                1000000: Baud1M
            }
            bittiming = switchrate.get(bitrate, 0)
            bittiming = bittiming()
            if bittiming == 0:
                print("bitrate invalid")
            else:
                try:
                    self.bus.UrbSetupDevice(self.Device, usbCanMode, bittiming)
                    self.bus.openInnoMakerDevice(self.Device)
                    print("Successfully Connected")
                except Exception:
                    print("Connection failed")

    #shutsdown the device but does NOT reset the internal memory of the device
    def shutdown(self):
        try:
            self.bus.UrbResetDevice(self.Device)
            self.bus.closeInnoMakerDevice(self.Device)
            print("Successfully Disconnected")
        except Exception:
            print("Disconnection failed")

    @staticmethod
    def _detect_available_configs():
        configs = [{'interface': 'can2usb',
                    'app_name': None,
                    'channel': 0}]
        return configs

    #receive function for CAN messages. Also converts the format of the CAN2USB frame into the predefined format of python-can
    def _recv_internal(self, timeout):
        self._is_filtered = False
        end_time = time.time() + timeout if timeout is not None else None
        try:
            recvdata = self.readData()
        except Exception:
            print("Receive unsuccessful")
            return None, self._is_filtered

        if recvdata == 0:
            # print("Receive unsuccessful")
            return None, self._is_filtered
        else:
            frameID = (recvdata[7] << 24) + (recvdata[6] << 16) + (recvdata[5] << 8) + (recvdata[4])
            # print("frameID: " + str(frameID))
            dlc = recvdata[8]
            data = [0, 0, 0, 0, 0, 0, 0, 0]
            for j in range(12, 12 + dlc):
                data[j - 12] = recvdata[j]
                # print("Data: " + str(data[j-12]))
            if recvdata[7] == 32:
                self.errorHandling(self,frameID, data)
            msg = Message(
                # timestamp= timestamp - self._time_offset,
                arbitration_id=frameID,
                dlc=dlc,
                data=data
            )
            return msg, self._is_filtered

    # readData gets the messages out of the buffer of the CAN2USB device
    def readData(self):
        myclasstype = clr.System.Type.GetType("InnoMakerUsb2CanLib.UsbCan, InnoMakerUsb2CanLib")
        method = myclasstype.GetMethod("getInnoMakerDeviceBuf")
        buffer = clr.System.Array.CreateInstance(clr.System.Byte, 20)
        parameters = clr.System.Array[clr.System.Object]([self.Device, buffer, 20])
        device = UsbCan()
        result = method.Invoke(device, parameters)
        readdata = parameters[1]

        if result:
            if readdata[1] == 0 and readdata[2] == 0 and readdata[3] == 0:  # fängt wiederhallende Signale von Send ab
                return 0
            else:
                # print("read data successful")
                # for i in range (0, 20):
                #    print(readdata[i])
                return readdata
        else:
            # print("read data failed")
            return 0

    # send function
    def send(self, msg, timeout=None):
        frame = self.buildDataFrame(msg.arbitration_id, msg.dlc, msg.data)
        result = CAN2BUS.bus.sendInnoMakerDeviceBuf(self.Device, frame, 20)
        if result:
            print("send data successful")
        else:
            print("send data failed")

    # buildDataFrame is used to convert the python-can frame to the format the CAN2USB devices is expecting
    @staticmethod
    def buildDataFrame(frameID, length, data):
        frame = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        buffer = struct.pack('H', frameID)
        # dbuffer = struct.pack('>Q', data) # only if data is not already in byte-format

        frame[4] = buffer[0]
        frame[5] = buffer[1]
        frame[8] = length
        for i in range(12, 12 + length):
            frame[i] = data[i - 12]
        # print(frame)
        return frame

    #todo: AddDeviceNotifyDelegate is included in the DLL of Innomaker but the purpose is not yet clear
    def AddDeviceNotifyDelegate(self):
        if self.Device is not None:
            self.shutdown()
            # self.Device = None
        CAN2BUS.bus.scanInnoMakerDevices()
        self.update()

    # todo: RemoveDeviceNotifyDelegate is included in the DLL of Innomaker but the purpose is not yet clear
    def RemoveDeviceNotifyDelegate(self):
        if self.Device is not None:
            self.shutdown()
            # self.Device = None
        CAN2BUS.bus.scanInnoMakerDevices()
        self.update()

    #The errorHandling function is called in case something went wrong during the send or receive functions
    # It prints out the respecting error with a short explanation on the terminal
    @staticmethod
    def errorHandling(self, frameID, data):
        la = 0  # lost arbitration
        cp = 0  # controller problems
        pv = 0  # protocol violations
        ts = 0  # transceiver status
        print('')
        print('Error code was detected:')
        buffer = frameID & 0x1
        if buffer != 0:
            print('TX timeout (by netdevice driver')
        buffer = frameID & 0x2
        if buffer != 0:
            la = 1
        buffer = frameID & 0x4
        if buffer != 0:
            cp = 1
        buffer = frameID & 0x8
        if buffer != 0:
            pv = 1
        buffer = frameID & 0x10
        if buffer != 0:
            ts = 1
        buffer = frameID & 0x20
        if buffer != 0:
            print('received no ACK on transmission')
        buffer = frameID & 0x40
        if buffer != 0:
            print('bus off')
        buffer = frameID & 0x80
        if buffer != 0:
            print('bus error (may flood!)')
        buffer = frameID & 0x100
        if buffer != 0:
            print('controller restarted')

        # lookup for lost arbitration
        if la == 1:
            print('lost arbitration occurred in bit number: ', end='')
            if data[0] == 0:
                print('unspecified')
            else:
                print(data[0])

        # lookup for controller problems
        if cp == 1:
            print('controller problem occurred: ')
            if data[1] == 0:
                print('unspecified')
            else:
                buffer = data[1] & 0x1
                if buffer != 0:
                    print('   RX buffer overflow')
                buffer = data[1] & 0x2
                if buffer != 0:
                    print('   TX buffer overflow')
                buffer = data[1] & 0x4
                if buffer != 0:
                    print('   reached warning level for RX errors')
                buffer = data[1] & 0x8
                if buffer != 0:
                    print('   reached warning level for TX errors')
                buffer = data[1] & 0x10
                if buffer != 0:
                    print('   reached error passive status RX')
                buffer = data[1] & 0x20
                if buffer != 0:
                    print('   reached error passive status TX')
                buffer = data[1] & 0x40
                if buffer != 0:
                    print('   recovered error active state')

        # lookup for protocol error
        if pv == 1:
            print('protocol error occurred: ')
            if data[2] == 0:
                print('unspecified')
            else:
                buffer = data[2] & 0x1
                if buffer != 0:
                    print('   single bit error')
                buffer = data[2] & 0x2
                if buffer != 0:
                    print('   frame format error')
                buffer = data[2] & 0x4
                if buffer != 0:
                    print('   bit stuffing error')
                buffer = data[2] & 0x8
                if buffer != 0:
                    print('   unable to send dominant bit')
                buffer = data[2] & 0x10
                if buffer != 0:
                    print('   unable to send recessive bit')
                buffer = data[2] & 0x20
                if buffer != 0:
                    print('   bus overload')
                buffer = data[2] & 0x40
                if buffer != 0:
                    print('   active error announcement')
                buffer = data[2] & 0x80
                if buffer != 0:
                    print('   error occurred on transmission')

            print('location of protocol error: ')
            if data[3] == 0:
                print('unspecified')
            else:
                buffer = data[3] & 0x3
                if buffer != 0:
                    print('   start of frame')
                buffer = data[3] & 0x2
                if buffer != 0:
                    print('   ID bits 28 - 21 (SFF: 10 - 3)')
                buffer = data[3] & 0x6
                if buffer != 0:
                    print('   ID bits 20 - 18 (SFF: 2 - 0)')
                buffer = data[3] & 0x4
                if buffer != 0:
                    print('   substitute RTR (SFF: RTR)')
                buffer = data[3] & 0x7
                if buffer != 0:
                    print('   ID bits 17 - 13')
                    buffer = data[3] & 0xF
                    if buffer != 0:
                        print('   ID bits 12 - 5')
                buffer = data[3] & 0xE
                if buffer != 0:
                    print('   ID bits 4 - 0')
                buffer = data[3] & 0xC
                if buffer != 0:
                    print('   RTR')
                buffer = data[3] & 0xD
                if buffer != 0:
                    print('   reserved bit 1')
                buffer = data[3] & 0x9
                if buffer != 0:
                    print('   reserved bit 0')
                buffer = data[3] & 0xB
                if buffer != 0:
                    print('   data length code')
                buffer = data[3] & 0xA
                if buffer != 0:
                    print('   data section')
                buffer = data[3] & 0x8
                if buffer != 0:
                    print('   CRC sequence')
                buffer = data[3] & 0x18
                if buffer != 0:
                    print('   CRC delimiter')
                buffer = data[3] & 0x19
                if buffer != 0:
                    print('   ACK slot')
                buffer = data[3] & 0x1B
                if buffer != 0:
                    print('   ACK delimiter')
                buffer = data[3] & 0x1A
                if buffer != 0:
                    print('   end of frame')
                buffer = data[3] & 0x12
                if buffer != 0:
                    print('   intermission')

        # lookup for CAN-transceiver status problems
        if ts == 1:
            print('transceiver status error occurred: ')
            if data[1] == 0:
                print('unspecified')
            else:
                print('   CANH CANL')
                buffer = data[4] & 0x1
                if buffer != 0:
                    print('   0000 0000')
                buffer = data[4] & 0x4
                if buffer != 0:
                    print('   0000 0100')
                buffer = data[4] & 0x5
                if buffer != 0:
                    print('   0000 0101')
                buffer = data[4] & 0x6
                if buffer != 0:
                    print('   0000 0110')
                buffer = data[4] & 0x7
                if buffer != 0:
                    print('   0000 0111')
                buffer = data[4] & 0x40
                if buffer != 0:
                    print('   0100 0000')
                buffer = data[4] & 0x50
                if buffer != 0:
                    print('   0101 0000')
                buffer = data[4] & 0x60
                if buffer != 0:
                    print('   0110 0000')
                buffer = data[4] & 0x70
                if buffer != 0:
                    print('   0111 0000')
                buffer = data[4] & 0x80
                if buffer != 0:
                    print('   1000 0000')
        print('Warning frame was:')


# The below functions predefine the values of the timing registers of the CAN2USB device
#Note: The values of the different baudrates are the adjusted values from Innomaker for the CAN2USB
#      and should not be altered unless the user has a full understanding of the funcionality of the bittiming registers.
#      A wrong configuration can lead to the device not being able to send or receive messages.

def Baud20K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 150
    return bittiming


def Baud33K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 1
    bittiming.sjw = 1
    bittiming.brp = 180
    return bittiming


def Baud40K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 60
    return bittiming


def Baud50K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 60
    return bittiming


def Baud66K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 1
    bittiming.sjw = 1
    bittiming.brp = 90
    return bittiming


def Baud80K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 1
    bittiming.sjw = 1
    bittiming.brp = 75
    return bittiming


def Baud83K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 1
    bittiming.sjw = 1
    bittiming.brp = 72
    return bittiming


def Baud100K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 30
    return bittiming


def Baud125K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 24
    return bittiming


def Baud200K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 15
    return bittiming


def Baud250K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 12
    return bittiming


def Baud400K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 1
    bittiming.sjw = 1
    bittiming.brp = 15
    return bittiming


def Baud500K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 6
    bittiming.phase_seg1 = 7
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 6
    return bittiming


def Baud666K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 3
    bittiming.phase_seg1 = 3
    bittiming.phase_seg2 = 2
    bittiming.sjw = 1
    bittiming.brp = 8
    return bittiming


def Baud800K():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 7
    bittiming.phase_seg1 = 8
    bittiming.phase_seg2 = 4
    bittiming.sjw = 1
    bittiming.brp = 3
    return bittiming


def Baud1M():
    bittiming = CAN2BUS.bus.innomaker_device_bittming()
    bittiming.prop_seg = 5
    bittiming.phase_seg1 = 6
    bittiming.phase_seg2 = 4
    bittiming.sjw = 1
    bittiming.brp = 3
    return bittiming
