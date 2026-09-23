# ============================================
# BACKEND - MONITORAMENTO PADARIA IoT
# ============================================

import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import SensorEvent
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


def serialize_event(e: SensorEvent) -> dict:
    """Converte uma linha do banco (SensorEvent) num dict pronto pra resposta JSON"""
    return {
        "id": e.id,
        "sensor_id": e.sensor_id,
        "timestamp": e.timestamp,
        "motion_detected": e.motion_detected,
        "location": e.location,
        "created_at": e.created_at
    }


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
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
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
    db_event = SensorEvent(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    return {
        "status": "received",
        "event_id": db_event.id,
        "sensor_id": db_event.sensor_id,
        "timestamp": db_event.timestamp.isoformat(),
        "message": "Evento recebido com sucesso"
    }


@app.get("/events", response_model=dict, tags=["Events"])
async def list_events(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Listar eventos com filtros opcionais"""
    query = db.query(SensorEvent)

    if location:
        query = query.filter(SensorEvent.location == location)
    if start_date:
        query = query.filter(SensorEvent.timestamp >= start_date)
    if end_date:
        query = query.filter(SensorEvent.timestamp <= end_date)

    total = query.count()
    events = query.order_by(SensorEvent.timestamp.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "count": len(events),
        "events": [serialize_event(e) for e in events]
    }


@app.get("/events/today", response_model=dict, tags=["Events"])
async def events_today(db: Session = Depends(get_db)):
    """Listar eventos de hoje"""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    today_events = (
        db.query(SensorEvent)
        .filter(SensorEvent.timestamp >= today_start, SensorEvent.timestamp <= today_end)
        .all()
    )

    return {
        "date": today.isoformat(),
        "count": len(today_events),
        "events": [serialize_event(e) for e in today_events]
    }


@app.get("/events/alerts", response_model=dict, tags=["Events"])
async def get_alerts(
    hours: int = Query(24, ge=1),
    db: Session = Depends(get_db)
):
    """Listar alertas (movimento fora do horário)"""
    time_threshold = datetime.utcnow() - timedelta(hours=hours)

    events = db.query(SensorEvent).filter(SensorEvent.timestamp > time_threshold).all()

    alerts = [
        e for e in events
        if (e.timestamp.hour < OPERATION_START or e.timestamp.hour >= OPERATION_END)
    ]

    return {
        "count": len(alerts),
        "operation_hours": f"{OPERATION_START:02d}:00 - {OPERATION_END:02d}:00",
        "period_hours": hours,
        "alerts": [serialize_event(e) for e in alerts]
    }


@app.get("/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics(db: Session = Depends(get_db)):
    """Obter estatísticas de movimentação"""
    events = db.query(SensorEvent).all()

    today = datetime.utcnow().date()
    today_events = [e for e in events if e.timestamp.date() == today]

    alerts = [
        e for e in events
        if (e.timestamp.hour < OPERATION_START or e.timestamp.hour >= OPERATION_END)
    ]

    last_motion = max([e.timestamp for e in events]) if events else None

    return StatisticsResponse(
        total_events=len(events),
        today_events=len(today_events),
        alerts_out_of_hours=len(alerts),
        last_motion=last_motion
    )


@app.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status(db: Session = Depends(get_db)):
    """Obter status atual do estabelecimento"""
    operation_hours = {
        "start": f"{OPERATION_START:02d}:00",
        "end": f"{OPERATION_END:02d}:00"
    }

    events = db.query(SensorEvent).all()
    last_motion = max([e.timestamp for e in events]) if events else None

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
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Endpoint especial para o dashboard: tudo que a interface precisa"""
    events = db.query(SensorEvent).order_by(SensorEvent.timestamp.asc()).all()

    today = datetime.utcnow().date()
    today_events = [e for e in events if e.timestamp.date() == today]

    alerts = [
        e for e in events
        if (e.timestamp.hour < OPERATION_START or e.timestamp.hour >= OPERATION_END)
    ]

    last_motion = max([e.timestamp for e in events]) if events else None

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "status": {
            "establishment": "Aberta" if OPERATION_START <= datetime.utcnow().hour < OPERATION_END else "Fechada",
            "api_health": "ok"
        },
        "statistics": {
            "total_events": len(events),
            "today_events": len(today_events),
            "alerts": len(alerts)
        },
        "recent_events": [serialize_event(e) for e in events[-5:]],  # Últimos 5 eventos
        "alerts": [serialize_event(e) for e in alerts],
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
