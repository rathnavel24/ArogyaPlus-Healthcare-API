"""
Standalone MySQL connectivity check for the cPanel deployment.

Run this ON THE CPANEL SERVER (via SSH or cPanel > Terminal), from the
Application Root (same directory as alembic.ini / .env / passenger_wsgi.py),
with the app's virtualenv active — e.g.:

    source /home/<cpanel_user>/virtualenv/<path-to-app>/3.x/bin/activate
    cd ~/<path-to-app>/backend/app
    python test_db_connection.py

It reads DATABASE_URL the exact same way the real app does (via
app.core.config.settings, i.e. from .env), so a pass here means the deployed
app should be able to connect too. It never prints the password.
"""

import sys

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import settings

HINTS = {
    1045: "Access denied — wrong username/password, or this MySQL user was never granted access. "
    "Double-check the password in .env, and in cPanel > MySQL Databases confirm the user is "
    "listed under 'Users in Database' for this exact database with ALL PRIVILEGES.",
    1044: "Access denied for this user on this specific database — the user exists but isn't "
    "assigned to this database. Add it via cPanel > MySQL Databases > 'Add User to Database'.",
    1049: "Unknown database — the database name in DATABASE_URL doesn't match what cPanel created. "
    "cPanel prefixes both the DB name and username with your cPanel account name "
    "(e.g. 'cpaneluser_dbname'); check the exact spelling in cPanel > MySQL Databases.",
    2003: "Can't connect to the MySQL server at all — wrong host/port, or MySQL isn't reachable "
    "on that interface. If host is 'localhost' and this still fails, try '127.0.0.1' instead "
    "(PyMySQL treats 'localhost' as TCP, not a unix socket, unlike some MySQL clients) or ask "
    "your host for the unix socket path.",
    1130: "This host is not allowed to connect to this MySQL server — check cPanel > Remote MySQL "
    "if connecting from outside this server, though this shouldn't apply for 'localhost'.",
}


def explain(exc: Exception) -> str:
    if isinstance(exc, pymysql.err.MySQLError) and exc.args:
        errno = exc.args[0]
        hint = HINTS.get(errno)
        if hint:
            return f"MySQL error {errno}: {exc.args[1] if len(exc.args) > 1 else ''}\n  -> {hint}"
    return str(exc)


def main() -> int:
    url = make_url(settings.DATABASE_URL)
    masked = url.render_as_string(hide_password=True)
    print(f"DATABASE_URL (password hidden): {masked}")
    print(f"driver={url.drivername} host={url.host} port={url.port or 3306} "
          f"user={url.username} database={url.database}\n")

    if url.drivername != "mysql+pymysql":
        print(f"WARNING: expected drivername 'mysql+pymysql', got '{url.drivername}'. "
              "Did .env get updated to the MySQL URL?")

    print("[1/2] Raw PyMySQL connection (isolates auth/network errors from SQLAlchemy)...")
    try:
        conn = pymysql.connect(
            host=url.host,
            port=url.port or 3306,
            user=url.username,
            password=url.password or "",
            database=url.database,
            connect_timeout=5,
        )
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION()")
            (version,) = cur.fetchone()
        conn.close()
        print(f"    OK — connected, MySQL server version: {version}\n")
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED: {explain(exc)}\n")
        return 1

    print("[2/2] SQLAlchemy engine (mirrors app/db/session.py exactly)...")
    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 5})
        with engine.connect() as db_conn:
            result = db_conn.execute(text("SELECT 1")).scalar()
            tables = db_conn.execute(text("SHOW TABLES")).fetchall()
        print(f"    OK — SELECT 1 returned {result}")
        if tables:
            print(f"    {len(tables)} table(s) already present: {', '.join(t[0] for t in tables)}")
        else:
            print("    Database is empty — run 'alembic upgrade head' from this directory to create the schema.")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"    FAILED: {explain(exc)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
