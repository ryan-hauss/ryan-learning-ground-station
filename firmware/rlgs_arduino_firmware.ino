Arduino Firmware v1.0
// =====================================================================
// Custom Ground Station Receiver Firmware v1.0 (No Libraries Required)
// =====================================================================

// Physical pins wired to ULN2003 driver boards
const int az_pins[] = {2, 3, 4, 5}; // Horizontal Pan Axis
const int el_pins[] = {6, 7, 8, 9}; // Vertical Tilt Axis

// Standard 8-step Half-Step sequence matrix to drive the internal electromagnets
const int seq[8][4] = {
  {1, 0, 0, 0}, {1, 1, 0, 0}, {0, 1, 0, 0}, {0, 1, 1, 0},
  {0, 0, 1, 0}, {0, 0, 1, 1}, {0, 0, 0, 1}, {1, 0, 0, 1}
};

// Index counters to track where we are inside the 8-step matrix pattern
int az_index = 0;
int el_index = 0;

void setup() {
  // Open the USB serial highway at 115200 baud to match your Python script
  Serial.begin(115200); 
  
  // Set all 8 motor drive pins as outputs to push 5V current to the driver chips
  for(int i = 0; i < 4; i++) {
    pinMode(az_pins[i], OUTPUT);
    pinMode(el_pins[i], OUTPUT);
  }
}

void loop() {
  // 1. Stare at the mailbox. Is there a character byte waiting in the USB buffer?
  if (Serial.available() > 0) {
    
    // 2. Read the single raw letter character passed from Python
    char cmd = Serial.read();
    
    // 3. Directly map the character instruction to a one-step physical muscle pulse:
    if (cmd == 'A') stepAxis(az_pins, az_index, 1);   // Azimuth Clockwise
    if (cmd == 'a') stepAxis(az_pins, az_index, -1);  // Azimuth Counter-Clockwise
    if (cmd == 'E') stepAxis(el_pins, el_index, 1);   // Elevation UP (Tilt)
    if (cmd == 'e') stepAxis(el_pins, el_index, -1);  // Elevation DOWN (Tilt)
  }
}

// Custom worker function to cycle the pins to the next physical step position
void stepAxis(const int pins[], int &index, int dir) {
  // Move forward or backward through the 8 rows, looping around safely at 0 and 7
  index = (index + dir + 8) % 8; 
  
  // Physically flip the 4 pins to match the 1s and 0s of the matrix row
  for(int i = 0; i < 4; i++) {
    digitalWrite(pins[i], seq[index][i]);
  }
}

