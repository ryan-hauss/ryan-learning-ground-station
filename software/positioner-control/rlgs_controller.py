#====================================================================
# RLGS Gen 1 Controller v1.0
#====================================================================
# Open Orbit RLGS (Ryan Learning Ground Station)
# Coded by Ryan H
#-----------------------------------------------------
# Thanks to:
# Google Gemini I guess
# GNU radio guided tutorials
# I will add websites / people / youtube channels etc here as resources are found and used
# And my friend Conner who gave me lots of advice and spent several hours helping me first learn python
#-----------------------------------------------------
# Notes:
# You need time and serial installed on your python venv
# You need to install the custom Arduino Positioner Controller Firmware on the Arduino
# This program will not work without an Arduino connected (or if you have the wrong port!)
# You need to set your laptop port as the port = variable
# V1.0 is made for Gen R1 positioner with 28BYJ-48 stepper motors, and ULN2003A controllers, and 9V battery
# Azimuth pins are digital pins 1, 2, 3, 4
# Elevation pins are digital pins 5, 6, 7, 8
# You will need an external power supply connected to the motor drivers and grounded to the Arduino
# To end the program, ctrl C
# In case of emergency, unplug the Arduino from the laptop or unplug the affected item from the Arduino
#====================================================================
# Import a bunch of stuff
#--------------------------------------------
# For eeping
import time
# To communicate with Arduino
import serial

#====================================================================
# Bunch of Variables
#--------------------------------------------
# 4096 steps = 360 degrees on these kit gears (~11.38 steps per degree)
MAX_AZ_STEPS = 2048   # +180° Max Right
MIN_AZ_STEPS = -2048  # -180° Max Left
MAX_EL_STEPS = 1024   # +90° Max Up (Ceiling)
MIN_EL_STEPS = -1024  # -90° Max Down (Floor / Table base limit)

# Shared Memory Tracking Variables (Assume we boot up pointing at Home 0,0)
current_az = 0
current_el = 0

#====================================================================
# Arduino board initialization
#--------------------------------------------
# set port
port = 'COM6'

# Open the raw USB pipe to board
ser = serial.Serial(port, 115200, timeout=1)
time.sleep(2.0) # Hold for 2 seconds to let the Arduino finish booting

#====================================================================
# Functions
#--------------------------------------------
# Coded "Limit Switches"
def send_safe_step(axis, direction):
    # Pull the memory counters out of the main brain so this function can modify them
    global current_az, current_el
    
    if axis == 'AZ':
        # Calculate what the position WOULD be if we took this step
        predicted_position = current_az + direction
        
        # LOGIC GATE: Is the predicted spot safely inside our wire limits?
        if MIN_AZ_STEPS <= predicted_position <= MAX_AZ_STEPS:
            current_az = predicted_position  # Commit the step to memory
            
            # SHORTCUT: If direction is 1, send 'A' (CW). Otherwise, send 'a' (CCW)
            command = 'A' if direction == 1 else 'a'
            ser.write(command.encode())      # Wrap the letter into bytes and ship it
        else:
            print("[WARN] Azimuth limit reached! Wire safety mechanism engaged.")
            
    elif axis == 'EL':
        predicted_position = current_el + direction
        
        # LOGIC GATE: Is the predicted tilt safely between flat horizon and the ceiling?
        if MIN_EL_STEPS <= predicted_position <= MAX_EL_STEPS:
            current_el = predicted_position  # Commit the step to memory
            
            # SHORTCUT: If direction is 1, send 'E' (Up). Otherwise, send 'e' (Down)
            command = 'E' if direction == 1 else 'e'
            ser.write(command.encode())      # Wrap the letter into bytes and ship it
        else:
            print("[WARN] Elevation limit reached! Motor tilt halted to protect brackets.")

#====================================================================
# UI Time yay
#--------------------------------------------
# 3. INTERACTIVE MAIN RUNNER LOOP

try:
    print("\n=============================================")
    print("      SAFE GSN CONTROLLER CONSOLE ONLINE     ")
    print("=============================================")
    print("Controls: W (Up) | S (Down) | A (Left) | D (Right)")
    print("Press Ctrl+C at any time to exit safely.\n")
    
    while True:
        # Pause terminal and grab user keystroke, force it lowercase
        user_key = input("Enter command key (W/A/S/D): ").lower()
        
        # To make the movement obvious, we will pulse 50 single-step checks 
        # sequentially for every single keystroke.
        for _ in range(50):
            if user_key == 'd': send_safe_step('AZ', 1)    # Pan Right
            if user_key == 'a': send_safe_step('AZ', -1)   # Pan Left
            if user_key == 'w': send_safe_step('EL', 1)    # Tilt Up
            if user_key == 's': send_safe_step('EL', -1)   # Tilt Down
            
            # Crucial 3-millisecond delay to let the physical copper coils inside 
            # the motor magnetize and build physical torque before the next step arrives.
            time.sleep(0.003) 
            
        print(f"[TRACKING STATUS] Present Rig Vector ➔ Azimuth: {current_az} steps | Elevation: {current_el} steps")

# SAFETY NET: If user hits Ctrl+C, step down here out of the loop cleanly
except KeyboardInterrupt:
    print("\n[HALT] Closing USB serial channel safely. Positioner locked.")
    ser.close()
