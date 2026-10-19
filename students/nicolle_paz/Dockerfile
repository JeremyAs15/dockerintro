FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache wget \
    && addgroup -S app \
    && adduser -S app -G app \
    && mkdir -p /var/log/app \
    && chown -R app:app /var/log/app /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY server.js ./
RUN chown app:app /app/server.js

USER app

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget -qO- http://127.0.0.1:8080/health >/dev/null || exit 1

CMD ["node", "server.js"]
