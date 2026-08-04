import os
import sys
import threading

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
# a2wsgi adapts the ASGI app to the WSGI callable Passenger expects, by
# spinning up a background thread running its own asyncio event loop.
#
# That thread must NOT be created here at module import time: Passenger's
# default "smart" spawn method preloads this module once in a master process
# and then forks worker processes from it. A background thread doesn't
# survive fork() — any lock it held stays locked forever in the child with
# no thread left to release it, which hangs every single request. Deferring
# construction to the first real call means it happens inside the
# already-forked worker process instead, regardless of spawn method.
_asgi_app = None
_asgi_app_lock = threading.Lock()


def application(environ, start_response):
    global _asgi_app
    if _asgi_app is None:
        with _asgi_app_lock:
            if _asgi_app is None:
                _asgi_app = ASGIMiddleware(fastapi_app)
    return _asgi_app(environ, start_response)
