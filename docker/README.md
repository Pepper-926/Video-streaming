## Redis con Docker para Celery

En esta carpeta se incluye un script que automatiza la configuración del entorno de desarrollo para la ejecución de tareas en segundo plano con Celery. El script realiza las siguientes acciones:

Inicia el contenedor de Redis utilizando Docker Compose.

Activa el entorno virtual de Python en la terminal actual.

Lanza una nueva ventana de PowerShell con el worker de Celery en ejecución.

De esta forma, el entorno queda completamente preparado para que el backend pueda enviar y procesar tareas asincrónicas.

📌 Requisitos previos
Tener Docker Desktop instalado y en ejecución antes de ejecutar el script.

Ejecutar desde PowerShell (no desde CMD).

Contar con un archivo .env ubicado en la raíz del proyecto, el cual debe contener las credenciales necesarias para acceder a los servicios de almacenamiento en la nube y demás configuraciones sensibles (por ejemplo, claves de API, variables de entorno para la base de datos, etc.).

```bash
.\docker\Scripts\activate_env.ps1

./docker/Scripts/activate_env.sh
```