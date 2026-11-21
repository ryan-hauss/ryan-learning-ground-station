# 🛰️ November 20 Session Summary

```Unset
mdate: 2026-11-20 17:15
tags:
  - CubeSat
  - RLGS
  - Logbook
```

**━━━━━━ . °‧ 𓆝  𝙻𝚘𝚐𝚋𝚘𝚘𝚔   °‧ 𓆝 𓆟 𓆞 ·。**

**Project:** Open Orbit RLGS (Ryan Learning Ground Station) — Gen R1 & Gen 1.5 (Kenpro Integration)  
**Subsystem:** Repository Documentation (`docs/`), Control Hardware Exploration & Gen 1.5 Rotator Rewiring  
**Date:** November 20  
**Time / Duration** 1:00 PM to ~ 5:30 PM  
**Lead:** Ryan H. (GSN Team Lead, CSU Fort Collins)  

**Objective:** Centralizing engineering logbooks and hardware BOM inside GitHub (`docs/`), evaluating ESP32 and laptop-less control upgrades, and auditing/rewiring the legacy Gen 1.5 Kenpro Az/El rotator.

#### **1. Version & Subsystem Scope Tracking**

**GitHub Repository (`open-orbit-rlgs` / `docs/`):** **Expanded & Standardized**
* Migrated logbook storage from local-only Obsidian + Google Docs into `docs/logbook/` using Unicode symbols (`±180°`, `≈`, `Ω`) in place of fragile inline LaTeX math delimiters.
* Created `docs/BOM.md` cataloging the full baseline hardware inventory across `positioner/`, `sdr/`, `satellite/`, and the 5-Antenna Array Toolkit.
* Initialized `docs/images/.gitkeep` to store version-controlled hardware photos for `README.md`.

**Python Controller (`positioner/controller/`):** **v1.2.1 (Unchanged)**
* Existing FSM, degree tracking, and serial pipeline preserved; confirmed compatible with Gen 1.5 closed-loop serial translation.

**Arduino Firmware (`positioner/firmware/uno_halfstep/`):** **v1.0.0 (Unchanged)**
* Existing 8-state half-step sequence (`115200` baud) locked for Gen R1; evaluated ESP32 and standalone pendant firmware variants.

**Rotator Hardware (Gen R1):** **Unchanged**
* Dual 28BYJ-48 motors, balsa/bracket frame, direct 5.0V / 3.0A rail, calibrated Elevation limits (`-46.0°` to `+51.0°`).

**Rotator Hardware (Gen 1.5 — Kenpro / Yaesu G-5400B):** **Audited & Rewiring Architecture Finalized**
* Stripped out legacy DE-15 shared-ground harness and mapped clean 1-to-6 isolated wiring harnesses (`18 AWG` 4-wire + 2-wire bundles bridged via 6-pin Molex connectors).

#### **2. Technical Milestones Completed**

**Centralized Repository Documentation & Hardware BOM:**
* Resolved GitHub file-tree folder collapsing (`docs/logbook`) by adding sibling documentation (`docs/BOM.md`) and asset directories (`docs/images/`).
* Documented Gen R1 active hardware, Gen R2 staged NEMA 17 motors (`17HS19-1684D`), RTL-SDR Blog V4 (`samp_rate = 2.4e6`), Heltec WiFi LoRa 32 V4 (`0 dBm` / 1 mW software choke), and antenna resonance bands.

**Audited Gen 1.5 Kenpro G-5400B & Diagnosed Legacy "Evil Junction":**
* Identified why only 10 wires reached the control box on the legacy harness: the previous builder tied **Pin 1 (Potentiometer Low)** and **Pin 6 (Motor Common)** together and used the frayed outer braided shield as a shared return through an undersized high-density **DE-15 (VGA) connector**, creating noise coupling and short-circuit risks.
* Verified the 8-screw terminal block layout on both Azimuth and Elevation: **Terminals 1–6** carry active signals while **Terminals 7–8** are unused factory spares.
* Caught and corrected an inverted pinout reference that had swapped 24V AC motor drive wires onto the 500 Ω potentiometer terminals.

**Finalized Color-Coded 1-to-6 Harness & Molex Pinout:**
* Standardized on two separate 6-conductor harnesses (one for Azimuth, one for Elevation) built from `18 AWG` **4-wire** (`Red, Black, Green, White`) and **2-wire** (`Red, Black`) bundles (~4 ft rotator side + ~2 ft control box side) joined by **2 pairs** of 6-pin Molex connectors.
* Kept both 24V AC motor drive phases isolated inside the 2-wire bundle and low-voltage potentiometer sense lines inside the 4-wire bundle:

| Terminal & Molex Pin | Cable Bundle | Wire Color | Function |
| :--- | :--- | :--- | :--- |
| **1** | 4-Wire | **Green** | Potentiometer Low (GND) |
| **2** | 4-Wire | **White** | Potentiometer Wiper (0–5V Sense) |
| **3** | 4-Wire | **Red** | Potentiometer High (+Ref) |
| **4** | 2-Wire | **Red** | Motor Phase 1 (CCW / Down) |
| **5** | 2-Wire | **Black** | Motor Phase 2 (CW / Up) |
| **6** | 4-Wire | **Black** | Motor Common (Return) |

* Verified that oily residue around the Kenpro housing seams is normal age-related base-oil separation from the internal lithium gear grease rather than a liquid oil leak.

#### **3. Architecture & Conceptual Foundations Established**

**ESP32 & Laptop-Less Field Control (Gen R1 / R2):**
* Verified that 3.3V ESP32 GPIO pins (`GPIO16–19`, `GPIO21–23`, `GPIO25`, avoiding strapping and input-only `GPIO34–39` pins) drive both Gen R1 ULN2003A Darlington boards and Gen R2 stepper drivers directly.
* Designed a standalone hardware pendant architecture using 4 `INPUT_PULLUP` pushbuttons (allowing simultaneous diagonal slewing) or a 2-axis analog thumb joystick (proportional slew speed), polled concurrently alongside USB `Serial.available()`.

**Control System Comparison (Gen R1/R2 vs. Gen 1.5 & ESP32 Options):**
* Contrasted Gen R1/R2 open-loop step counting (assumed `(0, 0)` boot origin, active holding current) against the Kenpro's closed-loop `24V AC` motor + `500 Ω` potentiometer feedback (true absolute `0–5V` angle on boot, self-locking worm gear, built-in internal hardware limit switches).
* Mapped out future microcontroller integration via the rear 8-pin `EXTERNAL CONTROL` DIN jack using an isolated 4-channel relay/optocoupler module (`Left/CCW`, `Right/CW`, `Up`, `Down`) and `A0`/`A1` analog feedback reads.
* Identified the rear 8-pin `EXTERNAL CONTROL` DIN jack (`Left/CCW`, `Right/CW`, `Up`, `Down`, plus `0–5V` Az/El analog outputs) as the future microcontroller interface via an isolated 4-channel relay/optocoupler module.
* Verified ESP32 `3.3V` GPIO compatibility (`GPIO16–19`, `GPIO21–23`, `GPIO25`) and a 4-button `INPUT_PULLUP` field pendant design for Gen R1/R2.

#### **4. Immediate Next Steps (Next Session)**

1. Crimp the blue `16–14 AWG` fork terminals (folding the stripped `18 AWG` copper in half for mechanical grip) and seat the two 6-pin Molex pairs for Azimuth and Elevation.
2. Perform multimeter verification with 117V AC mains unplugged: confirm `~500 Ω` across Pins `1–3`, low winding resistance across Pins `4–6`, and infinite resistance (`OL`) between motor and potentiometer circuits.
3. Wipe the Kenpro exterior seams clean, power on the control box for a bench slew test, and calibrate the front panel meters and `OUT VOLTAGE ADJ.` (`0–5V`) trim pots.
