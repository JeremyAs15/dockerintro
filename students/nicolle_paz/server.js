const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const student = process.env.STUDENT_NAME || 'Nicolle';
const barrio = process.env.BARRIO || 'San Carlos';
const logPath = process.env.VISIT_LOG_PATH || '/var/log/app/visitas.log';

try {
  fs.mkdirSync(path.dirname(logPath), { recursive: true });
} catch (error) {
  console.error(`unable to create log directory: ${error.message}`);
}

app.use((req, res, next) => {
  res.on('finish', () => {
    const timestamp = new Date().toISOString();
    const line = `${timestamp} method=${req.method} path=${req.originalUrl} status=${res.statusCode}\n`;

    fs.appendFile(logPath, line, (error) => {
      if (error) {
        console.error(`unable to write visit log: ${error.message}`);
      }
    });
  });

  next();
});

app.get('/', (_req, res) => {
  const message = `Hola, I am ${student} and I live in ${barrio}`;
  res.type('text/plain').send(message);
});

app.get('/health', (_req, res) => {
  res.status(200).json({ ok: true });
});

app.listen(8080, () => {
  console.log('Server running on port 8080');
});
