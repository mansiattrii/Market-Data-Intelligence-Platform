from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api import service
from api.schemas import CompanyDetail, CompanySummary, MetricTimeSeries, TopMetricResponse
from db import get_connection

router = APIRouter()


@router.get("/companies", response_model=list[CompanySummary])
def list_companies(q: Optional[str] = None, limit: int = Query(50, le=200), offset: int = 0):
    conn = get_connection()
    try:
        return service.search_companies(conn, q, limit, offset)
    finally:
        conn.close()


@router.get("/companies/{ticker}", response_model=CompanyDetail)
def get_company(ticker: str):
    conn = get_connection()
    try:
        return service.get_company(conn, ticker)
    except service.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    finally:
        conn.close()


@router.get("/companies/{ticker}/metrics/{metric}", response_model=MetricTimeSeries)
def get_metric_series(
    ticker: str,
    metric: str,
    start: Optional[date] = None,
    end: Optional[date] = None,
):
    conn = get_connection()
    try:
        return service.get_metric_series(conn, ticker, metric, start, end)
    except service.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except service.ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        conn.close()


@router.get("/metrics/{metric}/top", response_model=TopMetricResponse)
def get_top_metric(metric: str, period_end: date, limit: int = Query(10, le=100)):
    conn = get_connection()
    try:
        return service.get_top_metric(conn, metric, period_end, limit)
    except service.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    finally:
        conn.close()
