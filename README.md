# joystickjog

Use PS3 SIXAXIS to jog fabtotum.

Connect SIXAXIS to FabTotum USB port and click "Activate Joystick" button.

This version uses a JSON config file to connect buttons to a function.
The plan is for this config to be available from the JOG menu, but that has not been implemented yet.
For the moment a default config file located in "/var/www/fabui/application/plugins/joystickjog/assets/python/" is used.

The following functions is fixed and can not be set with the config file:
	Left Joystick X : FabTotum X-axis
	Left Joystick Y : FabTotum Y-axis
	Right Joystick Y: Fabtotum Z-axis
	Circle: Quit


The following functions is set in the default config file:
	Up Button		: Increase feedrate
	Down Button		: Decrease feedrate
	Select Button	: Z-Probe up /down
	PS Button		: Reset safety warning
	R2 Button		: Extruder feed
	L2 Button		: Extruder retract
	Start Button	: Set X,Y and Z zero position.
	Left JS Button	: Goto zero position
