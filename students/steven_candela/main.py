import os
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request, Response

# Ruta alineada con el volumen 'biblioteca-del-pueblo'
LOG_PATH = Path("/var/log/app/visitas.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Variables de entorno requeridas
STUDENT = os.getenv("STUDENT_NAME", "Brayan")
BARRIO = os.getenv("BARRIO", "Santa Fe")

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    timestamp = datetime.now(timezone.utc).isoformat()
    client_ip = request.client.host if request.client else "unknown"
    
    # Registro de actividad en el volumen compartido
    with LOG_PATH.open("a", encoding="utf-8") as access_log:
        access_log.write(
            f"{timestamp} ip={client_ip} method={request.method} "
            f"path={request.url.path} status={response.status_code} "
            f"msg=\"Hey! I am {STUDENT} and I live in {BARRIO}\"\n"
        )
    return response


@app.get("/")
async def root():
    message = f"Hey! I am {STUDENT} and I live in {BARRIO}"
    return Response(content=message, media_type="text/plain; charset=utf-8")


@app.get("/health")
async def health():
    return {"status": "healthy"}