FROM python:3.12-alpine

WORKDIR /students/jeremy

RUN apk add --no-cache wget \
    && addgroup -S app \
    && adduser -S app -G app \
    && mkdir -p /var/log/app \
    && chown -R app:app /var/log/app /students/jeremy

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

USER app

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:8080/health >/dev/null || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
