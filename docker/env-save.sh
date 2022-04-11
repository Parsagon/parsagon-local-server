#!/usr/bin/env bash

echo "export API_KEY=${API_KEY}; export PARSAGON_HOST=${PARSAGON_HOST};" > .env
echo "export PATH=${PATH}:/home/ubuntu/.local/bin" >> .env
