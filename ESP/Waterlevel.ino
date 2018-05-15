#define WATERLEVEL_ECHO_PIN 26
#define WATERLEVEL_TRIGGER_PIN 25

#define SPEED_OF_SOUND 74.0526810773

void initWaterlevel(void) {
  pinMode(WATERLEVEL_TRIGGER_PIN, OUTPUT);
  pinMode(WATERLEVEL_ECHO_PIN, INPUT_PULLUP);
}

float getWaterlevel(void) {
  digitalWrite(WATERLEVEL_TRIGGER_PIN, LOW); 
  delayMicroseconds(2); 
  digitalWrite(WATERLEVEL_TRIGGER_PIN, HIGH); 
  delayMicroseconds(10); 
  digitalWrite(WATERLEVEL_TRIGGER_PIN, LOW); 
 
  return(pulseIn(WATERLEVEL_ECHO_PIN, HIGH)/(2*SPEED_OF_SOUND));
}
