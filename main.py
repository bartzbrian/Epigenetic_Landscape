

# Brian Leighton Bartz <<<----------------------------------
# ---------->>> Python for a programmable 3D landscape model
# Inspired by C.H. Waddington's Epigenetic Landscape <<<----
# ------------------------------------------->>> Summer 2017
# ------------>>> Institute for Systems Biology: Seattle, WA
# Consilience Program Internship <<<------------------------
# ----------------------------->>> Free To Use (give credit)
# brianbartz1@gmail.com <<<---------------------------------


                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                                                                                                                                 
                                                                                                                                                      

import time
import Adafruit_PCA9685
import serial
import random

import assigner    #separate class that deals with tedious mappings (motor speeds, IR sensors to motors, etc)
import simulator   #separate script that handles all of the ODE simulation from the GRN paper
import LP          #sepearate class that handles the launchpad LED's and simulation parameters


#global objects (this is probably bad form but w/e)

#instantiate assigner class
ASS = assigner()

#instantiate launchpad class
lp = LP()

#establish serial connection to arduinos so sensor data can be accessed (these arguments need to be filled in before running. They change depending on the arduino's serial location) => ('location',baud-rate)
ser1 = serial.Serial('', ) #arduino mega 
ser2 = serial.Serial('', ) #arduino micro



#a class for handling each of the individual 25 motors
class motor:

        def __init__(self,address,channel,motornum):
                                        
            self.lv = None              #keeps track of the last sensor value this motor sent out         
            self.height = 0             #height will be defined as 0 being the middle position, with a max and min height of around -10 to 10(TBD)
            self.direction = 's'        #direction can be 's' for stopped, or 'u' and 'd' for up and down
            self.instruction = 0        #stores the motors current instruction when the main loop is runnign
            self.channel = channel      #the motors channel number on each of the servo breakout boards (0-15)
            self.address = address      #which of the two servo breakouts the motor is attached to
            self.pwm = self.i2cAddress(self.address)    #assigns a pwm object (from the adafruit library) based on the i2c address of its respective board
            self.speeds,self.ser = ASS.assign(self.address,self.channel)    #assigns individual motor speeds and serial index info per motor


        def calculate_relative_instruction(self,instruction):
            return -(self.height - instruction)


        def i2cAddress(self,address):						    # properly assign the right i2c address per motor
            if address == 0:
                pwm = Adafruit_PCA9685.PCA9685()
            elif address == 1:
                pwm = Adafruit_PCA9685.PCA9685(address=0x41)
            pwm.set_pwm_freq(60)
            return pwm


        #returns the current sensor value for each motor (zero is a white section of the encoder strip, 1 is black)
        def get_sensor_value(self):
            if self.ser[0] == 'ser1':
                
                vals = []
                while len(vals) != 15:
                    va = ser1.readline()
                    vals = [x for x in va.split(',')]

         
            elif self.ser[0] == 'ser2':
                vals = []
                while len(vals) != 12:
                    va = ser2.readline()
                    vals = [x for x in va.split(',')]
            
            
            #this handles the ValueError exception from being raised, preventing the dreaded sensor 
            #timeout error by handing back a stop value instead of the motor running forever
            try:
                v = int(vals[self.ser[1]])
            except:                               
                print 'serial error'     
                if self.lv == 1:
                    return 0
                else:
                    return 1
            
            if v > 150:
                self.lv = 1
                return 1
            else:
                self.lv = 0
                return 0       
            
        def up(self):
            self.pwm.set_pwm(self.channel,0,self.speeds[0])
            self.direction = "u"

        def down(self):
            self.pwm.set_pwm(self.channel,0,self.speeds[1])
            self.direction = "d"

        def stop(self):
            self.pwm.set_pwm(self.channel,0,self.speeds[2])
            self.direction = "s"


#   A class which handles the entire group of motors, and addresses them while running the simulation	
	def __init__(self):

        self.num_motors = 25
        self.motors = []
        self.order = [3,16,23,9,2,14,21,8,24,11,5,17,6,19,1,13,4,15,22,10,0,12,18,7,20]                         #defines the order for the motors to move in
        for x in xrange(0,self.num_motors):             #creates a list of individual motor objects based on their i2c address locations
            if x > 16:
                m = motor(1,(x-17),x)
                self.motors.append(m)
            else:
                m = motor(0,x,x)
                self.motors.append(m)


    def gen_rando(self):
        return [random.randrange(-6,6,1) for _ in range (25)]


#   Main loop (this is probably written with horrible form, and I am sorry. I do my best...). Buttons on the launchpad will allow a person 
#   to change the values of parameters in the bistable switch GRN model described in this paper: 

#                               https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3098230/

#   This model is then simulated (MANY THANKS TO DAVID GIBBS AT THE INSTITUTE FOR SYSTEMS BIOLOGY FOR THAT SIMULATION CODE), with the resulting 
#   probabilities at certain xy protein concentrations mapped onto the Z axis of the physical model 
	
    def run_model(self):

        while True:

            #pull the model parameters from the launchpad (this function won't return until a complete set of new values have been entered, or the random button pressed)
            current_params = lp.get_params()

            #either run the model or generate a random set of instructions based on the launchpad result
            if len(current_params) == 8:
                print('running model on new set of parameters')
                current_instructions = simulator.get_Z_vals(current_params):
                print('generating landscape from the model')
                time.sleep(1)
            else:
                print('generating a random landscape')
                current_instructions = self.gen_rando()
                time.sleep(1)

            instructions_active = True
            count = 0


            #create the landscape
            while instructions_active:

            is_finished = True 

            #while the instructions are still active, iterate through each motor, moving them as necessary
            for x in xrange(0,self.num_motors):
                print 'iterating through motors. Currently at motor number: ' + str(x)

                #calculate instructions relative to current motor height on first iteration
                if count == 0:
                    self.motors[self.order[x]].instruction = self.motors[self.order[x]].calculate_relative_instruction(current_instructions[x])
                    print 'new instruction for motor ' + str(x) + ' is ' + str(self.motors[self.order[x]].instruction)

                #if the relative instruction is not 0 (as in the motor needs to move) enter the moving loop and notify outer loop it isn't finished yet (because at least one motor still needs to move)
                if self.motors[self.order[x]].instruction != 0:
                    print('the instruction is not zero, moving into move loop')
                    is_finished = False
                    moving = True
                else:
                    print('the instruction is 0, moving on')
                    moving = False

                while moving:

                    #pull current sensor value
                    current_sensor_value = self.motors[self.order[x]].get_sensor_value()
                    print('the the current sensor value is ' + str(current_sensor_value))
                    #if the motor isn't moving yet
                    if self.motors[self.order[x]].dir == 's':
                        print('the motor is not yet moving, beginning now')
                        #init prev value as the current
                        previous_sensor_value = current_sensor_value

                        #move motor in proper direction according to instruction
                        if self.motors[self.order[x]].instruction > 0:
                            print('moving up')
                            self.motors[self.order[x]].Up()
                        elif self.motors[self.order[x]].instruction < 0:
                            print('moving down')
                            self.motors[self.order[x]].Down()

                    #if the motor has moved to a new section of the encoder strip
                    if previous_sensor_value != current_sensor_value:
                        print('the encoder strip has changed, now stopping')

                        #depending on the direction it moved, change the height values and instructions for the next iteration accordingly
                        if self.motors[self.order[x]].dir == 'u':
                            self.motors[self.order[x]].height += 1
                            self.motors[self.order[x]].instruction -= 1
                        elif self.motors[self.order[x]].dir == 'd':
                            self.motors[self.order[x]].height -= 1
                            self.motors[self.order[x]].instruction += 1
                
                        #stop moving
                        self.motors[self.order[x]].Stop()
                        moving = False

                    #update prev sensor value so as to detect when the change occurs
                    previous_sensor_value = current_sensor_value

            count += 1

            #if all motors were iterated through and none need to move, then the instruction is complete and the loop should be broken
            if is_finished:
                print('all instructions were zero, done with movements')
                instructions_active = False



#   provides a mode to hand set the heights to a zero location on the box before running the model
    def init_mode(self):

        stop_button = 207 #button to break this mode and move on to the model
        lp.init_mode_LED() #set LEDs for init mode
        init = True

         while init:
            if lp.controller.ButtonStateRaw() != []:
                xs = lp.controller.ButtonStateRaw()
                if xs[0] in lp.init_map:
                    ms = lp.init_map[xs[0]]
                if xs[1] == False:
                    self.motors[ms[0]].Stop()
                elif xs[1] == True:
                    if ms[1] == 'u':
                        self.motors[ms[0]].Up()
                    elif ms[1] == 'd':
                        self.motors[ms[0]].Down()

                if xs[0] == stop_button:
                    lp.controller.Close()q
                    init = False


#   moves the motors a bit during the calibration portion of the arduino code, exposing the sensors to the light and dark values of the encoder rings
    def calibrate(self):
        for x in xrange(0,self.num_motors):
            self.motors[x].down()
        time.sleep(3)
        for x in xrange(0,self.num_motors):
            self.motors[x].up() 
        time.sleep(3)
        for x in xrange(0,self.num_motors):
            self.motors[x].stop() 

             


if __name__ == "__main__":
    print('starting up\n')
    print('calibrating sensors\n')

    #instantiate the motor_group class
    cluster = motor_group()

    #have the motors move a bit, so as to calibrate the IR sensors to the encoder rings
    cluster.calibrate()

    #wait some time for the arduinos to finish doing their calibration and begin sending their serial data out
    time.sleep(15)
    print('5 more seconds...')
    time.sleep(5)
    print('done calibrating\n')

    #initialize the motor positions in the center of the box using the launchpad
    print('entering initialization mode, zero out all the motors then press the top right button\n')
    cluster.init_mode()
    print('leaving init mode\n')

    #run the model
    print('running model\n')
    cluster.run_model()



