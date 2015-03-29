<?php
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/config.php';
require_once $_SERVER['DOCUMENT_ROOT'] . '/fabui/ajax/lib/utilities.php';

function debug_to_console( $data ) {

    if ( is_array( $data ) )
        $output = "<script>console.log( 'Debug Objects: " . implode( ',', $data) . "' );</script>";
    else
        $output = "<script>console.log( 'Debug Objects: " . $data . "' );</script>";

    echo $output;
}

/** CREATE LOG FILES */
$_time                      = $_POST['time'];
/* $_time                      ='1417816594542'; */
$PYTHON_PATH = "/var/www/fabui/application/plugins/joystickjog/assets/python/";
// $TEMP_PATH = $PYTHON_PATH."temp/";
$TEMP_PATH = "/var/www/temp/";
$_destination_trace         = $TEMP_PATH . 'joystickjog_' . $_time . '.trace';


// shell_exec('sudo chmod 777 '.$TEMP_PATH);
write_file($_destination_trace, '', 'w');
chmod($_destination_trace, 0777);


/** WAIT JUST 1 SECOND */
sleep(1);



/** EXEC COMMAND */
$h_over = 50;

$_command = 'sudo python '.$PYTHON_PATH.'joyjog.py ' . $_destination_trace ;



$_output_command = shell_exec($_command); 
/** WAIT JUST 1 SECOND */
sleep(1);

/* $_response = json_decode(file_get_contents($_destination_response), TRUE); */

$_response = 'Done!';

echo $_response; 
?>

