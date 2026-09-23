#ifndef CONFIG_H
#define CONFIG_H

// Copie este arquivo para "config.h" (na mesma pasta) e preencha com os
// dados reais. O config.h fica fora do git (veja o .gitignore) pra não
// vazar a senha do WiFi no repositório.

const char* WIFI_SSID = "SEU_WIFI_AQUI";
const char* WIFI_PASSWORD = "SUA_SENHA_AQUI";
const char* API_URL = "http://192.168.0.100:8000/events"; // IP do PC rodando o backend

const int PIR_PIN = 27;
const char* SENSOR_ID = "ESP32_001";
const char* LOCATION = "porta";

#endif
