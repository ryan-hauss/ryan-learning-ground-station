# Bill of Materials (BOM) — RLGS

Complete hardware inventory across the **Positioner**, **SDR**, and **Satellite** subsystems, including current active hardware (Gen R1) and staged upgrade components (Gen R2).

---

## 1. Positioner Subsystem (`positioner/`)

### Compute & Control
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | Arduino Uno Clone (CH340) | Blue board; USB-to-Serial via CH340 at `115200` baud | Active (Gen R1) |
| 1 | USB Type-B to Type-A Cable | Host serial connection (`COM6` configurable) | Active (Gen R1) |

### Motors & Drivers
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 2 | 28BYJ-48 Stepper Motors | 5V geared unipolar; 4096 half-steps/rev (≈ 11.38 steps/°); Az (Pins 2–5), El (Pins 6–9) | Active (Gen R1) |
| 2 | ULN2003A Driver Boards | Darlington transistor array breakout boards | Active (Gen R1) |
| 2 | STEPPERONLINE 17HS19-1684D | Bipolar NEMA 17 stepper motors | Staged (Gen R2) |

### Power Infrastructure
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | 5.0V / 3.0A (15W) DC Power Supply | Dedicated regulated rail wired via female DC barrel-to-screw-terminal adapter (star-grounded) | Active (Gen R1 v1.2.1+) |
| 1 | MB102 Breadboard Power Supply | 5V regulator module (bypassed in v1.2.1 due to AMS1117 voltage dropout under load) | Retired / Backup |
| 1 | 9V Battery + Snap Clip | Initial portable power source | Retired / Backup |

### Mechanical Structure
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | Dual-Axis Gimbal Frame | Balsa wood plates, metal L-brackets, aluminum shaft couplers, M2 hardware, brass knurled threaded insert | Active (Gen R1) |

---

## 2. SDR Subsystem (`sdr/`)

### Receivers & Navigation
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | RTL-SDR Blog V4 Dongle | Built-in upconverter (keep Direct Sampling OFF); WinUSB driver via Zadig; `samp_rate = 2.4e6` | Active |
| 1 | Adafruit Ultimate GPS Breakout | Standalone GNSS receiver with coin-cell battery backup (for future TDM ground position fix) | Staged |

### Coaxial Cables
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | RG-316 Coax Pigtail | Low-loss pink coaxial extension cable (routes antenna away from laptop RFI) | Active |
| 1 | RG-174 Coax Cable | Thin black coaxial extension cable | Active |

---

## 3. Satellite / Beacon Subsystem (`satellite/`)

### Flight / Node Hardware
| Qty | Component | Specs / Details | Status |
| :--- | :--- | :--- | :--- |
| 1 | Heltec WiFi LoRa 32 V4 (`HTIT-WB32LAF`) | ESP32-S3 + SX1262 LoRa (28 dBm max; software-choked to `0 dBm` / 1 mW via `radio.setOutputPower(0)`) | Active |
| 1 | Quectel L76K GNSS Module | Integrated GPS module paired with the Heltec V4 node | Active |

---

## 4. Antenna Array Toolkit (Shared RF)

| ID | Antenna | Frequency Band | Physical / Role Notes |
| :--- | :--- | :--- | :--- |
| **Ant 1** | Giant Whip (~22 cm) | 868 / 915 MHz | Tuned sub-GHz whip; reserved exclusively for Heltec TX safety during development |
| **Ant 2** | Flat Paddle | 700 – 960 MHz | Wideband 4G/LTE/5G cellular antenna (primary RTL-SDR 915 MHz RX antenna) |
| **Ant 3** | Medium Cylinder A | 2.4 GHz | High-frequency Wi-Fi / nRF24L01 band |
| **Ant 4** | Medium Cylinder B | 2.4 GHz | High-frequency Wi-Fi / nRF24L01 band |
| **Ant 5** | Stubby Antenna | 2.4 GHz | Compact high-frequency antenna |
