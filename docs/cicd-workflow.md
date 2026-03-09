# CI/CD Workflow

## CI
Triggered on:
- push to `main`
- pull requests targeting `main`

CI stages:
1. Start PostgreSQL service
2. Install backend dependencies
3. Run `black --check`
4. Run `flake8`
5. Run `bandit`
6. Run `pytest -v`
7. Build backend Docker image
8. Build frontend Docker image

Workflow file:
- `.github/workflows/ci.yml`

## CD
Triggered when:
- the `CI` workflow completes successfully on `main`

CD stages:
1. Checkout the exact tested commit
2. Login to GitHub Container Registry (GHCR)
3. Build backend image
4. Push backend image to GHCR
5. Build frontend image
6. Push frontend image to GHCR

Workflow file:
- `.github/workflows/cd.yml`

## Published Images
- `ghcr.io/chris-rattana/logmein-backend:latest`
- `ghcr.io/chris-rattana/logmein-frontend:latest`
