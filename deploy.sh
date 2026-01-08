#!/bin/bash
if test -f ".env"; then
        set -a
        source .env
        set +a
fi

docker stack deploy --with-registry-auth --detach=false -c stack.yaml calendint
