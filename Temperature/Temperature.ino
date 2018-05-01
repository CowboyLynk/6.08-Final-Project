#include <WiFi.h>
#include <OneWire.h>
#include <DallasTemperature.h>
 
// Data wire is plugged into pin 26 on the ESP
#define ONE_WIRE_BUS 13
 
// Setup a oneWire instance to communicate with any OneWire devices 
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);
float tempC;
float tempF;
 
// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);
 
void setup(void)
{
  // start serial port
  Serial.begin(9600);
  Serial.println("Dallas Temperature IC Control Library Demo");

  // Start up the library
  sensors.begin();

  // Start wifi
  start_wifi();
}
 

void loop(void)
{
  // call sensors.requestTemperatures() to issue a global temperature
  // request to all devices on the bus
  Serial.print(" Requesting temperatures...");
  sensors.requestTemperatures(); // Send the command to get temperatures
  Serial.println("DONE");

  tempC = sensors.getTempCByIndex(0);
  tempF = DallasTemperature::toFahrenheit(tempC);

  Serial.print("Temp C: ");
  Serial.print(tempC);
  Serial.print(" Temp F: ");
  Serial.println(tempF);
  do_POST(tempF);
  delay(1000);  // wait one second (change for actual project)
}

