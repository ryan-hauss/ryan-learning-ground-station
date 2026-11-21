# 🛰️ November 7th Session Summary
```Unset
mdate: 2026-11-7 21:00
tags:
  - CubeSat
  - RLGS
  - Logbook
```

**━━━━━━ . °‧ 𓆝  𝙻𝚘𝚐𝚋𝚘𝚘𝚔 Home  °‧ 𓆝 𓆟 𓆞 ·。**  
**Project:** Open Orbit RLGS (Ryan Learning Ground Station) — Gen R1  
**Date:** November 7  
**Time / Finish:** Concluded at 10:45 PM  
**Lead:** Ryan H. (GSN Team Lead, CSU Fort Collins)  

---

#### **1. Version & Subsystem Scope Tracking**

**Python Controller:** Upgraded from **v1.1 ➔ v1.2.1**

* Built and verified the two-state Finite State Machine (`run_jog_mode` and `run_config_mode` linked by a central master loop).
* Added edge-triggered one-shot limit alerts to eliminate 120 Hz terminal flooding.
* Converted system coordinate tracking and soft boundaries from raw steps to human degrees ($^\circ$).
* Added live telemetry readouts inside the styled ASCII configuration dashboard.
**Arduino Firmware:** **v1.0 (Unchanged / Locked)**
* Verified latched pin states and driver LED illumination as normal holding torque behavior. (though i do want to fix this)
**Rotator Hardware (Gen R1):** **Upgraded Power Infrastructure & Calibrated Payload**
* Bypassed the Elegoo MB102 regulator using a female DC barrel-to-screw-terminal adapter, feeding a dedicated 5.0V / 3.0A (15W) rail directly to both drivers in parallel with shared star-grounding.
* Installed the target antenna onto the Elevation bracket and empirically calibrated mechanical clearances.
* Diagnosed Azimuth base tipping due to Center of Gravity (CG) displacement outside the base support polygon; resolved via bench clamping.
**RF / SDR Subsystem:** **Architecture & Hardware Planning**
* Evaluated Adafruit GPS integration constraints (3-USB-port laptop limit, single Arduino hardware UART) and planned a Time-Division Multiplexed architecture.

---

#### **2. Key Technical Findings & Changes in v1.2.1**

**The Linear Regulator Dropout Trap:**

* Diagnosed that feeding 5.0V into the Elegoo power module's barrel jack starved the onboard AMS1117 regulator and protection diode ($V_{\text{drop}} \approx 1.9\text{V}$ total), causing motor undervoltage ($\sim 3.5\text{V}$) and torque loss. Direct 5.0V rail wiring restored 100% rated motor torque.
**FSM Architecture & Bug Elimination:**
* Encapsulated real-time non-blocking jogging (`msvcrt`) and blocking human UI (`input()`) into isolated functions that return target state strings.
* Resolved the String vs. Integer Trap where `input()` text `"1"` failed comparison against integer `1`.
* Resolved the Silent None Trap that caused the master state loop to freeze in an unhandled infinite loop.
**Edge-Triggered Safety Alerts:**
* Replaced continuous terminal spam with rising-edge state flags (`az_limit_alerted`, `el_limit_alerted`) that alert the user once upon boundary collision and automatically re-arm upon reversing away from the stop.
**Kinematics & Antenna Clearance Calibration:**
* Implemented `STEPS_PER_DEGREE = 4096.0 / 360.0` ($\approx 11.3778\text{ steps/}^\circ$) and fixed-width f-string format specifiers (`{az_deg:+6.1f}°`, `{current_az:5d}`) to prevent ASCII border distortion.
* Empirically measured Elevation collision limits with the antenna mounted: $-51.0^\circ$ (-580 steps) to $+54.5^\circ$ (+620 steps).
* Configured safe software limits with safety margins: `MIN_EL_DEG = -46.0°` and `MAX_EL_DEG = 51.0°`.

---

#### **3. Conceptual Foundations Established for v1.3**

**Bresenham’s Line Algorithm / DDA Vector Drive:**

* Formalized the accumulator ("water bucket") pacing method to interleave discrete single-byte commands across the single serial pipe, allowing coordinated, simultaneous-feeling diagonal slewing to exact degree coordinates.
**Time-Division Multiplexed GPS Architecture:**
* Designed a strategy to read the Adafruit GPS via the Arduino's `SoftwareSerial` exclusively during `CONFIG` mode, completely muting interrupts during `JOG` mode to prevent motor stepping stutter while operating within the laptop's 3-USB-port constraint.
**Gen R2 Mechatronics Blueprint:**
* Reviewed the 28BYJ-48 center-tap cut bipolar modification, 1/16 microstepping resolution math for direct-drive NEMA 17s ($8.89\text{ steps/}^\circ$), and heatsinkless A4988 thermal duty-cycle pulsing via the `ENABLE` pin.

---

#### **4. Immediate Agenda for Next Lab Session**

1. Implement the Bresenham / DDA coordinated vector slewing function (`move_to_angle(az, el)`) and integrate it as Option 3 in the Config menu.
2. Add Arrow Key navigation (decoding Windows two-byte extended scan codes) alongside WASD into `run_jog_mode()`.
3. Clamp the Azimuth base to the bench and run a full $\pm 180^\circ$ pan calibration test.
