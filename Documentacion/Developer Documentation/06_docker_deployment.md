# Docker Deployment & Containerization

This guide covers how the project is orchestrated for deployment using Docker, abstracting away system-level dependencies.

## 1. Local Development vs. Production

The `radiographxpress/settings.py` is configured to auto-detect its environment:

*   **Bare-metal Local Dev:** By default, if NO environment variables are present, settings fall back to `sqlite3` and `InMemoryChannelLayer`.
*   **Docker Deployment:** The `docker-compose.yml` file sets `DATABASE_URL` and `REDIS_URL`. Settings detect these and switch the connections to PostgreSQL and Redis.

## 2. The `Dockerfile`

The environment utilizes a single Docker image built on `python:3.13-slim`.

**Key points:**
1.  **System Dependencies:** It uses `apt-get` to install required binary libraries:
    *   `libpango`, `libcairo` (Required for WeasyPrint/PDF).
    *   `libpq5` (Required for PostgreSQL connections natively via `psycopg[binary]`).
2.  **`collectstatic`:** Executed *during* the build phase (`RUN python manage.py collectstatic`). This copies all Django specific CSS, admin JS, and standard app static files into `/app/staticfiles`. This removes the necessity of running collectstatic dynamically on start.
3.  **Entrypoint:** Changes runtime execution to `entrypoint.sh`.

## 3. Orchestration (`docker-compose.yml`)

The stack consists of 5 tightly coupled services:

1.  **`web`:** The Daphne ASGI server exposing port `8000` internally.
2.  **`postgres`:** PostgreSQL 16 server. Uses a named volume `postgres_data` for persistence.
3.  **`redis`:** Redis 7 server handling WebSocket pub/sub message brokering.
4.  **`sync_pacs`:** A background worker scaling horizontally. It runs the exact same image as `web`, but overtakes the command loop to run `python manage.py sync_pacs_images`.
5.  **`nginx`:** A reverse proxy taking public traffic on port `80`. 

### The Nginx Reverse Proxy
Nginx resolves two critical architectural flaws of plain Python web servers:
*   **Static Files:** Nginx is highly optimized to read from `/app/staticfiles` (mounted via Docker volume) and serve the raw bytes to users without bothering Django.
*   **WebSocket Upgrade:** Python ASGI endpoints require HTTP Upgrade Headers to shift protocols `ws://`. The configuration handles exactly this:

```nginx
    location /ws/ {
        proxy_pass http://web:8000;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
```

## 4. `entrypoint.sh` Automations

To ensure reliability, the `web` container executes `entrypoint.sh`:
1.  **Wait for DB:** Uses a tiny python snippet connecting to Postgres until it succeeds. This solves race conditions where Django starts before the database is ready to accept connections.
2.  **Migrations:** Automatically forces `python manage.py migrate --noinput`.
3.  **Exec:** Starts Daphne (`exec daphne ...`). `exec` replaces the shell process with Daphne, transferring PID 1. This ensures that when Docker terminates the container, Daphne correctly receives the `SIGTERM` signal and shuts down safely.

## 5. Deployment Commands

```bash
# Build images and start all 5 containers detached
docker compose up --build -d

# Show real-time logs for the Django app
docker compose logs -f web

# Show logs for the background PACS synchronization
docker compose logs -f sync_pacs

# Open a shell inside the running web container
docker compose exec web bash

# Create an administrator
docker compose exec web python manage.py createsuperuser

# Stop and wipe everything (including databases/volumes)
docker compose down -v
```