#!/bin/bash
if test -f ".env"; then
        set -a
        source .env
        set +a
fi

if test ! -f ".env.deploy"; then
    echo "No .env.deploy file found"
    exit 1
fi

set -a
source .env.deploy
set +a


if [ ! -z "$SWARM_REGISTRY_PASSWORD" ] && [ ! -z "$CI_REGISTRY" ]; then
    echo "$SWARM_REGISTRY_PASSWORD" | docker login $CI_REGISTRY -u deploy --password-stdin
fi

mkdir -p ${VOLUMES}/cal.minet.net/postgres
mkdir -p ${VOLUMES}/cal.minet.net/minio
mkdir -p ${VOLUMES}/cal.minet.net/migration_state

if ! docker stack deploy --with-registry-auth --prune --detach=false -c stack.yaml calendint; then
    echo "Deployment failed! Fetching service status..."
    docker service ps --no-trunc calendint_backend
    docker service ps --no-trunc calendint_nginx
    exit 1
fi
