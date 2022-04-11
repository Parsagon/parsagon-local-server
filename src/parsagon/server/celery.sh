export SECRET_KEY=$(base64 /dev/urandom | head -c50)
export HOST=0.0.0.0
export PRODUCTION=1
celery -A server worker -Q run_code
