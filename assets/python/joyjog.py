import sys
import time, datetime
import serial
import json
import ConfigParser
import logging
import ps3
from time import sleep
import re
from threading import Thread, Lock
from joyFunctions import FabJoyFunctions

shutdown = False

config = ConfigParser.ConfigParser()
config.read('/var/www/fabui/python/config.ini')


try:
      
    log_trace = str(sys.argv[1])  # param for the log file
    log_console = str(sys.argv[2])  # param for the log file

except:
    print("Missing params")
    sys.exit()
    

def trace(string):
    global log_trace
    out_file = open(log_trace, "a+")
    out_file.write(str(string) + "\n")
    out_file.close()
    # headless
    print string
    return


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getShutdown():
    return shutdown

class CarriagePosition():
    
    def __init__(self, logFile):
        self._rePosCode = re.compile('X:?(.?\d+\.?\d*)\s*Y:?(.?\d+\.?\d*)\s*Z:?(.?\d+\.?\d*)\s*')
        self.mut = Lock()
        self.position = (0, 0, 0)
        self.prependString = ''
        self.appendString = ''
        self.temperatureString = ''
        self.logFile = logFile
        self._console = None
        self._openLogFile()
        
    def _openLogFile(self):
        self._console = open(self.logFile, 'w')
    
    def _writeLogFile(self, string):
        if self._console == None:
            self._openLogFile()
         
        self._console.seek(0)
        self._console.write(string)
        self._console.truncate()
        self._console.flush()
        
    def closeLogFile(self):
        if not self._console == None:
            self._console.seek(0)
            self._console.truncate()
            self._console.close()
                  
    def setPrependString(self, string):
        self.prependString = string
        
    def setAppendString(self, string):
        self.appendString = string
        
    def setTemperatureString(self, string):
        self.temperatureString = string
    
    def setPostition(self, pos):
        self.mut.acquire()
        self.position = pos
        self.mut.release()
    
    def getPosition(self):
        return self.position
    
    def updatePosition(self, pos):
        self.mut.acquire()
        self.position = tuple(map(sum, zip(self.position, pos)))
        self.mut.release()
    
    def updateConsole(self):
        self.mut.acquire()
        pos = self.position
        self.mut.release()
        self._writeLogFile(self.prependString + self.temperatureString + '\nX%0.2f Y%0.2f Z%0.2f\n' % pos + self.appendString)
        
    def stringToPos(self, string):
        try:
            posGroup = self._rePosCode.search(string).groups()
            return (float(posGroup[0]), float(posGroup[1]), float(posGroup[2]))
#             self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1], self.pos[2] + pos[2])
        except:
            return (0.0, 0.0, 0.0)

class GcodeSerial(serial.Serial):
         
    def __init__(self, serial_port, serial_baud, timeout, shutdown):
        serial.Serial.__init__(self, serial_port, serial_baud, timeout=timeout)
        self.shutdown = shutdown
        self.received = 0
        self.sent = 0
        self.lastPositionReply = ''
        self.lastTemperatureReply = ''
        self.listenThread = Thread(target=self.listener)
        self.listenThread.setDaemon(True)
        self.listenThread.start()
        
        
    def write(self, data):
        while self.received<self.sent and self.sent>0 and not self.shutdown():
            pass #wait!
#         print 'Sent: %i, received: %i' % (self.sent, self.received)
#         console1.setAppendString('Sent: %i, received: %i' % (self.sent, self.received))
        self.sent += 1
        
        return serial.Serial.write(self, data)
    
    
    def listener(self):

        resend = 0
        
        serial_in=""    
        while not self.shutdown():
            
            while serial_in=="" and not self.shutdown():
                serial_in=self.readline().rstrip()
                #time.sleep(0.05)
                pass #wait!
#             print serial_in
            if serial_in=="ok":
                #print "received ok"
                self.received+=1
                #print "sent: "+str(sent) +" rec: " +str(received)
    
            ##error
            if serial_in[:6]=="Resend":
                #resend line
                resend=serial_in.split(":")[1].rstrip()
                self.received-=1 #lost a line!
#                 trace("Error: Line no "+str(resend) + " has not been received correctly")
                

            if serial_in[:4]=="ok T":
                #Collected M105: Get Extruder & bed Temperature (reply)
                #EXAMPLE:
                #ok T:219.7 /220.0 B:26.3 /0.0 T0:219.7 /220.0 @:35 B@:0
                #trace(serial_in);
                self.lastTemperatureReply = serial_in
                                
                self.received+=1
            
                ## temp report (wait)    
            if serial_in[:2]=="T:":    
                #collected M109/M190 Snnn temp (Set temp and  wait until reached)
                pass
                #ok is sent separately.
            
            if serial_in[:2]=="X:":    
                #collected M114
                self.lastPositionReply = serial_in
                #ok is sent separately.
            
        #clear everything not recognized.
            serial_in=""
        
    def getPositionReply(self):
        while self.received<self.sent and self.sent>0 and not self.shutdown():
            pass #wait!
        return self.lastPositionReply
    
    def getTemperatureString(self):
        ext_temp = 0
        bed_temp = 0
        ext_temp_target = 0
        bed_temp_target = 0
        while self.received<self.sent and self.sent>0 and not self.shutdown():
            pass #wait!
        if self.lastTemperatureReply != '':
            temps=self.lastTemperatureReply.split(" ")
                    
            if is_number(temps[1].split(":")[1]):
                ext_temp=float(temps[1].split(":")[1])
            if is_number(temps[2].split("/")[1]):
                ext_temp_target=float(temps[2].split("/")[1])
            #print ext_temp_target
            
            if is_number(temps[3].split(":")[1]):
                bed_temp=float(temps[3].split(":")[1])
            
            if is_number(temps[4].split("/")[1]):
                bed_temp_target=float(temps[4].split("/")[1])
                        
            return 'Ext Temp/Target: %0.0f/%0.0f | Bed Temp/Target: %0.0f/%0.0f' % (ext_temp, ext_temp_target, bed_temp, bed_temp_target)
        else:
            return ''
     
console1 = CarriagePosition(log_console)

try:
    js = ps3.Ps3Com()
except:
    console1.setPrependString('Joystick not found!\n')
    console1.updateConsole()
    sleep(1) 
    console1.closeLogFile()
    sys.exit()


# write_status(True)

'''#### SERIAL PORT COMMUNICATION ####'''
serial_port = config.get('serial', 'port')
serial_baud = config.get('serial', 'baud')

serialPort = GcodeSerial(serial_port, serial_baud, 0.5, getShutdown)
serialPort.flushInput()
serialPort.write("G91\r\n")

def consoleUpdater():
    while 1:
        if int(time.time()) % 5 == 0:
            serialPort.write("M105\r\n")
            console1.setTemperatureString(serialPort.getTemperatureString())
        console1.updateConsole()
        time.sleep(0.5)
        if shutdown:
            break
      
def jsControl():
    
    functions = FabJoyFunctions(serialPort, console1)
      
    while 1:
        try:
            status = js.getStatus()
        except:
            console1.setPrependString('Joystick disconnected!\n')
            break
            
    
        if status['ButtonCircle']:
            console1.setPrependString('Joystick Jog aborted\n')
            break
                             
        functions.callFunctions(status)

consoleThread = Thread(target=consoleUpdater)
consoleThread.setDaemon(True)
consoleThread.start()  

serialPort.write("M114\r\n")
console1.setPostition(console1.stringToPos(serialPort.getPositionReply()))


jsThread = Thread(target=jsControl)   
jsThread.setDaemon(True)
jsThread.start()       
  
console1.setPrependString('Ready for joystick jog!\n')

   

jsThread.join()
sleep(1)
shutdown = True
consoleThread.join()
# clean the buffer and leave
serialPort.flush()
serialPort.close()
console1.closeLogFile()
sys.exit()  
    
