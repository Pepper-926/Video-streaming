#!/bin/bash

echo "🚀 Configurador de despliegue Django con Nginx + Gunicorn"
echo

# 🧠 Solicitar datos al usuario
read -p "🌐 Dominio o IP del servidor (ej. flixy.ddns.net): " SERVER_NAME
read -p "🔌 Puerto de Gunicorn (ej. 8000): " GUNICORN_PORT
read -p "📁 Ruta ABSOLUTA del proyecto Django (ej. /home/ubuntu/Desktop/proyectos/flixy): " PROJECT_DIR
read -p "📦 Ruta ABSOLUTA de la carpeta STATIC (ej. /home/ubuntu/Desktop/proyectos/flixy/static): " STATIC_PATH
read -p "🖼️ Ruta ABSOLUTA de la carpeta MEDIA (ej. /home/ubuntu/Desktop/proyectos/flixy/media): " MEDIA_PATH
read -p "🧩 Módulo WSGI (ej. flixy.wsgi): " WSGI_MODULE

echo
echo "✅ Confirmando:"
echo "- Dominio: $SERVER_NAME"
echo "- Puerto Gunicorn: $GUNICORN_PORT"
echo "- Proyecto: $PROJECT_DIR"
echo "- STATIC: $STATIC_PATH"
echo "- MEDIA: $MEDIA_PATH"
echo "- WSGI: $WSGI_MODULE"
echo

read -p "¿Continuar con la instalación? (s/n): " CONFIRM
if [[ "$CONFIRM" != "s" ]]; then
    echo "❌ Instalación cancelada."
    exit 1
fi

# 1. Detener Apache
echo "🛑 Deteniendo Apache (si existe)..."
sudo systemctl stop apache2 2>/dev/null
sudo systemctl disable apache2 2>/dev/null

# 2. Recolectar estáticos
echo "📦 Ejecutando collectstatic..."
cd "$PROJECT_DIR"
source venv/bin/activate
python manage.py collectstatic --noinput

# 3. Crear configuración Nginx
NGINX_CONF="/etc/nginx/sites-available/flixy"

echo "📝 Generando archivo de configuración de Nginx..."

sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    location /static/ {
        alias $STATIC_PATH/;
    }

    location /media/ {
        alias $MEDIA_PATH/;
    }

    location / {
        proxy_pass http://127.0.0.1:$GUNICORN_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# 4. Habilitar config
echo "🔗 Enlazando configuración en sites-enabled..."
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/flixy
sudo rm -f /etc/nginx/sites-enabled/default

# 5. Crear servicio Gunicorn
echo "🔧 Creando servicio systemd para Gunicorn..."

sudo tee /etc/systemd/system/gunicorn.service > /dev/null <<EOF
[Unit]
Description=gunicorn daemon para Flixy
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/venv/bin/gunicorn $WSGI_MODULE:application --bind 127.0.0.1:$GUNICORN_PORT --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. Activar Gunicorn
echo "🔄 Recargando systemd y activando gunicorn..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn

# 7. Reiniciar Nginx
echo "♻️ Reiniciando Nginx..."
sudo systemctl restart nginx

# 8. Estado
echo
echo "✅ Estado de los servicios:"
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo
echo "🎉 ¡Listo! Tu app Django debería estar disponible en: http://$SERVER_NAME"
