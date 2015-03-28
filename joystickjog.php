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
		
		//FLUSH SERIAL PORT BUFFER INPUT/OUTPUT
		$this->load->helper('print_helper');
		/** IF PRINTER IS BUSY I CANT JOG  */
		if(is_printer_busy()){
			redirect('dashboard');
		}
		
		$this->lang->load($_SESSION['language']['name'], $_SESSION['language']['name']);
		


	}

	public function index(){

		$this->layout->add_js_in_page(array('data'=> $this->load->view('index/js', '', TRUE), 'comment' => 'INDEX FUNCTIONS'));
		$this->layout->view('index/index');
	
	}
	


}



?>