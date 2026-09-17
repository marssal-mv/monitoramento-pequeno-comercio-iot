import requests
import time
from datetime import datetime
import random

URL = "http://127.0.0.1:8000/events"

while True:
    dados = {
        "sensor_id": "ESP32_001",
        "timestamp": datetime.now().isoformat(),
        "motion_detected": random.choice([True, False]),
        "location": "porta"
    }

    try:
        response = requests.post(URL, json=dados)
        print("Enviado:", dados)
        print("Status:", response.status_code)
        print("Resposta:", response.text)
        print("-" * 40)
    except Exception as e:
        print("Erro:", e)

    time.sleep(5)