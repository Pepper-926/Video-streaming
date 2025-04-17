from django.db import connection

try:
    connection.ensure_connection()
    print("¡Conexión a PostgreSQL exitosa!")
except Exception as e:
    print("Error de conexión:", e)