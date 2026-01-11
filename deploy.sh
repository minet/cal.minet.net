#!/bin/bash
if test -f ".env"; then
        set -a
        source .env
        set +a
fi

mkdir -p ${VOLUMES}/cal.minet.net/postgres
mkdir -p ${VOLUMES}/cal.minet.net/minio

docker stack deploy --with-registry-auth --detach=false -c stack.yaml calendint
