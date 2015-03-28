import time
import sys, os
import serial
from subprocess import call
import numpy as np
import json
import pprint
import ps3
from time import sleep


global feedrate

global start_time


try:
  
    log_trace=str(sys.argv[1])    #trace log file

except:
    print "Missing Log reference"
    sys.exit("Missing Log reference")

def trace(string):
    global log_trace
    out_file = open(log_trace,"a+")
    out_file.write(str(string) + "\n")
    out_file.close()
    #headless
    print string
    return


def macro1(code,expected_reply,timeout,error_msg,delay_after,warning=False,verbose=True):
    global s_error
    global s_warning
    global s_skipped
    serial.flushInput()
    if s_error==0:
        serial_reply=""
        macro_start_time = time.time()
        serial.write(code+"\r\n")
        if verbose:
            trace(error_msg)
        time.sleep(0.3) #give it some tome to start
        while not (serial_reply==expected_reply or serial_reply[:4]==expected_reply):
            #Expected reply
            #no reply:
            if (time.time()>=macro_start_time+timeout+5):
                if serial_reply=="":
                    serial_reply="<nothing>"
                if not warning:
                    s_error+=1
                    trace(error_msg + ": Failed (" +serial_reply +")")
                else:
                    s_warning+=1
                    trace(error_msg + ": Warning! ")
                return False #leave the function
            serial_reply=serial.readline().rstrip()
            #add safety timeout
            time.sleep(0.2) #no hammering
            pass
        time.sleep(delay_after) #wait the desired amount
    else:
        trace(error_msg + ": Skipped")
        s_skipped+=1
        return False
    return serial_reply


trace("Joystick Jog initialized")
try:
    joystick = ps3.Ps3Com()
except:
    trace('Joystick not connected!')
    sys.exit('Joystick not connected!')

port = '/dev/ttyAMA0'
baud = 115200
try:
    serial = serial.Serial(port, baud, timeout=0.6)
    serial.flushInput()
except:
    trace('Serial failed')
trace('Serial ok')
def axisScale(val, span = 255, deadband = 20):
    tmp = val - (span/2.0)
    if (abs(tmp) < deadband):
        return 0.0
    else:
        scaledVal = (abs(tmp) - deadband) / float((span/2.0) - deadband)
        if tmp < 0:
            scaledVal *= -1
        return scaledVal
        

    

def calculateGcode(jStatus):
    
    xSpeed = axisScale(jStatus['LeftStickX'])
    ySpeed = -axisScale(jStatus['LeftStickY'])
    zSpeed = axisScale(jStatus['RightStickY'])
    xyGain = 1.0
    zGain = 1.0
    feedRateGain = 5000.0
    
    gCode = 'G0 '
    gCode += 'X%s ' % str(xSpeed * xyGain)
    gCode += 'Y%s ' % str(ySpeed * xyGain)
    gCode += 'Z%s ' % str(zSpeed * zGain)
    gCode += 'F%s' % str(max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) * feedRateGain )
    
    return gCode
    
    



trace('before macro')
reply = macro('G91', 'ok', 5, 'Set relative ', 1)  
trace('Serial: ' & reply)

trace('starting')
while 1:
    status = joystick.getStatus()
    if status['ButtonCircle']:
        trace('Joystick Jog aborted')
        break
    gcode = calculateGcode(status)
    trace(gcode)
    macro(gcode, 'ok', 2, 'move', 0) 
    
    
    