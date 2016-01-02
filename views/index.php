<img hidden id="bed-img" src="/fabui/application/plugins/joystickjog/assets/img/bed.png">
<img hidden id="ps3-img" src="/fabui/application/plugins/joystickjog/assets/img/PS3_FABtotum.png">

<div class="row">
	
	<ul class="list-button pull-left">
		<li>
			<a id="start" class="my-btn" href="javascript:void(0)">Activate Joystick</a>
		</li>
		<li>
			<a id="shutdown" class="actionButton my-btn" href="javascript:void(0)" hidden>Deactivate Joystick</a>
		</li>
		</ul>
	

</div>

<div class="row">
	
	
	<div class="col-md-6">
	
		<div class="row">
		<details class="details-container" >
			<summary class="text-center"><i class="fab-lg fab-fw icon-fab-term "></i> <span>Extruder (<span class="nozzle-temperature"></span>)</span>
																	 &nbsp/&nbsp Bed (<span class="bed-temperature"></span>)</summary>
																	 
			<div id="nozzle-chart" class="nozzle-graph"></div>
			</details>
		</div>
		
		<div class="row">
		<details class="details-container">
		<summary class="text-center">Position:&nbsp <span>X:&nbsp (<span class="x-pos"></span>)</span>
																	 &nbsp/&nbsp Y:&nbsp (<span class="y-pos"></span>)</span>
																	 &nbsp/&nbsp Z:&nbsp (<span class="z-pos"></span>)</summary>
		<div class="text-center">														 
		<canvas id="bed-canvas" width="480" height="540"></canvas>
		</div>	
		</details>
		</div>
		
		<div class="row">
			<details class="details-container" open>
				<summary class="text-center">Button Layout</summary>
				<div class="text-center">														 
					<canvas id="ps3-canvas" width="1023" height="767"></canvas>
				</div>	
			</details>
		</div>
	</div>
		
		
		
	<div class="col-md-6">
		<div class="row">
			<details class="details-container" open>
				<summary class="text-center">MDI</summary>
				<ul class="list-button pull-right">
						
						<li>
							<a id="gcode-manual" data-toggle="modal" href="<?php echo site_url("jog/manual") ?>" data-target="#manula-modal" class="my-btn" href="javascript:void(0);"><i class="fa fa-support"></i> Help</a>
						</li>
						
						<li>
							<a class="my-btn" id="run" href="javascript:void(0)">Run</a>
						</li>

					</ul>
				
				<textarea rows="5" cols="50" id="mdi"></textarea>

			</details>
		</div>
		<div class="row">
			<details class="details-container" open>
				<summary class="text-center">Console</summary>

				<textarea rows="5" cols="50" id="console" readonly></textarea>
			</details>
		</div>
		<div class="row">
			<!-- JOG -->
			<details class="details-container" open>
				<summary class="text-center">Jog</summary>
				
					
						<div class="row">
							<!-- STEP, FEEDRATE -->
							<div class="col-md-4">
								<div class="form-horizontal">
									<fieldset>
										<div class="form-group">
											<div class="col-md-5 control-label">
												<strong>XY Step (mm)</strong>
											</div>
											<div class="col-md-7">
												<input  type="text" id="step" value="10">
											</div>
										</div>
										<div class="form-group">
											<div class="col-md-5 control-label">
												<strong>Feedrate</strong>
											</div>
											<div class="col-md-7">
												<input type="text" id="feedrate" value="1000">
											</div>
										</div>
										<div class="form-group">
											<div class="col-md-5 control-label">
												<strong>Z Step (mm)</strong>
											</div>
											<div class="col-md-7">
												<input  type="text" id="z-step" value="5">
											</div>
										</div>
									</fieldset>
								</div>
							</div>
			
							<!-- JOG DIRECTIONS -->
							<div class="col-md-8 text-center">
								<div class="btn-group-vertical">
									<a href="javascript:void(0)" data-attribute-direction="up-left" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="fa fa-arrow-left fa-1x fa-rotate-45"> </i> </a>
									<a href="javascript:void(0)" data-attribute-direction="left" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <span class="glyphicon glyphicon-arrow-left "> </span> </a>
									<a href="javascript:void(0)" data-attribute-direction="down-left" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="fa fa-arrow-down fa-rotate-45 "> </i> </a>
								</div>
								<div class="btn-group-vertical">
									<a href="javascript:void(0)" data-attribute-direction="up"  class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="fa fa-arrow-up fa-1x"> </i> </a>
									<a href="javascript:void(0)" data-attribute-direction="home"  class="btn btn-default btn-lg btn-circle btn-xl directions rotondo"> <i class="fa fa-bullseye"> </i> </a>
									<a href="javascript:void(0)" data-attribute-direction="down"  class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="glyphicon glyphicon-arrow-down "> </i> </a>
								</div>
								<div class="btn-group-vertical">
									<a href="javascript:void(0)" data-attribute-direction="up-right" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="fa fa-arrow-up fa-1x fa-rotate-45"> </i> </a>
									<a href="javascript:void(0)" data-attribute-direction="right" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <span class="glyphicon glyphicon-arrow-right"> </span> </a>
									<a href="javascript:void(0)" data-attribute-direction="down-right" class="btn btn-default btn-lg directions btn-circle btn-xl rotondo"> <i class="fa fa-arrow-right fa-rotate-45"> </i> </a>
								</div>
								<div class="btn-group-vertical" style="margin-left: 10px;">
									<a href="javascript:void(0)" class="btn btn-default directions" data-attribute-direction="zup"> <i class="fa fa-angle-double-up"> </i>&nbsp;Z </a>
									<hr />
									<a href="javascript:void(0)" class="btn btn-default directions" data-attribute-direction="zdown"> <i class="fa fa-angle-double-down"> </i>&nbsp; Z </a>
								</div>
							</div>
						</div>
					
			
			
				</details>
			</div>
			
		</div>
		
    	
	</div>
		
		

</div>



<!-- HELP MODAL -->
<div class="modal fade" tabindex="-1" role="dialog"  aria-hidden="true" id="manula-modal">
	<div class="modal-dialog modal-lg">
		<div class="modal-content"></div>
	</div>
</div>
	