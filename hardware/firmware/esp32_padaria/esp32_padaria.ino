#include <WiFi.h>
#include <HTTPClient.h>
#include <time.h>

#include "config.h"

void setupTime() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("Aguardando sincronizar hora...");
    delay(500);
  }
}

String getIsoTimestamp() {
  struct tm timeinfo;
  getLocalTime(&timeinfo);
  char buf[30];
  strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%S+00:00", &timeinfo);
  return String(buf);
}

void sendEvent(bool motionDetected) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"sensor_id\":\"" + String(SENSOR_ID) + "\",";
  payload += "\"timestamp\":\"" + getIsoTimestamp() + "\",";
  payload += "\"motion_detected\":" + String(motionDetected ? "true" : "false") + ",";
  payload += "\"location\":\"" + String(LOCATION) + "\"";
  payload += "}";

  int statusCode = http.POST(payload);
  Serial.print("Status: ");
  Serial.println(statusCode);
  Serial.println(http.getString());

  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado! IP: " + WiFi.localIP().toString());

  setupTime();
}

void loop() {
  int motionState = digitalRead(PIR_PIN);

  if (motionState == HIGH) {
    Serial.println("Movimento detectado!");
    sendEvent(true);
    delay(5000); // evita mandar evento repetido a cada 200ms
  }

  delay(200);
}
