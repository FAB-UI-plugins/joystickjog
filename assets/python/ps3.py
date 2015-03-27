'''
Created on Mar 27, 2015

@author: tom
'''

import usb.core
import usb.util
import threading as th
import array

HID_GET_REPORT = 0x01
HID_SET_REPORT = 0x09
HID_REPORT_TYPE_INPUT = 0x01
HID_REPORT_TYPE_OUTPUT = 0x02

VID_SONY = 0x054c
PID_SIXAXIS = 0x0268


# This method sets the state of the LEDs and rumble motors on the Game Controller. Values are: */
LED1 = 0x01
LED2 = 0x02
LED3 = 0x04
LED4 = 0x08
RUMBLE_HIGH = 0x10
RUMBLE_LOW = 0x20

class Ps3Com(object):
    '''
    Read from ps3 sixaxis remote
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.device = self._connect()
        

    def _connect(self):
        
        dev = usb.core.find(idProduct=PID_SIXAXIS, idVendor=VID_SONY)
        if dev is None:
            raise ValueError('Device not found')
        try:
            dev.detach_kernel_driver(0)
        except: 
            pass
  
        dev.set_configuration(1)
 
        setup_command = [0x42, 0x0c, 0x00, 0x00]
        dev.ctrl_transfer(usb.ENDPOINT_OUT | (0x01 << 5) | usb.RECIP_INTERFACE,
                                        HID_SET_REPORT,
                                        0x03f4,
                                        0,
                                        setup_command,
                                        100)
        return dev

    def read(self):
        
        return self.device.read(0x81, 0x31, 0)
            
    def getStatus(self):
        byteArray = self.read()
        
        
        
    
    def set_led_and_rumble(self, param):
        control_packet = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x02, 0xFF, 0x27, 0x10, 0x10, 0x32, 0xFF,
                             0x27, 0x10, 0x00, 0x32, 0xFF, 0x27, 0x10, 0x00,
                             0x32, 0xFF, 0x27, 0x10, 0x00, 0x32, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        ''' LED settings '''
        control_packet[9] = (param & 0x0F) << 1
        '''/* Rumble settings */'''
        if(param & 0x30):
            control_packet[1] = control_packet[3] = 0xFE
            if(param & 0x10):  # //High rumble
                control_packet[4] = 0xFF
            else:  # //Low rumble
                control_packet[2] = 0xFF
            
        return self.device.ctrl_transfer(usb.ENDPOINT_OUT | (0x01 << 5) | usb.RECIP_INTERFACE,
                                        HID_SET_REPORT,
                                        0x0201,
                                        0,
                                        control_packet,
                                        100)

if __name__ == '__main__':
#     test = Ps3Com()
    a = array.array('B', (1,) * 0x31)
    print a
    
    
