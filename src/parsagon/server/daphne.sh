export SECRET_KEY=$(base64 /dev/urandom | head -c50)
export HOST=0.0.0.0
export PRODUCTION=1
daphne -b 127.0.0.1 -p 8000 server.asgi:application
