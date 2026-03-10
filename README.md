# LogMeIn

LogMeIn is a small log dashboard project with:
- a Flask backend
- a PostgreSQL database
- a frontend served by Nginx
- a CI pipeline on GitHub Actions
- a CD workflow publishing Docker images to GHCR
- a Docker Swarm stack for deployment

## Project Structure

```text
.
├── .github/workflows/
├── backend/
├── frontend/
├── docs/
├── ops/
├── docker-compose.yml
├── docker-stack.yml
├── pyproject.toml
└── README.md
```

## Documentation

- [Documentation technique réseau](docs/network/logmein_network_documentation.md)
