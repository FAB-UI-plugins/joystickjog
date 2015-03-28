<script type="text/javascript">

$(function() {

    $(".start-jog").on('click', start_jog);
  
    



});


    function start_jog() {
        var buttonStartStop = $("#ButtonStartStop");
        buttonStartStop.text("Running");
        var now = jQuery.now();

        $.ajax({
                type: "POST",
                url: "/fabui/application/plugins/joystickjog/assets/ajax/startjog.php",
                data: {
                    time: now
                },
                dataType: "html"
            }).done(function(data) {
            	buttonStartStop.text("Start");
            });
    }


        
    	


    </script>