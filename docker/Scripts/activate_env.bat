@echo off
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo Levantando Redis con Docker...
docker-compose -f docker\redis\docker-compose.redis.yml up -d

echo.
echo Creando script temporal para lanzar el worker de Celery...

set TEMP_SCRIPT=%TEMP%\run_celery_worker.ps1
echo . venv\Scripts\Activate.ps1 > %TEMP_SCRIPT%
echo Write-Host '🔥 Entorno virtual activado.' >> %TEMP_SCRIPT%
echo celery -A mysite worker --loglevel=info --pool=solo >> %TEMP_SCRIPT%

echo.
echo Lanzando nueva terminal PowerShell con el worker...
start powershell -NoExit -File "%TEMP_SCRIPT%"
