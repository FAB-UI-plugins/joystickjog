<?php
/*
Plugin Name: Joystick Jog
Plugin URI: 
Version: 0.1
Description: Jog using ps3 controller
Author: Tom Haraldseid
Author URI: 
Plugin Slug: joystickjog
Icon:
*/
 

 
class Joystickjog extends Plugin {
	


public function __construct()
	{
		parent::__construct();
			
		$this->load->helper('url');
		
		define('MY_PLUGIN_URL', site_url().'plugin/joystickjog/');
		define('MY_PLUGIN_PATH', PLUGINSPATH.'joystickjog/');
		$this->load->add_package_path(MY_PLUGIN_PATH);
		


	}

	public function index(){

		$this->layout->view('index');
	
	}
	


}



?>