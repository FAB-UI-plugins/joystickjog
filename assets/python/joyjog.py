import sys
import time, datetime
import serial
import json
import ConfigParser
import logging
import ps3
from time import sleep

global feedrate

global start_time

config = ConfigParser.ConfigParser()
config.read('/var/www/fabui/python/config.ini')

macro_status = config.get('macro', 'status_file')

#read config steps/units
json_f = open(config.get('printer', 'settings_file'))
units = json.load(json_f)
#process params

try:
    safety_door = int(units['safety']['door'])
except KeyError:
    safety_door = 0

try:
      
    log_trace=str(sys.argv[1]) #param for the log file
#     log_response=str(sys.argv[3]) #param for the log file
except:
    print("Missing params")
    sys.exit()
    

#generic errors
probe_start_time=0 #start time
s_error=0
s_warning=0
s_skipped=0
feeder_disengage_offset=units['feeder']['disengage-offset'] #mm distance to disable extruder

trace_file=config.get('macro', 'trace_file')
# response_file=config.get('macro', 'response_file')

logging.basicConfig(filename=log_trace,level=logging.INFO,format='<span class="hidden-xs">[%(asctime)s] -</span> %(message)s',datefmt='%d/%m/%Y %H:%M:%S')




open(trace_file, 'w').close() #reset trace file
# open(response_file, 'w').close() #reset trace file

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
                    
                #trace_msg="failed macro (timeout):"+ code+ " expected "+ expected_reply+ ", received : "+ serial_reply
                #trace(trace_msg,log_trace)
                #print trace_msg
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
    

write_status(True)
'''#### SERIAL PORT COMMUNICATION ####'''
serial_port = config.get('serial', 'port')
serial_baud = config.get('serial', 'baud')

serial = serial.Serial(serial_port, serial_baud, timeout=0.5)
serial.flushInput()



reply = macro("G91","ok",1,"set relative movements",1)
# trace('Serial: ' + reply)

  
js = ps3.Ps3Com()
trace('starting')
buttonSelectMem = False
zProbeDown = False
while 1:
    status = js.getStatus()
#     trace(status)
    if status['ButtonCircle']:
        trace('Joystick Jog aborted')
        break
    if status['ButtonTriangle']:
		macro("M999","ok",1,"reset",1)
		

		
		
    if status['ButtonSelect'] and (not buttonSelectMem):
        buttonSelectMem = True
        if not zProbeDown:
            macro("M401","ok",1,"probe down",1)
            zProbeDown = True
        else:
            macro("M402","ok",1,"probe up",1)
            zProbeDown = False
    elif (not status['ButtonSelect']) and buttonSelectMem:
        buttonSelectMem = False
		
		
    gCode, move = calculateGcode(status)
#     trace(gCode, move)
    if move:
        #~ trace(gCode)
        serial.write(gCode+"\r\n")
        serial_reply=serial.readline().rstrip()
        #~ trace('Serial: ' + serial_reply)
        
		

    
#clean the buffer and leave
serial.flush()
serial.close()
write_status(False)
#open(trace_file, 'w').close() #reset trace file
sys.exit()  
    
    