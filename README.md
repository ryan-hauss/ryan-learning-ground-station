# ryan-learning-ground-station
Miniature model of a dual-axis satellite ground station positioner and SDR tracking controller.  
**Open Orbit RLGS (Ryan Learning Ground Station)** is a miniature, self-built satellite ground station project developed by Ryan H., a sophomore mechanical engineering student and Ground Station Network (GSN) Team Lead at Colorado State University (Fort Collins). Its primary purpose is to build hands-on leadership experience in positioner control, orbital tracking, and software-defined radio (SDR) signal decoding to mirror a full-scale ground station network.

<img src="docs/images/GenR1 oct 17.png" alt="Gen R1 Gimbal" width="300">

### Core Hardware & Software Stack

* **Mechanical & Actuation (Gen R1):** A dual-axis balsa and metal bracket gimbal driven by two 28BYJ-48 stepper motors and ULN2003A Darlington drivers, powered by a dedicated 5.0V/3.0A rail.


* **Control Architecture:** An Arduino Uno running library-free C++ half-step firmware (`v1.0`) paired with a Python serial controller (`v1.2.1`) featuring a Finite State Machine (FSM) for non-blocking manual jogging (`WASD`), an ASCII telemetry/configuration dashboard, degree-based coordinate tracking, and software safety limits to prevent wire entanglement or physical collisions.


* **RF & Navigation Suite:** An RTL-SDR Blog V4 receiver, a Quectel L76K/Adafruit GNSS breakout, and a Heltec WiFi LoRa 32 V4 board for future radio testing.



### Three-Phase Roadmap & Current Progress

1. **Positioner Control (In Progress):** Implementing safe, smooth dual-axis motion. Current milestones include establishing real-time manual jogging, bypassing voltage-drop regulator bottlenecks for full motor torque, and calibrating safe elevation limits (`-46.0°` to `+51.0°`) with the antenna mounted. Next steps focus on adding Bresenham/DDA vector math for coordinated diagonal slewing.


2. **Orbital Tracking (Planned):** Using the Python `Skyfield` library to pull live Two-Line Element (TLE) satellite data, calculate local angles over Fort Collins, and convert them into automated motor step commands.


3. **Live RF & Differential Tracking (Planned):** Transmitting low-power LoRa GPS telemetry from the handheld Heltec board to the RTL-SDR, decoding it via GNU Radio, and using differential GPS ("Poor Man's RTK") to actively track the mobile node.

## 🗺️ Repository Structure

```text
open-orbit-rlgs/
├── docs/                                # Documentation, BOM, & Engineering Logbooks
│   ├── images/                          # Hardware photos & wiring diagrams
│   ├── logbook/                         # Chronological session logs (YYYY-MM-DD-topic.md)
│   └── BOM.md                           # Full hardware Bill of Materials (Gen R1, R2, & RF)
│
├── positioner/                          # Ground Station Pointing & Motion Subsystem
│   ├── control-software/                # Host Python serial controller & pass runner
│   │   └── rlgs_controller.py           # v1.2.1 — FSM controller, WASD jog & safety limits
│   └── firmware/                        # Embedded microcontroller drivers
│       ├── uno_halfstep/
│       │   └── uno_halfstep.ino         # v1.0.0 — Arduino Uno 8-state half-step driver (Gen R1)
│       └── kenpro_din/                  # (Planned) Gen 1.5 closed-loop 8-pin DIN interface
│
├── sdr/                                 # Ground Station RF Reception & Decoding[cite: 10]
│   └── .gitkeep                         # (Planned) GNU Radio flowgraphs & ZMQ telemetry bridge
│
├── satellite/                           # Space Segment / Target Beacon Node[cite: 10]
│   └── .gitkeep                         # (Planned) Heltec WiFi LoRa 32 V4 GPS beacon firmware
│
├── .gitignore
└── README.md
