#include <Arduino.h>

#define RTD_PIN A0
#define MOSFET_PIN PB9
#define LED_PIN PC13

#define R_PULLDOWN 100.0
#define V_REF 3.3

float target_rtd = 0.0;  // Ohm target

HardwareTimer *pwmTimer;
HardwareTimer *controlTimer;
uint32_t pwmChannel;


const float Kp = 0.029;
const float Ki = 0.00245;
const float Ts = 0.01;  // 100 Hz = 10 ms

float error = 0, error_prev = 0;
float integral = 0;
float pwm_duty = 0;

bool started = false;
bool stopped = false;
String inputString = "";

void controlLoop() {


  // --- Read RTD ---
  int adc = analogRead(RTD_PIN);
  float vOut = (adc / 4095.0) * V_REF;
  float rRTD = (vOut > 0.001) ? R_PULLDOWN * (V_REF / vOut - 1.0) : 9999.0;

  // --- PI control with structured anti-windup ---
  error = target_rtd - rRTD;

  float u_P = Kp * error;
  integral += Ki * (error + error_prev) / 2 * Ts;
  float u_I = integral;
  error_prev = error;
  // Upper saturation
  if (u_P > 1.0f) {
    u_P = 1.0f;
  }
  if ((u_P + u_I) > 1.0f) {
    u_I = 1.0f - u_P;
  }

  // Lower saturation
  if (u_P < 0.0f) {
    u_P = 0.0f;
  }
  if ((u_P + u_I) < 0.0f) {
    u_I = -u_P;
  }
  float u = u_P + u_I;
  integral = u_I;  // Update integral state from saturated I-term

  // --- Convert u (0.0–1.0) to PWM duty (0–100%) ---
  pwm_duty = u * 100.0f;
  pwm_duty = constrain(pwm_duty, 0.0f, 100.0f);
  pwmTimer->setCaptureCompare(pwmChannel, pwm_duty, PERCENT_COMPARE_FORMAT);

  // --- LED feedback ---
  digitalWrite(LED_PIN, pwm_duty > 0 ? LOW : HIGH);  // Active-low LED

  // --- Debug output ---
  Serial.print(target_rtd, 2);
  Serial.print(", ");
  Serial.print(rRTD, 2);
  Serial.print(", ");

  Serial.println(pwm_duty, 1);
}

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;

  pinMode(LED_PIN, OUTPUT);
  pinMode(MOSFET_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // LED OFF
  analogReadResolution(12);

  // --- Setup PWM on PB9 ---
  TIM_TypeDef *pwmInstance = (TIM_TypeDef *)pinmap_peripheral(digitalPinToPinName(MOSFET_PIN), PinMap_PWM);
  pwmChannel = STM_PIN_CHANNEL(pinmap_function(digitalPinToPinName(MOSFET_PIN), PinMap_PWM));

  pwmTimer = new HardwareTimer(pwmInstance);
  pwmTimer->setPWM(pwmChannel, MOSFET_PIN, 1000, 0.0);  // Start at 0% duty

  // --- 100 Hz control loop on TIM3 ---
  controlTimer = new HardwareTimer(TIM3);
  controlTimer->setOverflow(10000, MICROSEC_FORMAT);  // 100 Hz = 10ms
  controlTimer->attachInterrupt(controlLoop);
  controlTimer->resume();

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
        integral = 0;
        error = error_prev = 0;
        target_rtd = 150.0;
      } else if (inputString.equalsIgnoreCase("stop")) {
        Serial.println("STOPPING");
        started = false;
        stopped = true;
        target_rtd = 0;
        pwmTimer->setCaptureCompare(pwmChannel, 0.0, PERCENT_COMPARE_FORMAT);  // Force 0% duty
      }

      inputString = "";
    } else {
      inputString += c;
    }
  }
}
