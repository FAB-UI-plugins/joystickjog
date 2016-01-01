import sys
import time
import serial
import json
import ConfigParser
import ps3
from time import sleep
import re
from threading import Thread, Lock
from joyFunctions import FabJoyFunctions
from subprocess import call
import BaseHTTPServer
from urlparse import parse_qs

shutdown = False

config = ConfigParser.ConfigParser()
config.read('/var/www/fabui/python/config.ini')


try:
#     pass 
    task_id = str(sys.argv[1])

except:
    print("Missing params")
    sys.exit()
    
HOST_NAME = ''
PORT_NUMBER = 9002

jsonEnc = json.JSONEncoder()

def setShutdown():
    global shutdown
    setMessage('Joystick Jog aborted')
    shutdown = True
    try:
        serialPort.write('M0')
    except:
        pass
    

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getShutdown():
    return shutdown

class CarriagePosition():
    
    def __init__(self):
        self._rePosCode = re.compile('X:?(.?\d+\.?\d*)\s*Y:?(.?\d+\.?\d*)\s*Z:?(.?\d+\.?\d*)\s*')
        self.mut = Lock()
        self.position = (0, 0, 0)
        
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
      
    def stringToPos(self, string):
        try:
            posGroup = self._rePosCode.search(string).groups()
            return (float(posGroup[0]), float(posGroup[1]), float(posGroup[2]))
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
        self.lastReply = ''
        self.listenThread = Thread(target=self.listener)
        self.listenThread.setDaemon(True)
        self.listenThread.start()
        self.pollThread = Thread(target=self.tempPoll)
        self.pollThread.setDaemon(True)
        self.pollThread.start()
        self.counterLock = Lock()
        
        
    def write(self, data):
        print 'Sent:', str(self.sent), '/ Received:', str(self.received)
        waitCount = 0
        while not self.received==self.sent and not self.shutdown():
            time.sleep(0.01)
            waitCount +=1
            if waitCount >= 100:
                self.received = self.sent
            #wait!
#         print 'Sent: %i, received: %i' % (self.sent, self.received)
#         console1.setAppendString('Sent: %i, received: %i' % (self.sent, self.received))
        self.sent += 1
        
        return serial.Serial.write(self, data)
    
    def tempPoll(self):
        while not self.shutdown():
            serialPort.write("M114\r\n")
            position.setPostition(position.stringToPos(self.getPositionReply()))
            
            self.write('M105\r\n')
            time.sleep(1.0)
            
    
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
            
            self.lastReply = serial_in
        #clear everything not recognized.
            serial_in=""
       
    def getLastReply(self):
        waitCount = 0
        while not self.received==self.sent and not self.shutdown():
            time.sleep(0.01)
            waitCount +=1
            if waitCount >= 100:
                self.received = self.sent
                
        return self.lastReply
        
    def getPositionReply(self):
        waitCount = 0
        while not self.received==self.sent and not self.shutdown():
            time.sleep(0.01)
            waitCount +=1
            if waitCount >= 100:
                self.received = self.sent
                
        return self.lastPositionReply
    
    
    def getTemperature(self):
        ext_temp = 0
        bed_temp = 0
        ext_temp_target = 0
        bed_temp_target = 0
        
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
                        
            return (ext_temp, ext_temp_target, bed_temp, bed_temp_target)
        else:
            return (0,0,0,0)
    
    def getTemperatureString(self):
        return 'Ext Temp/Target: %0.0f/%0.0f | Bed Temp/Target: %0.0f/%0.0f' % self.getTemperature()
        


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_POST(s):
        """Respond to a POST request."""
        s.send_response(200)
        s.send_header("Content-type", "json")
        s.send_header("Access-Control-Allow-Origin", "*")
        s.end_headers()
        
        length = int(s.headers.getheader('content-length'))
        postvars = parse_qs(s.rfile.read(length), keep_blank_values=1)
        s.wfile.write(handlePostRequest(postvars))

values = { 
        'message' : '',
        'e-sp' : 0,
        'e-temp' : 0,
        'bed-sp' : 0,
        'bed-temp' : 0,
        'x-pos' : 0,
        'y-pos' : 0,
        'z-pos' : 0,
        'e-pos' : 0,
        'button-conf' : {}
}

def setMessage(msg):
    global values
    values['message'] += msg + '\n'

def handlePostRequest(postvars):
    responsvars = {'type':'', 'action':'', 'reply':''}
    global values

 
    #postvars: type:
    #                 - command
    #                 - update
    #                 - config

    
    print postvars
    if postvars['type'][0] == 'command':
        responsvars['type'] = 'command'
        if postvars['action'][0] == 'shutdown':
            setShutdown()
            return
            
        elif postvars['action'][0] == 'up':
            serialPort.write("G0 Y%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'down':
            serialPort.write("G0 Y-%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'right':
            serialPort.write("G0 X%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'left':
            serialPort.write("G0 X-%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'up-left':
            serialPort.write("G0 X-%0.3f Y%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'up-right':
            serialPort.write("G0 X%0.3f Y%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'down-left':
            serialPort.write("G0 X-%0.3f Y-%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'down-right':
            serialPort.write("G0 X%0.3f Y-%0.3f F%0.0f\r\n" % (float(postvars['step'][0]), float(postvars['step'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'home':
            serialPort.write("G90\r\n")
            serialPort.write("G0 X0 Y0 F%0.0f\r\n" % (float(postvars['feedrate'][0]),))
            serialPort.write("G91\r\n")
        
        elif postvars['action'][0] == 'zup':
            serialPort.write("G0 Z-%0.3f F%0.0f\r\n" % (float(postvars['zstep'][0]), float(postvars['feedrate'][0])))
        
        elif postvars['action'][0] == 'zdown':
            serialPort.write("G0 Z%0.3f F%0.0f\r\n" % (float(postvars['zstep'][0]), float(postvars['feedrate'][0])))
        
        
            
        elif postvars['action'][0] == 'mdi':
            lines = str(postvars['mdi'][0]).splitlines()
            responsvars['action'] = 'mdi'
            for line in lines:
                if len(line) > 0:
                    serialPort.write(line + '\n')
                    responsvars['reply'] += serialPort.getLastReply() + '\n'
            
            
                
        elif postvars['action'][0] == 'config':
            pass

        
        
    elif postvars['type'][0] == 'update':
        
        responsvars['type'] = 'update'
        values['e-temp'], values['e-sp'], values['bed-temp'], values['bed-sp'] = serialPort.getTemperature()
        values['x-pos'], values['y-pos'], values['z-pos'] = position.getPosition()
        responsvars.update(values)
        values['message'] = ''
    
    
    return jsonEnc.encode(responsvars)


server_class = BaseHTTPServer.HTTPServer
httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
httpd.timeout = 2.0

def httpTask():
    try:
        while not getShutdown(): 
            httpd.handle_request()
    except:
        pass
    httpd.server_close()
     
position = CarriagePosition()

httpThread = Thread(target=httpTask)   
httpThread.setDaemon(True)
httpThread.start()

try:
    js = ps3.Ps3Com()
except:
    setMessage('Joystick not found!')
    setShutdown()
    call (['sudo php /var/www/fabui/application/plugins/joystickjog/ajax/finalize.php '+str(task_id)+' JoyJog'], shell=True)
    sleep(1) 
    sys.exit()



'''#### SERIAL PORT COMMUNICATION ####'''
serial_port = config.get('serial', 'port')
serial_baud = config.get('serial', 'baud')

serialPort = GcodeSerial(serial_port, serial_baud, 0.5, getShutdown)
serialPort.flushInput()
serialPort.write("G91\r\n")


      
def jsControl():
    
    functions = FabJoyFunctions(serialPort, position)
    functions.msg_callback = setMessage
      
    while not getShutdown():
        try:
            status = js.getStatus()
        except:
            setMessage('Joystick disconnected!')
            setShutdown()
            break
            
    
        if status['ButtonCircle']:
            setMessage('Joystick Jog aborted')
            setShutdown()
            break
                             
        functions.callFunctions(status)


serialPort.write("M114\r\n")
position.setPostition(position.stringToPos(serialPort.getPositionReply()))


jsThread = Thread(target=jsControl)   
jsThread.setDaemon(True)
jsThread.start()       
  
setMessage('Ready for joystick jog!')

   

jsThread.join()
httpThread.join()
sleep(1)


# clean the buffer and leave
serialPort.flush()
serialPort.close()


call (['sudo php /var/www/fabui/application/plugins/joystickjog/ajax/finalize.php '+str(task_id)+' JoyJog'], shell=True)