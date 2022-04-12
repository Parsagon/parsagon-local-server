#!/usr/bin/env bash

service redis-server start
service nginx start
./env-save
service supervisor start
supervisorctl start all

# To keep the container running:
tail -f /var/log/redis/redis-server.log & \
tail -f /var/log/nginx/access.log & \
tail -f /var/log/nginx/error.log & \
tail -f /var/log/supervisor/celery-stderr.log & \
tail -f /var/log/supervisor/celery-stdout.log & \
tail -f /var/log/supervisor/daphne-stderr.log & \
tail -f /var/log/supervisor/daphne-stdout.log & \
tail -f /var/log/supervisor/supervisord.log 