# Business logic and validation. Deliberately raises plain Python
# exceptions, not HTTPException -- this file has no idea it's being called
# from a web request, which is what keeps it decoupled from api/routes.py.
from api import queries


class NotFoundError(Exception):
    pass


class ValidationError(Exception):
    pass


def search_companies(conn, q, limit, offset):
    return queries.list_companies(conn, q, limit, offset)


def get_company(conn, ticker):
    company = queries.get_company_by_ticker(conn, ticker.upper())
    if company is None:
        raise NotFoundError(f"No company found for ticker '{ticker}'")
    return company


def get_metric_series(conn, ticker, metric, start, end):
    company = queries.get_company_by_ticker(conn, ticker.upper())
    if company is None:
        raise NotFoundError(f"No company found for ticker '{ticker}'")

    unit = queries.get_metric_unit(conn, metric)
    if unit is None:
        raise NotFoundError(f"Unknown metric '{metric}'")

    if start is not None and end is not None and start > end:
        raise ValidationError("start date must not be after end date")

    points = queries.get_metric_time_series(conn, company["cik"], metric, start, end)
    return {
        "ticker": company["ticker"],
        "metric": metric,
        "unit": unit,
        "points": points,
    }


def get_top_metric(conn, metric, period_end, limit):
    unit = queries.get_metric_unit(conn, metric)
    if unit is None:
        raise NotFoundError(f"Unknown metric '{metric}'")

    results = queries.get_top_for_metric(conn, metric, period_end, limit)
    return {
        "metric": metric,
        "period_end": period_end,
        "results": results,
    }
