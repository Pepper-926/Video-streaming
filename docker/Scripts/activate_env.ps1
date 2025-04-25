# 🐍 1. Activar entorno virtual en esta terminal
Write-Output "Activando entorno virtual..."
. venv\Scripts\Activate.ps1

# 🐳 2. Levantar Redis
Write-Output "Levantando Redis con Docker..."
$dockerComposePath = "docker\redis\docker-compose.redis.yml"
docker-compose -f $dockerComposePath up -d

# 🔁 3. Crear script temporal para lanzar el worker Celery
$tempScript = "$env:TEMP\run_celery_worker.ps1"
@"
. venv\Scripts\Activate.ps1
Write-Host '🔥 Entorno virtual activado.'
celery -A mysite worker --loglevel=info --pool=solo
"@ | Set-Content -Encoding UTF8 -Path $tempScript

# 📂 4. Abrir nueva terminal PowerShell que ejecuta ese script
Start-Process powershell.exe -ArgumentList "-NoExit", "-File", $tempScript