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


mkdir -p ${VOLUMES}/cal.minet.net/postgres
mkdir -p ${VOLUMES}/cal.minet.net/minio
mkdir -p ${VOLUMES}/cal.minet.net/migration_state

# Secure Registry Login
if [ -n "$CI_REGISTRY" ]; then
    if [ -n "$SWARM_REGISTRY_USER" ] && [ -n "$SWARM_REGISTRY_PASSWORD" ]; then
         echo "Logging into registry $CI_REGISTRY with SWARM_REGISTRY_USER..."
         echo "$SWARM_REGISTRY_PASSWORD" | docker login -u "$SWARM_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    elif [ -n "$CI_REGISTRY_USER" ] && [ -n "$CI_JOB_TOKEN" ]; then
         echo "Logging into registry $CI_REGISTRY with CI_JOB_TOKEN..."
         echo "$CI_JOB_TOKEN" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    fi
fi

if ! docker stack deploy --with-registry-auth --prune --detach=false -c stack.yaml calendint; then
    echo "Deployment failed! Fetching service status..."
    docker service ps --no-trunc calendint_backend
    docker service ps --no-trunc calendint_nginx
    exit 1
fi
