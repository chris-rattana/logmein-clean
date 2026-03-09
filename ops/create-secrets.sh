#!/usr/bin/env bash
set -euo pipefail

DB_NAME_VALUE="${1:-logs_db}"
DB_USER_VALUE="${2:-logs_user}"
DB_PASSWORD_VALUE="${3:-logs_password}"

create_or_replace_secret() {
  local secret_name="$1"
  local secret_value="$2"

  if docker secret ls --format '{{.Name}}' | grep -qx "$secret_name"; then
    echo "Removing existing secret: $secret_name"
    docker secret rm "$secret_name" >/dev/null
  fi

  printf "%s" "$secret_value" | docker secret create "$secret_name" -
  echo "Created secret: $secret_name"
}

create_or_replace_secret "db_name" "$DB_NAME_VALUE"
create_or_replace_secret "db_user" "$DB_USER_VALUE"
create_or_replace_secret "db_password" "$DB_PASSWORD_VALUE"

echo "Current secrets:"
docker secret ls
