web: cd backend && STATIC_DIR=/app/backend/static PYTHONPATH=$PYTHONPATH:. gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120 --access-logfile - --error-logfile - --log-level info