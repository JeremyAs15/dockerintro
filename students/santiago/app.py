import datetime
import os
from pathlib import Path

from fastapi import FastAPI, Request, Response


app = FastAPI()

STUDENT_NAME = os.getenv("STUDENT_NAME", "Santiago")
BARRIO = os.getenv("BARRIO", "Siloé")
LOG_PATH = Path("/var/log/app/visitas.log")

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_request(request: Request, status_code: int) -> None:
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    client_ip = request.client.host if request.client else "unknown"
    line = (
        f"{timestamp} ip={client_ip} method={request.method} "
        f"path={request.url.path} status={status_code}\n"
    )
    with LOG_PATH.open("a", encoding="utf-8") as log_file:
        log_file.write(line)


@app.middleware("http")
async def request_logger(request: Request, call_next):
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        log_request(request, response.status_code if response else 500)


@app.get("/")
async def root() -> Response:
    message = f"Hola, I am {STUDENT_NAME} and I live in {BARRIO}"
    return Response(content=message, media_type="text/plain; charset=utf-8")


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
