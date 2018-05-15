#define SAMPLE_INTERNAL 100
#define FEEDING_INTERNAL 1000*60*60*12

float timeOfSample, timeOfFeeding;

void setup(void) {
  Serial.begin(115200);

  analogReadResolution(11);

  initWiFi();
  initTemperature();
  initWaterlevel();
  initFeeder();

  timeOfSample = millis();
  timeOfFeeding = millis();

  pinMode(32, OUTPUT);
}

void loop(void) {
  if (millis() - timeOfSample > SAMPLE_INTERNAL) {
    Serial.println("--");
    Serial.println(getTemperature());
    Serial.println(getTurbidity());
    Serial.println(getWaterlevel());
    Serial.println(getPH());
    
    post(1, getTemperature());
    post(2, getTurbidity());
    post(3, getWaterlevel());
    bool led = post(4, getPH());
    digitalWrite(32, led);
    
    timeOfSample = millis();
  }

  if (millis() - timeOfFeeding > FEEDING_INTERNAL) {
    feed();

    timeOfFeeding = millis();
  }
}
