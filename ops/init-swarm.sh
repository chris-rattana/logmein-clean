#!/usr/bin/env bash
set -e

docker swarm init || true
docker node ls

echo
echo "Create/update secrets with:"
echo "  bash ops/create-secrets.sh"
