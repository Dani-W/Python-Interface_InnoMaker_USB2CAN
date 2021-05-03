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
   Go to the list and add a new entry: 'interface name':         ('can.interface.can2usb',    'CAN2BUS')
   Instead of interface name you can insert any name you wish for the interface to have.
   For example a new interface with the name myInterface is added:
   
   BACKENDS = {
	# other interfaces...
	'myInterface':          ('can.interfaces.can2usb',          'CAN2BUS')
   }
