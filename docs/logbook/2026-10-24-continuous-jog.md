# 🛰️ October 24 Session Summary

```Unset
mdate: 2026-10-24 21:00
tags:
  - CubeSat
  - RLGS
  - Logbook
```

**━━━━━━ . °‧ 𓆝  𝙻𝚘𝚐𝚋𝚘𝚘𝚔 Home  °‧ 𓆝 𓆟 𓆞 ·。**  
**Project:** Open Orbit RLGS (Ryan Learning Ground Station) — Gen R1  
**Subsystem:** Positioner Controller & Firmware Integration

**Date:** October 24  
**Time / Duration:** 1:00 PM – 8:39 PM (~7.5 hrs)  
**Lead:** Ryan H. (GSN Team Lead, CSU Fort Collins)

**Objective:** Transitioning from discrete, line-buffered step commands to smooth, continuous manual jogging and establishing motion architecture.

---

#### **1. Version & Subsystem Scope Tracking**

**Python Controller:** Upgraded from **v1.0 ➔ v1.1**

* Integrated non-blocking raw console polling via Windows `msvcrt`.
* Implemented continuous manual jog with parameter tuning (`STEP_DELAY = 0.008`, `JOG_BURST = 4`).
**Arduino Firmware:** **v1.0 (Unchanged / Locked)**
* Pin mapping verified: Azimuth (Pins 2–5), Elevation (Pins 6–9) at `115200` baud.
**Rotator Hardware (Gen R1):** **Unchanged**
* Dual 28BYJ-48 motors, balsa/bracket frame, MB102 5V rail fed by 9V battery.
**RF / SDR Subsystem:** **No Progress / Unchanged**
* RTL-SDR Blog V4, Heltec LoRa/GPS node, and GNU Radio work held for later phases.

---

#### **2. Technical Milestones Completed**

**Eliminated Line-Buffered Input/Output Bottleneck:**

* Replaced blocking `input()` calls (which required pressing Enter for every command) with Windows-native, non-blocking low-level console I/O using Python's built-in `msvcrt` module (`msvcrt.kbhit()` and `msvcrt.getch()`).
* Verified that holding a key now streams continuous motion by leveraging the operating system’s hardware keyboard repeat events.
* Plan to add arrow keys
**Diagnosed Kinematic & Electrical Constraints:**
* Identified the software bottleneck: at standard Windows repeat rates (~30 Hz), firing only 1 step per key event limits speed to $\sim 2.6^\circ\text{/s}$.
* Identified the electromagnetic limit: Step intervals below ~2 ms skipped under mechanical load. Stepping faster than the coil's L/R time constant prevents the magnetic field from saturating, causing rotor stalls / skipped steps.
* Decoupled step pulses from keyboard repeat rate by introducing `STEP_DELAY` (coil dwell time) and `JOG_BURST` (steps per repeat event).
* Settled on **STEP_DELAY = 0.008 (8 ms / 125 Hz)** for maximum holding/pull-in torque and **JOG_BURST = 4** to prevent keystroke queue lag after release.
* `STEP_DELAY = 0.008` (8 ms dwell $\approx 125\text{ Hz}$): Maximizes torque to eliminate skipped steps.
* `JOG_BURST = 4`: Provides a steady, responsive slew rate without creating buffer backlogs or post-release input lag.



---

#### **2. Architecture & Conceptual Foundations Established for v1.2**

**Step Interleaving / DDA Accumulator Math / Bresenham Vector Math:**

* Formalized the "water bucket" algorithm for multi-axis motion, demonstrating how integer accumulator math synchronizes Azimuth and Elevation to reach a target coordinate concurrently for future diagonal moves.
**Extended Key Scanning Mechanics:**
* Identified the Windows two-byte sequence (`\x00` / `\xe0` prefix + scan code) required to capture directional Arrow Keys alongside standard WASD inputs.
**Finite State Machine (FSM) Design:**
* Outlined the dual-mode architecture:
* **JOG_MODE:** Real-time, non-blocking motor execution (WASD + Arrow keys).
* **CONFIG_MODE:** Motor hold active; interactive ASCII terminal dashboard for live telemetry, speed profile selection, and electronic re-zeroing (`current_az = 0`, `current_el = 0`).



---

#### **3. Immediate Next Steps (Next Session)**

1. Implement the two-byte extended scan reader to map **Arrow Keys** alongside WASD.
2. Build the **FSM skeleton** and ASCII terminal dashboard for switching between Jog and Config modes.
3. Test Elevation axis holding torque once the RF antenna payload is physically mounted to verify gravity moment compensation.
