import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request, Response

# Ruta alineada con el volumen 'biblioteca-del-pueblo'
LOG_PATH = Path("/var/log/app/visitas.log")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Variables de entorno requeridas
STUDENT = os.getenv("STUDENT_NAME", "Steven")
BARRIO = os.getenv("BARRIO", "Santa Fe")
MESSAGE = f"Hola, I am {STUDENT} and I live in {BARRIO}"

# Rutas que no se registran en la biblioteca (el healthcheck corre cada 10 s)
SKIP_LOG_PATHS = {"/health"}

app = FastAPI()


def log_visit(line: str) -> None:
    """Escribe una línea en el log compartido sin tumbar la petición si falla.

    El volumen lo comparten contenedores de otros estudiantes, que pueden
    correr con otro UID; si no tenemos permiso de escritura, solo avisamos.
    """
    try:
        with LOG_PATH.open("a", encoding="utf-8") as access_log:
            access_log.write(line)
        # Si el archivo es nuestro, lo dejamos escribible para los demás servicios
        if LOG_PATH.stat().st_uid == os.getuid():
            LOG_PATH.chmod(0o666)
    except OSError as exc:
        print(f"WARN: no se pudo escribir en {LOG_PATH}: {exc}", file=sys.stderr)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    if request.url.path in SKIP_LOG_PATHS:
        return response

    timestamp = datetime.now(timezone.utc).isoformat()
    client_ip = request.client.host if request.client else "unknown"
    log_visit(
        f"{timestamp} ip={client_ip} method={request.method} "
        f"path={request.url.path} status={response.status_code} "
        f"student=\"{STUDENT}\" barrio=\"{BARRIO}\"\n"
    )
    return response


@app.get("/")
async def root():
    return Response(content=MESSAGE, media_type="text/plain; charset=utf-8")


@app.get("/health")
async def health():
    return {"status": "healthy"}
