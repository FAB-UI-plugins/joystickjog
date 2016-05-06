<script type="text/javascript">

var max_plot = 100;
var nozzle_temperatures = [];
var target_temperatures = [];
var target_bed_temperatures = [];
var bed_temperatures = [];
var nozzlePlot = "";
var now = new Date().getTime();
var values = [];
var message = '';
var $chrt_border_color = "#efefef";
var $chrt_grid_color = "#DDD";
var $chrt_main = "#E24913";
/* red       */
var $chrt_second = "#6595b4";
/* blue      */
var $chrt_third = "#FF9F01";
/* orange    */
var $chrt_fourth = "#7e9d3a";
/* green     */
var $chrt_fifth = "#BD362F";
/* dark red  */
var $chrt_mono = "#000";

var prev = 100;
var manualActive = false;
var autoActive = false;
var pid = 0;
var extruder = 0;
var wd = 2;


$(document).ready(function() {

	$(".actionButton").on('click', function() {
		sendReceive({type: 'command', action: $(this).attr('id')});

	});



	$("#start").on('click', function() {
		acivateJoystick();
		$("#start").attr("hidden",false);
		$("#shutdown").attr("hidden",true);
		wd = -5;

	});

	$("#run").on('click', function() {
		sendReceive({type: 'command', action: 'mdi', mdi: $("#mdi").val().toUpperCase()});
	});

	$(".directions").on("click", function() {
		
		sendReceive({type: "command", 
			         action: $(this).attr("data-attribute-direction"), 
			         zstep: $("#z-step").val(), 
			         step: $("#step").val(), 
			         feedrate: $("#feedrate").val()
			        });
		
	});

	$("#z-step").spinner({
		step : 0.01,
		numberFormat : "n",
		min: 0
	});
	
	
	$("#step").spinner({
			step :0.5,
			numberFormat : "n",
			min: 0
	});
	
	$("#feedrate").spinner({
			step :50,
			numberFormat : "n",
			min: 0
	});



	initGraphs();
	update();
	drawExtruder(100, 100);
	drawPs3Img();

	
	
}); /* End of init */



function drawExtruder(x, y) {

	var canvas = document.getElementById("bed-canvas");
	var ctx = canvas.getContext("2d");
	var xScale = (canvas.width - 5) / 210.0;
	var yScale = (canvas.height - 15) / 230.0; 

	x = (5 + x) * xScale;
	y = canvas.height - ((15 + y) * yScale);
	
	var img=document.getElementById("bed-img");
    ctx.drawImage(img,40,0,441,520,0,0,480, 540);

	var crossSize = 20;
	ctx.beginPath();
	ctx.moveTo(x - crossSize, y);
	ctx.lineTo(x + crossSize, y);
	ctx.moveTo(x , y-crossSize);
	ctx.lineTo(x , y+crossSize);
	
	ctx.stroke();
	
}

function drawPs3Img() {

	var canvas = document.getElementById("ps3-canvas");
	var ctx = canvas.getContext("2d");
	

	
	var img=document.getElementById("ps3-img");
    ctx.drawImage(img,0,0,1023, 767);


	
}

function update() {
	sendReceive({type: 'update'});

	wd += 1;
	if(wd > 2) {
		$("#start").attr("hidden",false);
		$("#shutdown").attr("hidden",true);
	} else {
		$("#start").attr("hidden",true);
		$("#shutdown").attr("hidden",false);
	}
	
	
	
	

	setTimeout(update, 1000);
}


function addTargetTemperature(temp){
	
	var now = new Date().getTime();
	var obj = {'temp': parseFloat(temp), 'time': now};
	
	if(target_temperatures.length == max_plot){
		target_temperatures.shift();
	}
	
	target_temperatures.push(obj);
}

function addTargetBedTemperature(temp){
	
	var now = new Date().getTime();
	var obj = {'temp': parseFloat(temp), 'time': now};
	
	if(target_bed_temperatures.length == max_plot){
		target_bed_temperatures.shift();
	}
	
	target_bed_temperatures.push(obj);
}

function addNozzleTemperature(temp){
	
	var now = new Date().getTime();
	var obj = {'temp': parseFloat(temp), 'time': now};
	
	if(nozzle_temperatures.length == max_plot){
		nozzle_temperatures.shift();
	}
	
	nozzle_temperatures.push(obj);
}

function addBedTemperature(temp){
	
	var now = new Date().getTime();
	var obj = {'temp': parseFloat(temp), 'time': now};
	
	if(bed_temperatures.length == max_plot){
		bed_temperatures.shift();
	}
	
	bed_temperatures.push(obj);
}


function getNozzlePlotTemperatures(){
	
	var res1 = [];
	var res2 = [];
	var res3 = [];
	var res4 = [];
	
	for (var i = 0; i < nozzle_temperatures.length; ++i) {
		var obj = nozzle_temperatures[i];
		res1.push([obj.time, obj.temp]);
	}

	for (var i = 0; i < target_temperatures.length; ++i) {
		var obj = target_temperatures[i];
		res2.push([obj.time, obj.temp]);
	}

	for (var i = 0; i < target_bed_temperatures.length; ++i) {
		var obj = target_bed_temperatures[i];
		res4.push([obj.time, obj.temp]);
	}

	for (var i = 0; i < bed_temperatures.length; ++i) {
		var obj = bed_temperatures[i];
		res3.push([obj.time, obj.temp]);
	}

	
	return [{ label: "Bed", data: res3 },
		    { label: "Bed Sp", data: res4 },
		    { label: "Extruder", data: res1 },
		    { label: "Extruder Sp", data: res2 }];


}

function updateNozzleGraph(){
	
	
	try{
		
		if(typeof nozzlePlot == "object" ){
		
			nozzlePlot.setData(getNozzlePlotTemperatures());
			nozzlePlot.setupGrid();
			nozzlePlot.draw();
			
		
		}
		
	}catch(e){
		console.log(e);
	}
	
	
}

function  initGraphs(){
	
	
	
	 nozzlePlot = $.plot("#nozzle-chart", getNozzlePlotTemperatures(), {
        	series : {
				lines : {
					show : true,
					lineWidth : 1.2,
					fill : false,
					fillColor : {
						colors : [{
							opacity : 0.1
						}, {
							opacity : 0.15
						}]
					}
				},
				
				shadowSize : 0
			},
			legend: {
				noColumns: 1
			},
			xaxis: {
			    mode: "time",
			    show: true
			},
			yaxis: {
		        min: 0,
		        max: 300,
		        tickSize: 50,        
		        tickFormatter: function (v, axis) {
		            return v + "&deg;C";
		        }
        
    		},
			grid : {
				hoverable : true,
				clickable : true,
				tickColor : $chrt_border_color,
				borderWidth : 0,
				borderColor : $chrt_border_color,
			},
			tooltip : true,
			tooltipOpts : {
				content : "%y &deg;C",
				defaultTheme : false
			},
			colors : ["#FF0000", "#00FF00", "#0000FF", "#000000"],
							
			});
	
	
	
	
	updateNozzleGraph();
	
	
}

var data = {
        type: 'shutdown',
        time: now,
        run: true
    };
function updateConsole(msg) {

	message += msg;
	$("#console").html(message);
	var psconsole = $('#console');
    psconsole.scrollTop(psconsole[0].scrollHeight - psconsole.height());
	
}
function handleReturn(data) {

/* 	console.log(data); */	
	
	
	if(data['type'] == 'update'){
		 
		
		$(".nozzle-temperature").html(parseFloat(data['e-temp']) + '&deg;C');
		$(".bed-temperature").html(parseFloat(data['bed-temp']) + '&deg;C');
		$(".target-temperature").html(parseFloat(data['e-sp']) + '&deg;C');
		$(".target-bed-temperature").html(parseFloat(data['bed-sp']) + '&deg;C');
		addTargetTemperature(parseFloat(data['e-sp']));
		addTargetBedTemperature(parseFloat(data['bed-sp']));
		addNozzleTemperature(parseFloat(data['e-temp']));
		addBedTemperature(parseFloat(data['bed-temp']));
		updateNozzleGraph();
		updateConsole(data['message']);

		drawExtruder(parseFloat(data['x-pos']),parseFloat(data['y-pos']));
		$(".x-pos").html(parseFloat(data['x-pos']).toFixed(2));
		$(".y-pos").html(parseFloat(data['y-pos']).toFixed(2));
		$(".z-pos").html(parseFloat(data['z-pos']).toFixed(2));
		
	
		
			
	}else if(data['type'] == 'command'){
		updateConsole(data['reply']);
		

	}


}

function sendReceive(data) {


    $.ajax({
            type: "POST",
            url: 'http://' + window.location.hostname + ':9002/',
            data: data,
            dataType: "json"
        }).done(function(data) {
        	wd = 0;
        	handleReturn(data);
        	
        });
}

function acivateJoystick() {

    var now = jQuery.now();


    $.ajax({
            type: "POST",
            url: "/fabui/application/plugins/joystickjog/ajax/run.php",
            data: {
                time: now
            },
            dataType: "html"
        }).done(function(data) {
        	
        	
        });
}
</script>
