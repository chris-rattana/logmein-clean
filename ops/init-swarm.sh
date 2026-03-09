#!/usr/bin/env bash
set -e

docker swarm init || true
docker node ls
