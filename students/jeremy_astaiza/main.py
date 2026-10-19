import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()
LOG_FILE = Path("/var/log/app/visitas.log")


def build_message() -> str:
    student_name = os.getenv("STUDENT_NAME", "Jeremy")
    barrio = os.getenv("BARRIO", "Unknown")
    return f"Hello, I am {student_name} and I live in {barrio}"


def append_visit_log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp} {message}\n")
    except OSError as exc:
        print(f"Error writing to {LOG_FILE}: {exc}", file=sys.stderr, flush=True)


@app.get("/", response_class=PlainTextResponse)
def root() -> str:
    message = build_message()
    append_visit_log(message)
    return message


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}
