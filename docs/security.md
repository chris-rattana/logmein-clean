# Security Notes

## Application
- Backend validates JSON requests and uses parameterized SQL queries via psycopg2
- CORS is enabled for frontend/backend interaction
- Containers are separated by Docker networks

## Docker
- `.env` is ignored by Git
- `.env.example` documents required variables without exposing secrets
- Build contexts are reduced with `.dockerignore`

## CI/CD
- GitHub Actions uses the built-in `GITHUB_TOKEN` for GHCR publishing
- Static checks:
  - Black
  - Flake8
  - Bandit
  - Pytest

## Remaining Improvements
- Move database credentials to Docker secrets for Swarm
- Add container healthchecks
- Run backend with Gunicorn instead of Flask dev server in production
- Restrict CORS policy more tightly in production
- Use a non-root user in containers
