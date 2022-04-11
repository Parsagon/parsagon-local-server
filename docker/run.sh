#!/usr/bin/env bash

# Example: ./docker/run.sh gabe.parsagon.io 1fc672c23791018556759fdfc5ab852606d99dff

fail_usage () {
	printf "Usage: ./docker/run.sh PARSAGON_HOST API_KEY\n"
	exit 1
}

if [ -z "$1" ]; then
	fail_usage
fi

if [ -z "$2" ]; then
	fail_usage
fi

PARSAGON_HOST=$1
shift

API_KEY=$2
shift

set -x
docker run -it --rm \
	-p 8080:80 \
	-e "PARSAGON_HOST=$PARSAGON_HOST" \
	-e "API_KEY=$API_KEY" \
	pslocal:latest "$@"
set +x
