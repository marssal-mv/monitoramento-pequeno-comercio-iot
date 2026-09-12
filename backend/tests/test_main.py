from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["projeto"] == "Monitoramento Padaria Rosa de Saron"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_event():
    payload = {
        "sensor_id": "ESP32_TEST",
        "timestamp": "2026-09-12T10:00:00",
        "motion_detected": True,
        "location": "porta",
    }
    response = client.post("/events", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "received"
    assert body["sensor_id"] == "ESP32_TEST"


def test_list_events():
    response = client.get("/events")
    assert response.status_code == 200
    body = response.json()
    assert "events" in body
    assert "total" in body


def test_events_today():
    response = client.get("/events/today")
    assert response.status_code == 200
    assert "date" in response.json()


def test_alerts():
    response = client.get("/events/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()


def test_statistics():
    response = client.get("/statistics")
    assert response.status_code == 200
    body = response.json()
    assert "total_events" in body
    assert "today_events" in body


def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] in ("normal", "movimento_recente", "alerta")


def test_dashboard_data():
    response = client.get("/dashboard-data")
    assert response.status_code == 200
    body = response.json()
    assert "statistics" in body
    assert "recent_events" in body
