# joystickjog
<br>
Use PS3 SIXAXIS to jog fabtotum.<br>
<br>
Connect SIXAXIS to FabTotum USB port and click "Activate Joystick" button.<br>
<br>
This version uses a JSON config file to connect buttons to a function.<br>
<br>
The plan is for this config to be available from the JOG menu, but that has not been implemented yet.<br>
For the moment a default config file located in "/var/www/fabui/application/plugins/joystickjog/assets/python/" is used.<br>
<br>
The following functions is fixed and can not be set with the config file:<br>
	Left Joystick X : FabTotum X-axis<br>
	Left Joystick Y : FabTotum Y-axis<br>
	Right Joystick Y: Fabtotum Z-axis<br>
	Circle: Quit<br>
<br>
<br>
The following functions is set in the default config file:<br>
	Up Button		: Increase feedrate					 (Step value can be set in the config file)<br>
	Down Button		: Decrease feedrate					 (Step value can be set in the config file)<br>
	Select Button	: Z-Probe up /down<br>
	PS Button		: Reset safety warning
	R2 Button		: Extruder feed						 (Feedate can be set in the config file)<br>
	L2 Button		: Extruder retract					 (Feedate can be set in the config file)<br>
	Start Button	: Set X,Y and Z zero position.<br>
	Left JS Button	: Goto zero position				 (Feedate can be set in the config file)<br>
	L1 Button		: Toggle between 5 and 100% feedrate (Slow rate can be set in the config file)<br>
	Square Button	: Toggle Bed temp between 0 and 210C (Temp can be set in the config file)<br>
    Cross Button	: Toggle Bed temp between 0 and 65C  (Temp can be set in the config file)<br>
