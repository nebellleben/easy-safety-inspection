#!/bin/sh
set -e

# Run based on SERVICE_TYPE environment variable
case "$SERVICE_TYPE" in
    bot)
        echo "Starting Telegram Bot worker..."
        exec python -m app.bot.worker
        ;;
    api|"")
        echo "Starting API server..."
        exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
        ;;
    *)
        echo "Unknown SERVICE_TYPE: $SERVICE_TYPE"
        echo "Defaulting to API server..."
        exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
        ;;
esac
