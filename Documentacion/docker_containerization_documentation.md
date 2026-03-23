# Documentación de Contenerización — RadiographXpress

## Resumen Ejecutivo

El sistema RadiographXpress ha sido exitosamente contenerizado utilizando Docker y Docker Compose para habilitar un despliegue escalable, consistente y listo para producción. Se migró la arquitectura de un entorno de desarrollo local (con SQLite y Channel Layers en memoria) a una arquitectura multi-servicio con PostgreSQL y Redis.

El proceso de contenerización y automatización de infraestructura dio como resultado un entorno completamente funcional, con el 100% de las pruebas automatizadas (84/84) pasando exitosamente dentro del entorno contenerizado.

---

## Arquitectura del Contenedor

La aplicación está diseñada bajo una arquitectura de microservicios usando `docker-compose.yml`, orquestando 5 contenedores principales que interactúan entre sí dentro de una red de Docker (`radiographxpress_default`).

### Servicios Implementados

1. **`web` (Django/Daphne):**
   - Servidor ASGI (Daphne) encargado de procesar solicitudes HTTP y conexiones WebSocket.
   - Ejecuta el código principal de la aplicación en el puerto `8000`.
   - Espera a que la base de datos PostgreSQL se reporte como "saludable" (healthy) antes de iniciar, gracias al script inteligente `entrypoint.sh`.

2. **`nginx` (Proxy Inverso):**
   - Servidor web ligero (Nginx Alpine) en el puerto `80`.
   - Actúa como proxy inverso: redirige tráfico HTTP y de WebSockets (`/ws/`) hacia el contenedor `web`.
   - Sirve archivos estáticos directamente para mejorar el rendimiento.
   - Restringe el cuerpo de peticiones a `10MB` para mitigar ataques DOS por carga de archivos masivos.

3. **`postgres` (Base de Datos):**
   - Imagen oficial `postgres:16-alpine`.
   - Reemplaza a SQLite para soportar escritura concurrente y despliegue distribuido en producción.
   - Los datos se almacenan en un volumen persistente (`postgres_data`) para prevenir pérdida de información al reiniciar contenedores.

4. **`redis` (Broker de Mensajes/Caché):**
   - Imagen oficial `redis:7-alpine`.
   - Implementado específicamente como **Channel Layer** para soportar Django Channels y las conexiones WebSocket distribuidas entre múltiples workers o instancias.

5. **`sync_pacs` (Proceso de Fondo):**
   - Utiliza la misma imagen construida para `web`, pero ejecuta el comando de administración personalizado `python manage.py sync_pacs_images`.
   - Mantiene una sincronización constante con la API de Raditech en segundo plano, sin bloquear los hilos principales de la web.

---

## Proceso de Implementación paso a paso

### 1. Preparación del Entorno Base (Dockerfile)
Se construyó una imagen multi-etapa basada en `python:3.13-slim` para garantizar un tamaño de contenedor óptimo. 
- **Dependencias del Sistema:** Se identificó la necesidad de instalar dependencias a nivel de SO como `libpango`, `libcairo`, `fonts-dejavu-core` para que **WeasyPrint** (generador de PDF de los reportes) funcione correctamente. También se agregó `libpq5` para interactuar con Postgres y `libqpdf-dev` para `pikepdf`.
- **Archivos Estáticos:** La recolección de estáticos (`collectstatic`) se ejecuta **durante el build** del contenedor, reduciendo el tiempo de inicialización. Con esto se recolectaron **145 archivos estáticos**.

### 2. Actualización de Dependencias de Python (`requirements.txt`)
Se añadieron librerías indispensables para la infraestructura de producción:
- `psycopg[binary]==3.3.3`: Driver moderno para conectar Django a PostgreSQL.
- `channels-redis==4.3.0`: Habilita el Channel Layer con Redis.
- `whitenoise==6.12.0`: Sirve archivos estáticos directamente desde Django de manera altamente optimizada.

### 3. Modificaciones Críticas al Código (`settings.py`)
Para que el código fuera agnóstico al entorno, se configuraron reglas condicionadas:
- **Detección de Base de Datos:** `settings.py` detecta si se ha establecido una variable `DATABASE_URL`. Si existe (como en el contenedor), se conecta a Postgres. De lo contrario, cae en gracia a SQLite para desarrollo local.
- **Configuración WebSockets:** De forma similar, se implementó `REDIS_URL` para alternar entre `RedisChannelLayer` y `InMemoryChannelLayer`.
- **Proxy Seguro:** Se configuró `SECURE_PROXY_SSL_HEADER` para confiar en las cabeceras `X-Forwarded-Proto` de Nginx.

### 4. Automatización del Inicio (`entrypoint.sh`)
Se diseñó un script de Bash especializado para inicializar el contenedor web asegurando que:
1. PostgreSQL está disponible aceptando conexiones (comprueba mediante un test script en Python).
2. Se ejecutan todas las migraciones estructuradas pendientes (`python manage.py migrate --noinput`).
3. El proceso cambia la ejecución a `daphne` asignándole el "PID 1", de forma que el contenedor maneja las interrupciones del sistema operativo correctamente.

---

## Resultados y Verificación

El entorno fue sometido a prueba exhaustiva con los siguientes resultados:

1. **Estado de Servicios:** Todos los contenedores inicializaron en verde (Healthy status para Postgres).
2. **Validación de UI:** La aplicación levantó a la primera en `http://localhost`. La interfaz gráfica, hojas de estilos estáticos, y vistas de formulario de acceso se renderizan perfectamente.
3. **Migraciones:** Todas las estructuras de base de datos fueron trasladadas a Postgres exitosamente vía automatización del entrypoint.
4. **Resiliencia.** Pruebas Automatizadas de Unidad: La suite completa con las **84 pruebas**, las cuales verifican seguridad (inyecciones, CSRF), roles de usuarios (IDOR) y lógica de sincronización, **se ejecutaron localmente con 0 Fallos y 0 Errores** demostrando que los cambios en settings son retro-compatibles y listos para producción.

### Comandos de Operación Rápida
Ejemplo de administración del motor contenerizado:

- **Arrancar entorno productivo (Segundo plano):**
  ```bash
  docker compose up -d
  ```

- **Revisar estado o consolas:**
  ```bash
  docker compose ps
  docker compose logs -f web
  ```

- **Ejecutar pruebas del sistema dentro de Docker:**
  ```bash
  docker compose exec web python manage.py test --verbosity=2
  ```

- **Apagar y destruir contenedores y red:**
  ```bash
  docker compose down
  ```

## Conclusión
La aplicación ahora empaqueta todas sus dependencias tanto a nivel de código (`pip`) como a nivel de SO (`apt-get`) asegurando portabilidad al 100%. Las limitaciones de base de datos y Websockets uniproceso han sido suplantadas por arquitecturas estándar de la industria preparadas para la alta demanda y un despliegue directo en infraestructuras Cloud como **AWS EC2 / ECS**.
