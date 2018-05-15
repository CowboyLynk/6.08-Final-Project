#define TURBIDITY_PIN A6

float getTurbidity(void) {
  return analogRead(TURBIDITY_PIN) * (5.0 / 2048.0);
}
