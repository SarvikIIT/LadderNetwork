from web.app import app

# Expose `app` for WSGI servers (e.g., Gunicorn)
__all__ = ["app"]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


