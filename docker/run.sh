#!/usr/bin/env bash

# Example: ./docker/run.sh 1fc672c23791018556759fdfc5ab852606d99dff

fail_usage () {
	printf "Usage: ./docker/run.sh API_KEY\n"
	exit 1
}

PARSAGON_HOST="host.docker.internal:8000"

if [ -z "$1" ]; then
	fail_usage
fi
API_KEY=$1
shift

set -x
docker run -it --rm \
	-p 8080:80 \
	-e "API_KEY=$API_KEY" \
	-e "PARSAGON_HOST=$PARSAGON_HOST" \
	--security-opt seccomp=./docker/chrome.json \
	--add-host=host.docker.internal:host-gateway \
	pslocal:latest "$@"
set +x