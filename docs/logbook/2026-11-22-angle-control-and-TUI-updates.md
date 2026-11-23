# 🛰️ November 22 Session Summary

```unset
mdate: 2026-11-22 22:19
tags:
- CubeSat
- RLGS
- Logbook
```

**━━━━━━ . °‧ 𓆝  𝙻𝚘𝚐𝚋𝚘𝚘𝚔   °‧ 𓆝 𓆟 𓆞 ·。**

**Project:** Open Orbit RLGS (Ryan Learning Ground Station) — Gen R1  
**Subsystem:** Modular ASCII Text-Based User Interface (TUI) & Multi-Mode FSM Expansion  
**Date:** November 22  
**Time / Finish:** Concluded at 10:19 PM  
**Lead:** Ryan H. (GSN Team Lead, CSU Fort Collins)  
**Objective:** Transitioning the Python positioner controller from static, monolithic print blocks (`v1.2.1`) to a modular, fixed-width (`69`-character) ASCII Text-Based User Interface (`v1.4.0`) with dynamic tab navigation, live local/UTC clocks, debug prompt splitting, and expanded operational modes.

---

#### **1. Version & Subsystem Scope Tracking**

**Python Controller (`positioner/control-software/`):** **Upgraded from `v1.2.1` ➔ `v1.4.0` (In Progress)**

* Architected and implemented reusable 69-character TUI rendering helpers (`draw_header()`, `draw_telemetry()`, `draw_footer()`).


* Built complete screen layouts for `Config` (`draw_config_screen()`), `Home & Calibration` (`draw_home_cal_screen()`), `Manual Jog` (`draw_jog_screen()`), and `Angle Input` (`draw_angle_screen()` across `ANGLE_SELECT`, `ANGLE_ABS`, and `ANGLE_REL` sub-modes).


* Integrated the Bresenham / DDA accumulator slew function (`move_to_angle(target_az_deg, target_el_deg)`) and designed the nested sub-mode state loop for `run_angle_mode()`.

**Arduino Firmware (`positioner/firmware/uno_halfstep/`):** **v1.0.0 (Unchanged / Locked)**

* Existing 8-state half-step sequence (`115200` baud, Azimuth pins `2–5`, Elevation pins `6–9`) preserved without modification.



**Rotator Hardware (Gen R1):** **Unchanged**

* Dual 28BYJ-48 motors, balsa/bracket frame, direct `5.0V / 3.0A` rail, calibrated Elevation limits (`-46.0°` to `+51.0°`).



**RF / SDR & Satellite Subsystems (`sdr/`, `satellite/`):** **Unchanged / Deferred**

* Focus kept strictly on Gen R1 controller UI and state machine integration.

---

#### **2. Technical Milestones Completed**

**Modular 69-Character TUI Architecture:**

* **`draw_header(subtitle, active_tab)`:** Implemented dynamic file-folder tab generation across 6 tabs (`Config`, `Home`, `Jog`, `Angle`, `Pass`, `Docs`), dynamically opening the double-line floor (`╛    ╘`) beneath the active tab while sealing inactive tabs (`╧════╧`).


* **`draw_telemetry(error=False, clock="linear")`:** Encapsulated step-to-degree rounding (`round(current_az / STEPS_PER_DEGREE)`) and live `datetime` local/UTC clock formatting directly inside the telemetry helper so screen functions can call `draw_telemetry()` with zero arguments. Added support for both `"linear"` (3-line) and `"stacked"` (corner clock) layouts, plus an `error=True` placeholder mode (`+###°`).


* **`draw_footer(mode_key, debug=None)`:** Built a dictionary-driven (`FOOTER_PROMPTS`) bottom prompt bar tied to a global `DEBUG` toggle via a `None` sentinel check (`if debug is None: debug = DEBUG`), splitting out a `│Debug│` badge on the left and applying slice-and-pad safety clipping (`{prompt[:54]:<54}`) so long strings never break the right border.



**Fixed-Width F-String Alignment & Formatting:**

* Standardized on `:+4d` for signed whole-degree readouts (`+0°`, `-46°`, `+180°`) and `:4d` for unsigned step counts inside the split-seam `EL` and `AZ` telemetry cards so box walls remain aligned across all coordinate values.



**Multi-Screen Angle Input & Nested Sub-Mode State Machine:**

* Expanded `FOOTER_PROMPTS` with dedicated keys (`ANGLE_SELECT`, `ANGLE_ABS`, `ANGLE_REL`) to match the three Angle sub-screens.


* Designed a self-contained sub-state loop (`submode = "ANGLE_SELECT"`) inside `run_angle_mode()` so users can select Absolute Degree mode, preview the Relative Degree screen ("Under Construction"), or switch sub-modes (`S`) without adding extra states to the master loop.

---

#### **3. Architecture & Conceptual Foundations Established**

**Master Loop Fail-Safe (`draw_error_screen(bad_state)`):**

* Designed a catch-all `else:` branch for the master `while active_mode != "QUIT":` loop to catch missing `return` statements (`None`) or misspelled state strings, render a full-frame fault banner using `draw_telemetry(error=True)`, and safely recover to `"CONFIG"` on `Enter`.

**Python Control Flow & Scope Mechanics Demystified:**

* Clarified read-only global variable lookup vs. `global` assignment declarations, `None` sentinel defaults for live global toggles (`DEBUG`), `continue` loop-skipping behavior inside nested menus, and quote-delimited string literals vs. variable identifiers in function calls.

---

#### **4. Immediate Next Steps (Next Session)**

1. **Finalize `run_angle_mode()` & `draw_angle_screen()`:** Replace the duplicate outer `while True:` loop in `run_angle_mode()` with the single `submode` loop, store `choice = input().strip().lower()` once per cycle, and pad `ANGLE_SELECT` to 6 content lines.


2. **Update `run_config_mode()` & Master Loop:** Update `run_config_mode()` to map all 6 menu options (`1` = `HOME`, `2` = `JOG`, `3` = `ANGLE`, `4` = `PASS`, `5`/`Q` = `QUIT`, `6` = `DOCS`) and wire all 6 states plus the `draw_error_screen()` fallback into the master `while active_mode != "QUIT":` loop.


3. **Implement `run_home_mode()` & Stub `PASS` / `DOCS` Screens:** Build `run_home_mode()` using `draw_home_cal_screen()` (supporting slewing to `(0.0°, 0.0°)` via `move_to_angle(0, 0)` and zero-origin calibration before returning `"CONFIG"`), add placeholder `run_pass_mode()` and `run_docs_mode()` functions, and fix the `el_limit_alerted` typo in `send_safe_step()`.


4. **Live Updates (`rich.live.Live`):** Once all 6 tabs are navigable end-to-end, explore live in-place terminal refreshing during Jog and Angle slews.
