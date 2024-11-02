#!/bin/sh
export ENV=prod &&
    export FLASK_APP=mshauri &&
    flask create-db &&
    flask db upgrade &&
    exec gunicorn \
        --workers=4
        --bind 0.0.0.0:8000 \
        "mshauri:create_app()" \
        --forwarded-allow-ips='*'
