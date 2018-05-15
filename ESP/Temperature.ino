#include <OneWire.h>
#include <DallasTemperature.h>

#define TEMPERATURE_PIN 13

OneWire temperatureWire(TEMPERATURE_PIN);
DallasTemperature temperature(&temperatureWire);

void initTemperature(void) {
  temperature.begin();
}

float getTemperature(void) {
  temperature.requestTemperatures();
  
  return DallasTemperature::toFahrenheit(temperature.getTempCByIndex(0));
}

