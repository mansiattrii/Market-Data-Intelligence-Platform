# Raw SQL only -- no HTTP concepts belong in this file. Each function takes
# an open connection and plain Python params, and returns plain dict rows.
from psycopg.rows import dict_row


def list_companies(conn, q, limit, offset):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT cik, ticker, name FROM companies
            WHERE %(q)s::text IS NULL OR ticker ILIKE %(q)s OR name ILIKE %(q)s
            ORDER BY ticker
            LIMIT %(limit)s OFFSET %(offset)s
            """,
            {"q": f"%{q}%" if q else None, "limit": limit, "offset": offset},
        )
        return cur.fetchall()


def get_company_by_ticker(conn, ticker):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            "SELECT cik, ticker, name, created_at FROM companies WHERE ticker = %s",
            (ticker,),
        )
        return cur.fetchone()


def get_metric_unit(conn, metric_key):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT unit FROM metrics WHERE metric_key = %s", (metric_key,))
        row = cur.fetchone()
        return row["unit"] if row else None


def get_metric_time_series(conn, cik, metric_key, start, end):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT period_start, period_end, fiscal_year, fiscal_period, value, form, filed_date
            FROM facts
            WHERE cik = %(cik)s AND metric_key = %(metric_key)s
              AND (%(start)s::date IS NULL OR period_end >= %(start)s)
              AND (%(end)s::date IS NULL OR period_end <= %(end)s)
            ORDER BY period_end
            """,
            {"cik": cik, "metric_key": metric_key, "start": start, "end": end},
        )
        return cur.fetchall()


def get_top_for_metric(conn, metric_key, period_end, limit):
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT c.ticker, c.name, f.value
            FROM facts f
            JOIN companies c ON c.cik = f.cik
            WHERE f.metric_key = %(metric_key)s AND f.period_end = %(period_end)s
            ORDER BY f.value DESC
            LIMIT %(limit)s
            """,
            {"metric_key": metric_key, "period_end": period_end, "limit": limit},
        )
        return cur.fetchall()
