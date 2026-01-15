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

docker stack deploy --with-registry-auth --prune --detach=false -c stack.yaml calendint
