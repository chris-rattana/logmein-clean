#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${1:-logmein}"

for secret in db_name db_user db_password; do
  if ! docker secret ls --format '{{.Name}}' | grep -qx "$secret"; then
    echo "Missing Docker secret: $secret"
    echo "Run: bash ops/create-secrets.sh"
    exit 1
  fi
done

docker stack deploy -c docker-stack.yml "$STACK_NAME"
docker stack services "$STACK_NAME"
