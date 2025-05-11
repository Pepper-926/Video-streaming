#!/bin/bash

echo "🐍 Activando entorno virtual..."
source venv/bin/activate

echo "🐳 Levantando Redis con Docker..."
docker-compose -f docker/redis/docker-compose.redis.yml up -d

echo "🔁 Lanzando worker Celery..."
# El worker se lanza en una nueva terminal (opcional), o directamente en background aquí
celery -A mysite worker --loglevel=info --pool=solo