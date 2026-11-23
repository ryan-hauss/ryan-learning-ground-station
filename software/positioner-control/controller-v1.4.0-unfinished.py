#====================================================================
# RLGS Gen 1 Controller v1.4.0 (TUI Update!) UNFINISHED!!!
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
# Azimuth pins are digital pins 2, 3, 4, 5
# Elevation pins are digital pins 6, 7, 8, 9
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

import msvcrt
from datetime import datetime, timezone

#====================================================================
# Bunch of Variables
#--------------------------------------------
# what it says on the tin
DEBUG = False

# 4096 half-steps per 360-degree rotation
STEPS_PER_DEGREE = 4096.0 / 360.0  # ~11.3778 steps per degree

# 4096 steps = 360 degrees on these kit gears (~11.38 steps per degree)
MAX_AZ_STEPS = 2048   # +180° Max Right
MIN_AZ_STEPS = -2048  # -180° Max Left

# --- Physical Rig Clearance Limits (Degrees) ---
MAX_EL_DEG = 51.0    # Soft stop before mechanical collision
MIN_EL_DEG = -46.0   # Soft stop before antenna touches base

# Automatic step limit calculation
MAX_EL_STEPS = round(MAX_EL_DEG * STEPS_PER_DEGREE)
MIN_EL_STEPS = round(MIN_EL_DEG * STEPS_PER_DEGREE)

# Shared Memory Tracking Variables (Assume we boot up pointing at Home 0,0)
current_az = 0
current_el = 0

# --- Speed & Jog Configuration ---
STEP_DELAY = 0.008  # Time per step in seconds (0.002 = fast/max, 0.004 = slower/high torque)
JOG_BURST = 4        # Number of steps dispatched per keyboard hit

# other stuff
active_mode = "CONFIG"
az_limit_alerted = False
el_limit_alerted = False

#====================================================================
# Arduino board initialization
#--------------------------------------------
# set port
port = 'COM6'

# Open the raw USB pipe to board
ser = serial.Serial(port, 115200, timeout=1)
time.sleep(2.0) # Hold for 2 seconds to let the Arduino finish booting
#====================================================================
# TUI Drawing Functions
#--------------------------------------------

def draw_header(subtitle, active_tab):
    tabs = ["Config", "Home", " Jog ", "Angle", "Pass", "Docs"]
    
    # Build the tab row: "│Config││Home││ Jog ││Angle││Pass││Docs│"
    tab_row = "".join(f"│{t}│" for t in tabs)
    
    # Build the dynamic floor: open "╛    ╘" under active_tab, "╧════╧" under others
    floor_tabs = "".join(
        f"╛{' ' * len(t)}╘" if t.strip() == active_tab else f"╧{'═' * len(t)}╧"
        for t in tabs
    )

    print("╭────────────────────────────────────────────────────────────.✧★｡.─╮")
    print("│ RLGS Controller          ╭──────╮╭────╮╭─────╮╭─────╮╭────╮╭────╮ │")
    print(f"│ {subtitle:<25}{tab_row} │")
    print(f"╞══════════════════════════{floor_tabs}═╡")
    #Start with the left double-bar: floor = "╞" + ("═" * 26)
    #Loop over each tab in tabs:
    # if tab.strip() == active_tab: append "╛" + (" " * len(tab)) + "╘" elif: append "╧" + ("═" * len(tab)) + "╧" Finish with the right end: floor += "═╡"

def draw_telemetry(error=False, clock="linear"):
    # Stacked: config, home, jog, angle Linear: everytning else

    # convert steps into degrees here cuz el/az_degree isn't a global varable
    az_deg = round(current_az / STEPS_PER_DEGREE)
    el_deg = round(current_el / STEPS_PER_DEGREE)

    # get time
    local_str = datetime.now().strftime("%I:%M%p")           # e.g., "06:28PM"
    utc_str   = datetime.now(timezone.utc).strftime("%H:%M") # e.g., "01:28"

    # draw!
    if clock == "stacked":
        print("│ ╭─────────────────────┐┌─────────────────────╮   ╭────────────╮ │")
        if error:
            # Error mode!!!!!
            print("│ │EL: +###° (#### step)││AZ: -###° (#### step)│   │ ##:## PM   │ │")
            print("│ ╰─────────────────────┘└─────────────────────╯   │ ##:## UTC  │ │")  
        else:
            local_spaced = datetime.now().strftime("%I:%M %p")  # e.g., "06:48 PM" (8 chars)
            print(f"│ │EL: {el_deg:+4d}° ({current_el:4d} step)││AZ: {az_deg:+4d}° ({current_az:4d} step)│   │ {local_spaced}   │ │")
            print(f"│ ╰─────────────────────┘└─────────────────────╯   │ {utc_str} UTC  │ │")
    else:
        print("│ ╭─────────────────────┐┌─────────────────────╮╭─────────────────╮ │")
        if error:
            # Error mode!!!!!
            print("│ │EL: +###° (#### step)││AZ: -###° (#### step)││##:##PM ##:## UTC│ │")
        else:
            print(f"│ │EL: {el_deg:+4d}° ({current_el:4d} step)││AZ: {az_deg:+4d}° ({current_az:4d} step)││{local_str:>7} {utc_str:>5} UTC│ │")
        print("│ ╰─────────────────────┘└─────────────────────╯╰─────────────────╯ │")

def draw_footer(mode_key, debug=None):
    if debug is None:
        debug = DEBUG   # Look up the live global DEBUG toggle 
    #Prints the bottom prompt bar (splitting off the │Debug│ box on the left if debug=True) plus the .｡✧★. bottom border

    FOOTER_PROMPTS = {
        "CONFIG": "Enter a number to select a mode",
        "HOME":   "Enter a number to select an operation",
        "JOG":    "Hold WASD OR Arrow Keys to jog, press Q to quit",
        "ANGLE_SELECT": "Enter a number to select a mode",
        "ANGLE_ABS":    "Enter target Azimuth and Elevation angles",
        "ANGLE_REL":    "Enter Azimuth & Elevation degree changes (+/-)",        
        "PASS":   "Enter a number to select a pass",
        "DOCS":   "Enter a number to select a document",
    }
    prompt = FOOTER_PROMPTS[mode_key]
    if debug == True:
        print("│ ╭─────┐┌────────────────────────────────────────────────────────╮ │")
        print(f"│ │Debug││ {prompt[:54]:<54} │ │")
        print("│ ╰─────┘└────────────────────────────────────────────────────────╯ │")
    else:
        print("│ ╭───────────────────────────────────────────────────────────────╮ │")
        print(f"│ │ {prompt:<61} │ │")
        print("│ ╰───────────────────────────────────────────────────────────────╯ │")
    print("╰─.｡✧★.────────────────────────────────────────────────────────────╯")


def draw_config_screen():
    draw_header("Configuration Menu", "Config")
    draw_telemetry(clock="stacked")

    print("│  Option 1: Home & Calibration                      ╰────────────╯ │")
    print("│  Option 2: Jog Mode                                               │")
    print("│  Option 3: Angle Input Mode                                       │")
    print("│  Option 4: Satellite Pass Mode                                    │")
    print("│  Option 5: Quit the Program (or enter Q)                          │")
    print("│  Option 6: Documentation                                          │")

    draw_footer("CONFIG")

def draw_home_cal_screen():
    draw_header("Home & Calibration", "Home")
    draw_telemetry(clock="stacked")

    print("│  Select an operation to perform:                   ╰────────────╯ │")
    print("│  1. Go to Home (0.0°, 0.0°)                                       │")
    print("│  2. Set Current Position as Home (Zero)                           │")
    print("│  3. Calibrate Limits (WIP)                                        │")
    print("│                                                                   │")
    print("│  Each of these will send you back to Config Menu when complete    │")

    draw_footer("HOME")


def draw_jog_screen():
    draw_header("Manual Jog Mode", " Jog ")
    draw_telemetry(clock="stacked")
    
    print("│  Hold W/A/S/D OR Arrow Keys to manually jog axes.  ╰────────────╯ │")
    print("│  Press Q to quit.                                                 │")
    print("│                                                                   │")
    print("│ ╭────────────────────────────────╮                                │")
    ####### COME BACK TO FIX THIS #######
    print("│ │ Current Input: [#], +## (####) │                                │") 
    print("│ ╰────────────────────────────────╯                                │")

    draw_footer("JOG")


def draw_angle_screen(submode="ANGLE_SELECT"):
    draw_header("Angle Input Mode", "Angle")
    draw_telemetry(clock="linear")

    if submode == "ANGLE_SELECT":
        print("│  Move positioner using angles. Select a mode:                     │")
        print("│  Option 1: Absolute Degree (Set an angle for AZ and EL, postioner │")
        print("│            moves to it)                                           │")
        print("│  Option 2: Relative Degree (Enter +/- number of degrees, positoner│")
        print("│            adds that to the total angle and moves to it)          │")
        print("│  (To switch modes, enter S and select from this menu again)       │")

    elif submode == "ANGLE_ABS":
        print("│  Move positioner using angles. [Absolute Degree Selected]         │")
        print("│  (To change to relative degree, enter S and select from the menu) │")
        print("│ ╭───────────────────────────────────────────╮                     │")
        print("│ │ Moving AZ: +###°/+###° (+####/#### step)  │                     │")
        print("│ │ Moving EL: -###°/-###° (-####/#### step)  │                     │")
        print("│ ╰───────────────────────────────────────────╯                     │")

    elif submode == "ANGLE_REL":
        print("│ ╭───────────────────────────────────────────────────────────────╮ │")
        print("│ │ ╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲  UNDER CONSTRUCTION   ╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱ │ │")
        print("│ │ ╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱  Mode in development  ╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲╱╲ │ │")
        print("│ ╰───────────────────────────────────────────────────────────────╯ │")
        print("│   S to go back to angle mode select                               │")
        print("│   Q to go back to config                                          │")

    draw_footer(submode)



#====================================================================
# Functions
#--------------------------------------------
# Coded "Limit Switches"
def send_safe_step(axis, direction):
    # Pull the memory counters out of the main brain so this function can modify them
    global current_az, current_el, az_limit_alerted, el_limit_alerted
    
    if axis == 'AZ':
        # Calculate what the position WOULD be if we took this step
        predicted_position = current_az + direction
        
        # LOGIC GATE: Is the predicted spot safely inside our wire limits?
        if MIN_AZ_STEPS <= predicted_position <= MAX_AZ_STEPS:
            current_az = predicted_position  # Commit the step to memory
            az_limit_alerted = False  # Re-arm the alert because we are moving safely
            # SHORTCUT: If direction is 1, send 'A' (CW). Otherwise, send 'a' (CCW)
            command = 'A' if direction == 1 else 'a'
            ser.write(command.encode())      # Wrap the letter into bytes and ship it
        else:
            if not az_limit_alerted:
                print("[WARN] Azimuth limit reached! Wire safety mechanism engaged.")
                az_limit_alerted = True  # Disarm so it won't print again until re-armed
            
    elif axis == 'EL':
        predicted_position = current_el + direction
        
        # LOGIC GATE: Is the predicted tilt safely between flat horizon and the ceiling?
        if MIN_EL_STEPS <= predicted_position <= MAX_EL_STEPS:
            current_el = predicted_position  # Commit the step to memory
            el_limit_alerted = False  # Re-arm the alert because we are moving safely
            # SHORTCUT: If direction is 1, send 'E' (Up). Otherwise, send 'e' (Down)
            command = 'E' if direction == 1 else 'e'
            ser.write(command.encode())      # Wrap the letter into bytes and ship it
        else:
            if not el_limit_alerted:
                print("[WARN] Elivation limit reached! Wire safety mechanism engaged.")
                el_limit_alerted = True  # Disarm so it won't print again until re-armed

# Angle move function, uses send_safe_step
def move_to_angle(target_az_deg, target_el_deg):
    # Pull the memory counters out so this function can modify them
    global current_az, current_el

    # Convert degrees to target steps
    target_az_steps = round(target_az_deg * STEPS_PER_DEGREE)
    target_el_steps = round(target_el_deg * STEPS_PER_DEGREE)

    # Check limits
    if not (MIN_AZ_STEPS <= target_az_steps <= MAX_AZ_STEPS and MIN_EL_STEPS <= target_el_steps <= MAX_EL_STEPS):
        print("[ERROR] Target angle exceeds safe limits! Slew aborted.")
        return

    # Calculate deltas, step counts, and directions for BOTH axes:
    delta_az = target_az_steps - current_az
    steps_az = abs(delta_az)
    dir_az = 1 if delta_az > 0 else -1

    delta_el = target_el_steps - current_el
    steps_el = abs(delta_el)
    dir_el = 1 if delta_el > 0 else -1

    # initialize two "buckets" starting at zero
    accum_az = 0
    accum_el = 0

    # compare the positive step distances (abs(delta_az) and abs(delta_el) using max() function:
    total_ticks = max(steps_az, steps_el)

    # Zero-Move Guard (total_ticks == 0):
    if total_ticks == 0:
        print("[INFO] Dish is already at target angle.")
        return

    # Accumulator Loop!
    for _ in range(total_ticks):
        # Track if either motor moved on this tick:
        stepped = False

        # Pour into the Azimuth bucket 
        accum_az += steps_az
        # & check for overflow:
        if accum_az >= total_ticks:
            accum_az -= total_ticks
            send_safe_step('AZ', dir_az)
            stepped = True

        # Pour into the Elevation bucket
        accum_el += steps_el
        # & check for overflow:
        if accum_el >= total_ticks:
            accum_el -= total_ticks
            send_safe_step('EL', dir_el)
            stepped = True

        # Pause for coil dwell time (STEP_DELAY):
        if stepped:
            time.sleep(STEP_DELAY)
    
    
#====================================================================
# UI Time yay
#--------------------------------------------

def run_config_mode():
    global current_az, current_el, az_limit_alerted, el_limit_alerted
    az_deg = current_az / STEPS_PER_DEGREE
    el_deg = current_el / STEPS_PER_DEGREE

    draw_config_screen()
    
    while True:
        choice = input().strip().lower()
        if choice == "1":
            return "JOG"
        elif choice == "2":
            return "ANGLE"
        elif choice == "3":
            current_az = 0
            current_el = 0
            az_limit_alerted = False
            el_limit_alerted = False
            print("[INFO] Home origin calibrated to current position (0.0°, 0.0°).")
            break
        elif choice in ("4", "q"):
            return "QUIT"
        else:
            print("\n╭───────────────────────────────────.★ ..─╮")
            print("│ Invalid option, please type a number:")
            print("│ Option 1: Jog Mode")
            print("│ Option 2: Angle input Mode")
            print("│ Option 3: Set Current Position as Zero")
            print("│ Option 4: Quit the Program (or press Q)")
            print("╰─..★ .───────────────────────────────────╯")

def run_jog_mode():
    print("\n╭───────────────────────────────────.★ ..─╮")
    print("│ [ACTIVE] Continuous Jog Mode Online.")
    print("│ Hold W/A/S/D to move. Press Q to quit.")
    print("╰─..★ .───────────────────────────────────╯")

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch().decode('utf-8', errors='ignore').lower()

            if key == 'q':
                print("\nExiting jog mode...")
                return "CONFIG"

            # Pulse a burst of steps for each keystroke event
            for _ in range(JOG_BURST):
                if key == 'd': send_safe_step('AZ', 1)
                elif key == 'a': send_safe_step('AZ', -1)
                elif key == 'w': send_safe_step('EL', 1)
                elif key == 's': send_safe_step('EL', -1)
                
                time.sleep(STEP_DELAY)
        else:
            time.sleep(0.01)

def run_angle_mode():
    # To calculate with:
    global current_az, current_el
    
    while True:
        # Calculate current angles
        az_deg = current_az / STEPS_PER_DEGREE
        el_deg = current_el / STEPS_PER_DEGREE

        submode = "ANGLE_SELECT"

        # UI
        #Keep a local submode = "ANGLE_SELECT" variable at the top of run_angle_mode(). 
        # Your outer while True: loop inside run_angle_mode() simply checks which submode is active:
        #    
        # When submode == "ANGLE_SELECT":
        # Call draw_angle_screen("ANGLE_SELECT").
        # Read choice = input().strip().lower(). 
        # "1"  set submode = "ANGLE_ABS".
        # "2" set submode = "ANGLE_REL".
        # "q" return "CONFIG" (exits Angle Mode back to the master loop).   
        # Anything else: loop back and redraw "ANGLE_SELECT".
        # 
        # When submode == "ANGLE_ABS":
        # Call draw_angle_screen("ANGLE_ABS").
        # Read raw_input = input().strip().   
        # If raw_input.lower() == 'q': return "CONFIG".   
        # If raw_input.lower() == 's': set submode = "ANGLE_SELECT" and continue 
        # (switches right back to the Angle Select menu without leaving Angle Mode).
        # 
        # Otherwise, parse the two numbers and call move_to_angle(target_az, target_el).   
        # 
        # When submode == "ANGLE_REL" (Under Construction):Call draw_angle_screen("ANGLE_REL").
        # Read raw_input = input().strip().lower().
        # If 'q': return "CONFIG".
        # If 's' (or anything else): set submode = "ANGLE_SELECT".

        while True:
            if submode == "ANGLE_SELECT":
                draw_angle_screen("ANGLE_SELECT")
                if input().strip().lower() == 1:
                    submode = "ANGLE_ABS"
                    # "and continue?"
                elif input().strip().lower() == 2:
                    submode = "ANGLE_REL"
                    # "and continue?"
                elif input().strip().lower() == q:
                    return "CONFIG"
                else:
                    #idk how to "switches right back to the Angle Select menu without leaving Angle Mode"

            elif submode == "ANGLE_ABS":
                draw_angle_screen("ANGLE_ABS")
                # "Read raw_input = input().strip()" how? can you get an inpu without a prompt? i mean obviously that's how we get here
                if raw_input.lower() == 'q': 
                    return "CONFIG"  
                elif raw_input.lower() == 's': 
                    submode = "ANGLE_SELECT" 
                    continue #(again what does continue do?)
                    # "(switches right back to the Angle Select menu without leaving Angle Mode)"
                ###### I just copy pasted eveything that was here previously to here#######
                # Split into two parts 
                parts = parts = raw_input.replace(',', ' ').split()
                
                # Check that you got both numbers
                if len(parts) != 2:
                    print("[ERROR] Please enter two numbers separated by a space or comma (e.g., '30 20').")
                    continue
                
                try:
                    target_az = float(parts[0])
                    target_el = float(parts[1])
                except ValueError:
                    print("[ERROR] Those weren't valid numbers! Try again.")
                    continue
                
                # Move the positioner!
                move_to_angle(target_az, target_el)

            elif submode == "ANGLE_REL":
                draw_angle_screen("ANGLE_REL")
                # Read raw_input = input().strip().lower().
                        # If 'q': return "CONFIG".
                        # If 's' (or anything else): set submode = "ANGLE_SELECT".

        ### Old stuff
        ## Prompt for input 
        #raw_input = input("Enter Target Azimuth & Elevation or 'q' to return: ").strip()
        ## Check for 'q'
        #if raw_input.lower() == 'q':
            #return "CONFIG"

        



while active_mode != "QUIT":
    if active_mode == "CONFIG":
        active_mode = run_config_mode()
    elif active_mode == "ANGLE":
        active_mode = run_angle_mode()
    elif active_mode == "JOG":
        active_mode = run_jog_mode()
