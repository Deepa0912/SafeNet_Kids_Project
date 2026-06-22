# SafeNet Kids — Production Dockerfile
# Builds frontend and serves everything from FastAPI

FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend-parent/package*.json ./
RUN npm ci
COPY frontend-parent/ ./
RUN npm run build
# Output: /app/frontend/dist

FROM python:3.11-slim AS backend
WORKDIR /app

# System deps for bcrypt / Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev libssl-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/
COPY agent/ ./agent/
COPY .env* ./

# Copy built frontend into FastAPI static folder
COPY --from=frontend-build /app/frontend/dist ./static

# Create data dir for SQLite and screenshots
RUN mkdir -p data/screenshots

EXPOSE 8000

CMD ["uvicorn", "backend.main:sio_app", "--host", "0.0.0.0", "--port", "8000"]
