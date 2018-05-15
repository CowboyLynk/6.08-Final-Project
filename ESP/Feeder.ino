#include <ESP32_Servo.h>

#define SERVO_PIN 14
#define NUMBER_OF_SHAKES 3

Servo feederServo;
int servoPosition;

void initFeeder(void) {
  feederServo.attach(SERVO_PIN);
  servoPosition = feederServo.read();
}

void feed(void) {
  for (int i = 0; i < NUMBER_OF_SHAKES; i++) {
    feederServo.write(servoPosition + 120);
    delay(150);
    feederServo.write(servoPosition - 120);
    servoPosition = feederServo.read();
  }
}

