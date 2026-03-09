# Application Architecture

## Components
- **Frontend**: static dashboard served by Nginx
- **Backend**: Flask API exposing `/health`, `/logs`, `/stats`, `/logs/clear`
- **Database**: PostgreSQL 15 for log persistence

## Local Runtime
- Frontend exposed on port `8080`
- Backend exposed on port `5000`
- PostgreSQL exposed on port `5432`

## Request Flow
1. User opens the dashboard on port `8080`
2. Nginx serves static assets
3. Requests to `/api/*` are proxied to the backend
4. Backend reads/writes logs in PostgreSQL

## Main Files
- `frontend/index.html`
- `frontend/script.js`
- `frontend/nginx.conf`
- `backend/app.py`
- `docker-compose.yml`
- `docker-stack.yml`
