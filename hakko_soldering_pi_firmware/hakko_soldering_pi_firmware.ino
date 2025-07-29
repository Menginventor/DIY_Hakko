#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

// ------------------ Pin Definitions ------------------
#define RTD_PIN A0
#define POT_PIN PA1
#define MOSFET_PIN PB9
#define LED_PIN PC13

#define R_PULLDOWN 100.0
#define V_REF 3.3

// ------------------ OLED Setup ------------------
#define I2C_ADDRESS 0x3c
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// ------------------ Control Variables ------------------
float target_rtd = 0.0;
float current_temp = 25.0;
float current_rtd = 50.0;
float filtered_rtd = 50.0;
HardwareTimer *pwmTimer;
HardwareTimer *controlTimer;
uint32_t pwmChannel;

const float Kp = 2 * 0.029;  //2x for using with 12V supply
const float Ki = 2 * 0.00245;
const float Ts = 0.01;  // 100 Hz

float error = 0, error_prev = 0;
float integral = 0;
float pwm_duty = 0;
float filtered_temp = 25.0;
// ------------------ OLED Display Timer ------------------
unsigned long lastDisplayUpdate = 0;
unsigned long displayIntervalMs = 100;  // 10 Hz = every 100 ms

void updateSetpoint() {
  int potValue = analogRead(POT_PIN);
  float setTemp = map(potValue, 0, 4095, 150, 250);
  float slope = (120.0 - 50.0) / (250.0 - 25.0);  // RTD ohm per °C
  target_rtd = 50.0 + slope * (setTemp - 25.0);
}

void controlLoop() {
  updateSetpoint();

  int adc = analogRead(RTD_PIN);
  float vOut = (adc / 4095.0f) * V_REF;
  current_rtd = (vOut > 0.001) ? R_PULLDOWN * (V_REF / vOut - 1.0f) : 9999.0;
  filtered_rtd = 0.9 * filtered_rtd + 0.1 * current_rtd;

  float slope = (250.0 - 25.0) / (120.0 - 50.0);  // °C per ohm
  current_temp = 25.0 + slope * (current_rtd - 50.0);
  filtered_temp = 0.9 * filtered_temp + 0.1 * current_temp;

  error = target_rtd - filtered_rtd;
  float u_P = Kp * error;
  integral += Ki * (error + error_prev) / 2 * Ts;
  float u_I = integral;
  error_prev = error;

  if (u_P > 1.0f) {
    u_P = 1.0f;
  }
  if ((u_P + u_I) > 1.0f) {
    u_I = 1.0f - u_P;
  }
  if (u_P < 0.0f) {
    u_P = 1.0f;
  }
  if ((u_P + u_I) < 0.0f) {
    u_I = 0 - u_P;
  }

  float u = u_P + u_I;
  integral = u_I;
  pwm_duty = constrain(u * 100.0f, 0.0f, 100.0f);

  pwmTimer->setCaptureCompare(pwmChannel, pwm_duty, PERCENT_COMPARE_FORMAT);
  digitalWrite(LED_PIN, pwm_duty > 0 ? LOW : HIGH);

  Serial.print("SP_R: ");
  Serial.print(target_rtd, 2);
  Serial.print(", PV_R: ");
  Serial.print(current_rtd, 2);
  Serial.print(", OP: ");
  Serial.println(pwm_duty, 1);
}

void setup() {
  Serial.begin(115200);

  pinMode(LED_PIN, OUTPUT);
  pinMode(MOSFET_PIN, OUTPUT);
  analogReadResolution(12);
  digitalWrite(LED_PIN, HIGH);

  display.begin(I2C_ADDRESS, true);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0, 0);
  display.println("Heater Controller");
  display.display();
  delay(1000);

  TIM_TypeDef *pwmInstance = (TIM_TypeDef *)pinmap_peripheral(digitalPinToPinName(MOSFET_PIN), PinMap_PWM);
  pwmChannel = STM_PIN_CHANNEL(pinmap_function(digitalPinToPinName(MOSFET_PIN), PinMap_PWM));
  pwmTimer = new HardwareTimer(pwmInstance);
  pwmTimer->setPWM(pwmChannel, MOSFET_PIN, 1000, 0.0);

  controlTimer = new HardwareTimer(TIM3);
  controlTimer->setOverflow(10000, MICROSEC_FORMAT);
  controlTimer->attachInterrupt(controlLoop);
  controlTimer->resume();
}

void loop() {
  unsigned long now = millis();
  if (now - lastDisplayUpdate >= displayIntervalMs) {
    lastDisplayUpdate = now;

    float sp_temp = (target_rtd - 50.0) / 0.3111 + 25.0;

    display.clearDisplay();

    // Bigger text for SP and PV
    display.setTextSize(2);
    display.setCursor(0, 0);
    display.print("SP:");
    display.print(sp_temp, 0);
    display.print(" C");

    display.setCursor(0, 20);
    display.print("PV:");
    display.print(filtered_temp, 0);
    display.print(" C");

    // Smaller text for OP
    display.setTextSize(1);
    display.setCursor(0, 45);
    display.print("OP:");
    display.print(pwm_duty, 1);
    display.println("%");

    display.display();
  }
}
