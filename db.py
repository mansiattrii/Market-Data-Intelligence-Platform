import os

import psycopg
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

_conninfo = (
    f"host={os.environ['DB_HOST']} port={os.environ['DB_PORT']} "
    f"dbname={os.environ['DB_NAME']} user={os.environ['DB_USER']} "
    f"password={os.environ['DB_PASSWORD']}"
)

# open=False: opened explicitly from main.py's lifespan, so pool startup
# happens once at process start rather than lazily on first request.
pool = ConnectionPool(_conninfo, min_size=2, max_size=10, open=False)


def get_connection():
    # For one-shot scripts (ingest/run.py), not the API. A batch job
    # that opens one connection for its whole run has no need for the
    # pool, which exists to amortize connection setup across many
    # short-lived API requests in a long-running process.
    return psycopg.connect(_conninfo)
