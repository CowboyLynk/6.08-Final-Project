#define BLYNK_PRINT Serial

#include <WiFi.h>
#include <WiFiClient.h>
#include <BlynkSimpleEsp32.h>

char auth[] = "e59f25208cd64dd78eb0e6b587bf978f";

#define WIFI_SSID "MIT GUEST"
#define WIFI_PSWD ""

void initWiFi(void) {
  
  WiFi.begin(WIFI_SSID, WIFI_PSWD);
  
  int count = 0;
  while(WiFi.status() != WL_CONNECTED && count < 6) {
    delay(500);
    Serial.print(".");
    count++;
  }
  
  delay(2000);
  if(WiFi.isConnected()) {
    Blynk.config(auth);  // in place of Blynk.begin(auth, ssid, pass);
    Blynk.connect(3333);  // timeout set to 10 seconds and then continue without Blynk
    while (Blynk.connect() == false) {
      // Wait until connected
    }
    Serial.println(WiFi.localIP().toString() + " (" + WiFi.macAddress() + ") (" + WiFi.SSID() + ")");
    delay(500);
  } else {
    Serial.println(WiFi.status());
    ESP.restart();
  }
}

bool post(int sensor, float voltage) {
  // Sends the data to the Blynk app
  Blynk.run();
  if (sensor == 1) {
    Blynk.virtualWrite(V0, voltage);
  } else if (sensor == 2) {
    Blynk.virtualWrite(V1, voltage);
  } else if (sensor == 3) {
    Blynk.virtualWrite(V2, voltage);
  } else {
    Blynk.virtualWrite(V3, voltage);
  }
  
  WiFiClient client;
  bool result = false;
  
  if(client.connect("iesc-s1.mit.edu",80)) {
    client.println("POST /608dev/sandbox/clynk/final_project/server_code.py?sensor=" + String(sensor) + "&value=" + String(voltage) + " HTTP/1.1");
    client.println("Host: iesc-s1.mit.edu");
    client.println("\r\n");
    
    unsigned long count = millis();
    while(client.connected()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
      
      if(line == "\r" || millis() - count > 6000) break;
    }
    
    count = millis();
    
    String op;
    while(client.available()) op += (char) client.read();
    Serial.println(op);
    
    result = op.equals("ON");
    client.stop();
    Serial.println();
    Serial.println("----------");
  } else {
    Serial.println("Connection failed");
    Serial.println("Wait 0.5 sec...");
    client.stop();
    delay(300);
  }

  return result;
}
