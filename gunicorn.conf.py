import os

# Bind to platform-provided PORT or default to 5000
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"

# Sensible defaults; can be overridden via env
workers = int(os.getenv('WEB_CONCURRENCY', '4'))
timeout = int(os.getenv('WEB_TIMEOUT', '120'))
graceful_timeout = int(os.getenv('WEB_GRACEFUL_TIMEOUT', '30'))
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')
accesslog = os.getenv('GUNICORN_ACCESSLOG', '-')  # '-' = stdout
errorlog = os.getenv('GUNICORN_ERRORLOG', '-')

