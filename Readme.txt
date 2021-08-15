Name: Software for CAN2USB-Converter
Author: Daniel Wetzel
Year: 2021

Description:
This Python-Script allows the usage of the CAN2USB-Converter from Innomaker on Windows.
It was designed to be used in combination with python-can.
It can also be used without python-can but must then be modified to suit the indiviual use case.


How to install (for python-can):
1. Locate the interfaces folder of the installed python-can module on your device.
2. Copy the can2usb folder from this repository into the interface folder.
3. Make sure the CAN2USB.py and the two dll are located inside that folder.
4. Go back to the interfaces folder and locate the __init__.py (NOT the __init__.py inside the can2usb folder!)
5. If you open the file there should be a list called BACKENDS. This list contains three parameter: 
   the name of the interface, the folder where it is located and the name of the class.
   Go to the list and add a new entry: 'interface name':         ('can.interface.can2usb',    'InnoMakerBus')
   Instead of interface name you can insert any name you wish for the interface to have.
   For example a new interface with the name myInterface is added:
   
   BACKENDS = {
	# other interfaces...
	'myInterface':          ('can.interfaces.can2usb',          'InnoMakerBus')
   }

How to use:
After the successfull installation of the module you should be able to use CAN2USB devices in combination with python-can.
Inside the Testprogramm folder is a short program that demonstrates the usage of CAN2USB with python can.
It contains three Python files.
If the TastaturTest.py is run CAN-messages can be send by pressing 1 or 2 on the keyboard.
When messages are send or received the associated frames are printed out on the terminal.

The can_lib.py contains a class canLib that creates a Threadsafe Bus with a send-thread and a receive thread. 
It also creates two queues from CommunicationList.py to create a buffer for the send-messages and the receive-messages.
Furthermore it contains all vital functions you need to use the CAN2USB-interface with the python-can overlay.

The CommunicationList.py contains a queue and the necessary functions for the queue to work.

The converters.py is contains functions to convert different datatypes.