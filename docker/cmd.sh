#!/usr/bin/env bash

service redis-server start
service nginx start
./env-save
service supervisor start
supervisorctl start all

# To keep the container running:
bash
