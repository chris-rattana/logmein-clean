#!/usr/bin/env bash
set -e

STACK_NAME=logmein

docker stack deploy -c docker-stack.yml "$STACK_NAME"
docker stack services "$STACK_NAME"
