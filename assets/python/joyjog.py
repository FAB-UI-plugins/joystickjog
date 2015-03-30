import sys
import time, datetime
import serial
import json
import ConfigParser
import logging
import ps3
from time import sleep
import re




config = ConfigParser.ConfigParser()
config.read('/var/www/fabui/python/config.ini')

macro_status = config.get('macro', 'status_file')

try:
      
    log_trace=str(sys.argv[1]) #param for the log file
    log_console=str(sys.argv[2]) #param for the log file

except:
    print("Missing params")
    sys.exit()
    

#generic errors

s_error=0
s_warning=0
s_skipped=0


def write_status(status):
    global macro_status
    json='{"type": "status", "status": ' + str(status).lower() +'}'
    handle=open(macro_status,'w+')
    print>>handle, json
    return

#track trace

def trace(string):
    global log_trace
    out_file = open(log_trace,"a+")
    out_file.write(str(string) + "\n")
    out_file.close()
    #headless
    print string
    return

consoleStr = ''
console_file = None
def console(string = '', action = 'o'):
    global log_console
    global console_file
    if action == 'o':
      console_file = open(log_console,"w")
      console_file.write(str(string))
      console_file.flush()
    elif action == 'w':
        console_file.seek(0)
        console_file.write(str(string))
        console_file.truncate()
        console_file.flush()
    elif action == 'c':
        console_file.seek(0)
        console_file.truncate()
        console_file.close()

#get process pid so the UI can kill it if needed
#myPID = os.getpid()
#print myPID
#trace(myPID,log_trace)
#gcode macro exec

def macro(code,expected_reply,timeout,error_msg,delay_after,warning=False,verbose=True):
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
    zGain = 0.5
    feedRateGain = 5000.0
    
    gCode = 'G0 '
    gCode += 'X%0.2f ' % (xSpeed * xyGain)
    gCode += 'Y%0.2f ' % (ySpeed * xyGain)
    gCode += 'Z%0.2f ' % (zSpeed * zGain)
    gCode += 'F%0.0f' % (max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) * feedRateGain )
    
    move = max((abs(xSpeed), abs(ySpeed), abs(zSpeed))) > 0.0
    
    return gCode, move

rePosCode = re.compile('X:?(.?\d+\.?\d*)\s*Y:?(.?\d+\.?\d*)\s*Z:?(.?\d+\.?\d*)\s*')
lastPos = (0.0, 0.0, 0.0)
def updateConsole(stopped, prependString='', gCode = ''):
    global lastPos
    if stopped:    
        serial.write("M114\r\n")
        posGroup = rePosCode.search(serial.readall().rstrip()).groups()
        pos = (float(posGroup[0]), float(posGroup[1]), float(posGroup[2]))
        consoleStats = consoleStr + 'X%0.2f Y%0.2f Z%0.2f' % pos
        console(consoleStats, 'w')
        lastPos = pos
    else:
        if gCode != '': 
            posGroup = rePosCode.search(gCode).groups()
            pos = (float(posGroup[0]), float(posGroup[1]), float(posGroup[2]))
            lastPos = (lastPos[0] + pos[0],lastPos[1] + pos[1], lastPos[2] +pos[2])
            consoleStats = consoleStr + 'X%0.2f Y%0.2f Z%0.2f' % lastPos
            console(consoleStats, 'w')
            


write_status(True)
'''#### SERIAL PORT COMMUNICATION ####'''
serial_port = config.get('serial', 'port')
serial_baud = config.get('serial', 'baud')

serial = serial.Serial(serial_port, serial_baud, timeout=0.5)
serial.flushInput()



reply = macro("G91","ok",1,"set relative movements",0)


try:
    js = ps3.Ps3Com()
except:
    console('Joystick not found!\n')
    sleep(1)
    console(action = 'c')
    sys.exit()
    
consoleStr = 'Ready for joystick jog!\n'
console(consoleStr)


buttonSelectMem = False
zProbeDown = False
stopped = True
updateConsole(True, consoleStr)
while 1:
    status = js.getStatus()

    if status['ButtonCircle']:
        console('Joystick Jog aborted\n', 'w')
        break
    
    if status['ButtonTriangle']:
		macro("M999","ok",1,"reset",0)
		

		
		
    if status['ButtonSelect'] and (not buttonSelectMem):
        buttonSelectMem = True
        if not zProbeDown:
            macro("M401","ok",1,"probe down",0)
            zProbeDown = True
        else:
            macro("M402","ok",1,"probe up",0)
            zProbeDown = False
    elif (not status['ButtonSelect']) and buttonSelectMem:
        buttonSelectMem = False
		
		
    gCode, move = calculateGcode(status)

    if move:

        serial.write(gCode+"\r\n")
        serial_reply=serial.readline().rstrip()
        updateConsole(False, consoleStr, gCode)
        stopped = True
    elif stopped:
        stopped = False


    
#clean the buffer and leave
serial.flush()
serial.close()
write_status(False)
open(log_trace, 'w').close() #reset trace file
sleep(1)
console(action = 'c')
sys.exit()  
    
