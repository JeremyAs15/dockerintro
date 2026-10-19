import os
from pathlib import Path

from flask import Flask, Response, jsonify

app = Flask(__name__)
LOG_FILE = Path("/var/log/app/visitas.log")


def student_message() -> str:
    student_name = os.getenv("STUDENT_NAME", "Anon")
    barrio = os.getenv("BARRIO", "Unknown")
    return f"Hola, I am {student_name} and I live in {barrio}"


@app.get("/")
def home() -> Response:
    message = student_message()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
    return Response(message, mimetype="text/plain")


@app.get("/health")
def health():
    return jsonify({"ok": True}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
