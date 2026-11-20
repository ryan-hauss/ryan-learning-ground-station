# 🛰️ November 19 Session Summary


```Unset
mdate: 2026-11-19 14:00
tags:
  - CubeSat
  - RLGS
  - Logbook
```

**━━━━━━ . °‧ 𓆝  𝙻𝚘𝚐𝚋𝚘𝚘𝚔   °‧ 𓆝 𓆟 𓆞 ·。**

**Project:** Open Orbit RLGS (Ryan Learning Ground Station) — Gen R1  
**Subsystem:** Repository Architecture, Orbital Tracking & RF Direction-Finding Roadmap

**Date:** November 19  
**Time / Duration:** 2:00 PM to ~ 6:00 PM  
**Lead:** Ryan H. (GSN Team Lead, CSU Fort Collins)

**Objective:** Transitioning from manual duplicate-file versioning to a structured, three-subsystem GitHub repository and mapping out the Phase 2 orbital propagation and Phase 3 RF tracking pipelines.

---

#### **1. Version & Subsystem Scope Tracking**

**GitHub Repository (`open-orbit-rlgs`):** **Initialized & Restructured**
* Replaced ad-hoc duplicate file naming with Semantic Versioning (`vMAJOR.MINOR.PATCH`) tracked via Git commit history and internal `__version__` metadata headers (with system release tags deferred for retroactive assignment).
* Organized codebase into three functional subsystems (`positioner/`, `sdr/`, `satellite/`) plus `docs/` and `README.md`.


**Python Controller (`positioner/controller/`):** **v1.2.1 (Code Unchanged / Migrating to Git)**
* Planned path migration to `positioner/controller/` without version numbers in the filename to preserve line-by-line Git diff history.


**Arduino Firmware (`positioner/firmware/uno_halfstep/`):** **v1.0.0 (Code Unchanged / Migrating to Git)**
* Renamed and structured into `positioner/firmware/uno_halfstep/uno_halfstep.ino` to satisfy Arduino IDE folder-matching rules and accommodate future `esp32_driver/` firmware alongside it.


**Rotator Hardware (Gen R1):** **Unchanged**
* Dual 28BYJ-48 motors, balsa/bracket frame, direct 5.0V / 3.0A rail, calibrated Elevation limits (`-46.0°` to `+51.0°`).




**RF / SDR & Satellite Subsystems (`sdr/`, `satellite/`):** **Architecture & Tracking Pipeline Defined**
* Finalized inter-process communication strategy (`ZeroMQ PUB/SUB`) between GNU Radio and the Python controller, and evaluated RF null-seeking vs. orbital TLE tracking methodologies.



---

#### **2. Repository Architecture & Workflow Decisions**

**Three-Subsystem Separation:**
* Bundled the host Python controller and microcontroller firmware under `positioner/` since they are physically tethered over USB and dependent on each other, while isolating wireless RF nodes into `sdr/` (GNU Radio flowgraphs) and `satellite/` (Heltec WiFi LoRa 32 V4 GPS/beacon firmware).


**Git Workflow & Side-by-Side Comparison:**
* Eliminated version suffixes in filenames so Git tracks file lineage continuously across commits.
* Established a clean workflow for comparing versions using GitHub Desktop/VS Code history diffs (or temporary raw exports) paired with an internal `__version__` constant printed in the terminal boot banner.


**Standalone Windows Terminal Execution:**
* Identified Windows Terminal (`wt`) / Command Prompt execution and a `.bat` launcher script (`cd /d "%~dp0"`) to run the ASCII telemetry dashboard in a dedicated, full-screen window outside of VS Code's integrated terminal panel.



---

#### **3. Orbital Tracking & RF Direction-Finding Roadmap (Phases 2 & 3)**

**Phase 2 — Decoupled TLE Pass Execution (`Skyfield`):**
* Audited the production GSN `openc3-cosmos-tracker` architecture (`pass_predict.py` and `test_pass_predict.py`), confirming that local `Skyfield` propagation (`EarthSatellite`, `wgs84.latlon`, `.altaz()`) and Alpha-5 6-digit NORAD catalog decoding (`> 100,000`, e.g., `A0960` $\rightarrow$ `100960`) already function offline when TLEs are supplied locally.
* Selected a **two-step decoupled architecture** mirroring the production `TRAJ` $\rightarrow$ `gs-sequencer` pipeline: a standalone `Skyfield` pass-planner script will pre-compute time-tagged `(timestamp, az_deg, el_deg)` waypoint files, which `rlgs_controller.py` will load via a Config menu option (`run_pass_mode`) with progress telemetry, `[P]`ause, and `[ESC]` E-Stop polling.


**Phase 3 — Closed-Loop RF Tracking & ZeroMQ Bridge:**
* **IPC Bridge:** Selected **ZeroMQ (`ZMQ PUB/SUB` over `tcp://127.0.0.1:5555`)** with `zmq.NOBLOCK` and `zmq.CONFLATE` to stream fresh GNU Radio measurements into `rlgs_controller.py` without buffer lag.
* **Tracking Escalation Path:** Identified short-range GPS parallax and altitude jitter limits for desk/campus testing; planned an escalation path starting with **whip-tip RF null-seeking** (hill-climbing on RSSI/dBFS dips using a continuous carrier or rapid beacon), progressing to **dual-antenna amplitude/phase comparison**, and optional **IR/optical tracking**.



---

#### **4. Immediate Next Steps (Next Session)**

1. Complete the migration of local `v1.0.0`, `v1.1.0`, and `v1.2.1` controller and firmware files into the `open-orbit-rlgs` Git repository on the Windows laptop.


2. Implement the **Bresenham / DDA coordinated vector slewing function** (`move_to_angle(az, el)`) in `v1.3.0` and integrate it into the Config menu (laying the direct motion foundation for future `run_pass_mode` trajectory execution).


3. Add **Arrow Key navigation** (decoding Windows two-byte extended scan codes) alongside WASD in `run_jog_mode()`.


4. Clamp the Azimuth base to the bench and run a full ±180° pan calibration test.
