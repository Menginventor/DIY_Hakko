#define RTD_PIN A0
#define MOSFET_PIN PB9
#define LED_BUILTIN PC13

#define R_PULLDOWN 100.0
#define V_REF 3.3

#define NUM_CYCLES 10
#define TARGET_RTD 150.0         // Ohms threshold to turn off
#define SAMPLE_INTERVAL_MS 10    // 100 Hz
#define OFF_DURATION_MS 120000    // Off time in milliseconds

bool include_float = true;
bool control_state = false;
bool off_waiting = false;
bool started = false;
bool stopped = false;

int current_cycle = 0;
unsigned long last_sample_time = 0;
unsigned long off_timer_start = 0;

String inputString = "";

void setup() {
  Serial.begin(115200);
  while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(MOSFET_PIN, OUTPUT);
  analogReadResolution(12);

  digitalWrite(MOSFET_PIN, LOW);
  digitalWrite(LED_BUILTIN, HIGH);

  Serial.println("WAITING_FOR_START");
}

void loop() {
  // --- Serial command handling ---
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      inputString.trim();

      if (inputString.equalsIgnoreCase("start")) {
        Serial.println("STARTING");
        started = true;
        stopped = false;
        current_cycle = 0;
        control_state = false;
        off_waiting = false;
        digitalWrite(MOSFET_PIN, LOW);
      } else if (inputString.equalsIgnoreCase("stop")) {
        Serial.println("STOPPING");
        started = false;
        stopped = true;
        digitalWrite(MOSFET_PIN, LOW);
        control_state = false;
      }

      inputString = "";
    } else {
      inputString += c;
    }
  }

  if (!started || stopped) return;

  // --- Main loop at 100 Hz ---
  unsigned long now = millis();
  if (now - last_sample_time >= SAMPLE_INTERVAL_MS) {
    last_sample_time = now;

    int adc = analogRead(RTD_PIN);
    float vOut = (adc / 4095.0) * V_REF;
    float rRTD = (vOut > 0.001) ? R_PULLDOWN * (V_REF / vOut - 1.0) : 9999.0;

    int off_time_sec = 0;
    if (off_waiting) {
      off_time_sec = (now - off_timer_start) / 1000;
    }

    // --- Print formatted data ---
    Serial.print("round=");
    Serial.print(current_cycle + 1);  // Human-friendly 1-indexed
    Serial.print(", adc=");
    Serial.print(adc);
    Serial.print(", R=");
    Serial.print(rRTD, 2);
    Serial.print(", u=");
    Serial.print(control_state ? 1 : 0);
    Serial.print(", t_off=");
    Serial.println(off_time_sec);

    // --- Step response logic ---
    if (current_cycle < NUM_CYCLES) {
      if (!off_waiting && !control_state) {
        digitalWrite(MOSFET_PIN, HIGH);
        control_state = true;
      }

      if (control_state && rRTD >= TARGET_RTD) {
        digitalWrite(MOSFET_PIN, LOW);
        control_state = false;
        off_waiting = true;
        off_timer_start = now;
        current_cycle++;
      }

      if (off_waiting && (now - off_timer_start >= OFF_DURATION_MS)) {
        off_waiting = false;
      }
    } else {
      digitalWrite(MOSFET_PIN, LOW);
      control_state = false;
    }
  }
}
