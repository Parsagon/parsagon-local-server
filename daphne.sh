export SECRET_KEY=$(base64 /dev/urandom | head -c50) && export PRODUCTION=1 && export HOST=$(dig @resolver4.opendns.com myip.opendns.com +short) && daphne -b 127.0.0.1 -p 8000 server.asgi:application
