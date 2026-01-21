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

# Authenticate with registry to resolve image digests
if [ ! -z "$CI_REGISTRY_USER" ] && [ ! -z "$SWARM_REGISTRY_PASSWORD" ] && [ ! -z "$CI_REGISTRY" ]; then
    echo "$SWARM_REGISTRY_PASSWORD" | docker login $CI_REGISTRY -u "$CI_REGISTRY_USER" --password-stdin
fi

mkdir -p ${VOLUMES}/cal.minet.net/postgres
mkdir -p ${VOLUMES}/cal.minet.net/minio
mkdir -p ${VOLUMES}/cal.minet.net/migration_state

docker stack deploy --with-registry-auth --prune --detach=false -c stack.yaml calendint
