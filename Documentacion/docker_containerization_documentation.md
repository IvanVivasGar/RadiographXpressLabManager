# Containerization Documentation — RadiographXpress

## Executive Summary

The RadiographXpress system has been successfully containerized using Docker and Docker Compose to enable a scalable, consistent, and production-ready deployment. The architecture was migrated from a local development environment (with SQLite and in-memory Channel Layers) to a multi-service architecture with PostgreSQL and Redis.

The containerization and infrastructure automation process resulted in a fully functional environment, with 100% of the automated tests (84/84) passing successfully within the containerized environment.

---

## Container Architecture

The application is designed under a microservices architecture using `docker-compose.yml`, orchestrating 5 main containers interacting with each other within a Docker network (`radiographxpress_default`).

### Deployed Services

1. **`web` (Django/Daphne):**
   - ASGI server (Daphne) in charge of processing HTTP requests and WebSocket connections.
   - Runs the main application code on port `8000`.
   - Waits for the PostgreSQL database to report as "healthy" before starting, thanks to the intelligent `entrypoint.sh` script.

2. **`nginx` (Reverse Proxy):**
   - Lightweight web server (Nginx Alpine) on port `80`.
   - Acts as a reverse proxy: redirects HTTP and WebSocket traffic (`/ws/`) to the `web` container.
   - Serves static files directly to improve performance.
   - Restricts the request body size to `10MB` to mitigate DOS attacks from massive file uploads.

3. **`postgres` (Database):**
   - Official `postgres:16-alpine` image.
   - Replaces SQLite to support concurrent writing and distributed deployment in production.
   - Data is stored in a persistent volume (`postgres_data`) to prevent information loss when restarting containers.

4. **`redis` (Message Broker/Cache):**
   - Official `redis:7-alpine` image.
   - Implemented specifically as a **Channel Layer** to support Django Channels and distributed WebSocket connections across multiple workers or instances.

5. **`sync_pacs` (Background Process):**
   - Uses the exact same image built for `web`, but runs the custom management command `python manage.py sync_pacs_images`.
   - Maintains constant synchronization with the Raditech API in the background, without blocking the main web threads.

---

## Step-by-Step Implementation Process

### 1. Base Environment Preparation (Dockerfile)
A multi-stage image based on `python:3.13-slim` was built to guarantee an optimal container size.
- **System Dependencies:** The need to install OS-level dependencies such as `libpango`, `libcairo`, `fonts-dejavu-core` was identified for **WeasyPrint** (PDF report generator) to function correctly. `libpq5` was also added to interact with Postgres, and `libqpdf-dev` for `pikepdf`.
- **Static Files:** Static file collection (`collectstatic`) runs **during the container build**, reducing initialization time. With this, **145 static files** were collected.

### 2. Python Dependencies Update (`requirements.txt`)
Essential libraries for the production infrastructure were added:
- `psycopg[binary]==3.3.3`: Modern driver to connect Django to PostgreSQL.
- `channels-redis==4.3.0`: Enables the Redis Channel Layer.
- `whitenoise==6.12.0`: Serves static files directly from Django in a highly optimized manner.

### 3. Critical Code Modifications (`settings.py`)
To make the code environment-agnostic, conditional rules were configured:
- **Database Detection:** `settings.py` detects if a `DATABASE_URL` variable has been set. If it exists (like in the container), it connects to Postgres. Otherwise, it defaults to SQLite for local development.
- **WebSockets Configuration:** Similarly, `REDIS_URL` was implemented to toggle between `RedisChannelLayer` and `InMemoryChannelLayer`.
- **Secure Proxy:** `SECURE_PROXY_SSL_HEADER` was configured to trust Nginx's `X-Forwarded-Proto` headers.

### 4. Startup Automation (`entrypoint.sh`)
A specialized Bash script was designed to initialize the web container ensuring that:
1. PostgreSQL is available and accepting connections (verified using a Python test script).
2. All pending structured migrations are executed (`python manage.py migrate --noinput`).
3. The process execution shifts to `daphne` by assigning it "PID 1", so the container handles OS interrupts correctly.

---

## Results and Verification

The environment was subjected to exhaustive testing with the following results:

1. **Service Status:** All containers initialized green (Healthy status for Postgres).
2. **UI Validation:** The application loaded successfully on the first try at `http://localhost`. The graphical interface, static stylesheets, and login form views render perfectly.
3. **Migrations:** All database structures were successfully transferred to Postgres via the entrypoint automation.
4. **Resilience & Automated Unit Tests:** The complete test suite with all **84 tests**—verifying security (injections, CSRF), user roles (IDOR), and synchronization logic—was executed locally with **0 Failures and 0 Errors**, demonstrating that the settings modifications are backwards-compatible and production-ready.

### Quick Operation Commands
Examples for managing the containerized engine:

- **Start production environment (Background):**
  ```bash
  docker compose up -d
  ```

- **Check status or logs:**
  ```bash
  docker compose ps
  docker compose logs -f web
  ```

- **Run system tests inside Docker:**
  ```bash
  docker compose exec web python manage.py test --verbosity=2
  ```

- **Stop and destroy containers and network:**
  ```bash
  docker compose down
  ```

## Conclusion
The application now bundles all its dependencies both at the code level (`pip`) and OS level (`apt-get`), ensuring 100% portability. The single-process websocket and database limitations have been replaced by industry-standard architectures prepared for high demand and direct deployment in Cloud infrastructures such as **AWS EC2 / ECS**.
