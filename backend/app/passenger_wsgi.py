import os
import sys

# cPanel Passenger sets the process cwd to the Application Root (this directory,
# backend/app/ — same directory as alembic.ini and .env). Make sure it's on
# sys.path so `import app.main` resolves exactly like `uvicorn app.main:app`
# does locally, regardless of how Passenger invokes this file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from a2wsgi import ASGIMiddleware  # noqa: E402

from app.main import app as fastapi_app  # noqa: E402

# Passenger's Python support is WSGI-only; FastAPI/Starlette is ASGI.
# a2wsgi adapts the ASGI app to the WSGI callable Passenger expects.
# cPanel's "Application Entry point" field must be set to "application".
application = ASGIMiddleware(fastapi_app)
