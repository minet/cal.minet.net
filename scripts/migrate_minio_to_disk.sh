#!/usr/bin/env bash
# One-off copy of every object in the MinIO bucket into the uploads directory.
#
# Run on the swarm node hosting the MinIO task, as a user allowed to use docker
# and to write the destination directory:
#
#   ./migrate_minio_to_disk.sh <uploads dir> [minio container]
#   ./migrate_minio_to_disk.sh "$VOLUMES/cal.minet.net/uploads"
#
# Objects are streamed out of the MinIO container with `mc cat`, using the root
# credentials already set in that container. Files already present are skipped,
# so it is safe to run again (e.g. after the deploy, to catch late uploads).

set -euo pipefail

DEST="${1:?usage: $0 <uploads dir> [minio container]}"
CONTAINER="${2:-$(docker ps -q -f name=calendint_minio | head -n1)}"
BUCKET="${MINIO_BUCKET:-calendint}"

if [ -z "$CONTAINER" ]; then
    echo "No running calendint_minio container on this node, pass one as second argument." >&2
    exit 1
fi

# Read the credentials from the container config, without relying on tools inside it
container_env() {
    docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$CONTAINER" \
        | sed -n "s/^$1=//p"
}

urlencode() {
    local s="$1" out="" c i
    for (( i = 0; i < ${#s}; i++ )); do
        c="${s:i:1}"
        case "$c" in
            [a-zA-Z0-9.~_-]) out+="$c" ;;
            *) printf -v c '%%%02X' "'$c"; out+="$c" ;;
        esac
    done
    printf '%s' "$out"
}

USER_ENC="$(urlencode "$(container_env MINIO_ROOT_USER)")"
PASS_ENC="$(urlencode "$(container_env MINIO_ROOT_PASSWORD)")"

mc() {
    docker exec \
        -e "MC_HOST_src=http://$USER_ENC:$PASS_ENC@localhost:9000" \
        -e MC_CONFIG_DIR=/tmp/.mc \
        "$CONTAINER" mc "$@"
}

if ! mc --version >/dev/null 2>&1; then
    echo "mc is not available in container $CONTAINER." >&2
    exit 1
fi

mkdir -p "$DEST"
chmod 755 "$DEST"

# List first so a listing error (bad credentials, missing bucket) aborts the script
listing="$(mc ls --recursive --json "src/$BUCKET")"

copied=0 skipped=0 failed=0
while IFS= read -r key; do
    # Only flat names are served from disk (all uploads are <uuid>.<ext>)
    if [ -z "$key" ] || [[ "$key" == */* ]]; then
        echo "SKIP  '$key': nested object names are not served from disk"
        failed=$((failed + 1))
        continue
    fi
    if [ -e "$DEST/$key" ]; then
        skipped=$((skipped + 1))
        continue
    fi

    # Write under a temp name then rename, so nginx never serves a partial file
    tmp="$(mktemp -p "$DEST" .tmp-XXXXXX)"
    if mc cat "src/$BUCKET/$key" > "$tmp"; then
        chmod 644 "$tmp"
        mv -f "$tmp" "$DEST/$key"
        copied=$((copied + 1))
    else
        rm -f "$tmp"
        echo "FAIL  $key"
        failed=$((failed + 1))
    fi
done < <(printf '%s\n' "$listing" \
    | grep '"type":"file"' \
    | sed -n 's/.*"key":"\([^"]*\)".*/\1/p')

echo "copied=$copied skipped=$skipped failed=$failed"
[ "$failed" -eq 0 ]
