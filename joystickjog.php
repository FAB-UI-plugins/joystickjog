<?php
/*
Plugin Name: Joystick Jog
Plugin URI: http://github.com/FAB-UI-plugins/joystickjog
Version: 1.00
Description: Jog using ps3 controller
Author: Tom Haraldseid
Author URI: 
Plugin Slug: joystickjog
Icon: icon-fab-jog
*/
 

 
class Joystickjog extends Plugin {

	public function __construct()
	{
		parent::__construct();
		
		$this->load->helper('url');
		
		define('MY_PLUGIN_URL', site_url().'plugin/joystickjog/');
		define('MY_PLUGIN_PATH', PLUGINSPATH.'joystickjog/');

		
        //FLUSH SERIAL PORT BUFFER INPUT/OUTPUT
        $this->load->helper('print_helper');
        /** IF PRINTER IS BUSY I CANT JOG  */
        if(is_printer_busy()){
            redirect('dashboard');
        }
        /** LOAD HELPER */
        $this->load->helper('update_helper');
        $this->lang->load($_SESSION['language']['name'], $_SESSION['language']['name']);
        
	}

	public function index(){
		
		$this->load->model('tasks');
		$this->load->helper('os_helper');
		
		$_task = $this->tasks->get_running('joystickjog', 'JoyJog');
		$_running = $_task ? true : false;
		
		if($_running){
		
			/** GET TASK ATTRIBUTES */
			$_attributes = json_decode($_task['attributes'], TRUE);
				
				
			/** CHECK IF PID IS STILL ALIVE */
			if(!exist_process($_attributes['pid'])){
				
				/** PROCESS IS DEAD */
				$_running = false;
				$this->tasks->delete($_task['id']);
		
			}
		
		}
		

		$this->layout->add_js_file(array('src'=> site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.cust.min.js', 'comment'=>'create utilities'));
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.resize.min.js', 'comment'=>'create utilities'));
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.fillbetween.min.js', 'comment'=>'create utilities'));
		
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.orderBar.min.js', 'comment'=>'create utilities'));
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.pie.min.js', 'comment'=>'create utilities'));
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.time.min.js', 'comment'=>'create utilities'));
		
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.tooltip.min.js', 'comment'=>'create utilities'));
		$this->layout->add_js_file(array('src'=>site_url(). 'application/layout/assets/js/plugin/flot/jquery.flot.axislabels.js', 'comment'=>'create utilities'));
		
		
		
		$css_in_page = $this->load->view('css', '', TRUE);
		$this->layout->add_css_in_page(array('data'=> $css_in_page, 'comment' => ''));
		
		$js_in_page = $this->load->view('js', '', TRUE);
		$this->layout->add_js_in_page(array('data'=> $js_in_page, 'comment' => ''));
		
		$this->layout->view('index');
		
  
	}
    
    
    
    


	
	
	public function update()
	{
		$_is_internet_ok = is_internet_avaiable();
		
	
		if($_is_internet_ok){
			$cmd = 'sudo rm -r -f application/plugins/joystickjog/';
			echo shell_exec($cmd);
			$cmd = 'sudo git clone https://github.com/FAB-UI-plugins/joystickjog.git application/plugins/joystickjog';
			echo shell_exec($cmd);
		
		}
		redirect(MY_PLUGIN_URL);

	
	}





}

?>