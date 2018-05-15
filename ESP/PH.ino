#define PH_PIN A7

float getPH(void) {
  return analogRead(PH_PIN) * (3.3 / 2048.0) + 5.1;
}
