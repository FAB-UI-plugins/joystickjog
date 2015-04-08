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

shutdown = False

config = ConfigParser.ConfigParser()
config.read('/var/www/fabui/python/config.ini')

macro_status = config.get('macro', 'status_file')

try:
      
    log_trace = str(sys.argv[1])  # param for the log file
    log_console = str(sys.argv[2])  # param for the log file

except:
    print("Missing params")
    sys.exit()
    

# generic errors

s_error = 0
s_warning = 0
s_skipped = 0


def write_status(status):
    global macro_status
    json = '{"type": "status", "status": ' + str(status).lower() + '}'
    handle = open(macro_status, 'w+')
    print >> handle, json
    return

# track trace

def trace(string):
    global log_trace
    out_file = open(log_trace, "a+")
    out_file.write(str(string) + "\n")
    out_file.close()
    # headless
    print string
    return



def macro(code, expected_reply, timeout, error_msg, delay_after, warning=False, verbose=True):
    global s_error
    global s_warning
    global s_skipped
    serial.flushInput()
    if s_error == 0:
        serial_reply = ""
        macro_start_time = time.time()
        serial.write(code + "\r\n")
        if verbose:
            trace(error_msg)
        time.sleep(0.3)  # give it some tome to start
        while not (serial_reply == expected_reply or serial_reply[:4] == expected_reply):
            # Expected reply
            # no reply:
            if (time.time() >= macro_start_time + timeout + 5):
    
                if serial_reply == "":
                    serial_reply = "<nothing>"
                    
                
                if not warning:
                    s_error += 1
                    trace(error_msg + ": Failed (" + serial_reply + ")")
                else:
                    s_warning += 1
                    trace(error_msg + ": Warning! ")
                return False  # leave the function
       
            serial_reply = serial.readline().rstrip()
          
            # add safety timeout
            time.sleep(0.2)  # no hammering
            pass
       
        time.sleep(delay_after)  # wait the desired amount
    else:
        trace(error_msg + ": Skipped")
        s_skipped += 1
        return False
   
    return serial_reply

def axisScale(val, span=255, deadband=20):
    tmp = val - (span / 2.0)
    if (abs(tmp) < deadband):
        return 0.0
    else:
        scaledVal = (abs(tmp) - deadband) / float((span / 2.0) - deadband)
        if tmp < 0:
            scaledVal *= -1
        return scaledVal
        
def calculateGcode(jStatus, gain = 1.0):
    
    xSpeed = axisScale(jStatus['LeftStickX'])
    ySpeed = -axisScale(jStatus['LeftStickY'])
    zSpeed = axisScale(jStatus['RightStickY'])
    xyGain = 1.0 * gain
    zGain = 0.5 * gain
    feedRateGain = 5000.0 * gain
    
    gCode = 'G0 '
    gCode += 'X%0.3f ' % (xSpeed * xyGain)
    gCode += 'Y%0.3f ' % (ySpeed * xyGain)
    gCode += 'Z%0.3f ' % (zSpeed * zGain)
    gCode += 'F%0.0f' % (max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) * feedRateGain)
    
    move = max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) > 0.0
    
    return gCode, move


class CarriagePosition():
    
    def __init__(self, logFile):
        self._rePosCode = re.compile('X:?(.?\d+\.?\d*)\s*Y:?(.?\d+\.?\d*)\s*Z:?(.?\d+\.?\d*)\s*')
        self.mut = Lock()
        self.position = (0, 0, 0)
        self.prependString = ''
        self.appendString = ''
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
        self._writeLogFile(self.prependString + '\nX%0.2f Y%0.2f Z%0.2f\n' % pos + self.appendString)
        
    def stringToPos(self, string):
        try:
            posGroup = self._rePosCode.search(string).groups()
            return (float(posGroup[0]), float(posGroup[1]), float(posGroup[2]))
#             self.pos = (self.pos[0] + pos[0], self.pos[1] + pos[1], self.pos[2] + pos[2])
        except:
            return (0.0, 0.0, 0.0)

console1 = CarriagePosition(log_console)

try:
    js = ps3.Ps3Com()
except:
    console1.setPrependString('Joystick not found!\n')
    console1.updateConsole()
    sleep(1) 
    console1.closeLogFile()
    sys.exit()


write_status(True)

'''#### SERIAL PORT COMMUNICATION ####'''
serial_port = config.get('serial', 'port')
serial_baud = config.get('serial', 'baud')

serial = serial.Serial(serial_port, serial_baud, timeout=0.5)
serial.flushInput()

macro("G91", "ok", 1, "set relative movements", 0)
 

def consoleUpdater():
    while 1:
        console1.updateConsole()
        time.sleep(0.5)
        if shutdown:
            break
      
def jsControl():
    buttonSelectMem = False
    zProbeDown = False
    speedGain = 1.0
    speedGainMem = False
     
    while 1:
        try:
            status = js.getStatus()
        except:
            console1.setPrependString('Joystick disconnected!\n')
            break
            
    
        if status['ButtonCircle']:
            console1.setPrependString('Joystick Jog aborted\n')
            break
        
        if status['ButtonTriangle']:
            macro("M999", "ok", 1, "reset", 0)
                
        ''' Lower and raise z-probe with select button '''  
        if status['ButtonSelect'] and (not buttonSelectMem):
            buttonSelectMem = True
            if not zProbeDown:
#                 macro("M401","ok",1,"probe down",0)
                serial.write("M401\r\n")
                serial.readall()
                zProbeDown = True
            else:
#                 macro("M402","ok",1,"probe up",0)
                serial.write("M402\r\n")
                serial.readall()
                zProbeDown = False
        elif (not status['ButtonSelect']) and buttonSelectMem:
            buttonSelectMem = False
                    
        if status['ButtonDown']:
            if not speedGainMem and speedGain > 0.05:
                speedGain -= 0.05
            speedGainMem = True
        elif status['ButtonUp']:
            if not speedGainMem and speedGain < 1.0:
                speedGain += 0.05
            speedGainMem = True
        else:
            speedGainMem = False
            
        console1.setAppendString('Speed: %0.0f%s' % (speedGain*100, '%'))
        
        gCode, move = calculateGcode(status, speedGain)
    
        if move:
    
            serial.write(gCode + "\r\n")
            serial.readline().rstrip()
            console1.updatePosition(console1.stringToPos(gCode))

consoleThread = Thread(target=consoleUpdater)
consoleThread.setDaemon(True)
consoleThread.start()  

serial.write("M114\r\n")
console1.setPostition(console1.stringToPos(serial.readall().rstrip()))

jsThread = Thread(target=jsControl)   
jsThread.setDaemon(True)
jsThread.start()       
  
console1.setPrependString('Ready for joystick jog!\n')

   

jsThread.join()
sleep(1)
shutdown = True
consoleThread.join()
# clean the buffer and leave
serial.flush()
serial.close()
write_status(False)
open(log_trace, 'w').close()  # reset trace file
console1.closeLogFile()
sys.exit()  
    
