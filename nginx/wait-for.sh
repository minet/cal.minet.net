#!/bin/sh
# Wait for services defined in WAIT_FOR_SERVICES environment variable
# Format: host:port host:port (space separated)

if [ -z "$WAIT_FOR_SERVICES" ]; then
  echo "No services to wait for."
  exit 0
fi

for service in $WAIT_FOR_SERVICES; do
  host=$(echo $service | cut -d: -f1)
  port=$(echo $service | cut -d: -f2)
  
  echo "Waiting for $host:$port..."
  # Timeout after 60 seconds loop to avoid infinite hang
  retries=60
  while ! nc -z $host $port; do
    retries=$((retries-1))
    if [ $retries -le 0 ]; then
       echo "Timeout waiting for $host:$port"
       exit 1
    fi
    sleep 2
  done
  echo "$host:$port is up!"
done
