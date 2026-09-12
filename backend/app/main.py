# ============================================
# BACKEND - MONITORAMENTO PADARIA IoT
# ============================================

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import models  # noqa: F401 (registra as tabelas no Base.metadata)
from .database import Base, engine
from .schemas import EventCreate, StatisticsResponse, StatusResponse

# ============================================
# INICIALIZAR FASTAPI
# ============================================

app = FastAPI(
    title="API Monitoramento Padaria Rosa de Saron",
    description="Sistema IoT de detecção de movimento para pequeno comércio",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS - Permitir requisições do dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: ["https://seu-domain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria as tabelas no banco (SQLite local por padrão, ver database.py)
Base.metadata.create_all(bind=engine)

# Horário de funcionamento (configurável via .env) - fora desse intervalo,
# movimento detectado é considerado alerta
OPERATION_START = int(os.getenv("HORA_INICIO", "6"))
OPERATION_END = int(os.getenv("HORA_FIM", "22"))

# ============================================
# DADOS SIMULADOS (para início)
# ============================================

mock_events = [
    {
        "id": 1,
        "sensor_id": "ESP32_001",
        "timestamp": datetime.utcnow() - timedelta(hours=2),
        "motion_detected": True,
        "location": "porta",
        "created_at": datetime.utcnow()
    },
    {
        "id": 2,
        "sensor_id": "ESP32_001",
        "timestamp": datetime.utcnow() - timedelta(hours=1),
        "motion_detected": True,
        "location": "interior",
        "created_at": datetime.utcnow()
    }
]

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Info"])
async def root():
    """Raiz da API - Informações"""
    return {
        "projeto": "Monitoramento Padaria Rosa de Saron",
        "versao": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "events": "/events",
            "statistics": "/statistics",
            "status": "/status"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Verificar saúde da API"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "API Monitoramento Padaria"
    }


@app.post("/events", response_model=dict, tags=["Events"], status_code=201)
async def create_event(event: EventCreate):
    """
    Receber evento do ESP32/Sensor

    Body esperado:
    ```json
    {
        "sensor_id": "ESP32_001",
        "timestamp": "2026-09-12T22:30:15",
        "motion_detected": true,
        "location": "porta"
    }
    ```
    """
    # TODO: Implementar salvamento no banco de dados (via models.SensorEvent)
    return {
        "status": "received",
        "event_id": len(mock_events) + 1,
        "sensor_id": event.sensor_id,
        "timestamp": event.timestamp.isoformat(),
        "message": "Evento recebido com sucesso"
    }


@app.get("/events", response_model=dict, tags=["Events"])
async def list_events(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Listar eventos com filtros opcionais"""
    # TODO: Implementar query no banco com filtros

    filtered_events = mock_events

    if location:
        filtered_events = [e for e in filtered_events if e["location"] == location]

    total = len(filtered_events)
    events = filtered_events[offset : offset + limit]

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "count": len(events),
        "events": events
    }


@app.get("/events/today", response_model=dict, tags=["Events"])
async def events_today():
    """Listar eventos de hoje"""
    # TODO: Implementar filtro por data no banco

    today = datetime.utcnow().date()
    today_events = [e for e in mock_events if e["timestamp"].date() == today]

    return {
        "date": today.isoformat(),
        "count": len(today_events),
        "events": today_events
    }


@app.get("/events/alerts", response_model=dict, tags=["Events"])
async def get_alerts(
    hours: int = Query(24, ge=1)
):
    """Listar alertas (movimento fora do horário)"""
    # TODO: Implementar lógica de alertas no banco

    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    alerts = [
        e for e in mock_events
        if e["timestamp"] > time_threshold and
        (e["timestamp"].hour < OPERATION_START or e["timestamp"].hour >= OPERATION_END)
    ]

    return {
        "count": len(alerts),
        "operation_hours": f"{OPERATION_START:02d}:00 - {OPERATION_END:02d}:00",
        "period_hours": hours,
        "alerts": alerts
    }


@app.get("/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """Obter estatísticas de movimentação"""
    # TODO: Implementar cálculos no banco

    today = datetime.utcnow().date()
    today_events = [e for e in mock_events if e["timestamp"].date() == today]

    alerts = [
        e for e in mock_events
        if (e["timestamp"].hour < OPERATION_START or e["timestamp"].hour >= OPERATION_END)
    ]

    last_motion = max([e["timestamp"] for e in mock_events]) if mock_events else None

    return StatisticsResponse(
        total_events=len(mock_events),
        today_events=len(today_events),
        alerts_out_of_hours=len(alerts),
        last_motion=last_motion
    )


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status():
    """Obter status atual do estabelecimento"""
    # TODO: Implementar lógica no banco

    operation_hours = {
        "start": f"{OPERATION_START:02d}:00",
        "end": f"{OPERATION_END:02d}:00"
    }

    last_motion = max([e["timestamp"] for e in mock_events]) if mock_events else None

    current_status = "normal"
    motion_in_last_30min = False

    if last_motion:
        time_diff = datetime.utcnow() - last_motion

        if time_diff < timedelta(minutes=30):
            motion_in_last_30min = True
            current_status = "movimento_recente"

            current_hour = datetime.utcnow().hour
            if current_hour < OPERATION_START or current_hour >= OPERATION_END:
                current_status = "alerta"

    return StatusResponse(
        status=current_status,
        last_motion=last_motion,
        operational_hours=operation_hours,
        motion_in_last_30min=motion_in_last_30min
    )


@app.get("/dashboard-data", response_model=dict, tags=["Dashboard"])
async def get_dashboard_data():
    """Endpoint especial para o dashboard: tudo que a interface precisa"""
    today = datetime.utcnow().date()
    today_events = [e for e in mock_events if e["timestamp"].date() == today]

    alerts = [
        e for e in mock_events
        if (e["timestamp"].hour < OPERATION_START or e["timestamp"].hour >= OPERATION_END)
    ]

    last_motion = max([e["timestamp"] for e in mock_events]) if mock_events else None

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": {
            "establishment": "Aberta" if OPERATION_START <= datetime.utcnow().hour < OPERATION_END else "Fechada",
            "api_health": "ok"
        },
        "statistics": {
            "total_events": len(mock_events),
            "today_events": len(today_events),
            "alerts": len(alerts)
        },
        "recent_events": mock_events[-5:],  # Últimos 5 eventos
        "alerts": alerts,
        "last_motion": last_motion
    }


# ============================================
# TRATAMENTO DE ERROS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Tratador customizado de exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================
# MAIN - Rodar localmente
# ============================================

if __name__ == "__main__":
    import uvicorn

    print("""
    ============================================================
      API Monitoramento Padaria Rosa de Saron
      http://localhost:8000
      Docs: http://localhost:8000/docs
    ============================================================
    """)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
